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
                                           ('CETES','CETES'),('UDIBONOS','UDIBONOS'),
                                           ('BONOS','BONOS'),('i_will_pay','I Will Pay'),
                                           ('titles','Titles'),('foreign_currency','Foreign Currency')
                                           ],string="Type Of Investment")
    
    fund_id = fields.Many2one('request.open.balance.invest','Fund')
    fund_type_id = fields.Many2one('fund.type','Type of Fund')
    type_of_agreement_id = fields.Many2one('agreement.agreement.type','Type of Agreement')
    bases_collaboration_id = fields.Many2one('bases.collaboration','Name of Agreement')
    
    def set_to_requested(self):
        self.state = 'requested'
    
    