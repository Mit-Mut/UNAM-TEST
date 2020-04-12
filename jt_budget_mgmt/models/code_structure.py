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


class CodeStructure(models.Model):

    _name = 'code.structure'
    _description = 'Code Structure'
    _rec_name = 'position_priority'

    position_priority = fields.Integer(string='Position priority')
    section = fields.Selection([
        ('year', 'Year'),
        ('pr', 'Program'),
        ('sp', 'Sub Program'),
        ('dep', 'Dependency'),
        ('sd', 'Sub Dependency'),
        ('par', 'Expenditure Item'),
        ('dv', 'Check Digit'),
        ('or', 'Source of Resource'),
        ('ai', 'Institutional Activity'),
        ('conpp', 'Conversion of Budgetary Program'),
        ('conpa', 'SHCP items'),
        ('tg', 'Type of Expenditure'),
        ('ug', 'Geographic Location'),
        ('cc', 'Wallet Key'),
        ('tp', 'Type of Project'),
        ('np', 'Project Number'),
        ('e', 'Stage'),
        ('tc', 'Type of Agreement'),
        ('nc', 'Agreement Number')], string='Section of the Program Code')

    _sql_constraints = [
        ('uniq_section', 'unique (section)', 'The section must be unique!'),
    ]

    @api.constrains('position_priority')
    def _check_position_priority(self):
        # To check size of the position is exact 2
        if len(str(self.position_priority)) != 2 and self.position_priority not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            raise ValidationError(_('The position priority size must be two!'))
        # To check position value is  (> 0 and < 20)
        if self.position_priority and (self.position_priority < 1 or self.position_priority > 19):
            raise ValidationError(_('The position is only between 01-19'))
        # To check unique position
        position = self.search(
            [('position_priority', '=', self.position_priority), ('id', '!=', self.id)], limit=1)
        if position:
            raise ValidationError(_('The position must be unique!'))
