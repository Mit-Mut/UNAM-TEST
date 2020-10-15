from odoo import models, fields, api

class PurchaseSaleSecurity(models.Model):

    _name = 'purchase.sale.security'
    _description = "Purchase Sale Security"
    
    
    name = fields.Char("Reference")
    
    invesment_date = fields.Date("Investment Date")
    type_of_investment = fields.Char("Type of Investment")
    price = fields.Float("Price")
    price_previous_day = fields.Float("Price previous day")
    average_price_of_the_month = fields.Float("Average price of the month")
    title = fields.Float("Title")
    term = fields.Integer("Investment Term")
    due_date = fields.Date("Due Date")
    movement = fields.Selection([('buy','Purchase'),('sell','Sale')],string="What move do I want to make?")
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('confirmed','Confirmed'),('approved','Approved'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')
    observations = fields.Text("Observations")    
    file_data = fields.Binary("Supporting document")
    file_name = fields.Char("File Name")
    
    last_quote_id = fields.Many2one('investment.stock.quotation','Last Quote')
    last_quote_price = fields.Float(related='last_quote_id.price',string="Last Quote Price")
    last_quote_date = fields.Date(related="last_quote_id.date",string="Last Quote Date")
    
    journal_id = fields.Many2one("account.journal","Bank")
    bank_account_id = fields.Many2one(related='journal_id.bank_account_id')
    account_balance = fields.Float("Account Balance")
    movement_price = fields.Float("Price")
    number_of_titles = fields.Float("Quantity of Securities")
    amount = fields.Float(string="Investment amount",compute="get_investment_amount",store=True)

    @api.depends('movement_price','number_of_titles')
    def get_investment_amount(self):
        for rec in self:
            rec.amount = rec.movement_price * rec.number_of_titles
            
#     @api.model
#     def create(self,vals):
#         vals['name'] = self.env['ir.sequence'].next_by_code('purchase.sale.security')
#         return super(PurchaseSaleSecurity,self).create(vals)
    
    def action_confirm(self):
        self.state = 'confirmed'

    def action_reject(self):
        self.state = 'rejected'