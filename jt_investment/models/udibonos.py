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
    time_for_each_cash_flow = fields.Integer(string="Time for each cash flow",size=4)
    time_to_expiration_date = fields.Integer(string="Time to Expiration Date",size=4)
    coupon = fields.Float("Coupon")
    state = fields.Selection([('draft','Draft'),('in_process','In Process')],string="Status",default="draft")
    
    present_value_bond = fields.Float(string="Present Value of the Bond",compute="get_present_value_bond",store=True)    
    estimated_interest = fields.Float(string="Estimated Interest",compute="get_estimated_interest",store=True)
    
    real_interest = fields.Float("Real Interest")
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)    

    
    month_key = fields.Char("Identification Key")
    month_issue_date = fields.Date('Date of issue')
    month_due_date = fields.Date('Due Date')
    number_of_title = fields.Float("Number of Titles")
    udi_value = fields.Float("UDI value")
    udi_value_multiplied = fields.Float("The value of the Udi is multiplied by 100")
    coupon_rate = fields.Float("Coupon Rate")
    period_days = fields.Float("Period days")  
    

    monthly_nominal_value = fields.Float(string="Nominal value of the security in investment units",compute="get_monthly_nominal_value",store=True)    
    monthly_estimated_interest = fields.Float(string="Estimated Interest",compute="get_monthly_estimated_interest",store=True)    
    monthly_real_interest = fields.Float("Real Interest")
                
    monthly_profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_month_profit_variation",store=True)    
      
    @api.depends('interest_rate','time_for_each_cash_flow','nominal_value')
    def get_present_value_bond(self):
        for rec in self:
            print ("======",(rec.nominal_value*rec.interest_rate)*((1+rec.interest_rate)**float(rec.time_for_each_cash_flow-1))/(rec.interest_rate+(1+rec.interest_rate)**rec.interest_rate)+rec.nominal_value*(1/(1+rec.interest_rate)**rec.interest_rate))
            value = (rec.nominal_value*rec.interest_rate)*((1+rec.interest_rate)**float(rec.time_for_each_cash_flow-1))/(rec.interest_rate+(1+rec.interest_rate)**rec.interest_rate)+rec.nominal_value*(1/(1+rec.interest_rate)**rec.interest_rate)
            value = format(float(value), 'f')
            print ("========value",value)
            rec.present_value_bond = value 
            

    @api.depends('present_value_bond','nominal_value')
    def get_estimated_interest(self):
        for rec in self:
            rec.estimated_interest = rec.present_value_bond - rec.nominal_value
    
    @api.depends('estimated_interest','real_interest')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation = rec.real_interest - rec.estimated_interest
    
    @api.depends('number_of_title','udi_value','udi_value_multiplied')
    def get_monthly_nominal_value(self):
        for rec in self:
            rec.monthly_nominal_value = rec.number_of_title*(rec.udi_value*rec.udi_value_multiplied)
    
    
    @api.depends('monthly_nominal_value','coupon_rate','period_days')
    def get_monthly_estimated_interest(self):
        for rec in self:
            rec.monthly_estimated_interest = rec.monthly_nominal_value*rec.coupon_rate/360*rec.period_days
        
    @api.depends('monthly_estimated_interest','monthly_real_interest')
    def get_month_profit_variation(self):
        for rec in self:
            rec.monthly_profit_variation = rec.monthly_estimated_interest - rec.monthly_real_interest
        
    def action_confirm(self):
        self.state='in_process'

    def action_calculation(self):
        return 
    
    def action_reinvestment(self):
        return 
