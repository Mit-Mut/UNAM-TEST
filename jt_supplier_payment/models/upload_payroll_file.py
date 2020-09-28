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
from datetime import datetime
from odoo.exceptions import UserError, ValidationError,Warning

class EmployeePayroll(models.Model):

    _inherit = 'employee.payroll.file'

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Method',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, Credit Card, etc.')
    substate = fields.Selection(related="move_id.payment_state",string="SubState")
    
    def action_reviewed(self):
        if any(self.filtered(lambda x:x.state not in ('draft','revised'))):
            raise UserError(_("You can Reviewed only for those Payroll which are in "
            "'Draft'!"))
        for record in self:
            record.reference= self.env['ir.sequence'].next_by_code('seq.payroll.employee.reference')
            record.state = 'revised'

    def get_invoice_line_vals(self):
        invoice_line_vals = { 'quantity' : 1,
                            'price_unit' : self.amount_payable,
                            }
        return invoice_line_vals
    
    def get_payroll_payment_vals(self):
        journal = self.env.ref('jt_payroll_payment.payroll_payment_request_jour')
        invoice_line_vals = self.get_invoice_line_vals()
        partner_id = self.employee_id and self.employee_id.user_id and self.employee_id.user_id.partner_id and self.employee_id.user_id.partner_id.id or False 
        vals = {'payment_bank_id':self.bank_receiving_payment_id and self.bank_receiving_payment_id.id or False,
                'payment_bank_account_id': self.receiving_bank_acc_pay_id and self.receiving_bank_acc_pay_id.id or False,
                'payment_issuing_bank_id': self.payment_issuing_bank_id and self.payment_issuing_bank_id.id or False,
                'l10n_mx_edi_payment_method_id' : self.l10n_mx_edi_payment_method_id and self.l10n_mx_edi_payment_method_id.id or False,
                'partner_id' : partner_id,
                'is_payroll_payment_request':True,
                'type' : 'in_invoice',
                'journal_id' : journal and journal.id or False,
                'invoice_date' : fields.Date.today(),
                'invoice_line_ids':[(0,0,invoice_line_vals)]
                }
        return vals
    
    def create_payroll_payment(self):
        payroll_payment_vals = self.get_payroll_payment_vals()
        return self.env['account.move'].create(payroll_payment_vals)
        
    def action_done(self):
        if any(self.filtered(lambda x:x.state != 'revised')):
            raise UserError(_("You can Request for payment only for those Payroll which are in "
            "'Reviewed'!"))
        payment_providers = self.filtered(lambda x:x.payment_request_type == 'payment_provider')
        direct_employee = self.filtered(lambda x:x.payment_request_type == 'direct_employee')
        
        if payment_providers and direct_employee:
            raise UserError(_("You can not Request for payment for both Payment Provider and Direct Employee"))
        
        if payment_providers:
            return {
                'name': _('Payment Provider'),
                'res_model':'payroll.payment.provider.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_supplier_payment.payroll_payment_provider_form_view').id,
                'context': {'default_emp_payroll_ids': [(6, 0, payment_providers.ids)]},
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            
        elif direct_employee:
            for record in self:
                move_id = record.create_payroll_payment()
                record.move_id = move_id.id
                record.state = 'done'