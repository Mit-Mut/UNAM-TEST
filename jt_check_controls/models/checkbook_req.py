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
    bank_account_id = fields.Many2one("res.partner.bank", string="Bank Account", domain=[('type', '=', 'bank')])
    amount_checks = fields.Integer("Amount of Checks")
    applicant_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    observations = fields.Char("Observations")
    checkbook_no = fields.Char("Checkbook No.")
    intial_folio = fields.Char("Initial Folio")
    final_folio = fields.Char("Fianl Folio")
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
                               ('approved', 'Approved'), ('rejected', 'Rejected')], string="Status", default='draft')

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

    def action_request(self):
        self.ensure_one()
        self.state = 'requested'

    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'

    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'