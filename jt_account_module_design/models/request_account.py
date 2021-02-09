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

    @api.model
    def create(self,vals):
        res = super(AccountMove,self).create(vals)
        print ("res.line_ids===",res.line_ids)
        if res.line_ids:
            program_code_id = res.line_ids.filtered(lambda x:x.program_code_id)
            if program_code_id:
                res.programatic_code = True
            account_ie_id = res.line_ids.filtered(lambda x:x.account_ie_id)
            if account_ie_id:
                res.ie_account = True
        return res
        
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    is_programatic_code = fields.Boolean(related="move_id.programatic_code",store=True)
    is_ie_account = fields.Boolean(related="move_id.ie_account",store=True)

