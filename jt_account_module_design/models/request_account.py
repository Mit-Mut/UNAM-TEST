from odoo import models, fields, api,_


class RequestAccounts(models.Model):

    _inherit = 'request.accounts'
    _description = "Request to open account"
    
    bank_id = fields.Many2one('res.bank','Bank')

    @api.constrains('ministrations_amount')
    def check_ministrations_amount(self):
        return True

    @api.constrains('authorized_amount')
    def check_authorized_amount(self):
        return True
    

class AccountJournal(models.Model):

    _inherit = 'account.journal'

    def name_get(self):
        if 'from_account_design' in self._context:
            res = []
            for journal in self:
                bank_acc = journal.name
                if journal.bank_account_id:
                    bank_acc = journal.bank_account_id.acc_number
                res.append((journal.id, bank_acc))
        else:
            res = super(AccountJournal, self).name_get()
        return res
    
class AccountMove(models.Model):

    _inherit = 'account.move'

    programatic_code = fields.Boolean('Programmatic Code')
    ie_account = fields.Boolean('IEAccount')
    program_code_id = fields.Many2one('program.code','Program Code')
    account_ie_id = fields.Many2one('association.distribution.ie.accounts','I.E. Accounts')