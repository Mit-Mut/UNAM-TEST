from odoo import models, fields, api

class CETES(models.Model):

    _name = 'investment.cetes'
    _description = "Investment CETES"
    
    name = fields.Char("Name")
    kind_of_product = fields.Selection([('investment','Investment')],string="Kind Of Product",default="investment")
    key = fields.Char("Identification Key")
    start_date = fields.Date('Start Date')
    due_date = fields.Date('Due Date')
    nominal_value = fields.Float("Nominal Value")
    
    cetes_price = fields.Float("CETES Price")
    cetes_quantity = fields.Float("CETES Quantity")
    estimated_interest = fields.Float("Estimated Interest")
    estimated_profit = fields.Float("Estimated Profit")
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float("Real Profit")
    
    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation = rec.real_profit - rec.estimated_profit
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)
    
    
