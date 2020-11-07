# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class AccountMove(models.Model):

    _inherit = 'account.move'

    parnter_id = fields.Many2one(
        'res.partner', string="Beneficiary of the payment")
    baneficiary_key = fields.Char(
        'Baneficiary Code', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='parnter_id.vat', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Char(
        "Category Key", related='partner_id.category_key', store=True)
    workstation_id = fields.Many2one(
        'hr.job', "Appointment", related='partner_id.workstation_id')
    folio_against_reciept = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type_id = fields.Many2one('operation.type', "Operation Type")
    date_receipt = fields.Datetime("Date and time of receipt")
    date_approval_request = fields.Date('Application Approval Date')
    administrative_forms = fields.Integer("Number of Administrative Forms")
    no_of_document = fields.Integer("Number of Documents")
    sheets = fields.Integer("Sheets")
    payment_state = fields.Selection([('draft', 'Draft'), ('registered', 'Registered'),
                                      ('approved_payment', 'Approved for payment'),
                                      ('for_payment_procedure',
                                       'For Payment Procedure'),
                                      ('paid', 'Paid'),
                                      ('payment_not_applied',
                                       'Payment not Applied'),
                                      ('done', 'Done'),
                                      ('rejected', 'Rejected'),
                                      ('cancel', 'Cancel')], default='draft', copy=False)

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Method',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc.')

    document_type = fields.Selection(
        [('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Many2one('policy.keys', 'UPA Code')
    upa_document_type = fields.Many2one(
        'upa.document.type', string="Document Type UPA")
    batch_folio = fields.Integer("Batch Folio")
    vault_folio = fields.Char("Vault folio")
    payment_bank_id = fields.Many2one('res.bank', "Bank receiving payment")
    payment_bank_account_id = fields.Many2one(
        'res.partner.bank', "Payment receipt bank account")
    payment_issuing_bank_id = fields.Many2one(
        'account.journal', "Payment issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one(
        related="payment_issuing_bank_id.bank_account_id", string="Payment issuing bank Account")
    responsible_id = fields.Many2one(
        'hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one(
        'hr.employee', 'Administrative Secretary')
    holder_of_unit_id = fields.Many2one(
        'hr.employee', "Holder of the Unit")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    user_registering_id = fields.Many2one(
        'res.users', string='User who registers')
    diary = fields.Many2one('account.journal', string='Diary')
    reason_rejection_req = fields.Text(
        "Reason for Application Rejection", help="Budget insufficiency")
    reason_rejection = fields.Text("Reason for Rejection")
    reason_cancellation = fields.Text("Reason for Cancellation")
    dependence = fields.Many2one('dependency', string="Dependency")
    subdependence = fields.Many2one('sub.dependency', string='Sub Dependence')
    leaves = fields.Integer('Leaves')
    project_code = fields.Char('Project Code')
    exchange_rate = fields.Char('Exchange Rate')
    foreign_currency_amount = fields.Monetary('Foreign currency amount')
    project_number_id = fields.Many2one(
        'project.project', string='Project Number')
    agreement_number = fields.Char(
        related='project_number_id.number_agreement', string='Agreement Number')
    stage = fields.Char(
        related='project_number_id.stage_identifier', string='Stage')
    excercise = fields.Char('excercise')
    project_key = fields.Char('Project Key')
    invoice_vault_folio = fields.Char('Invoice vault folio')
    status = fields.Selection(
        [('accept', 'Accepted'), ('reject', 'Rejected')], string='Status')
    is_project_payment = fields.Boolean('Is Project Payment', default=True)
    line = fields.Integer("Line")
    previous = fields.Monetary('Previous')

    # More info Tab
    reason_for_expendiure = fields.Char("Reason for Expenditure/Trip")
    destination = fields.Char("Destination")
    origin_payment = fields.Char("Origin")
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_id = fields.Many2one(
        'hr.employee', "Responsible Name")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Char("Responsible category key")
    responsible_rfc = fields.Char(
        'VAT', related='responsible_id.rfc', store=True)
    responsible_job_position = fields.Many2one(
        'hr.job', 'Responsible job position')
    payment_line_ids = fields.One2many('account.move.line', 'payment_req_id')

    def generate_folio(self):
        folio = ''
        if self.upa_key and self.upa_key.organization:
            folio += self.upa_key.organization + "/"
        if self.upa_document_type and self.upa_document_type.document_number:
            folio += self.upa_document_type.document_number + "/"
        folio += self.env['ir.sequence'].next_by_code('payment.folio')
        self.folio = folio

    def action_cancel_budget(self):
        self.ensure_one()
        self.payment_state = 'cancel'
        self.button_cancel()

    def button_cancel(self):
        for record in self:
            if record.is_payment_request or record.is_payroll_payment_request:
                if record.payment_state == 'cancel':
                    record.cancel_payment_revers_entry()
                    record.add_budget_available_amount()
        return super(AccountMove, self).button_cancel()

    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
        self.button_draft()
        conac_move = self.line_ids.filtered(lambda x: x.conac_move)
        conac_move.sudo().unlink()
        for line in self.line_ids:
            line.coa_conac_id = False

        self.add_budget_available_amount()

    def cancel_payment_revers_entry(self):
        revers_list = []
        for line in self.line_ids:
            revers_list.append((0, 0, {
                'account_id': line.account_id.id,
                'coa_conac_id': line.coa_conac_id and line.coa_conac_id.id or False,
                'credit': line.debit,
                'debit': line.credit,
                'exclude_from_invoice_tab': True,
                'conac_move': line.conac_move,
                'name': 'Reversa',
                'currency_id': line.currency_id and line.currency_id.id or False,
                'amount_currency': line.amount_currency,
            }))
        self.line_ids = revers_list

    def action_register(self):
        for move in self:
            move.generate_folio()
            move.payment_state = 'registered'


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    concept = fields.Char('Concept')
    payment_req_id = fields.Many2one('account.move')
    bill = fields.Many2one('account.account')
    programatic_code_id = fields.Many2one(
        'program.code', string='Programmatic Code')
    egress_key_id = fields.Many2one("egress.keys", string="Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    vat = fields.Char('Vat')
    retIVA = fields.Char('RetIVA')
    turn_type = fields.Char("Turn type")
    other_amounts = fields.Monetary("Other Amounts")
    # price_payment = fields.Monetary("Price")
