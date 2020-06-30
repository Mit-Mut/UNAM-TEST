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


class SubDependency(models.Model):

    _name = 'sub.dependency'
    _description = 'Sub-Dependency'
    _rec_name = 'display_name'

    dependency_id = fields.Many2one('dependency', string='Dependency')
    sub_dependency = fields.Char(string='Sub dependency', size=2)
    description = fields.Text(string='Sub dependency description')
    display_name = fields.Char(string='Sub Dependency Name', compute="_compute_display_name")

    _sql_constraints = [('sub_dependency_dependency_id', 'unique(sub_dependency,dependency_id)',
                         'The sub dependency must be unique per dependency')]

    def _compute_display_name(self):
        for record in self:
            if 'from_move' in self._context:
                name = ''
                if record.sub_dependency:
                    name += str(record.sub_dependency)
                if record.description:
                    name += ' '
                    name += str(record.description)
                record.display_name = name
            else:
                record.display_name = record.sub_dependency

    @api.constrains('sub_dependency')
    def _check_sub_dependency(self):
        if not str(self.sub_dependency).isnumeric():
            raise ValidationError(_('The Sub Dependency must be numeric value'))

    def fill_zero(self, code):
        return str(code).zfill(2)

    @api.model
    def create(self, vals):
        if vals.get('sub_dependency') and len(vals.get('sub_dependency')) != 2:
            vals['sub_dependency'] = self.fill_zero(vals.get('sub_dependency'))
        return super(SubDependency, self).create(vals)

    def write(self, vals):
        if vals.get('sub_dependency') and len(vals.get('sub_dependency')) != 2:
            vals['sub_dependency'] = self.fill_zero(vals.get('sub_dependency'))
        return super(SubDependency, self).write(vals)

    def unlink(self):
        for subdependency in self:
            program_code = self.env['program.code'].search([('sub_dependency_id', '=', subdependency.id)], limit=1)
            if program_code:
                raise ValidationError('You can not delete sub-dependency which are mapped with program code!')
        return super(SubDependency, self).unlink()

    def validate_subdependency(self, subdependency_string, dependency):
        if len(str(subdependency_string)) > 1:
            subdependency_str = str(subdependency_string).zfill(2)
            if subdependency_str.isnumeric():
                subdependency = self.search(
                    [('dependency_id', '=', dependency.id), ('sub_dependency', '=', subdependency_string)], limit=1)
                if subdependency:
                    return subdependency
        return False
