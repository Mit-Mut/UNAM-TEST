from odoo import models, fields,_,api
from odoo.exceptions import UserError, ValidationError

class BankBalanceCheck(models.TransientModel):

    _name = 'bank.balance.check'    
    _description = 'Bank Balance Check'
    
    journal_id = fields.Many2one('account.journal','Bank Of Payment Issue')
    account_id = fields.Many2one('account.account','Bank Account')
    total_amount = fields.Float('Total Amount')
    total_request = fields.Float('Total Request')
    is_balance = fields.Boolean('Balance')
    invoice_ids = fields.Many2many('account.move', 'account_invoice_payment_rel_bank_balance', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True)
    
    @api.onchange('journal_id')
    def onchange_jounal(self):
        if self.journal_id:
            self.account_id = self.journal_id.default_debit_account_id and self.journal_id.default_debit_account_id.id or False
        else:
            self.journal_id = False
    
    def verify_balance(self):
        account_balance = 0
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
                     'folio' : rec.folio
                     }) 
        
        return data
    
    def schedule_payment(self):
        for rec in self.invoice_ids:
            payment_record = self.env['account.payment.register'].with_context(active_ids=rec.ids).create({'journal_id':self.journal_id.id,'invoice_ids':[(6, 0, rec.ids)]})
            Payment = self.env['account.payment']
            datas = payment_record.get_payments_vals()
            for data in datas:
                new_dict = self.get_payment_data(rec, data)
                payments = Payment.create(new_dict)
            rec.write({'payment_state': 'for_payment_procedure'})
        
        
        