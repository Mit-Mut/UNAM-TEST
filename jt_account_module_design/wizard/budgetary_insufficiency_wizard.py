##############################################################################
from odoo import models, fields
from datetime import datetime

class BudegtInsufficiencWiz(models.TransientModel):

    _inherit = 'budget.insufficien.wiz'
    _description = 'Budgetary Insufficienc'

    provision_id = fields.Many2one('provision','Provision')

    def action_ok(self):
        res = super(BudegtInsufficiencWiz,self).action_ok()
        if self.provision_id:
            self.provision_id.payment_state = 'rejected'
            self.provision_id.reason_rejection = self.msg
            
        return res
    
    def action_budget_allocation(self):
        res = super(BudegtInsufficiencWiz,self).action_budget_allocation()
        if self.provision_id:
            self.provision_id.payment_state = 'provision'
            self.provision_id.date_approval_request = datetime.today().date()
            self.provision_id.is_from_reschedule_payment = False
            #self.decrease_available_amount()
            #self.move_id.create_journal_line_for_approved_payment()
            
        return res