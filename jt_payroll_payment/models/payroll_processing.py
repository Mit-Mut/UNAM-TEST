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
from odoo.exceptions import UserError

class CustomPayrollProcessing(models.Model):

    _name = 'custom.payroll.processing'
    _description = "Custom Payroll Processing"
    

    name = fields.Char("Name")

    period_start = fields.Date("Period")
    period_end = fields.Date("Period End")
    fornight = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'),
                                      ('06', '06'), ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'),
                                      ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
                                      ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
                                      ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24')],
                                string="Fornight")
    
    payroll_ids = fields.One2many('employee.payroll.file','payroll_processing_id')

    def generate_payroll(self):
        return {
                'name': _('Generate Payroll'),
                'res_model':'generate.payroll.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_payroll_payment.generate_payroll_wizard_view1').id,
                'context': {'default_payroll_process_id': self.id},
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

    def generate_adjustment(self):
        return {
                'name': _('Generate Adjustment'),
                'res_model':'adjusted.payroll.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_payroll_payment.adjusted_payroll_wizard_view1').id,
                'context': {'default_payroll_process_id': self.id},
                'target': 'new',
                'type': 'ir.actions.act_window',
            }

        
    def view_payment_receipt(self):
        return {
                'name': _('Payroll'),
                'res_model':'employee.payroll.file',
                'view_type': 'form',
                # 'view_id': self.env.ref('jt_agreement.view_req_open_balance_tree').id,
                'view_mode': 'tree,form',
                'views': [(self.env.ref('jt_payroll_payment.employee_payroll_file_tree_process').id, 'tree'), (self.env.ref("jt_payroll_payment.employee_payroll_file_form_processing").id, 'form')],
                #'context': {'default_payroll_process_id': self.id},
                'target': 'current',
                'type': 'ir.actions.act_window',
                'domain':[('id','in',self.payroll_ids.ids)]
            }
        