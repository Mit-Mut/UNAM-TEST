from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class BasesCollabration(models.Model):

    _inherit = 'request.open.balance.finance'
    
    bonds_id = fields.Many2one('investment.bonds','Bonds')
    cetes_id = fields.Many2one('investment.cetes','cetes')
    udibonos_id = fields.Many2one('investment.udibonos','Udibonos')
    will_pay_id = fields.Many2one('investment.will.pay','Will Pay')
    purchase_sale_security_id = fields.Many2one('purchase.sale.security','Purchase Sale Security')
    investment_id = fields.Many2one('investment.investment','Investment')
    

    def approve_finance(self):
        result = super(BasesCollabration,self).approve_finance()
        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.action_done()
        return result 
