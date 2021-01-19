from odoo import models, fields,_,api
from odoo.exceptions import UserError, ValidationError

class BankBalanceCheck(models.TransientModel):

    _inherit = 'bank.balance.check'

    check_balance_in_transit = fields.Float("Check balance in transit")
    balance_available = fields.Float("Balance Available")

    def verify_balance(self):
        account_balance = 0
        if not self.account_id:
            raise ValidationError("Please Configure default debit account into Bank Journal")

        if self.account_id:
            values = self.env['account.move.line'].search(
                [('account_id', '=', self.account_id.id), ('move_id.state', '=', 'posted')])
            check_req = self.env['check.log'].search([('checklist_id.checkbook_req_id.bank_id', '=', self.journal_id.id),
                                                      ('status', '=', 'Delivered')])
            total_check_amt = sum(x.check_amount for x in check_req)
            account_balance = sum(x.debit - x.credit for x in values)
            if account_balance >= self.total_amount:
                self.is_balance = True
                self.account_balance = account_balance
                self.minimum_balance = self.journal_id and self.journal_id.min_balance or 0
                self.required_balance = self.total_amount
                self.different_balance = account_balance - self.total_amount
                self.check_balance_in_transit = total_check_amt
                self.balance_available = account_balance - total_check_amt

                return {
                    'name': 'Balance',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_model': 'balance.check.wizard',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': {'default_account_balance': account_balance, 'default_is_balance': True,
                                'default_wizard_id': self.id},
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
                    'context': {'default_account_balance': account_balance, 'default_is_balance': False,
                                'default_wizard_id': self.id},
                }