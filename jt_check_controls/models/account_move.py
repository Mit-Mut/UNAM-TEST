from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class SupplierPaymentRequest(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(selection_add=[('payment_method_cancelled', 'Payment method cancelled'),
                                                    ('rotated','Rotated')])

    def cancel_payment_method(self):
        for payment_req in self:
            if payment_req.payment_state == 'for_payment_procedure' and payment_req.is_payment_request == True:
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
