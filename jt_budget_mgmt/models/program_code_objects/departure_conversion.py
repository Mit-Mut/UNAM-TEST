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


class DepartureConversion(models.Model):

    _name = 'departure.conversion'
    _description = 'Conversion with Departure'
    _rec_name = 'federal_part'

    federal_part = fields.Char(string='Federal part', size=5)
    federal_part_desc = fields.Text(string='Federal part description')
    item_id = fields.Many2one('expenditure.item','Item of Expenditure')
    
    _sql_constraints = [('federal_part', 'unique(federal_part)', 'The federal part must be unique.')]

    @api.constrains('federal_part')
    def _check_federal_part(self):
        if not str(self.federal_part).isnumeric():
            raise ValidationError(_('The Institutional activity number must be numeric value'))

    def fill_zero(self, code):
        return str(code).zfill(5)

    @api.model
    def create(self, vals):
        if vals.get('federal_part') and len(vals.get('federal_part')) != 5:
            vals['federal_part'] = self.fill_zero(vals.get('federal_part'))
        return super(DepartureConversion, self).create(vals)

    def write(self, vals):
        if vals.get('federal_part') and len(vals.get('federal_part')) != 5:
            vals['federal_part'] = self.fill_zero(vals.get('federal_part'))
        return super(DepartureConversion, self).write(vals)

    def unlink(self):
        for conversion in self:
            program_code = self.env['program.code'].search([('conversion_item_id', '=', conversion.id)], limit=1)
            if program_code:
                raise ValidationError('You can not delete conversion item which are mapped with program code!')
        return super(DepartureConversion, self).unlink()

    def validate_conversion_item(self, conversion_item_string):
        if len(str(conversion_item_string)) > 4:
            conversion_item_str = str(conversion_item_string).zfill(4)
            if conversion_item_str.isnumeric():
                conversion_item = self.search(
                    [('federal_part', '=', conversion_item_str)], limit=1)
                if conversion_item:
                    return conversion_item
        return False
