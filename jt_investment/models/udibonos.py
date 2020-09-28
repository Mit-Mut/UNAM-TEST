from odoo import models, fields, api

class UDIBONOS(models.Model):

    _name = 'investment.udibonos'
    _description = "Investment UDIBONOS"
    
    name = fields.Char("Name")
    kind_of_product = fields.Selection([('investment','Investment')],string="Kind Of Product",default="investment")
    key = fields.Char("Identification Key")
    issue_date = fields.Date('Date of issue')
    due_date = fields.Date('Due Date')
    nominal_value = fields.Float("Nominal Value")
    interest_rate = fields.Float("Interest Rate")
    time_for_each_cash_flow = fields.Char(string="Time for each cash flow",size=4)
    time_to_expiration_date = fields.Char(string="Time to Expiration Date",size=4)
    coupon = fields.Float("Coupon")
    
    present_value_bond = fields.Float("Present Value of the Bond")    
    estimated_interest = fields.Float("Estimated Interest")
    real_interest = fields.Float("Real Interest")
    @api.depends('estimated_interest','real_interest')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation = rec.real_interest - rec.estimated_interest
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)    

    
    month_key = fields.Char("Identification Key")
    month_issue_date = fields.Date('Date of issue')
    month_due_date = fields.Date('Due Date')
    number_of_title = fields.Float("Number of Titles")
    udi_value = fields.Float("UDI value")
    udi_value_multiplied = fields.Float("The value of the Udi is multiplied by 100")
    coupon_rate = fields.Float("Coupon Rate")
    period_days = fields.Float("Period days")  
    
    monthly_nominal_value = fields.Float("Nominal value of the security in investment units")    
    monthly_estimated_interest = fields.Float("Estimated Interest")
    monthly_real_interest = fields.Float("Real Interest")
    
    @api.depends('monthly_estimated_interest','monthly_real_interest')
    def get_month_profit_variation(self):
        for rec in self:
            rec.profit_variation = rec.real_interest - rec.estimated_interest
            
    monthly_profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_month_profit_variation",store=True)    
      
    
