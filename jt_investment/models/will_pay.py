from odoo import models, fields, api
from datetime import datetime

class WillPay(models.Model):

    _name = 'investment.will.pay'
    _description = "Investment Will Pay"
    _rec_name = 'folio' 
 
    folio = fields.Integer("Folio")
    date_time = fields.Datetime("Date Time")
    journal_id= fields.Many2one("account.journal",'Bank Account')
    bank_id = fields.Many2one(related="journal_id.bank_id")
    amount_invest = fields.Float("Amount to invest")
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    investment_rate_id = fields.Many2one("investment.period.rate","Exchange rate")
    total_currency_rate = fields.Float(string="Total",compute="get_total_currency_amount",store=True)
    contract_id = fields.Many2one("investment.contract","Contract")
    document_type = fields.Selection([('cetes','CETES'),('udibonos','Udibonos'),('bonds','Bonds'),('promissory_note','Promissory note')],string="Document")
    instrument_it = fields.Selection([('bank','Bank'),('paper_government','Paper Government Paper')],string="Instrument It")
    account_executive = fields.Char("Account Executive")
    UNAM_operator = fields.Char("UNAM Operator")
    is_federal_subsidy_resources = fields.Boolean("Federal Subsidy Resourcesss")
    observations = fields.Text("Observations")
    
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
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('confirmed','Confirmed'),('approved','Approved'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')
    
    simple_interest_capital = fields.Float(string="Capital",compute="get_simple_interest_capital",store=True)
    simple_interest_future_value = fields.Float(string="Future Value",compute="get_simple_interest_future_value",store=True)
    simple_interest_estimated_yield = fields.Float(string="Estimated Yield",compute="get_simple_interest_estimated_yield",store=True)
    simple_interest_real_performance = fields.Float(string="Real Performance")
    simple_estimated_real_variation = fields.Float(string="Estimated vs. Real Yield Variation",compute="get_simple_estimated_real_variation",store=True)
    
    compound_interest_total = fields.Float(string="Total",compute="get_compound_interest_total",store=True)
    compound_interest_estimated_yield = fields.Float(string="Estimated Yield",compute="get_compound_interest_estimated_yield",store=True)
    compound_interest_real_performance = fields.Float(string="Real Performance")
    compound_estimated_real_variation = fields.Float(string="Estimated vs. Real Yield Variation",compute="get_compound_estimated_real_variation",store=True)

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    
    
    @api.depends('amount_invest')
    def get_total_currency_amount(self):
        for rec in self:
            if rec.amount_invest and rec.currency_rate_id:
                rec.total_currency_rate = rec.amount_invest * rec.currency_rate_id.rate
            else:
                rec.total_currency_rate = 0

    @api.depends('annual_term','monthly_term','term_days')
    def get_time_frame(self):
        for rec in self:
            rec.time_frame = (rec.annual_term*360)+(rec.monthly_term*30)+rec.term_days

    @api.depends('amount','interest_rate','time_frame','simple_interest')
    def get_simple_interest_capital(self):
        for rec in self:
            interest_rate = rec.interest_rate/100
            if rec.simple_interest:
                rec.simple_interest_capital = rec.amount/(1+(interest_rate*(rec.time_frame/360)))
            else:
                rec.simple_interest_capital = 0
                
    @api.depends('simple_interest_capital','interest_rate','time_frame','simple_interest')
    def get_simple_interest_future_value(self):
        for rec in self:
            interest_rate = rec.interest_rate/100
            if rec.simple_interest:
                rec.simple_interest_future_value =rec.simple_interest_capital*(1+(rec.time_frame/360)*interest_rate)
            else:
                rec.simple_interest_future_value = 0
                

    @api.depends('simple_interest_capital','simple_interest_future_value','simple_interest')
    def get_simple_interest_estimated_yield(self):
        for rec in self:
            if rec.simple_interest:
                rec.simple_interest_estimated_yield =rec.simple_interest_future_value - rec.simple_interest_capital
            else:
                rec.simple_interest_estimated_yield = 0 

    @api.depends('simple_interest_estimated_yield','simple_interest_real_performance','simple_interest')
    def get_simple_estimated_real_variation(self):
        for rec in self:
            if rec.simple_interest:
                rec.simple_estimated_real_variation =rec.simple_interest_real_performance - rec.simple_interest_estimated_yield
            else:
                rec.simple_estimated_real_variation = 0

    @api.depends('amount','interest_rate','time_frame','compound_interest')
    def get_compound_interest_total(self):
        for rec in self:
            interest_rate = rec.interest_rate/100
            if rec.compound_interest:
                rec.compound_interest_total = rec.amount*((1+interest_rate))**(rec.time_frame/360)
            else:
                rec.compound_interest_total = 0

    @api.depends('compound_interest_total','amount','compound_interest')
    def get_compound_interest_estimated_yield(self):
        for rec in self:
            if rec.compound_interest:
                rec.compound_interest_estimated_yield = rec.compound_interest_total - rec.amount
            else:
                rec.compound_interest_estimated_yield = 0 

    @api.depends('compound_interest_estimated_yield','compound_interest_real_performance','compound_interest')
    def get_compound_estimated_real_variation(self):
        for rec in self:
            if rec.compound_interest:
                rec.compound_estimated_real_variation = rec.compound_interest_real_performance - rec.compound_interest_estimated_yield
            else:
                rec.compound_estimated_real_variation = 0 

    @api.model
    def create(self,vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code('folio.will.pay')
        return super(WillPay,self).create(vals)
    
    def action_confirm(self):
        today = datetime.today().date()
        user = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        fund_type = False
        if self.contract_id and self.contract_id.fund_id:
            fund_type = self.contract_id.fund_id.id
            
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.money.market.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_amount': self.amount_invest,
                'default_date': today,
                'default_employee_id': employee.id if employee else False,
                'default_will_pay_id' : self.id,
                'default_fund_type' : fund_type,
            }
        }

    def action_reset_to_draft(self):
        self.state='draft'
    
    def action_calculation(self):
        return 
    
    def action_reinvestment(self):
        return 
    
    def action_published_entries(self):
        return {
            'name': 'Published Entries',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'request.open.balance.finance',
            'domain': [('will_pay_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_will_pay_id': self.id}
        }
    