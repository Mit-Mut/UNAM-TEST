from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class BlankCheckRequest(models.Model):

    _name = 'blank.checks.request'
    _description = "Blank Check Requests"
    _rec_name = "application_no"

    application_no = fields.Char("Application No")
    dependence_id = fields.Many2one('dependency', "Dependence")
    subdependence_id = fields.Many2one('sub.dependency', "Subdependence")
    amount_checks = fields.Integer("Amount of Checks")
    reason_request = fields.Text("Reason for Request")
    applicant_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    are_test_prin_formats_sent = fields.Boolean("Are test print formats sent?")
    area = fields.Char("Area")
    number_of_folios = fields.Integer("Number of Folios")
    print_sample_folio_number = fields.Integer("Print Sample Folio Number")
    delivery_of_checks = fields.Binary("Office of delivery of checks to dependency")
    check_request = fields.Binary("Check Request")
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'),
                              ('approved', 'Approved'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
                              ], string="Status", default='draft')

    department = fields.Selection([('General Directorate of Personnel', 'General Directorate of Personnel'),
                                   ('Payment coordination', 'Payment coordination'),
                                   ('Financial transaction', 'Financial transaction'),
                                   ('ACATLAN', 'ACATLAN'),
                                   ('ARAGON', 'ARAGON'),
                                   ('CUAUTITLAN', 'CUAUTITLAN'),
                                   ('CUERNAVACA', 'CUERNAVACA'), ('COVE', 'COVE'),
                                   ('IZTACALA', 'IZTACALA'), ('JURIQUILLA', 'JURIQUILLA'),
                                   ('LION', 'LION'), ('MORELIA', 'MORELIA'), ('YUCATAN', 'YUCATAN')])
    bank_account_id = fields.Many2one('account.journal', "Bank Account")
    checkbook_req_id = fields.Many2one('checkbook.request',"Checkbook no")
    number_of_checks_auth = fields.Integer("Number of checks authorized")
    intial_folio = fields.Integer("Intial Folio")
    final_folio = fields.Integer("Final Folio")
    distribution_of_module_ids = fields.One2many('check.distribution.modules', 'request_id')

    @api.model
    def create(self, vals):
        res = super(BlankCheckRequest, self).create(vals)
        application_no = self.env['ir.sequence'].next_by_code('blank.check.application')
        year = datetime.today().year
        res.application_no = "DIOF / CTRLCHEQ / " + str(application_no) + "/" + str(year)
        return res

    @api.constrains('amount_checks')
    def _check_amount_checks(self):
        if self.dependence_id and self.subdependence_id:
            auth = self.env['check.authorized.dependency'].search([('dependency_id', '=', self.dependence_id.id),
                                                    ('subdependency_id', '=', self.subdependence_id.id)], limit=1)
            if auth and self.amount_checks > auth.max_authorized_checks:
                raise ValidationError(_('Value of Amount of checks does not more than authorized.'))

    def action_request(self):
        self.ensure_one()
        self.state = 'requested'

    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'

    def action_approve(self):
        self.ensure_one()
        return {
            'name': _('Check Authorization'),
            'type': 'ir.actions.act_window',
            'res_model': 'approve.blank.check',
            'view_mode': 'form',
            'target': 'new',
            'context': {'from_approve_check':1}
        }

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
        check_logs = self.env['check.log'].search([('checklist_id.checkbook_req_id', '=', self.checkbook_req_id.id),
                                                   ('folio', '>=', self.intial_folio),
                                                   ('folio', '<=', self.final_folio)])
        for log in check_logs:
            log.status = 'Assigned for shipping'
            log.module = self.department
        check_log = self.env['check.log'].search([('checklist_id.checkbook_req_id', '=', self.checkbook_req_id.id),
                                                   ('folio', '=', self.print_sample_folio_number)])
        if check_log:
            check_log.status = 'Cancelled'
            check_log.module = self.department

    def change_status_suthorized_checks(self):
        for rec in self:
            if rec.state == 'confirmed':
                check_logs = self.env['check.log'].search(
                    [('checklist_id.checkbook_req_id', '=', self.checkbook_req_id.id),
                     ('folio', '>=', self.intial_folio),
                     ('folio', '<=', self.final_folio)])
                for log in check_logs:
                    log.status = 'Available for printing'

    def action_apply_distribution(self):
        self.ensure_one()
        for rec in self.distribution_of_module_ids:
            check_logs = self.env['check.log'].search(
                [('checklist_id.checkbook_req_id', '=', self.checkbook_req_id.id),
                 ('folio', '>=', rec.intial_filio.folio),
                 ('folio', '<=', rec.final_folio.folio)])
            for log in check_logs:
                log.module = rec.module


class DistributionModules(models.Model):
    _name = 'check.distribution.modules'
    _description = "Distribution Of modules"

    request_id = fields.Many2one('blank.checks.request')
    checkbook_req_id = fields.Many2one('checkbook.request', related='request_id.checkbook_req_id', store=True)
    module = fields.Selection([('ACATLAN', 'ACATLAN'),
                               ('ARAGON', 'ARAGON'), ('CUAUTITLAN', 'CUAUTITLAN'),
                               ('CUERNAVACA','CUERNAVACA'),
                               ('COVE', 'COVE'), ('IZTACALA','IZTACALA'),
                               ('JURIQUILLA','JURIQUILLA'),('LION','LION'),
                               ('MORELIA','MORELIA'),('YUCATAN','YUCATAN')], string="Module")
    intial_filio = fields.Many2one('check.log', "Intial Folio")
    final_folio = fields.Many2one('check.log', "Final Folio")
    amounts_of_checks = fields.Integer("Amounts of Checks")

    @api.onchange('intial_filio', 'final_folio')
    def onchange_folios(self):
        self.amounts_of_checks = self.final_folio.folio - self.intial_filio.folio