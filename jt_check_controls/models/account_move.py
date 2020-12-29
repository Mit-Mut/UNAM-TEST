from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class SupplierPaymentRequest(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(selection_add=[('payment_method_cancelled', 'Payment method cancelled'),
                                                    ('rotated','Rotated'),
                                                    ('assigned_payment_method','Assigned Payment Method')])
    check_folio_id = fields.Many2one('check.log', "Check Sheet")
    check_status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                          ('Assigned for shipping', 'Assigned for shipping'),
                          ('Available for printing', 'Available for printing'),
                          ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                          ('In transit', 'In transit'), ('Sent to protection','Sent to protection'),
                          ('Protected and in transit','Protected and in transit'),
                          ('Protected', 'Protected'), ('Detained','Detained'),
                          ('Withdrawn from circulation','Withdrawn from circulation'),
                          ('Cancelled', 'Cancelled'),
                          ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                          ('On file','On file'),('Destroyed','Destroyed'),
                          ('Reissued', 'Reissued'),('Charged','Charged')], related='check_folio_id.status')

    def cancel_payment_method(self):
        for payment_req in self:
            if payment_req.is_payment_request == True or payment_req.is_project_payment == True:
                if payment_req.payment_state == 'for_payment_procedure':
                    payment_req.payment_state = 'payment_method_cancelled'
                    payment_req.payment_bank_id = False
                    payment_req.payment_bank_account_id = False
                    payment_req.payment_issuing_bank_id = False
                    payment_req.payment_issuing_bank_account_id = False
                    payment_req.l10n_mx_edi_payment_method_id = False
            if payment_req.payment_state == 'rotated' and payment_req.is_payment_request == True:
                payment_req.action_cancel_budget()

    def action_rotated(self):
        self.ensure_one()
        self.payment_state = 'rotated'

    def write(self, vals):
        res = super(SupplierPaymentRequest, self).write(vals)
        for move in self:
            if move.is_payment_request and vals.get('payment_state') == 'paid' and move.check_folio_id:
                move.check_folio_id.status = 'Charged'
        return res

