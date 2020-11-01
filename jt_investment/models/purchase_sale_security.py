from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class PurchaseSaleSecurity(models.Model):

    _name = 'purchase.sale.security'
    _description = "Purchase Sale Security"
    
    
    name = fields.Char("Reference")

    last_quote_id = fields.Many2one('investment.stock.quotation','Last Quote')
    last_quote_price = fields.Float(related='last_quote_id.price',string="Last Quote Price")
    last_quote_date = fields.Date(related="last_quote_id.date",string="Last Quote Date")

    
    invesment_date = fields.Date("Investment Date")
    type_of_investment = fields.Char("Type of Investment")
    price = fields.Float(related='last_quote_id.price',string="Price")
    price_previous_day = fields.Float(compute='get_previous_price_days',string="Price previous day")
    average_price_of_the_month = fields.Float(compute='get_average_price_of_the_month',string="Average price of the month")
    title = fields.Float("Title")
    term = fields.Integer("Investment Term")
    due_date = fields.Date("Due Date")
    movement = fields.Selection([('buy','Purchase'),('sell','Sale')],string="What move do I want to make?")
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('approved','Approved'),('confirmed','Confirmed'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')
    observations = fields.Text("Observations")    
    file_data = fields.Binary("Supporting document")
    file_name = fields.Char("File Name")
    
    
    journal_id = fields.Many2one("account.journal","Bank")
    bank_account_id = fields.Many2one(related='journal_id.bank_account_id')
    account_balance = fields.Float("Account Balance",compute="get_account_balance",store=True)
    movement_price = fields.Float(related='last_quote_id.price',string="Price")
    number_of_titles = fields.Float(related='title',string="Quantity of Securities")
    amount = fields.Float(string="Investment amount",compute="get_investment_amount",store=True)

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    #=====Profit==========#
    estimated_interest = fields.Float(string="Estimated Interest")
    estimated_profit = fields.Float(string="Estimated Profit")
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float(string="Real Profit")
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)

    @api.depends('last_quote_id','last_quote_id.price_id')
    def get_previous_price_days(self):
        for rec in self:
            if rec.last_quote_id and rec.last_quote_id.price_id:
                previous_rec = self.env['stock.quote.price'].search([('date','<',rec.last_quote_id.price_id.date)],limit=1,order='date desc')
                if previous_rec:
                    rec.price_previous_day = previous_rec.price
                else:
                    rec.price_previous_day = 0.0
            else:
                rec.price_previous_day = 0.0

    @api.depends('last_quote_id','last_quote_id.price_id')
    def get_average_price_of_the_month(self):
        for rec in self:
            if rec.last_quote_id and rec.last_quote_id.price_id:
                p_date = rec.last_quote_id.price_id.date.replace(day=1)
                day_diff = rec.last_quote_id.price_id.date - p_date
                day_diff = day_diff.days+1

                previous_rec = self.env['stock.quote.price'].search([('date','>=',p_date),('date','<=',rec.last_quote_id.price_id.date)],order='date desc')
                if previous_rec:
                    sum_price =  sum(x.price for x in previous_rec)
                    if day_diff:
                        sum_price = sum_price/day_diff
                        rec.average_price_of_the_month = sum_price
                    else: 
                        rec.average_price_of_the_month = sum_price
                else:
                    rec.average_price_of_the_month = 0.0
            else:
                rec.average_price_of_the_month = 0.0
                
    @api.depends('journal_id','bank_account_id','journal_id.default_debit_account_id')
    def get_account_balance(self):     
        for rec in self:
            if rec.journal_id and rec.bank_account_id and rec.journal_id.default_debit_account_id:
                values= self.env['account.move.line'].search([('account_id', '=', rec.journal_id.default_debit_account_id.id),('move_id.state', '=', 'posted')])
                rec.account_balance = sum(x.debit-x.credit for x in values)
                
            else:
                rec.account_balance = 0
    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation =  rec.real_profit - rec.estimated_profit
            

    @api.depends('movement_price','number_of_titles')
    def get_investment_amount(self):
        for rec in self:
            rec.amount = rec.movement_price * rec.number_of_titles
            
#     @api.model
#     def create(self,vals):
#         vals['name'] = self.env['ir.sequence'].next_by_code('purchase.sale.security')
#         return super(PurchaseSaleSecurity,self).create(vals)
    
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
                'default_amount': self.amount,
                'default_date': today,
                'default_purchase_sale_security_id' : self.id,
                'default_fund_type' : fund_type,
                'show_for_supplier_payment':1,
            }
        }


    def action_reject(self):
        self.state = 'rejected'

    def action_done(self):
        self.state = 'done'
                