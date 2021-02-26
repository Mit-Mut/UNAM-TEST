from odoo import fields, models, api, _
from datetime import datetime

class CancelAvailableCheck(models.TransientModel):
    _name = 'cancel.available.check'
    _description = 'Cancel Available Check'

    check_folio_ids = fields.Many2many('check.log',string="Check number")
    reason_cancellation = fields.Text(string='Reason Cancellation')
    is_physical_check = fields.Boolean(string="Do you have the physical check?",copy=False,default=False)
    
    def apply(self):
        for folio in self.check_folio_ids:
            folio.reason_cancellation = self.reason_cancellation
            folio.is_physical_check = self.is_physical_check
            folio.general_status = 'cancelled'
            if self.is_physical_check:
                folio.status = 'Canceled in custody of Finance'
            else:
                folio.status = 'Cancelled'
                folio.date_cancellation = datetime.now().today()

