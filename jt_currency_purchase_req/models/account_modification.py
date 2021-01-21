# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api,_
class AccountModification(models.Model):

    _inherit = 'request.accounts'

    move_type = fields.Selection(selection_add=[
        ('account_modify', 'Account Modification')])
    no_trade = fields.Char('No. Trade')
    legal_number = fields.Char('legal Number')
    modification_date = fields.Date("Date")
    
    @api.model
    def create(self, vals):
        res = super(AccountModification,self).create(vals)
        if res.move_type == 'account_modify':
            invoice = self.env['ir.sequence'].next_by_code('request.accounts.modification')
            res.invoice = invoice        
        if res.invoice:
            res.invoice = res.invoice.zfill(8)
        return res

    def send_notification_msg(self):
        print ("calll")

    def action_confirm_modification(self):
        self.write({'status': 'confirmed'})
        