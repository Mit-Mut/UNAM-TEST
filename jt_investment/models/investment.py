from odoo import models, fields, api
from datetime import datetime

class Investment(models.Model):

    _name = 'investment.investment'
    _description = "Productive Accounts Investment"
    _rec_name = 'contract_id'
     
    invesment_date = fields.Datetime("Investment Date")
    journal_id = fields.Many2one("account.journal","Bank")
    contract_id = fields.Many2one('investment.contract','Contract')
    amount_to_invest = fields.Float("Amount to invest")
    is_fixed_rate = fields.Boolean('Fixed Rate',default=False)
    is_variable_rate = fields.Boolean('Variable Rate',default=False)
    interest_rate = fields.Float("Interest rate")
    extra_percentage = fields.Float("Extra percentage")
    term = fields.Integer("Fixed Term")
    term_variable = fields.Integer("Variable Term")
    capitalizable = fields.Integer("Days of capitalization")
    frequency = fields.Integer("Frequency of interest payments")
    currency_id = fields.Many2one("res.currency","Currency")
    currency_rate_id = fields.Many2one("res.currency.rate","Exchange rate")
    observations = fields.Text("Observations")    
    file_data = fields.Binary("Supporting document")
    file_name = fields.Char("File Name")
    
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('confirmed','Confirmed'),('approved','Approved'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')

    #=====Profit==========#
    estimated_interest = fields.Float(string="Estimated Interest")
    estimated_profit = fields.Float(string="Estimated Profit")
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float(string="Real Profit")
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    
        
    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation =  rec.real_profit - rec.estimated_profit



    def action_confirm(self):
        today = datetime.today().date()
        fund_type = False            
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.money.market.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_amount': self.amount_to_invest,
                'default_date': today,
                'default_investment_id' : self.id,
                'default_fund_type' : fund_type,
            }
        }


    def action_reject(self):
        self.state = 'rejected'
