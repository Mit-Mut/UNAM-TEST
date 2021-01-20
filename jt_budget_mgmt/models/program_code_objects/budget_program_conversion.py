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
from odoo.exceptions import ValidationError, UserError
import re


class BudgetProgramConversion(models.Model):

    _name = 'budget.program.conversion'
    _description = 'Budget Program Conversion'
    _rec_name = 'shcp'

    unam_key_id = fields.Many2one('program', string='Key UNAM')
    desc = fields.Text(string='Description of key UNAM')
    shcp = fields.Many2one("shcp.code", string='Conversion of SHCP program')
    description = fields.Text(string='Description conversion of SHCP program')

    _sql_constraints = [('uniq_unam_key_id', 'unique(unam_key_id)',
                         'The Key UNAM must be unique.')]

    @api.constrains('shcp')
    def _check_shcp(self):
        if self.shcp:
            # To check size of the position is exact 4
            if len(self.shcp.name) != 4:
                raise ValidationError(_('The Conversion of SHCP program value size must be four.'))
            if self.shcp.name and len(self.shcp.name) == 4:
                if not (re.match("[A-Z]{1}\d{3}", str(self.shcp.name).upper())):
                    raise UserError(
                        _('Please enter first digit as letter and last 3 digits as numbers for SHCP.'))

    @api.onchange('unam_key_id')
    def _onchange_key_unam(self):
        if self.unam_key_id:
            self.desc = self.unam_key_id.desc_key_unam
        else:
            self.desc = False

    @api.onchange('shcp')
    def _onchange_shcp(self):
        if self.shcp:
            self.description = self.shcp.desc
        else:
            self.description = False

    @api.model
    def create(self,vals):
        res = super(BudgetProgramConversion,self).create(vals)
        if not res.desc and res.unam_key_id and res.unam_key_id.desc_key_unam:
            res.desc = res.unam_key_id.desc_key_unam
        if not res.description and res.shcp and res.shcp.desc:
            res.description = res.shcp.desc
        return res

    def write(self,vals):
        result = super(BudgetProgramConversion,self).write(vals)
        if vals.get('unam_key_id') or vals.get('shcp'):
            for res in self:
                if vals.get('unam_key_id'):
                    if not res.desc and res.unam_key_id and res.unam_key_id.desc_key_unam:
                        res.desc = res.unam_key_id.desc_key_unam
                if vals.get('shcp'):
                    if not res.description and res.shcp and res.shcp.desc:
                        res.description = res.shcp.desc
        return result
        
    def unlink(self):
        for bpc in self:
            program_code = self.env['program.code'].search([('budget_program_conversion_id', '=', bpc.id)], limit=1)
            if program_code:
                raise ValidationError('You can not delete conversion program SHCP which are mapped with program code!')
        return super(BudgetProgramConversion, self).unlink()

    def validate_shcp(self, shcp_string, program):
        if len(str(shcp_string)) > 3:
            shcp_str = str(shcp_string)
            if len(shcp_str) == 4:
                if not (re.match("[A-Z]{1}\d{3}", str(shcp_str).upper())):
                    return False
                else:
                    shcp = self.search(
                        [('shcp.name', '=', shcp_str), ('unam_key_id', '=', program.id)], limit=1)
                    if shcp:
                        return shcp
        return False
