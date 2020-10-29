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
        if self.investment_id:
            self.investment_id.action_approved()

        if self.bonds_id:
            self.bonds_id.action_approved()

        if self.cetes_id:
            self.cetes_id.action_approved()

        if self.udibonos_id:
            self.udibonos_id.action_approved()

        if self.will_pay_id:
            self.will_pay_id.action_approved()
            
        return result
     
    def confirmed_finance(self):
        result = super(BasesCollabration,self).confirmed_finance()
        if self.investment_id:
            self.investment_id.action_confirmed()

        if self.bonds_id:
            self.bonds_id.action_confirmed()

        if self.cetes_id:
            self.cetes_id.action_confirmed()

        if self.udibonos_id:
            self.udibonos_id.action_confirmed()

        if self.will_pay_id:
            self.will_pay_id.action_confirmed()

        return result 