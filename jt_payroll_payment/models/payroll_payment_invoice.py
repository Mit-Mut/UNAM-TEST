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
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta

class AccountMove(models.Model):

    _inherit = 'account.move'

    is_payroll_payment_request = fields.Boolean("Payroll",default=False,copy=False)
    fornight = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'),
                                 ('06', '06'), ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'),
                                 ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
                                 ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24')],
                                string="Fornight")

    payroll_request_type = fields.Selection([('university', 'Payment to University Worker'),
                                     ('add_benifit', 'Additional Benifit'),
                                     ('alimony', 'Payment Special payroll'),
                                     ('payment', 'Payment')], "Type of request for payroll payment")
    
    payroll_register_user_id = fields.Many2one('res.users',default=lambda self: self.env.user,copy=False,string="User who registers")
    payroll_send_user_id = fields.Many2one('res.users',default=lambda self: self.env.user,copy=False,string="User who sends")
    employee_paryoll_ids = fields.One2many('employee.payroll.file','move_id')
    
    @api.model_create_multi
    def create(self, vals_list):
        results = super(AccountMove, self).create(vals_list)
        for rec in results:
            if rec.is_payroll_payment_request and rec.partner_id:
                users = self.env['res.users'].sudo().search([('partner_id','=',rec.partner_id.id)],limit=1)
                if users:
                    emp_id = self.env['hr.employee'].sudo().search([('user_id','=',users.id)],limit=1)
                    if emp_id and emp_id.account_payable_id:
                        for line in rec.line_ids:
                            if line.account_id.user_type_id.type == 'payable':
                                line.account_id = emp_id.account_payable_id.id
                    elif emp_id and not emp_id.account_payable_id:
                        raise ValidationError("Please Configure payable account into related employee")
        return results  
 
    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if vals.get('partner_id'):
            for rec in self:
                if rec.is_payroll_payment_request and rec.partner_id:
                    users = self.env['res.users'].sudo().search([('partner_id','=',rec.partner_id.id)],limit=1)
                    if users:
                        emp_id = self.env['hr.employee'].sudo().search([('user_id','=',users.id)],limit=1)
                        if emp_id and emp_id.account_payable_id:
                            for line in rec.line_ids:
                                if line.account_id.user_type_id.type == 'payable':
                                    line.account_id = emp_id.account_payable_id.id
                        elif emp_id and not emp_id.account_payable_id:
                            raise ValidationError("Please Configure payable account into related employee")
        return res
    
class AccountPayment(models.Model):
    
    _inherit = 'account.payment'
    
    payment_request_type = fields.Selection([('supplier_payment','Supplier Payment'),('payroll_payment','Payroll Payment')],default="supplier_payment",copy=False)
    fornight = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'),
                                 ('06', '06'), ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'),
                                 ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
                                 ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24')],
                                string="Fornight")
        
    payroll_request_type = fields.Selection([('university', 'Payment to University Worker'),
                                     ('add_benifit', 'Additional Benifit'),
                                     ('alimony', 'Payment Special payroll'),
                                     ('payment', 'Payment')], "Type of request for payroll payment")
    