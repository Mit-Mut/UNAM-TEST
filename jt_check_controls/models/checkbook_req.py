from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class CheckbookRequest(models.Model):

    _name = 'checkbook.request'
    _description = "Checkbook Request"

    name = fields.Char("Name", default="Checkbook Request")
    application_no = fields.Integer("Application No.")
    folio_legal = fields.Char("Folio Legal")
    appliaction_date = fields.Date("Application Date", default=datetime.today())
    bank_id = fields.Many2one("account.journal", string="Bank", domain=[('type', '=', 'bank')])
    bank_account_id = fields.Many2one("res.partner.bank", string="Bank Account")
    amount_checks = fields.Integer("Amount of Checks")
    applicant_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    observations = fields.Char("Observations")
    checkbook_no = fields.Char("Checkbook No.")
    intial_folio = fields.Integer("Initial Folio")
    final_folio = fields.Integer("Final Folio")
    confirmation_letter = fields.Binary("Confirmation Letter")
    are_test_prin_formats_sent = fields.Boolean("Are test print formats sent?")
    dependence_id = fields.Many2one('dependency', "Dependence")
    subdependence_id = fields.Many2one('sub.dependency', "Subdependence")
    area = fields.Char("Area", default="Financial Operations Department")
    number_of_folios = fields.Char("Number of Folios")
    print_sample_folio_number = fields.Char("Print Sample Folio Number")

    full_address = fields.Text("Full Address")
    check_receipt_date = fields.Date("Check Receipt Date")

    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'),
                              ('approved', 'Approved'), ('submitted', 'Submitted'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
                             ], string="Status", default='draft')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name or ''
            if 'from_approve_check' in self._context and rec.checkbook_no:
                name = rec.checkbook_no
            result.append((rec.id, name))
        return result

    @api.constrains('intial_folio', 'final_folio')
    def _check_amount(self):
        if ((self.final_folio - self.intial_folio) + 1) != self.amount_checks:
            raise ValidationError(_('Value of Amount of checks does not match.'))

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id and self.bank_id.bank_account_id:
            self.bank_account_id = self.bank_id.bank_account_id.id

    @api.model
    def default_get(self, fields):
        res = super(CheckbookRequest, self).default_get(fields)
        dependence = self.env['dependency'].search([('dependency', '=', '744')], limit=1)
        if dependence:
            res.update({'dependence_id': dependence.id})
            subdependence = self.env['sub.dependency'].search([('dependency_id', '=', dependence.id),
                                                               ('sub_dependency', '=', '01')], limit=1)
            if subdependence:
                res.update({'subdependence_id': subdependence.id})
        return res

    @api.model
    def create(self, vals):
        res = super(CheckbookRequest, self).create(vals)
        application_no = self.env['ir.sequence'].next_by_code('checkbook.application')
        res.application_no = application_no
        legal_folio = self.env['ir.sequence'].next_by_code('checkbook.legal.folio')
        year = datetime.today().year
        res.folio_legal = "DIOF / CTRLCHEQ / " + str(legal_folio) + "/" + str(year)
        return res

    def action_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def action_request(self):
        self.ensure_one()
        self.state = 'requested'

    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'

    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'

    def action_submit(self):
        self.ensure_one()
        self.state = 'submitted'

    def action_confirmed_reject(self):
        self.ensure_one()
        self.state = 'cancelled'

    def action_confirm(self):
        self.ensure_one()
        return {
            'name': _('Check Reception'),
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.checkbook',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_checklist(self):
        self.ensure_one()
        checklist = self.env['checklist'].search([('checkbook_req_id', '=', self.id)], limit=1)
        if checklist:
            return {
                'name': _('Cheklist'),
                'type': 'ir.actions.act_window',
                'res_model': 'checklist',
                'view_mode': 'form',
                'res_id': checklist.id
            }

    def get_checklist(self, checkbook):
        checklist = self.env['checklist'].search([('checkbook_req_id', '=', checkbook.id)], limit=1)
        return checklist

    def get_application_date(self, date):
        application = date
        if application:
            day = application.day
            month = application.month
            year = application.year
            month_name = ''
            if month == 1:
                month_name = 'Enero'
            elif month == 2:
                month_name = 'Febrero'
            elif month == 3:
                month_name = 'Marzo'
            elif month == 4:
                month_name = 'Abril'
            elif month == 5:
                month_name = 'Mayo'
            elif month == 6:
                month_name = 'Junio'
            elif month == 7:
                month_name = 'Julio'
            elif month == 8:
                month_name = 'Agosto'
            elif month == 9:
                month_name = 'Septiembre'
            elif month == 10:
                month_name = 'Octubre'
            elif month == 11:
                month_name = 'Noviembre'
            elif month == 12:
                month_name = 'Diciembre'

            return str(day) + ' de ' + month_name + ' de ' + str(year)

    def get_date(self):
        today = datetime.today().date()
        day = today.day
        month = today.month
        month_name = ''
        if month == 1:
            month_name = 'Enero'
        elif month == 2:
            month_name = 'Febrero'
        elif month == 3:
            month_name = 'Marzo'
        elif month == 4:
            month_name = 'Abril'
        elif month == 5:
            month_name = 'Mayo'
        elif month == 6:
            month_name = 'Junio'
        elif month == 7:
            month_name = 'Julio'
        elif month == 8:
            month_name = 'Agosto'
        elif month == 9:
            month_name = 'Septiembre'
        elif month == 10:
            month_name = 'Octubre'
        elif month == 11:
            month_name = 'Noviembre'
        elif month == 12:
            month_name = 'Diciembre'
        year = today.year
        return str(day) + ' de ' + month_name + ' de ' + str(year)

    def get_trade_configuration_1(self):
        trade = self.env['trades.config'].search([('job_template', '=', 'check_req_1')], limit=1)
        return trade

    def get_trade_configuration_2(self):
        trade = self.env['trades.config'].search([('job_template', '=', 'check_req_2')], limit=1)
        return trade

    def get_trade_configuration_3(self):
        trade = self.env['trades.config'].search([('job_template', '=', 'register_checks')], limit=1)
        return trade

class CheckList(models.Model):

    _name = 'checklist'
    _description = "Checklist"
    _rec_name = 'checkbook_no'

    checkbook_no = fields.Char("Checkbook No.")
    received_boxes = fields.Integer("Number of boxes received")
    check_per_box = fields.Integer("Checks per box")
    additional_checks = fields.Integer("Additional checks without cash")
    total_cash = fields.Integer("Total Checks")
    checklist_lines = fields.One2many('check.log', 'checklist_id', "List of checks")
    checkbook_req_id = fields.Many2one("checkbook.request", "Checkbook")

class CheckListLine(models.Model):

    _name = 'check.log'
    _description = "Checklist Line"
    _rec_name = 'folio'

    checklist_id = fields.Many2one("checklist", "Checkbook Request")
    folio = fields.Integer("Folio")
    bank_id = fields.Many2one('account.journal',"Bank")
    bank_account_id = fields.Many2one('res.partner.bank', "Bank Account")
    checkbook_no = fields.Char("Checkbook No")
    dependence_id = fields.Many2one('dependency', "Dependence")
    subdependence_id = fields.Many2one('sub.dependency', "Subdependence")
    reason_cancellation = fields.Text("Reason for cancellation")
    reason_retention = fields.Text("Reason for retention")
    date_printing = fields.Date("Printing Date")
    date_protection = fields.Date("Protection Date")
    date_expiration = fields.Date("Expiration Date")
    date_cancellation = fields.Date("Cancellation Date")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")
    check_amount = fields.Monetary("Check Amount", currency_field='currency_id')
    related_checks = fields.Char("Related Checks")
    module = fields.Selection([('General Directorate of Personnel', 'General Directorate of Personnel'),
                                   ('Payment coordination', 'Payment coordination'),
                                   ('Financial transaction', 'Financial transaction'),('ACATLAN', 'ACATLAN'),
                               ('ARAGON', 'ARAGON'), ('CUAUTITLAN', 'CUAUTITLAN'),
                               ('CUERNAVACA', 'CUERNAVACA'),
                               ('COVE', 'COVE'), ('IZTACALA', 'IZTACALA'),
                               ('JURIQUILLA', 'JURIQUILLA'), ('LION', 'LION'),
                               ('MORELIA', 'MORELIA'), ('YUCATAN', 'YUCATAN')], string="Module")
    status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                          ('Assigned for shipping', 'Assigned for shipping'),
                          ('Available for printing', 'Available for printing'),
                          ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                          ('In transit', 'In transit'), ('Sent to protection','Sent to protection'),
                          ('Protected and in transit','Protected and in transit'),
                          ('Protected', 'Protected'), ('Detained','Detained'),
                          ('Withdrawn from circulation','Withdrawn from circulation'),
                          ('Cancelled', 'Cancelled'),
                          ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                          ('On file','On file'),('Destroyed','Destroyed'),
                          ('Reissued', 'Reissued'),('Charged','Charged')])
    general_status = fields.Selection([('available', 'Available'),
                                       ('assigned', 'Assigned'),
                                       ('cancelled', 'Cancelled'),
                                       ('paid_out', 'Paid Out')])
    
    def write(self, vals):
        if self.status == 'Cancelled' and vals.get('status') in ('Checkbook registration', 'Assigned for shipping',
          'Available for printing', 'Printed', 'Delivered', 'In transit', 'Sent to protection',
           'Protected and in transit', 'Protected', 'Detained', 'Withdrawn from circulation'):
            raise ValidationError(_("You can't change check log from 'Cancelled' to following status: \n"
                                    "Checkbook registration \n"
                                    "Assigned for shipping \n"
                                    "Available for printing \n"
                                    "Printed \n"
                                    "Delivered \n"
                                    "In transit \n"
                                    "Sent to protection \n"
                                    "Protected and in transit \n"
                                    "Protected \n"
                                    "Detained \n"
                                    "Withdrawn from circulation \n"))
        res = super(CheckListLine, self).write(vals)
        return res

    def action_send_to_custody(self):
        cancel_checks = self.env['cancel.checks']
        for rec in self:
            if rec.status == 'Cancelled' and rec.dependence_id:
                cancel_checks.create({
                    'check_folio':rec.folio,
                    'dependency_id': rec.dependence_id.id,
                    'check_status': rec.status,
                    'bank_id': rec.bank_id.id if rec.bank_id else False,
                    'bank_account_id': rec.bank_account_id.id if rec.bank_account_id else False,
                    'checkbook_no': rec.bank_id.checkbook_no if rec.bank_id else False,
                    'check_log_id': rec.id
                    })

class ResBank(models.Model):

    _inherit = 'res.bank'

    check_validity = fields.Integer("Check Validity")