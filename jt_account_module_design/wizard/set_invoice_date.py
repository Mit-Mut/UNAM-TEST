from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError

class ConfirmPaymentDate(models.TransientModel):
    _name = 'confirm.invoice.date'
    _description = 'Confirm Invoice date'

    inv_date = fields.Date('Invoice Date',default=fields.Date.context_today)
    invoice_ids = fields.Many2many('account.move')



    def action_invoice_date(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        for payment in self.env['account.move'].browse(active_ids):
            if payment.payment_state not in ('registered','draft'):
                raise UserError(_("You can set the Invoice date  only for those payments which are in "
                "'Draft and For Registered'!"))
        

        
        return {
            'name': _('Set Invoice Date'),
            'res_model': 'confirm.invoice.date',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_account_module_design.view_confirm_invoice_date_wizard').id,
            'context': {'default_invoice_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    


    def set_invoice_date(self):
        for inv in self.invoice_ids:
            if inv.payment_state not in ('draft','registered'):
                raise UserError(_("You can set the Invoice date  only for those payments which are in "
                "'Draft and For Payment Procedure'!"))
            if inv:
                inv.invoice_date = self.inv_date
                