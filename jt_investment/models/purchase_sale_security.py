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
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('done','Done'),('rejected','rejected'),('canceled','Canceled')],string="Status",default='draft')
    observations = fields.Text("Observations")    
    file_data = fields.Binary("Supporting document")
    file_name = fields.Char("File Name")
    
    journal_id = fields.Many2one("account.journal","Bank")
    bank_account_id = fields.Many2one(related='journal_id.bank_account_id')
    account_balance = fields.Float("Account Balance")
    movement_price = fields.Float("Price")
    number_of_titles = fields.Float("Quantity of Securities")
    amount = fields.Float("Investment amount")
    
#     @api.model
#     def create(self,vals):
#         vals['name'] = self.env['ir.sequence'].next_by_code('purchase.sale.security')
#         return super(PurchaseSaleSecurity,self).create(vals)
    
    def action_confirm(self):
        self.state = 'requested'

    def action_reject(self):
        self.state = 'rejected'