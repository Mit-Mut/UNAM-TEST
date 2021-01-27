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
import base64
import xlrd
from datetime import datetime
from odoo.modules.module import get_resource_path
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import ustr

class AdjustedPayrollWizard(models.TransientModel):

    _name = 'adjusted.payroll.wizard'
    _description = "Adjusted Payroll Wizard"

    type_of_movement = fields.Selection([('adjustment','Adjustment'),
                                         ('perception_adjustment_detail','Perception Adjustment Detail'),
                                         ('deduction_adjustment_detail','Deduction Adjustment Detail'),
                                         ('detail_alimony_adjustments','Detail of Alimony Adjustments'),
                                         ],string='Adjustment Type')
    
    file = fields.Binary('File to import')
    filename = fields.Char('FileName')
    
    employee_ids = fields.Many2many('hr.employee','employee_adjusted_payroll_wizard_rel','employee_id','wizard_id','Employees')
    payroll_process_id = fields.Many2one('custom.payroll.processing','Payroll Process')
    
    def generate(self):
        if self.file:
            data = base64.decodestring(self.file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)

            if self.type_of_movement == 'adjustment':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    case = row[0].value
                    check_no = row[1].value
                    bank_no = row[2].value
                    deposite_no = row[3].value
                    new_bank_no = row[4].value
                    emp_no = row[5].value
                    q_digit = row[6].value
                    q_new_digit = row[7].value
                    rfc = row[8].value
                    old_amount = row[9].value
                    new_amount = row[10].value
                    
                    employee_id = False
                    emp_payroll_ids = []
                    if rfc:
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            employee_id = employee_id.id
                    
                    case_id = self.env['adjustment.cases'].search([('case','=',case)],limit=1)
                        
                    if employee_id:
                        emp_payroll_ids = self.payroll_process_id.payroll_ids.filtered(lambda x:x.employee_id.id==employee_id)
                        
                    for rec in emp_payroll_ids:
                        rec.adjustment_case_id = case_id and case_id.id or False
                        if case=='A' or case=='R' or case=='F' or case=='Z' or case=='H' or case=='E' or case=='S' or case=='V' or case=='C':
                            if check_no:
                                if  type(check_no) is int or type(check_no) is float:
                                    check_no = int(check_no)
                                rec.check_number = check_no

                            check_payment_method = self.env.ref('l10n_mx_edi.payment_method_cheque').id
                            if deposite_no and rec.l10n_mx_edi_payment_method_id and \
                                rec.l10n_mx_edi_payment_method_id.id == check_payment_method and case == 'A':
                                if deposite_no and new_bank_no:
                                    log = self.env['check.log'].search([('folio', '=', deposite_no),
                                                    ('bank_id.bank_id.l10n_mx_edi_code', '=', new_bank_no)], limit=1)
                                    if log:
                                        rec.check_final_folio_id = log.id
                            elif deposite_no:
                                if  type(deposite_no) is int or type(deposite_no) is float:
                                    deposite_no = int(deposite_no)
                                
                                rec.deposite_number = deposite_no
    
                        if case=='D' or case=='A' or case=='C' or case=='P':
                            if rec.net_salary==old_amount:
                                rec.net_salary = new_amount
                        
                        if case=='B' or case=='V':
                            rec.net_salary = new_amount 

            employee_id = False
            if self.type_of_movement == 'perception_adjustment_detail':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    counter = 0
                    rfc = row[0].value
                    clave_categ = row[1].value
                    program_code = row[2].value
                    payment_place = row[3].value
                    payment_method = row[4].value
                    bank = row[5].value
                    check_no = row[6].value
                    deposite_no = row[7].value
                    ben = row[8].value
                    perception = row[9].value
                    amount = row[10].value
                    
                    program_id = False
                    if program_code:
                        p_id = self.env['program.code'].search([('program_code','=',program_code)],limit=1)
                        if p_id:
                            program_id = p_id.id
                    emp_payroll_ids = []
                    if rfc:
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            employee_id = employee_id.id

                    if employee_id:
                        emp_payroll_ids = self.payroll_process_id.payroll_ids.filtered(lambda x:x.employee_id.id==employee_id)

                    for rec in emp_payroll_ids:
                        if perception:
                            if  type(perception) is int or type(perception) is float:
                                perception = int(perception)
                            
                            pre_id = self.env['preception'].search([('key','=',perception)],limit=1)
                            if pre_id:
                                lines = rec.preception_line_ids.filtered(lambda x:x.preception_id.id==pre_id.id)
                                for line in lines:
                                    line.program_code_id = program_id
                                    line.amount = amount
                                
                                if not lines:
                                    rec.write({'preception_line_ids':[(0,0,{'program_code_id':program_id,'preception_id':pre_id.id,'amount':amount})]})

            employee_id = False
            if self.type_of_movement == 'deduction_adjustment_detail':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    rfc = row[0].value
                    account_code = row[1].value
                    deduction_key = row[2].value
                    amount = row[3].value
                    net_salary = row[4].value
                    
                    
                    emp_payroll_ids = []
                    if rfc:
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            employee_id = employee_id.id
                        
                    if employee_id:
                        emp_payroll_ids = self.payroll_process_id.payroll_ids.filtered(lambda x:x.employee_id.id==employee_id)
                        
                    for rec in emp_payroll_ids:
                        if deduction_key:
                            if  type(deduction_key) is int or type(deduction_key) is float:
                                deduction_key = int(deduction_key)
                            
                            pre_id = self.env['deduction'].search([('key','=',deduction_key)],limit=1)
                            if pre_id:
                                lines = rec.deduction_line_ids.filtered(lambda x:x.deduction_id.id==pre_id.id)
                                for line in lines:
                                    line.amount = amount
                                
                                if not lines:
                                    rec.write({'deduction_line_ids':[(0,0,{'deduction_id':pre_id.id,'amount':amount})]})                                    


            if self.type_of_movement == 'detail_alimony_adjustments':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    rfc = row[0].value
                    ben_name = row[2].value
                    payment_method = row[3].value
                    bank_key = row[4].value
                    check_no = row[5].value
                    deposite = row[6].value
                    bank_account = row[7].value
                    total_pension = row[8].value
                    
                    partner_id = False
                    deposite_data = deposite
                    check_no_data = check_no
                    
                    if ben_name:
                        per_rec = self.env['res.partner'].search([('name','=',ben_name)],limit=1)
                        if per_rec:
                            partner_id = per_rec.id
                    if deposite:         
                        if  type(deposite) is int or type(deposite) is float:
                            deposite_data = int(deposite)
                    
                    if check_no:         
                        if  type(check_no) is int or type(check_no) is float:
                            check_no_data = int(check_no)
                    
                    emp_payroll_ids = []
                    if rfc:
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            employee_id = employee_id.id
                        
                    if employee_id:
                        emp_payroll_ids = self.payroll_process_id.payroll_ids.filtered(lambda x:x.employee_id.id==employee_id)
                    
                    for rec in emp_payroll_ids:
                        if payment_method:
                            payment_method_id = False
                            journal_id = False
                            bank_id = False
                            bank_account_id = False
                            
                            if  type(payment_method) is int or type(payment_method) is float:
                                payment_method = int(payment_method)

                            if  type(bank_account) is int or type(bank_account) is float:
                                bank_account = int(bank_account)

                            if payment_method:         
                                if  type(payment_method) is int or type(payment_method) is float:
                                    payment_method = int(payment_method)
                                payment_method_rec = self.env['l10n_mx_edi.payment.method'].search([('name','=',str(payment_method))],limit=1)
                                if payment_method_rec:
                                    payment_method_id = payment_method_rec.id
        
                            if bank_account:
                                if  type(bank_account) is int or type(bank_account) is float:
                                    bank_account = int(bank_account)
                                bank_account_rec = self.env['res.partner.bank'].search([('acc_number','=',str(bank_account))],limit=1)
                                if bank_account_rec:
                                    bank_account_id = bank_account_rec.id
        
                            if bank_key:
                                if  type(bank_key) is int or type(bank_key) is float:
                                    bank_key = int(bank_key)
                                bank_rec = self.env['res.bank'].search([('l10n_mx_edi_code','=',str(bank_key))],limit=1)
                                if bank_rec:
                                    bank_id = bank_rec.id

                            if payment_method_id:
                                lines = rec.pension_payment_line_ids.filtered(lambda x:
                                        x.l10n_mx_edi_payment_method_id.id==payment_method_id and
                                        x.bank_key == str(bank_key))
                                for line in lines:
                                    line.total_pension = total_pension
                                    line.partner_id = partner_id 
                                    line.deposit_number = deposite_data
                                    line.check_number = check_no_data
                                    line.bank_acc_number = bank_account_id
                                    line.bank_key = bank_key
                                
                                if not lines:
                                    rec.write({'pension_payment_line_ids':[(0,0,{'partner_id':partner_id,
                                                                                 'l10n_mx_edi_payment_method_id':payment_method_id,
                                                                                 'bank_id':bank_id,
                                                                                 'bank_acc_number' : bank_account_id,
                                                                                 'total_pension':total_pension,
                                                                                 'deposit_number':deposite_data,
                                                                                 'check_number' : check_no_data,
                                                                                 'bank_key':bank_key,
                                                                                 })]})
                                    
                                    
                                                                        
                                    