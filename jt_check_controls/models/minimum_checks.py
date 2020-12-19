from odoo import models, fields, api, _

class MinimumCheck(models.Model):

    _name = 'minimum.checks'
    _description = "Minimum of Checks"
    _rec_name = 'checkbook'

    checkbook = fields.Char("Checkbook")
    bank_id = fields.Many2one('account.journal', "Bank")
    bank_account_id = fields.Many2one("res.partner.bank", string="Bank Account")
    minimum_of_checks = fields.Integer("Mimimum of Checks")
    reorder_point = fields.Integer("Reorder Point")

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id and self.bank_id.bank_account_id:
            self.bank_account_id = self.bank_id.bank_account_id.id