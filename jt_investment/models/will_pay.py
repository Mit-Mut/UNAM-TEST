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
    time_frame = fields.Float(string="Time frame",compute="get_time_frame",store=True)
    simple_interest = fields.Boolean(string="Simple Interest",default=False)
    compound_interest = fields.Boolean(string="Compound Interest",default=False)
    state = fields.Selection([('draft','Draft'),('in_process','In Process')],string="Status",default="draft")
    
    simple_interest_capital = fields.Float(string="Capital",compute="get_simple_interest_capital",store=True)
    simple_interest_future_value = fields.Float(string="Future Value",compute="get_simple_interest_future_value",store=True)
    simple_interest_estimated_yield = fields.Float(string="Estimated Yield",compute="get_simple_interest_estimated_yield",store=True)
    simple_interest_real_performance = fields.Float(string="Real Performance")
    simple_estimated_real_variation = fields.Float(string="Estimated vs. Real Yield Variation",compute="get_simple_estimated_real_variation",store=True)
    
    compound_interest_total = fields.Float(string="Total",compute="get_compound_interest_total",store=True)
    compound_interest_estimated_yield = fields.Float(string="Estimated Yield",compute="get_compound_interest_estimated_yield",store=True)
    compound_interest_real_performance = fields.Float(string="Real Performance")
    compound_estimated_real_variation = fields.Float(string="Estimated vs. Real Yield Variation",compute="get_compound_estimated_real_variation",store=True)
    

    @api.depends('annual_term','monthly_term','term_days')
    def get_time_frame(self):
        for rec in self:
            rec.time_frame = (rec.annual_term*360)+(rec.monthly_term*30)+rec.term_days

    @api.depends('amount','interest_rate','time_frame')
    def get_simple_interest_capital(self):
        for rec in self:
            rec.simple_interest_capital = rec.amount/(1+(rec.interest_rate*(rec.time_frame/360)))

    @api.depends('simple_interest_capital','interest_rate','time_frame')
    def get_simple_interest_future_value(self):
        for rec in self:
            rec.simple_interest_future_value =rec.simple_interest_capital*(1+(rec.time_frame/360)*rec.interest_rate)

    @api.depends('simple_interest_capital','simple_interest_future_value')
    def get_simple_interest_estimated_yield(self):
        for rec in self:
            rec.simple_interest_estimated_yield =rec.simple_interest_future_value - rec.simple_interest_capital

    @api.depends('simple_interest_estimated_yield','simple_interest_real_performance')
    def get_simple_estimated_real_variation(self):
        for rec in self:
            rec.simple_estimated_real_variation =rec.simple_interest_real_performance - rec.simple_interest_estimated_yield

    @api.depends('amount','interest_rate','time_frame')
    def get_compound_interest_total(self):
        for rec in self:
            rec.compound_interest_total = rec.amount*((1+rec.interest_rate))**(rec.time_frame/360)

    @api.depends('compound_interest_total','time_frame')
    def get_compound_interest_estimated_yield(self):
        for rec in self:
            rec.compound_interest_estimated_yield = rec.compound_interest_total - rec.time_frame 

    @api.depends('compound_interest_estimated_yield','compound_interest_real_performance')
    def get_compound_estimated_real_variation(self):
        for rec in self:
            rec.compound_estimated_real_variation = rec.compound_interest_estimated_yield - rec.compound_interest_real_performance 
    
    def action_confirm(self):
        self.state='in_process'
    
    def action_calculation(self):
        return 
    
    def action_reinvestment(self):
        return 
    