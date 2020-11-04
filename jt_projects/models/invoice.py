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

    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_type', 'entry')
        journal_type = 'general'
        if move_type in self.get_sale_types(include_receipts=True):
            journal_type = 'sale'
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_type = 'purchase'

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(
                self._context['default_journal_id'])

            if move_type != 'entry' and journal.type != journal_type:
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (
                    move_type, journal.type))
        else:
            company_id = self._context.get('force_company',
                                           self._context.get('default_company_id', self.env.company.id))
            domain = [('company_id', '=', company_id),
                      ('type', '=', journal_type)]

            journal = None
            if self._context.get('default_currency_id'):
                currency_domain = domain + \
                    [('currency_id', '=', self._context['default_currency_id'])]
                journal = self.env['account.journal'].search(
                    currency_domain, limit=1)

            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)

            if not journal:
                error_msg = _(
                    'Please define an accounting miscellaneous journal in your company')
                if journal_type == 'sale':
                    error_msg = _(
                        'Please define an accounting sale journal in your company')
                elif journal_type == 'purchase':
                    error_msg = _(
                        'Please define an accounting purchase journal in your company')
                raise UserError(error_msg)

        if 'default_is_payment_request' in self._context:
            journal = self.env.ref('jt_supplier_payment.payment_request_jour')
        if 'default_is_payroll_payment_request' in self._context:
            journal = self.env.ref(
                'jt_payroll_payment.payroll_payment_request_jour')
        if 'default_is_different_payroll_request' in self._context:
            journal = self.env.ref(
                'jt_payroll_payment.different_payroll_payment_request_jour')

        return journal

    baneficiary_id = fields.Many2one(
        'hr.employee', string="Beneficiary of the payment")
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
    is_from_reschedule_payment = fields.Boolean(
        string="From Reschedule", default=False)
    baneficiary_key = fields.Char(
        'Baneficiary Code', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='partner_id.vat', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Char(
        "Category Key", related='partner_id.category_key', store=True)
    workstation_id = fields.Many2one(
        'hr.job', "Appointment", related='partner_id.workstation_id')
    folio = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type_id = fields.Many2one('operation.type', "Operation Type")
    date_receipt = fields.Datetime("Date and time of receipt")
    date_approval_request = fields.Date('Application Approval Date')
    administrative_forms = fields.Integer("Number of Administrative Forms")
    no_of_document = fields.Integer("Number of Documents")
    sheets = fields.Integer("Sheets")
    payment_method = fields.Selection(
        [('check', 'Check'), ('electronic_transfer', 'Electronic Transfer'), ('cash', 'Cash')])
    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Method',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc.')

    document_type = fields.Selection(
        [('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Many2one('policy.keys', 'UPA Key')
    upa_document_type = fields.Many2one(
        'upa.document.type', string="Document Type UPA")
    batch_folio = fields.Integer("Batch Folio")
    vault_folio = fields.Char("Vault folio")
    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one(
        'res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_id = fields.Many2one(
        'account.journal', "Payment issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one(
        related="payment_issuing_bank_id.bank_account_id", string="Payment issuing bank Account")
    responsible_id = fields.Many2one(
        'hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one(
        'hr.employee', 'Administrative Secretary')
    holder_of_dependency_id = fields.Many2one(
        'hr.employee', "Holder of the Dependency")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    user_registering_id = fields.Many2one('res.users')
    commitment_date = fields.Date("Commitment Date")
    reason_rejection_req = fields.Text("Reason for Rejecting Request")
    reason_rejection = fields.Text("Reason for Rejection")
    reason_cancellation = fields.Text("Reason for Cancellation")
    is_payment_request = fields.Boolean("Payment Request")
    type = fields.Selection(selection_add=[('payment_req', 'Payment Request')])
    dependence = fields.Many2one('dependency', string="Dependency")
    subdependence = fields.Many2one('sub.dependency', string='Sub Dependence')

    # More info Tab
    reason_for_expendiure = fields.Char("Reason for Expenditure/Trip")
    destination = fields.Char("Destination")
    origin_payment = fields.Char("Origin")
    provenance = fields.Text("Provenance")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="[('company_id', '=', company_id)]",
                                 default=_get_default_journal)
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_expend_id = fields.Many2one(
        'hr.employee', "Name of the responsible")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Char("Responsible category key")
    manager_job_id = fields.Many2one('hr.job', "Manager’s job")
    responsible_rfc = fields.Char(
        'VAT', related='responsible_expend_id.rfc', store=True)
    payment_line_ids = fields.One2many('account.move.line', 'payment_req_id')
    is_show_beneficiary_key = fields.Boolean(
        'Show Beneficiary Key', default=False)
    is_show_student_account = fields.Boolean(
        'Show Student Account', default=False)
    is_show_category_key = fields.Boolean('Show Category Key', default=False)
    is_show_appointment = fields.Boolean('Show Appointment', default=False)
    is_show_responsible = fields.Boolean('Show Responsible', default=False)
    diary = fields.Many2one('account.journal', string='Diary')
    is_show_holder_of_dependency = fields.Boolean(
        'Show holder_of_dependency', default=False)
    is_show_commitment_date = fields.Boolean(
        'Show Commitmet Date', default=False)
    is_show_turn_type = fields.Boolean('Show Turn Type', default=False)
    is_show_reason_for_expendiure = fields.Boolean(
        'reason_for_expendiure', default=False)
    is_show_destination = fields.Boolean('is_show_destination', default=False)
    is_show_origin = fields.Boolean('is_show_origin', default=False)
    is_zone_res = fields.Boolean('Show Zone Res', default=False)
    is_show_resposible_group = fields.Boolean(
        'Resposible Group', default=False)

    @api.depends('payment_state', 'is_payroll_payment_request', 'is_payment_request', 'state')
    def get_conac_line_display(self):
        for rec in self:
            if rec.is_payroll_payment_request or rec.is_payment_request and rec.payment_state in ('draft', 'registered', 'approved_payment'):
                rec.show_conac_line_views = True
            else:
                rec.show_conac_line_views = False

    def generate_folio(self):
        folio = ''
        if self.upa_key and self.upa_key.organization:
            folio += self.upa_key.organization + "/"
        if self.upa_document_type and self.upa_document_type.document_number:
            folio += self.upa_document_type.document_number + "/"
        folio += self.env['ir.sequence'].next_by_code('payment.folio')
        self.folio = folio

    def action_register(self):
        for move in self:
            move.generate_folio()
            if not self.commitment_date:
                today = datetime.today()
                current_date = today + timedelta(days=30)
                move.commitment_date = current_date
            move.payment_state = 'registered'


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    payment_req_id = fields.Many2one('account.move')
    egress_key_id = fields.Many2one("egress.keys", string="Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    other_amounts = fields.Monetary("Other Amounts")
    amount = fields.Monetary("Amount")
    price_payment = fields.Monetary("Price")
    sub_total_payment = fields.Monetary("Sub Total")
    tax = fields.Float("Tax")
    turn_type = fields.Char("Turn type")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    vault_folio = fields.Char("Vault folio")
