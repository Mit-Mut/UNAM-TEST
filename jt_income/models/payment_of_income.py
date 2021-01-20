from odoo import models, fields, api

class PaymentOfIncome(models.Model):

    _name = 'payment.of.income'
    _description = "Payment Of Income"
    
    name = fields.Char("Payment of")
    description = fields.Text("Description")
    
    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.name:
                name = rec.name
            if rec.description: 
                name += ' ' + rec.description
                
            result.append((rec.id, name))
        return result
    
