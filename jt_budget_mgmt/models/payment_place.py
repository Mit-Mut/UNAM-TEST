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
from odoo import models, fields, api

class PaymentPlace(models.Model):

    _inherit = 'payment.place'
    _description = 'Place of Payment'

    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')
    des_dependency = fields.Text("Dependency Description")
    des_sub_dependency = fields.Text("Sub Dependency Description")

    @api.onchange('dependancy_id', 'sub_dependancy_id')
    def onchange_dep_sub_dep(self):
        if self.dependancy_id and self.sub_dependancy_id:
            self.name = self.dependancy_id.dependency + self.sub_dependancy_id.sub_dependency
        if self.dependancy_id:
            self.des_dependency = self.dependancy_id.description
        else:
            self.des_dependency = ''
        if self.sub_dependancy_id:
            self.des_sub_dependency = self.sub_dependancy_id.description
        else:
            self.des_sub_dependency = ''

    @api.model
    def create(self, vals):
        res = super(PaymentPlace, self).create(vals)
        if vals.get('dependancy_id') and vals.get('sub_dependancy_id'):
            dependency = self.env['dependency'].browse(vals.get('dependancy_id'))
            sub_dependency = self.env['sub.dependency'].browse(vals.get('sub_dependancy_id'))
            res.name = dependency.dependency + sub_dependency.sub_dependency
            if dependency.description:
                res.des_dependency = dependency.description
            if sub_dependency.description:
                res.des_sub_dependency = sub_dependency.description
        return res
