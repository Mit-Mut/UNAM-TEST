from odoo import models, fields, api
from datetime import datetime

class Bonds(models.Model):

    _name = 'investment.bonds'
    _description = "Investment Bonds"
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
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    
    kind_of_product = fields.Selection([('investment','Investment')],string="Kind Of Product",default="investment")
    key = fields.Char("Identification Key")
    issue_date = fields.Date('Date of issue')
    due_date = fields.Date('Due Date')
    nominal_value = fields.Float(related='amount_invest',string="Nominal Value")
    interest_rate = fields.Float("Interest Rate")
    time_for_each_cash_flow = fields.Integer(string="Time for each cash flow",size=4)
    time_to_expiration_date = fields.Integer(string="Time to Expiration Date",size=4)
    coupon = fields.Float(string="Coupon",compute="get_coupon_amount",store=True)
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('approved','Approved'),('confirmed','Confirmed'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')
        
    present_value_bond = fields.Float(string="Present Value of the Bond",compute="get_present_value_bond",store=True)    
    estimated_interest = fields.Float(string="Estimated Interest",compute="get_estimated_interest",store=True)
    real_interest = fields.Float("Real Interest")
    
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)    
    
    month_key = fields.Char("Identification Key")
    month_issue_date = fields.Date('Date of issue')
    month_due_date = fields.Date('Due Date')
    number_of_title = fields.Float("Number of Titles")
    udi_value = fields.Float("UDI value")
    udi_value_multiplied = fields.Float(string="The value of the Udi is multiplied by 100",default=100)
    coupon_rate = fields.Float("Coupon Rate")
    period_days = fields.Float("Period days")  
    
    monthly_nominal_value = fields.Float(string="Nominal value of the security in investment units",compute="get_monthly_nominal_value",store=True)    
    monthly_estimated_interest = fields.Float(string="Estimated Interest",compute="get_monthly_estimated_interest",store=True)
    monthly_real_interest = fields.Float(string="Real Interest")

    monthly_profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_month_profit_variation",store=True)

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    request_finance_ids = fields.One2many('request.open.balance.finance','bonds_id')
                     
    @api.depends('nominal_value','interest_rate')
    def get_coupon_amount(self):
        for rec in self:
            rec.coupon = (rec.nominal_value * rec.interest_rate)/100

    @api.depends('amount_invest')
    def get_total_currency_amount(self):
        for rec in self:
            if rec.amount_invest:
                rec.total_currency_rate = rec.amount_invest
            else:
                rec.total_currency_rate = 0
    
    @api.depends('interest_rate','time_for_each_cash_flow','nominal_value')
    def get_present_value_bond(self):
        for rec in self:
            VA = rec.nominal_value
            r = rec.interest_rate /100
            n = rec.time_for_each_cash_flow
            value = (VA * r) * ((1 + r) ** n-1) / (r + (1 + r) ** r) + VA * (1 / (1 + r) ** r)
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
            rec.monthly_profit_variation = rec.monthly_real_interest - rec.monthly_estimated_interest

    @api.model
    def create(self,vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code('folio.bonds')
        return super(Bonds,self).create(vals)
        
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
                'default_bonds_id' : self.id,
                'default_fund_type' : fund_type,
                'show_for_supplier_payment':1,
            }
        }
        
    def action_reset_to_draft(self):
        self.state='draft'
        for rec in self.request_finance_ids:
            rec.canceled_finance()

    def action_requested(self):
        self.state = 'requested'

    def action_approved(self):
        self.state = 'approved'

    def action_confirmed(self):
        self.state = 'confirmed'

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
            'domain': [('bonds_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_bonds_id': self.id}
        }
