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
from odoo.exceptions import ValidationError , UserError
from datetime import datetime

class InvestmentFunds(models.Model):

    _name = 'investment.funds'
    _description = "Investment Funds"
    _rec_name = 'first_number'
    
    first_number = fields.Char('First Number:')
    new_journal_id = fields.Many2one("account.journal", 'Journal')

     
    fund_id = fields.Many2one('agreement.fund','Fund Name')
    fund_key = fields.Char(related='fund_id.fund_key',string="Fund Code")


    @api.model
    def create(self, vals):
        res = super(InvestmentFunds, self).create(vals)
        first_number = self.env['ir.sequence'].next_by_code('funds.number')
        res.first_number = first_number
        return res
