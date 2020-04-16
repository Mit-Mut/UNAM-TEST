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


class ExpenditureItem(models.Model):

    _name = 'expenditure.item'
    _description = 'Item of Expenditure'
    _rec_name = 'item'

    item = fields.Char(string='Item', size=3)
    exercise_type = fields.Selection(
        [('r', 'R'), ('c', 'C'), ('d', 'D')], string='Exercise type')
    description = fields.Text(string='Item description')
    unam_account_id = fields.Many2one('account.account', string='UNAM account')
    shcp = fields.Char(string='Expenditure Item SHCP')
    desc_shcp = fields.Char(string='Description of expenditure item of SHCP')
    cog_id = fields.Many2one('coa.conac', string='COG CONAC')
    cog_desc = fields.Char(string='Description of COG CONAC')
    assigned_account = fields.Char(string='Assigned account')

    _sql_constraints = [('item', 'unique(item)', 'The item must be unique.')]

    @api.constrains('item')
    def _check_item(self):
        if not str(self.item).isnumeric():
            raise ValidationError(_('The Item value must be numeric value'))

    @api.onchange('unam_account_id')
    def _onchange_unam_account_id(self):
        if self.unam_account_id and len(self.unam_account_id.tag_ids.ids) > 0:
            # Prepare Expenditure Item SHCP and Description of expenditure item of SHCP From Account tags
            tag_code = ''
            tag_name = ''
            for tag in self.unam_account_id.tag_ids:
                split_list = str(tag.name).split(' ')
                if len(split_list) > 0:
                    tag_code += split_list[0]
                if len(split_list) > 1:
                    tag_name += ' '.join(split_list[1:])
            # Set Expenditure Item SHCP
            self.shcp = tag_code
            # Set Description of expenditure item of SHCP
            self.desc_shcp = tag_name
            # Set COG CONAC
            if self.unam_account_id.coa_conac_id:
                self.cog_id = self.unam_account_id.coa_conac_id.id
            else:
                self.cog_id = False
            # Set Description of COG CONAC
            if self.unam_account_id.conac_name:
                self.cog_desc = self.unam_account_id.conac_name
            else:
                self.cog_desc = False
            # Set Assign Account
            if self.unam_account_id.name:
                self.assigned_account = self.unam_account_id.name
            else:
                self.assigned_account = False

    def fill_zero(self, code):
        return str(code).zfill(3)

    @api.model
    def create(self, vals):
        if vals.get('item') and len(vals.get('item')) != 3:
            vals['item'] = self.fill_zero(vals.get('item'))
        return super(ExpenditureItem, self).create(vals)

    def write(self, vals):
        if vals.get('item') and len(vals.get('item')) != 3:
            vals['item'] = self.fill_zero(vals.get('item'))
        return super(ExpenditureItem, self).write(vals)

    def unlink(self):
        for item in self:
            program_code = self.env['program.code'].search([('item_id', '=', item.id)], limit=1)
            if program_code:
                raise ValidationError('You can not delete item which are mapped with program code!')
        return super(ExpenditureItem, self).unlink()
