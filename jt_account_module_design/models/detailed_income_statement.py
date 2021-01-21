from odoo import models, fields, api,_

class DetailedIncomeStatement(models.Model):

    _name = 'detailed.statement.income'
    _description = "Detailed Statement of income"
    _rec_name = "concept"

    concept = fields.Char(string='Concept')
    account_ids = fields.Many2many('account.account', string='Account')
    inc_exp_type = fields.Selection([('income', 'Income'), ('expenses', 'Expenses')],string='Type')