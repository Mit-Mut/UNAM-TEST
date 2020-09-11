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
from datetime import datetime

class EmployeePayroll(models.Model):

    _name = 'employee.payroll.file'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Upload Files"

    name = fields.Char("Name")
    employee_id = fields.Many2one('hr.employee', "Employee")
    employee_number = fields.Char(related='employee_id.identification_id', string="Employee Number")
    fornight = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'),
                                      ('06', '06'), ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'),
                                      ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
                                      ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'),
                                      ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24')],
                                string="Fornight")
    period_start = fields.Date("Period")
    period_end = fields.Date("Period End")
    reference = fields.Char("Reference")
    bank_receiving_payment_id = fields.Many2one('res.bank', string="Bank Receiving Payment")
    payment_issuing_bank_id = fields.Many2one("account.journal", string="Payment Issuing Bank")
    receiving_bank_acc_pay_id = fields.Many2one('res.partner.bank', string="Receiving bank account for payment")
    bank_acc_payment_insur_id = fields.Many2one('res.partner.bank', string="Bank account of payment issuance")
    amount_payable = fields.Float("Amount Payable",tracking=True)
    batch_folio = fields.Integer("Batch Folio")
    request_type = fields.Selection([('university', 'Payment to University Worker'),
                                     ('add_benifit', 'Additional Benifit'),
                                     ('alimony', 'Payment Special payroll payments Alimony'),
                                     ('payment', 'Payment')], "Type of request for payroll payment")
    payroll_adjustment = fields.Selection([('withdrawal', 'Withdrawal from the university worker'),
                                           ('leave_without_pay', 'Leave without Pay'),
                                           ('judical', 'Judicial Instruction'),
                                           ('add_payment', 'Additional Payments'),
                                           ('salary_mod_inc', 'Salary modification: Increases'),
                                           ('salary_mod_dec', 'Salary modification: Decreases'),
                                           ('salary_mod_don', 'Salary modification: Donation')],
                                          string="Payroll Adjustment")
    substate = fields.Char("SubState")
    beneficiary_id = fields.Many2one('res.partner', "Beneficiary")
    state = fields.Selection([('draft', 'Draft'), ('revised', 'Revised'), ('done', 'Done')], string="State",
                             default='draft')
    payment_request_type = fields.Selection([('direct_employee','Direct Employee'),('payment_provider','Payment Provider')],string="Payment Request Type")
    

    def request_for_payment(self):
        today_date = datetime.today()
        payment_req_obj = self.env['payment.request']
        for record in self:
            vals = {
                'employee_id': record.employee_id,
                'amount': record.amount_payable,
                'request_type': record.request_type,
                'bank_receiving_payment_id': record.bank_receiving_payment_id,
                'payment_receipt_bank_id': record.payment_issuing_bank_id,
                'receipt_date': today_date,
                'payment_method': record.payment_method,
                'payroll_origin_id': record.payroll_origin_id,
                'bank_acc_payment_insur_id': bank_acc_payment_insur_id,
                'payment_issuing_bank_id': record.payment_issuing_bank_id,
                'fornight': record.fornight
            }
            payment_req_obj.create(vals)
            record.state = 'done'
