from odoo import models, fields,_,api
from odoo.exceptions import UserError, ValidationError

class BankBalanceCheck(models.TransientModel):

    _name = 'bank.balance.check'    
    _description = 'Bank Balance Check'
    
    journal_id = fields.Many2one('account.journal','Bank Of Payment Issue')
    account_id = fields.Many2one('account.account','Bank Account')
    bank_account_id = fields.Many2one(related="journal_id.bank_account_id",string="Bank Account")
    total_amount = fields.Float('Total Amount')
    total_request = fields.Float('Total Request')
    is_balance = fields.Boolean('Balance')
    invoice_ids = fields.Many2many('account.move', 'account_invoice_payment_rel_bank_balance', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True)
    
    @api.onchange('journal_id')
    def onchange_jounal(self):
        if self.journal_id:
            self.account_id = self.journal_id.default_debit_account_id and self.journal_id.default_debit_account_id.id or False
        else:
            self.account_id = False
    
    def verify_balance(self):
        account_balance = 0
        if not self.account_id:
            raise ValidationError("Please Configure default debit account into Bank Journal")
        
        if self.account_id:
            values= self.env['account.move.line'].search([('account_id', '=', self.account_id.id),('move_id.state', '=', 'posted')])
            account_balance = sum(x.debit-x.credit for x in values)
            if account_balance >= self.total_amount:
                self.is_balance = True
                return {
                'name': 'Balance',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'balance.check.wizard',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'default_account_balance':account_balance,'default_is_balance':True,'default_wizard_id':self.id},
            } 
            else:
                self.is_balance = False
                return {
                'name': 'Balance',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'balance.check.wizard',
                'domain': [],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':{'default_account_balance':account_balance,'default_is_balance':False,'default_wizard_id':self.id},
                }
            
    def get_payment_data(self,rec,data):
        data.update({'payment_bank_id':rec.payment_bank_id and rec.payment_bank_id.id or False,
                     'payment_bank_account_id' : rec.payment_bank_account_id and rec.payment_bank_account_id.id or False,
                     'payment_issuing_bank_acc_id' : rec.payment_issuing_bank_acc_id and rec.payment_issuing_bank_acc_id.id or False,
                     'batch_folio' : rec.batch_folio,
                     'folio' : rec.folio,
                     'payment_state': 'for_payment_procedure',
                     'payment_request_id':rec.id,
                     }) 
        
        return data

    def create_journal_line_for_payment_procedure(self,invoice):
        #===== for the accounting impact of the "Accrued" Budget====#
        if invoice.journal_id and not invoice.journal_id.accured_credit_account_id \
            or not invoice.journal_id.conac_accured_credit_account_id \
            or not invoice.journal_id.accured_debit_account_id \
            or not invoice.journal_id.conac_accured_debit_account_id :
            raise ValidationError("Please configure UNAM and CONAC Accrued account in payment request journal!")
        
        invoice.line_ids = [(0, 0, {
                                     'account_id': invoice.journal_id.accured_credit_account_id and invoice.journal_id.accured_credit_account_id.id or False,
                                     'coa_conac_id': invoice.journal_id.conac_accured_credit_account_id and invoice.journal_id.conac_accured_credit_account_id.id or False,
                                     'credit': invoice.amount_total, 
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 }), 
                        (0, 0, {
                                     'account_id': invoice.journal_id.accured_debit_account_id and  invoice.journal_id.accured_debit_account_id.id or False,
                                     'coa_conac_id': invoice.journal_id.conac_accured_debit_account_id and invoice.journal_id.conac_accured_debit_account_id.id or False,
                                     'debit': invoice.amount_total,
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 })]
        #====== the Bank Journal, for the accounting impact of the "Exercised" Budget ======#
        if not self.journal_id.execercise_credit_account_id or not self.journal_id.conac_exe_credit_account_id \
            or not self.journal_id.execercise_debit_account_id or not self.journal_id.conac_exe_debit_account_id :
            raise ValidationError("Please configure UNAM and CONAC Exercised account in Bank journal!")
        
        invoice.line_ids = [(0, 0, {
                                     'account_id': self.journal_id.execercise_credit_account_id and self.journal_id.execercise_credit_account_id.id or False,
                                     'coa_conac_id': self.journal_id.conac_exe_credit_account_id and self.journal_id.conac_exe_credit_account_id.id or False,
                                     'credit': invoice.amount_total, 
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 }), 
                        (0, 0, {
                                     'account_id': self.journal_id.execercise_debit_account_id and self.journal_id.execercise_debit_account_id.id or False,
                                     'coa_conac_id': self.journal_id.conac_exe_debit_account_id and self.journal_id.conac_exe_debit_account_id.id or False,
                                     'debit': invoice.amount_total,
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 })]
        
        
        
    def schedule_payment(self):
        all_payments = self.env['account.payment']
        for rec in self.invoice_ids:
            rec.payment_issuing_bank_id = self.journal_id.id
            self.create_journal_line_for_payment_procedure(rec)
            payment_record = self.env['account.payment.register'].with_context(active_ids=rec.ids).create({'journal_id':self.journal_id.id,'invoice_ids':[(6, 0, rec.ids)]})
            Payment = self.env['account.payment']
            datas = payment_record.get_payments_vals()
            for data in datas:
                new_dict = self.get_payment_data(rec, data)
                payments = Payment.create(new_dict)
                all_payments += payments 
            rec.write({'payment_state': 'for_payment_procedure'})
        for payment in all_payments:
            payment.action_validate_payment_procedure()

        
        
        