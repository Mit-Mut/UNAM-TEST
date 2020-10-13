from odoo import models, fields, api

class PurchaseSaleSecurity(models.Model):

    _name = 'purchase.sale.security'
    _description = "Purchase Sale Security"

    name = fields.Char("Title")
    invesment_date = fields.Date("Investment Date")
    type_of_investment = fields.Char("Type of Investment")
    amount = fields.Float("Investment amount")
    price = fields.Float("Price")
    term = fields.Integer("Investment Term")
    due_date = fields.Date("Due Date")
    movement = fields.Selection([('buy','Buy'),('sell','Sell')],string="Movement")
    
    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.sale.security')
        return super(PurchaseSaleSecurity,self).create(vals)
    