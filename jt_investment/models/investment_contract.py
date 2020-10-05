from odoo import models, fields, api

class InvestementContract(models.Model):

    _name = 'investment.contract'
    _description = "Investment Contract"
    
    name = fields.Char("Associate Contract")
    journal_id = fields.Many2one('account.journal','Bank')
    bank_account_id = fields.Many2one(related="journal_id.bank_account_id",string="Bank Account")
    investent_type = fields.Selection([('bank_paper','Bank Paper'),('government_role','Government Role')],string="Investment Type")
    term = fields.Integer("Term")
    observations = fields.Text("Observations") 
