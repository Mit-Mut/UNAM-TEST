from odoo import models, fields, api, _
from datetime import datetime

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
    area = fields.Char("Area", default="Are test print formats sent?")
    number_of_folios = fields.Char("Number of Folios")
    print_sample_folio_number = fields.Char("Print Sample Folio Number")

    full_address = fields.Text("Full Address")
    check_receipt_date = fields.Date("Check Receipt Date")

    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'),
                              ('approved', 'Approved'), ('submitted', 'Submitted'),
                              ('confirmed', 'Confirmed'),
                              ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
                             ], string="Status", default='draft')

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

class CheckList(models.Model):

    _name = 'checklist'
    _description = "Checklist"
    _rec_name = 'checkbook_no'

    checkbook_no = fields.Char("Checkbook No.")
    received_boxes = fields.Integer("Number of boxes received")
    check_per_box = fields.Integer("Checks per box")
    additional_checks = fields.Integer("Additional checks without cash")
    total_cash = fields.Integer("Total Checks")
    checklist_lines = fields.One2many('checklist.line', 'checklist_id', "List of checks")
    checkbook_req_id = fields.Many2one("checkbook.request", "Checkbook")

class CheckListLine(models.Model):

    _name = 'checklist.line'
    _description = "Checklist Line"

    checklist_id = fields.Many2one("checklist", "Checklist")
    folio = fields.Integer("Folio")
    status = fields.Char("Status")