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
        if 'default_is_payroll_payment_request' in self._context:
            journal = self.env.ref('jt_payroll_payment.payroll_payment_request_jour')
        if 'default_is_different_payroll_request' in self._context:
            journal = self.env.ref('jt_payroll_payment.different_payroll_payment_request_jour')
        if 'default_is_project_payment' in self._context:
            journal = self.env.ref('jt_payroll_payment.project_payment_request_jour')

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
    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Method',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc.')
    
    document_type = fields.Selection([('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Many2one('policy.keys','UPA Key')
    upa_document_type = fields.Many2one('upa.document.type',string="Document Type UPA")
    batch_folio = fields.Integer("Batch Folio")
    vault_folio = fields.Char("Vault folio")
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


    @api.depends('payment_state','is_payroll_payment_request','is_payment_request','state')
    def get_conac_line_display(self):
        for rec in self:
            if rec.is_payroll_payment_request or rec.is_payment_request and rec.payment_state in ('draft','registered','approved_payment'):
                rec.show_conac_line_views = True
            else:
                rec.show_conac_line_views = False
                
    show_conac_line_views = fields.Boolean(string='Show Conac Line',compute="get_conac_line_display",store=True)
    
    def show_payment_line_ids(self):
        for rec in self:
            payments = self.env['account.payment'].search([('payment_request_id','=',rec.id),('state','not in',('draft','cancelled'))])
            for payment in payments:
                rec.payment_move_line_ids +=  payment.move_line_ids
            if not payments:
                rec.payment_move_line_ids = []
                
    payment_move_line_ids = fields.Many2many('account.move.line', 'rel_account_move_payment_line','payment_req_id','line_id',string='Payment Journal Items',
                                     compute="show_payment_line_ids")
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        res = super(AccountMove, self).copy(default)
        if res and res.is_payment_request:
            res.line_ids = False
        return res

    def unlink(self):
        for rec in self:
            if rec.is_payment_request and rec.payment_state not in ['draft']:
                raise UserError(_('You can delete only draft request'))
            if rec.is_payroll_payment_request and rec.payment_state not in ['draft']:
                raise UserError(_('You can delete only draft request'))
            if rec.is_different_payroll_request and rec.payment_state not in ['draft']:
                raise UserError(_('You can delete only draft request'))
            
        return super(AccountMove, self).unlink()

    @api.onchange('partner_id') 
    def onchange_partner_bak_account(self):
        if self.partner_id and self.partner_id.bank_ids:
            self.payment_bank_account_id = self.partner_id.bank_ids[0].id
            self.payment_bank_id = self.partner_id.bank_ids[0].bank_id and self.partner_id.bank_ids[0].bank_id.id or False
        else:
            self.payment_bank_account_id = False
            self.payment_bank_id = False 
                               
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
            conac_move = self.line_ids.filtered(lambda x:x.conac_move)            
            conac_move.sudo().unlink()
            for line in self.line_ids:
                line.coa_conac_id = False 
            
            move.payment_state = 'draft'

    def get_non_business_day(self,invoice_date,next_date):
        non_business_day = self.env['calendar.payment.regis'].search([('type_pay','=','Non Business Day'),('date','>=',invoice_date),('date','<=',next_date)])
        return non_business_day
     
    def get_patment_date(self,total_days,invoice_date):
        
        next_date =  invoice_date + timedelta(days=total_days)
        non_business_day_ids = self.get_non_business_day(invoice_date,next_date)
        if non_business_day_ids:
            next_date = next_date + timedelta(days=1)
            return self.get_patment_date(len(non_business_day_ids) - 1,next_date)   
        return next_date
     
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

    def write(self,vals):
        res = super(AccountMove,self).write(vals)
        if vals.get('payment_issuing_bank_id'):
            for rec in self:
                rec.employee_paryoll_ids.write({'payment_issuing_bank_id':rec.payment_issuing_bank_id and rec.payment_issuing_bank_id.id or False,
                                                'bank_acc_payment_insur_id' : rec.payment_issuing_bank_acc_id and rec.payment_issuing_bank_acc_id.id or False
                                                })
        
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

    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    vault_folio = fields.Char("Vault folio")

    @api.depends('price_subtotal','price_total')
    def get_price_tax_cr(self):
        for rec in self:
             
            if rec.currency_id and rec.company_id.currency_id and rec.currency_id != rec.company_id.currency_id:
                amount_currency = abs(rec.price_total - rec.price_subtotal)
                balance = self.currency_id._convert(amount_currency, rec.company_currency_id, rec.company_id, rec.move_id.date)
                rec.tax_price_cr = balance 
            else:
                balance = abs(rec.price_total - rec.price_subtotal)
                rec.tax_price_cr = balance
                
            
    tax_price_cr = fields.Monetary(string='Tax Price', store=True, readonly=True,
        currency_field='always_set_currency_id',compute="get_price_tax_cr")
    
    @api.model_create_multi
    def create(self, vals_list):
        lines = super(AccountMoveLine, self).create(vals_list)
        print 
        if any(lines.filtered(lambda x:x.move_id.is_payment_request and not x.egress_key_id and not x.exclude_from_invoice_tab)):
            raise ValidationError(_("Please add Egress Key into lines"))
        return lines
            
    def write(self,vals):
        result = super(AccountMoveLine,self).write(vals)
        if 'egress_key_id' in vals:
            if any(self.filtered(lambda x:x.move_id.is_payment_request and not x.egress_key_id and x.move_id.payment_state=='draft' and not x.exclude_from_invoice_tab)):
                raise ValidationError(_("Please add Egress Key into lines"))
             
            
#         if vals.get('account_id'):
#             for res in self:
#                 if res.account_id and res.account_id.coa_conac_id and not res.coa_conac_id:
#                     res.coa_conac_id = res.account_id.coa_conac_id.id
        return result

