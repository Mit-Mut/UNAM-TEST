from odoo import fields, models, api, _
from datetime import datetime

class CancelAvailableCheck(models.TransientModel):
    _name = 'cancel.available.check'
    _description = 'Cancel Available Check'

    check_folio_id = fields.Many2one('check.log',"Check number")
    reason_cancellation = fields.Text(string='Reason Cancellation')
    is_physical_check = fields.Boolean(string="Do you have the physical check?",copy=False,default=False)
    
    def apply(self):
        if self.check_folio_id:
            self.check_folio_id.reason_cancellation = self.reason_cancellation
            self.check_folio_id.is_physical_check = self.is_physical_check
            self.check_folio_id.general_status = 'cancelled'
            if self.is_physical_check:
                self.check_folio_id.status = 'Canceled in custody of Finance'
            else:
                self.check_folio_id.status = 'Cancelled'
                self.check_folio_id.date_cancellation = datetime.now().today()

