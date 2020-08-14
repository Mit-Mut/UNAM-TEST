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
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type != journal_type:
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (
                move_type, journal.type))
        else:
            company_id = self._context.get('force_company',
                                           self._context.get('default_company_id', self.env.company.id))
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            journal = None
            if self._context.get('default_currency_id'):
                currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)

            if not journal:
                error_msg = _('Please define an accounting miscellaneous journal in your company')
                if journal_type == 'sale':
                    error_msg = _('Please define an accounting sale journal in your company')
                elif journal_type == 'purchase':
                    error_msg = _('Please define an accounting purchase journal in your company')
                raise UserError(error_msg)

        if 'default_is_payment_request' in self._context:
            journal = self.env.ref('jt_supplier_payment.payment_request_jour')

        return journal
    
    baneficiary_id = fields.Many2one('hr.employee', string="Beneficiary of the payment")
    payment_state = fields.Selection([('draft', 'Draft'),('registered','Registered'),
                                      ('approved_payment','Approved for payment'),
                                      ('for_payment_procedure','For Payment Procedure'),
                                      ('paid','Paid'),
                                      ('payment_not_applied','Payment not Applied'),
                                      ('done','Done'),
                                      ('rejected','Rejected'),
                                      ('cancel','Cancel')],default='draft',copy=False)
    is_from_reschedule_payment = fields.Boolean(string="From Reschedule",default=False)
    baneficiary_key = fields.Char('Baneficiary Key', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='partner_id.vat', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Char("Category Key", related='partner_id.category_key', store=True)
    workstation_id = fields.Many2one('hr.job', "Appointment", related='partner_id.workstation_id')
    folio = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type_id = fields.Many2one('operation.type', "Operation Type")
    date_receipt = fields.Datetime("Date of Receipt")
    date_approval_request  = fields.Date("Date Approval Request")
    administrative_forms = fields.Integer("Number of Administrative Forms")
    no_of_document = fields.Integer("Number of Documents")
    sheets = fields.Integer("Sheets")
    payment_method = fields.Selection([('check', 'Check'), ('electronic_transfer', 'Electronic Transfer'),('cash','Cash')])
    document_type = fields.Selection([('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Many2one('policy.keys','UPA Key')
    upa_document_type = fields.Many2one('upa.document.type',string="Document Type UPA")
    batch_folio = fields.Integer("Batch Folio")
    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one('res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_id = fields.Many2one('account.journal', "Payment issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one(related="payment_issuing_bank_id.bank_account_id", string="Payment issuing bank Account")
    responsible_id = fields.Many2one('hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one('hr.employee', 'Administrative Secretary')
    holder_of_dependency_id = fields.Many2one('hr.employee', "Holder of the Dependency")
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

    # More info Tab
    reason_for_expendiure = fields.Char("Reason for Expenditure/Trip")
    destination = fields.Char("Destination")
    origin_payment = fields.Char("Origin")
    provenance = fields.Text("Provenance")
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_expend_id = fields.Many2one('hr.employee', "Name of the responsible")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Char("Responsible category key")
    manager_job_id = fields.Many2one('hr.job', "Manager’s job")
    responsible_rfc = fields.Char('VAT',related='responsible_expend_id.rfc', store=True)
    payment_line_ids = fields.One2many('account.move.line', 'payment_req_id')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        default=_get_default_journal)
    
    is_show_beneficiary_key = fields.Boolean('Show Beneficiary Key',default=False)
    is_show_student_account = fields.Boolean('Show Student Account',default=False)
    is_show_category_key = fields.Boolean('Show Category Key',default=False)
    is_show_appointment = fields.Boolean('Show Appointment',default=False)
    is_show_responsible = fields.Boolean('Show Responsible',default=False)
    is_show_holder_of_dependency = fields.Boolean('Show holder_of_dependency',default=False)
    is_show_commitment_date = fields.Boolean('Show Commitmet Date',default=False)
    is_show_turn_type = fields.Boolean('Show Turn Type',default=False)
    is_show_reason_for_expendiure = fields.Boolean('reason_for_expendiure',default=False)
    is_show_destination = fields.Boolean('is_show_destination',default=False)
    is_show_origin = fields.Boolean('is_show_origin',default=False)
    is_zone_res = fields.Boolean('Show Zone Res',default=False)
    is_show_resposible_group = fields.Boolean('Resposible Group',default=False)

                    
    @api.onchange('operation_type_id')
    def onchange_operation_type_id(self):
        if self.operation_type_id and self.operation_type_id.name:
            my_str1 = "Reimbursement to third parties"
            my_str2 = "Airline tickets"
            my_str3 = "Reimbursement to the fixed fund"
            my_str4 = "Reimbursement to third parties, verification of administration"
            my_str5 = "Payment to supplier"
            is_show_turn_type= False
            is_show_reason_for_expendiure = False
            is_show_destination = False
            is_show_origin = False
            is_zone_res = False
            is_show_resposible_group = False
            if self.operation_type_id.name.upper() == my_str1.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str2.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str3.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str4.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str5.upper():
                self.is_show_beneficiary_key = True
                self.is_show_commitment_date = True
                is_show_turn_type = True
            else:
                self.is_show_beneficiary_key = False
            
            self.is_show_turn_type = is_show_turn_type
            str_account = "Fellows"
            if self.operation_type_id.name.upper() == str_account.upper():
                self.is_show_student_account = True
            else:
                self.is_show_student_account = False

            str_category1 = "Viaticals"
            str_category2 = "Viatical expenses replacement of resources to the fixed fund"
            if self.operation_type_id.name.upper() == str_category1.upper():
                self.is_show_category_key = True
                self.is_show_appointment = True
                is_show_reason_for_expendiure = True
                is_zone_res = True
            elif self.operation_type_id.name.upper() == str_category2.upper():
                self.is_show_category_key = True
                self.is_show_appointment = True
                is_zone_res = True
            else:
                self.is_show_category_key = False
                self.is_show_appointment = False
            
            #====For is_show_responsible =====#
            str_responsible1 = "Scholarship recipients"
            str_responsible2 = "Third party reimbursement"
            str_responsible3 = "Airline tickets"
            str_responsible4 = "Accounts payable creation"
            if self.operation_type_id.name.upper() == str_responsible1.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible2.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible3.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible4.upper():
                self.is_show_responsible = True
                is_show_resposible_group = True
                is_show_reason_for_expendiure = True
            else:
                self.is_show_responsible = False
            
            #======is_show_holder_of_dependency =====:
            str_holder1 = "Field work and school practices"
            str_holder2 = "Reimbursement to the fixed fund"
            str_holder3 = "Reimbursement to third parties, proof of administration"
            str_holder4 = "Exchange expenses"
            str_holder5 = "Expenses of per diem replacement of resources to the fixed fund"
            str_holder6 = "Per diem"
            str_holder7 = "Payment to supplier"
            if self.operation_type_id.name.upper() == str_holder1.upper():
                self.is_show_holder_of_dependency = True
                is_show_reason_for_expendiure = True
                is_show_destination = True
                is_show_resposible_group = True
            elif self.operation_type_id.name.upper() == str_holder2.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder3.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder4.upper():
                self.is_show_holder_of_dependency = True
                is_show_reason_for_expendiure=True
                is_show_origin = True
                is_show_resposible_group = True
            elif self.operation_type_id.name.upper() == str_holder5.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder6.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder7.upper():
                self.is_show_holder_of_dependency = True
            else:
                self.is_show_holder_of_dependency = False
            
            # ===== For the is_show_reason_for_expendiure ====#
            str_expendiure = "Travel expenses replacement of resources to the fixed fund"
            if self.operation_type_id.name.upper() == str_expendiure.upper():      
                is_show_reason_for_expendiure = True
                is_show_destination = True
            str_destination = "Travel expenses"
            if self.operation_type_id.name.upper() == str_destination.upper():
                is_show_destination = True
                
            self.is_show_reason_for_expendiure = is_show_reason_for_expendiure
            self.is_show_destination = is_show_destination 
            self.is_show_origin = is_show_origin
            self.is_zone_res = is_zone_res
            self.is_show_resposible_group = is_show_resposible_group
            
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        if self.state == 'draft':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.type]
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name
        return (draft_name or self.name) + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    def generate_folio(self):
        folio = ''
        if self.upa_key and self.upa_key.organization:
            folio += self.upa_key.organization+"/"
        if self.upa_document_type and  self.upa_document_type.document_number:
            folio += self.upa_document_type.document_number +"/"
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

    def action_reschedule(self):
        for move in self:
            move.is_from_reschedule_payment = True
            move.payment_issuing_bank_id = False
            move.payment_state = 'registered'        

    # def check_operation_name(self):
    #     if self.operation_type_id and self.operation_type_id.name:
    #         my_str = "Payment to supplier"
    #         if self.operation_type_id.name.upper() == my_str.upper():
    #             return True
    #
    #     return False

    @api.depends('name', 'state')
    def name_get(self):
        res = super(AccountMove,self).name_get()
        if self.env.context and self.env.context.get('show_for_bank_transfer', False):
            result = []
            for rec in self:
                if rec.batch_folio:
                    name = str(rec.batch_folio) or ''
                    result.append((rec.id, name))
                else:
                    result.append((rec.id, rec._get_move_display_name(show_ref=True)))
            return result and result or res
        else:
            return res

#     def remove_journal_line(self):
#         if self.

#     @api.onchange('invoice_line_ids')
#     def _onchange_invoice_line_ids(self):
#         res = super(AccountMove,self)._onchange_invoice_line_ids()
#         if self.is_payment_request:
#          cc   #{'subtype_ids': [(3, sid) for sid in old_sids]}
#             #self.line_ids = [(3, sid) for sid in self.line_ids.ids]
#             self.line_ids = [(5,self.line_ids.ids)]
#         return res
            
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



#     @api.model
#     def create(self, vals):
#         result = super(AccountMoveLine, self).create(vals)
#         if result.move_id and result.move_id.is_payment_request:
#             result.coa_conac_id = result.account_id and result.account_id.coa_conac_id and result.account_id.coa_conac_id.id or False
#             result.conac_move = True  
#         return result
#     
#     
#     def write(self, vals):
#         result = super(AccountMoveLine, self).write(vals)
#         if vals.get('account_id',False):
#             for rec in self:
#                 if rec.move_id and rec.move_id.is_payment_request:
#                     rec.coa_conac_id = rec.account_id and rec.account_id.coa_conac_id and rec.account_id.coa_conac_id.id or False
#                     rec.conac_move = True  
#         return result




