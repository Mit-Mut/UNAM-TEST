from odoo import models, fields, api
from datetime import timedelta

class InvestmentStockQuotation(models.Model):

    _name = 'investment.stock.quotation'
    _description = "Investment Stock Quotation"

    name = fields.Char("Title")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')],string="Status",default='draft')
    date = fields.Date("Date")
    price_id = fields.Many2one('stock.quote.price',string="Price History")
    price = fields.Float(related="price_id.price")
    journal_id = fields.Many2one("account.journal","Bank")
    bank_rate_id = fields.Many2one("res.currency","Bank Rate")
    term = fields.Integer("Term")
    cetes_currency_id = fields.Many2one("res.currency","CETES Rate")
    term_cetes = fields.Integer("Terms")
    dollar_currency_id = fields.Many2one("res.currency","Dollars")
    term_dollar = fields.Integer("Term")
    observations = fields.Text("Observations")
    
    #=======Calculation========#
    daily_nominal = fields.Float(string='Nominal',compute="get_daily_variation",store=True)
    daily_percentage = fields.Float("Percentage",compute="get_daily_variation",store=True)
    daily_interest = fields.Float("Interest",compute="get_daily_variation",store=True)

    weekly_nominal = fields.Float(string='Nominal',compute="get_weekly_variation",store=True)
    weekly_percentage = fields.Float("Percentage",compute="get_weekly_variation",store=True)
    weekly_interest = fields.Float("Interest",compute="get_weekly_variation",store=True)

    last_30_days_nominal = fields.Float(string='Nominal',compute="get_last_30_days_variation",store=True)
    last_30_days_percentage = fields.Float("Percentage",compute="get_last_30_days_variation",store=True)
    last_30_days_interest = fields.Float("Interest",compute="get_last_30_days_variation",store=True)

    current_month_nominal = fields.Float(string='Nominal',compute="get_current_month_variation",store=True)
    current_month_percentage = fields.Float("Percentage",compute="get_current_month_variation",store=True)
    current_month_interest = fields.Float("Interest",compute="get_current_month_variation",store=True)

    current_year_nominal = fields.Float(string='Nominal',compute="get_current_year_variation",store=True)
    current_year_percentage = fields.Float("Percentage",compute="get_current_year_variation",store=True)
    current_year_interest = fields.Float("Interest",compute="get_current_year_variation",store=True)

    @api.depends('date','price_id','price_id.price')
    def get_daily_variation(self):
        for rec in self:
            if rec.date and rec.price_id:
                previous_rec = self.env['stock.quote.price'].search([('date','<',rec.date)],limit=1,order='date desc')
                if previous_rec:
                    rec.daily_nominal = rec.price - previous_rec.price
                    if previous_rec.price > 0:
                        rec.daily_percentage = rec.daily_nominal*100/previous_rec.price
                    else:
                        rec.daily_percentage = 0
                        
                    rec.daily_interest = rec.daily_percentage * 360 
                else:
                    rec.daily_nominal = 0
                    rec.daily_percentage = 0
                    rec.daily_interest = 0
            else:
                rec.daily_nominal = 0 
                rec.daily_percentage = 0
                rec.daily_interest = 0

    @api.depends('date','price_id','price_id.price')
    def get_weekly_variation(self):
        for rec in self:
            if rec.date and rec.price_id:
                previos_week_date = rec.date - timedelta(days=7)
                previous_rec = self.env['stock.quote.price'].search([('date','<=',previos_week_date)],limit=1,order='date desc')
                if previous_rec:
                    rec.weekly_nominal = rec.price - previous_rec.price
                    if previous_rec.price > 0:
                        rec.weekly_percentage = rec.weekly_nominal*100/previous_rec.price
                    else:
                        rec.weekly_percentage = 0
                        
                    rec.weekly_interest = (rec.weekly_percentage/7) * 360 
                else:
                    rec.weekly_nominal = 0
                    rec.weekly_percentage = 0
                    rec.weekly_interest = 0
            else:
                rec.weekly_nominal = 0 
                rec.weekly_percentage = 0
                rec.weekly_interest = 0

    @api.depends('date','price_id','price_id.price')
    def get_last_30_days_variation(self):
        for rec in self:
            if rec.date and rec.price_id:
                previos_week_date = rec.date - timedelta(days=30)
                previous_rec = self.env['stock.quote.price'].search([('date','<=',previos_week_date)],limit=1,order='date desc')
                if previous_rec:
                    rec.last_30_days_nominal = rec.price - previous_rec.price
                    if previous_rec.price > 0:
                        rec.last_30_days_percentage = rec.last_30_days_nominal*100/previous_rec.price
                    else:
                        rec.last_30_days_percentage = 0
                        
                    rec.last_30_days_interest = (rec.last_30_days_percentage/30) * 360 
                else:
                    rec.last_30_days_nominal = 0
                    rec.last_30_days_percentage = 0
                    rec.last_30_days_interest = 0
            else:
                rec.last_30_days_nominal = 0 
                rec.last_30_days_percentage = 0
                rec.last_30_days_interest = 0

    @api.depends('date','price_id','price_id.price')
    def get_current_month_variation(self):
        for rec in self:
            if rec.date and rec.price_id:
                previos_week_date = rec.date.replace(day=1) - timedelta(days=1)
                day_diff = rec.date - previos_week_date
                day_diff = day_diff.days
                
                previous_rec = self.env['stock.quote.price'].search([('date','<=',previos_week_date)],limit=1,order='date desc')
                if previous_rec:
                    rec.current_month_nominal = rec.price - previous_rec.price
                    if previous_rec.price > 0:
                        rec.current_month_percentage = rec.current_month_nominal*100/previous_rec.price
                    else:
                        rec.current_month_percentage = 0
                    
#                     a1 = rec.current_month_percentage/day_diff
#                     a1 = a1/1
#                     a1 = a1*360
                    rec.current_month_interest = rec.current_month_percentage*360
                else:
                    rec.current_month_nominal = 0
                    rec.current_month_percentage = 0
                    rec.current_month_interest = 0
            else:
                rec.current_month_nominal = 0 
                rec.current_month_percentage = 0
                rec.current_month_interest = 0

    @api.depends('date','price_id','price_id.price')
    def get_current_year_variation(self):
        for rec in self:
            if rec.date and rec.price_id:
                previos_week_date = rec.date.replace(day=1,month=1) - timedelta(days=1)
                day_diff = rec.date - previos_week_date
                day_diff = day_diff.days
                previous_rec = self.env['stock.quote.price'].search([('date','<=',previos_week_date)],limit=1,order='date desc')
                if previous_rec:
                    rec.current_year_nominal = rec.price - previous_rec.price
                    if previous_rec.price > 0:
                        rec.current_year_percentage = rec.current_year_nominal*100/previous_rec.price
                    else:
                        rec.current_year_percentage = 0
                    
                    a1 = rec.current_year_percentage/day_diff
#                     a1 = a1/1
                    a1 = a1*360
                    rec.current_year_interest = a1
                else:
                    rec.current_year_nominal = 0
                    rec.current_year_percentage = 0
                    rec.current_year_interest = 0
            else:
                rec.current_year_nominal = 0 
                rec.current_year_percentage = 0
                rec.current_year_interest = 0

    def action_confirm(self):
        self.state = 'confirmed'

class StockQuotePrice(models.Model):
    
    _name = 'stock.quote.price'
    _description = "Stock Quote Price"
    _rec_name = 'date'
    
    date = fields.Date('Date')
    price = fields.Float(digit=0,string='Price')
    