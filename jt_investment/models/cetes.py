from odoo import models, fields, api
from datetime import datetime

class CETES(models.Model):

    _name = 'investment.cetes'
    _description = "Investment CETES"
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
    start_date = fields.Date('Start Date')
    due_date = fields.Date('Due Date')
    nominal_value = fields.Float("Nominal Value")
    yield_rate = fields.Float("Yield Rate")
    term= fields.Selection([('28','28 Days'),
                                  ('91','91 Days'),
                                  ('182','182 Days'),
                                  ('364','364 Days')
                                  ],string="Term")
    
    
    cetes_price = fields.Float(string="CETES Price",compute="get_cetes_price",store=True)
    cetes_quantity = fields.Float(string="CETES Quantity",compute="get_cetes_quantity",store=True)
    estimated_interest = fields.Float(string="Estimated Interest",compute="get_estimated_interest",store=True)
    estimated_profit = fields.Float(string="Estimated Profit",compute="get_estimated_profit",store=True)
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float(string="Real Profit",compute="get_real_profit",store=True)
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('approved','Approved'),('confirmed','Confirmed'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    request_finance_ids = fields.One2many('request.open.balance.finance','cetes_id')
    

    @api.depends('amount_invest')
    def get_total_currency_amount(self):
        for rec in self:
            if rec.amount_invest:
                rec.total_currency_rate = rec.amount_invest
            else:
                rec.total_currency_rate = 0
            
    @api.depends('term','yield_rate','nominal_value')
    def get_cetes_price(self):
        for rec in self:
            term_value = 0
            if rec.term:
                term_value = int(rec.term)
            rec.cetes_price = (1/(rec.yield_rate*term_value/36000+1))*rec.nominal_value

    @api.depends('nominal_value')
    def get_cetes_quantity(self):
        for rec in self:
            rec.cetes_quantity = rec.nominal_value/10

    @api.depends('nominal_value','yield_rate','term')
    def get_estimated_interest(self):
        for rec in self:
            term_value = 0
            if rec.term:
                term_value = int(rec.term)
            rec.estimated_interest = rec.yield_rate/100*term_value*rec.nominal_value/360

    @api.depends('nominal_value','yield_rate','term','estimated_interest')
    def get_estimated_profit(self):
        for rec in self:
            rec.estimated_profit = rec.nominal_value + rec.estimated_interest

    @api.depends('nominal_value','real_interest')
    def get_real_profit(self):
        for rec in self:
            rec.real_profit = rec.nominal_value + rec.real_interest

    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation =  rec.real_profit - rec.estimated_profit
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)
    

    @api.model
    def create(self,vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code('folio.cetes')
        return super(CETES,self).create(vals)
        
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
                'default_cetes_id' : self.id,
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
            'domain': [('cetes_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_cetes_id': self.id}
        }
