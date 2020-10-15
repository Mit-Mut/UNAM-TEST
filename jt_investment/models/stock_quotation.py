from odoo import models, fields, api

class InvestmentStockQuotation(models.Model):

    _name = 'investment.stock.quotation'
    _description = "Investment Stock Quotation"

    name = fields.Char("Title")
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed')],string="Status",default='draft')
    date = fields.Date("Date")
    price = fields.Float("Price")
    journal_id = fields.Many2one("account.journal","Bank")
    bank_rate_id = fields.Many2one("res.currency","Bank Rate")
    term = fields.Integer("Term")
    cetes_currency_id = fields.Many2one("res.currency","CETES Rate")
    term_cetes = fields.Integer("Terms")
    dollar_currency_id = fields.Many2one("res.currency","Dollars")
    term_dollar = fields.Integer("Term")
    observations = fields.Text("Observations")
    
    def action_confirm(self):
        self.state = 'confirmed'
    