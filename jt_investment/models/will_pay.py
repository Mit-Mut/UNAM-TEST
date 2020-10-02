from odoo import models, fields, api

class WillPay(models.Model):

    _name = 'investment.will.pay'
    _description = "Investment Will Pay"
    
    name = fields.Char("Name")
    kind_of_product = fields.Selection([('investment','Investment')],string="Kind Of Product",default="investment")
    key = fields.Char("Identification Key")
    investment_date = fields.Date('Investment Date')
    due_date = fields.Date('Due Date')
    amount = fields.Float('Amount')
    interest_rate = fields.Float("Interest Rate")
    annual_term = fields.Integer("Annual Term")
    monthly_term = fields.Integer("Monthly Term")
    term_days = fields.Integer("Term Days")
    simple_interest = fields.Boolean(string="Simple Interest",default=False)
    compound_interest = fields.Boolean(string="Compound Interest",default=False)
    
    simple_interest_capital = fields.Float("Capital")
    simple_interest_future_value = fields.Float("Future Value")
    simple_interest_estimated_yield = fields.Float("Estimated Yield")
    simple_interest_real_performance = fields.Float("Real Performance")
    
    compound_interest_total = fields.Float("Total")
    