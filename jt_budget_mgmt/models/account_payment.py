from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):

    _inherit = 'account.payment'
    
    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')
    
    def post(self):
        record = super(AccountPayment,self).post()
        for rec in self:
            move_ids = rec.move_line_ids.mapped('move_id')
            for move in move_ids:
                if rec.dependancy_id:
                    move.dependancy_id = rec.dependancy_id.id
                if rec.sub_dependancy_id:
                    move.sub_dependancy_id = rec.sub_dependancy_id.id 
        return record
