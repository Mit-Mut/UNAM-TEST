from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one('res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_acc_id = fields.Many2one('res.partner.bank', "Payment issuing bank Account")
    batch_folio = fields.Integer("Batch Folio")
    folio = fields.Char("Folio against Receipt")
    reason_for_rejection = fields.Text('Reason For Rejection')
    reason_for_cancel = fields.Text('Reason For Cancellation')
    payment_state = fields.Selection([('draft', 'Draft'), 
                              ('for_payment_procedure','For Payment Procedure'),
                               ('posted', 'Validated'), 
                              ('reconciled', 'Reconciled'), 
                              ('rejected','Rejected'),
                              ('cancelled', 'Cancelled')], 
                              readonly=True, default='draft', copy=False, string="Status")
 
    banamex_description = fields.Char('Description',size=24)
    banamex_concept = fields.Char('Concept',size=34)
    banamex_reference = fields.Char('Reference',size=10)
    
    net_cash_reference = fields.Char('Reference',size=7)
    net_cash_availability = fields.Selection([('SPEI','SPEI'),('CECOBAN','CECOBAN')],string='Availability')
    
    sit_file_key = fields.Char('File Key')
    sit_operation_code = fields.Selection([('payment_on_account_bancomer','Payment on account bancomer'),
                                           ('payment_interbank','Payment interbank account next day')],string="Operation Code")
    sit_reference =fields.Char(size=25,string="SIT Reference")
    sit_reason_for_payment = fields.Char(size=37,string="Reason For Payment")
    sit_additional_data = fields.Char('Additional Data')
    
    santander_payment_concept = fields.Text('Payment Concept')
    
    hsbc_reference = fields.Char('HSBC Reference',size=40)
    
    jp_method = fields.Selection([('WIRES','WIRES'),('BOOKTX','BOOKTX')],string='Method')
    jp_bank_transfer = fields.Selection([('non_financial_institution','Non Financial Institution'),
                                         ('financial_institution','Financial Institutions')
                                         ],string="Bank To Bank Transfer")
    jp_id_type = fields.Selection([('clabe','CLABE'),
                                    ('debit_card','Debit Card'),
                                    ('vostro','Vostro')
                                         ],string="ID Type Beneficiary")
    jp_id_type_beneficiary_bank = fields.Selection([('None','None'),
                                    ('SPEI','SPEI'),
                                    ('SWIFT','SWIFT')
                                         ],string="ID Type Beneficiary Bank")
    jp_charges = fields.Selection([('shared','Shared'),
                                    ('beneficiary','Beneficiary'),
                                    ('remitter','Remitter')
                                         ],string="Charges")
    jp_drawdown_type = fields.Selection([('WIRE','WIRE'),
                                    ('BOOK','BOOK'),('Drawdown','Drawdown')],string="Drawdown Type")
    
    jp_payment_concept = fields.Char('Payment Concept')
    
    payment_request_id = fields.Many2one('account.move','circular')
    
    @api.constrains('banamex_reference')
    def _check_banamex_reference(self):
        if self.banamex_reference and not str(self.banamex_reference).isnumeric():
            raise ValidationError(_('The Banamex Reference must be numeric value'))

    def cancel(self):
        result = super(AccountPayment,self).cancel()
        if self.env.context and self.env.context.get('call_from_reject',False):
            return result
        self.write({'payment_state': 'cancelled'})
        return result

    def action_validate_payment_procedure(self):
        for rec in self:
            if not rec.name:
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                
                    rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                    if not rec.name and rec.payment_type != 'transfer':
                        raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
            rec.payment_state = 'for_payment_procedure'            

    def action_reschedule_payment_procedure(self):
        for payment in self:
            payment.action_draft()
            payment.payment_state = 'for_payment_procedure'
        
    def create_journal_for_paid(self,invoice):
        #==== he Bank Journal will be taken, corresponding to the “Paid” accounting moment ===#
        invoice.line_ids = [(0, 0, {
                                     'account_id': self.journal_id.paid_credit_account_id and self.journal_id.paid_credit_account_id.id or False,
                                     'coa_conac_id': self.journal_id.conac_paid_credit_account_id and self.journal_id.conac_paid_credit_account_id.id or False,
                                     'credit': invoice.amount_total, 
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 }), 
                        (0, 0, {
                                     'account_id': self.journal_id.paid_debit_account_id and self.journal_id.paid_debit_account_id.id or False,
                                     'coa_conac_id': self.journal_id.conac_paid_debit_account_id and self.journal_id.conac_paid_debit_account_id.id or False,
                                     'debit': invoice.amount_total,
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 })]
    
    def post(self):
        result = super(AccountPayment,self).post()
        self.write({'payment_state': 'posted'})
        for payment in self:
            for inv in payment.invoice_ids:
                if inv.invoice_payment_state == 'paid':
                    inv.payment_state = 'paid'
                    payment.create_journal_for_paid(inv)
            is_supplier_payment = payment.invoice_ids.filtered(lambda x:x.is_payment_request)
            if is_supplier_payment:
                for line in payment.move_line_ids:
                    line.coa_conac_id = line.account_id and line.account_id.coa_conac_id and line.account_id.coa_conac_id.id or False
                    line.conac_move = True  
            payment.banamex_concept = payment.name
        return result
 
    def action_draft(self):
        result = super(AccountPayment,self).action_draft()
        self.write({'payment_state': 'draft'})
        return result
               
    def action_register_payment(self):
        res =super(AccountPayment,self).action_register_payment()
        
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        
        record_ids = self.env['account.move'].browse(active_ids)
        if not record_ids or any(invoice.payment_state != 'approved_payment' and invoice.is_payment_request for invoice in record_ids):
            raise UserError(_("You can only register payment for  Approved for payment request"))
#         if not record_ids or any(invoice.state != 'posted' for invoice in record_ids):
#             raise UserError(_("You can only register payments for open invoices"))
        
        record_ids = record_ids.filtered(lambda x:x.is_payment_request and x.is_invoice(include_receipts=True))
        if record_ids:
            payment_issuing_bank_id = record_ids.mapped('payment_issuing_bank_id')
            if len(payment_issuing_bank_id) != 1 :
                raise UserError(_("You can not register payment for multiple Payment issuing Bank"))
            
            amount = self._compute_payment_amount(record_ids, record_ids[0].currency_id, record_ids[0].journal_id,fields.Date.today())
            return {
                'name': _('Schedule Payment'),
                'res_model':'bank.balance.check',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_supplier_payment.view_bank_balance_check').id,
                'context': {'default_journal_id':payment_issuing_bank_id.id,'default_total_amount': abs(amount),'default_total_request':len(record_ids),'default_invoice_ids': [(6, 0, record_ids.ids)]},
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            
        else:
            return res
