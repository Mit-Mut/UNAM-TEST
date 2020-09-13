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
from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError,Warning
from datetime import datetime, timedelta

class PayrollPaymentProviderwizard(models.TransientModel):

    _name = 'payroll.payment.provider.wizard'
    _description = 'PayrollPaymentProviderwizard'
    
    partner_id = fields.Many2one('res.partner','Payment Provider')
    emp_payroll_ids = fields.Many2many('employee.payroll.file','employee_payroll_file_provider_rel','provider_id','emp_file_id','Employee Payroll')

    def action_payroll_payment_provider(self):
        journal = self.env.ref('jt_supplier_payment.payment_request_jour')
        if self.partner_id and self.partner_id.bank_ids:
            payment_bank_account_id = self.partner_id.bank_ids[0].id
            payment_bank_id = self.partner_id.bank_ids[0].bank_id and self.partner_id.bank_ids[0].bank_id.id or False
        else:
            payment_bank_account_id = False
            payment_bank_id = False 
        invoice_line_list = []
        for record in self.emp_payroll_ids:
            line_vals = record.get_invoice_line_vals()
            invoice_line_list.append((0,0,line_vals))
            
        vals = {
                'partner_id' : self.partner_id.id,
                #'journal_id' : journal and journal.id or False,
                'payment_bank_id' : payment_bank_id,
                'payment_bank_account_id' : payment_bank_account_id,
                'is_payroll_payment_request':True,
                'type' : 'in_invoice',
                'invoice_date' : fields.Date.today(),
                'invoice_line_ids':invoice_line_list,
                
            }
        move_id = self.env['account.move'].create(vals)
        self.emp_payroll_ids.write({'move_id':move_id.id})