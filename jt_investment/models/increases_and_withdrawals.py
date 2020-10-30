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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class RequestOpenBalanceInvestment(models.Model):

    _inherit = 'request.open.balance.invest'

    type_of_investment = fields.Selection([('productive_account','Productive Account'),
                                           ('securities','Securities'),('money_market','Money Market')
                                           ],string="Type Of Investment")
    
    type_of_financial_products = fields.Selection([
                                           ('CETES','CETES'),('UDIBONOS','UDIBONOS'),
                                           ('BondsNotes','BondsNotes'),('Promissory','Promissory'),
                                           ],string="Type Of Investment")

    contract_id = fields.Many2one('investment.contract','Contract')
    
    def set_to_requested(self):
        self.state = 'requested'
    
    