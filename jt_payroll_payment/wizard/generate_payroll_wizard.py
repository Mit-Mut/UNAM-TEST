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

class GeneratePayrollWizard(models.TransientModel):

    _name = 'generate.payroll.wizard'
    _description = "Generate Payroll Wizard"

    type_of_movement = fields.Selection([('payroll_perceptions','Payroll Perceptions'),
                                         ('payroll_deductions','Payroll Deductions'),
                                         ('pension_payment','Pension Payment'),
                                         ('additional_payments','Additional Payments'),
                                         ('additional_pension_payments','Additional Pension Payments')
                                         ],string='Type of Movement')
    
    file = fields.Binary('File to import')
    filename = fields.Char('FileName')
    
    employee_ids = fields.Many2many('hr.employee','employee_generate_payroll_wizard_rel','employee_id','wizard_id','Employees')
    payroll_process_id = fields.Many2one('custom.payroll.processing','Payroll Process')
    
    def generate(self):
        if self.file:
            data = base64.decodestring(self.file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)

            result_dict = {
                }
            line_data = []
            exit_payroll_id = False
            #======================== payroll_perceptions ================# 
            if self.type_of_movement == 'payroll_perceptions':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    program_code = row[2].value
                    
                    check_number = row[6].value
                    deposite_number = row[7].value
                    
                    pre_key = row[9].value
                    amount = row[10].value
                    
                    if rfc:
                        if exit_payroll_id and line_data:
                            exit_payroll_id.write({'preception_line_ids':line_data})
                            line_data = []
                            exit_payroll_id = False
                            result_dict = {}
                            
                        if result_dict:
                            result_dict.update({'preception_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                            exit_payroll_id = False
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            rec_check_number = False
                            rec_deposite_number = False
                            
                            if check_number:
                                if  type(check_number) is int or type(check_number) is float:
                                    rec_check_number = int(check_number)

                            if deposite_number:
                                if  type(deposite_number) is int or type(deposite_number) is float:
                                    rec_deposite_number = int(deposite_number)
                                    
                            exit_payroll_id = self.env['employee.payroll.file'].search([('employee_id','=',employee_id.id),('id','in',self.payroll_process_id.payroll_ids.ids)],limit=1)
                            if not exit_payroll_id:
                                result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                    'period_start' : self.payroll_process_id.period_start,
                                                    'period_end' : self.payroll_process_id.period_end,
                                                    'fornight' : self.payroll_process_id.fornight,
                                                    'employee_id':employee_id.id,
                                                    'deposite_number' : rec_deposite_number,
                                                    'check_number' : rec_check_number,
                                                    'payment_request_type':'direct_employee'})
                    
                    program_id = False
                    if program_code:
                        p_id = self.env['program.code'].search([('program_code','=',program_code)],limit=1)
                        if p_id:
                            program_id = p_id.id
                        
                    if pre_key:
                        if  type(pre_key) is int or type(pre_key) is float:
                            pre_key = int(pre_key)
                        
                        pre_id = self.env['preception'].search([('key','=',pre_key)],limit=1)
                        if pre_id:
                            line_data.append((0,0,{'program_code_id':program_id,'preception_id':pre_id.id,'amount':amount})) 

                if exit_payroll_id and line_data:
                    exit_payroll_id.write({'preception_line_ids':line_data})
                    line_data = []
                    exit_payroll_id = False
                         
                if result_dict:
                    result_dict.update({'preception_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict) 
                    line_data = []
                    result_dict = {}
                    

            #======================== payroll_deductions ================# 
            if self.type_of_movement == 'payroll_deductions':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    ded_key = row[2].value
                    amount = row[3].value
                    net_salary = row[4].value
                    
                    if rfc:
                        if exit_payroll_id and line_data:
                            exit_payroll_id.write({'deduction_line_ids':line_data})
                            line_data = []
                            exit_payroll_id = False
                            result_dict = {}
                            
                        if result_dict:
                            result_dict.update({'deduction_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                            exit_payroll_id = False
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:

                            exit_payroll_id = self.env['employee.payroll.file'].search([('employee_id','=',employee_id.id),('id','in',self.payroll_process_id.payroll_ids.ids)],limit=1)
                            if exit_payroll_id:
                                exit_payroll_id.net_salary = net_salary
                                
                            if not exit_payroll_id:                             
                                result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                    'period_start' : self.payroll_process_id.period_start,
                                                    'period_end' : self.payroll_process_id.period_end,
                                                    'fornight' : self.payroll_process_id.fornight,
                                                    'employee_id':employee_id.id,
                                                    'net_salary':net_salary,
                                                    'payment_request_type':'direct_employee'})
                    
                    if ded_key:
                        if  type(ded_key) is int or type(ded_key) is float:
                            ded_key = int(ded_key)
                        
                        ded_id = self.env['deduction'].search([('key','=',ded_key)],limit=1)
                        if ded_id:
                            line_data.append((0,0,{'deduction_id':ded_id.id,'amount':amount})) 

                if exit_payroll_id and line_data:
                    exit_payroll_id.write({'deduction_line_ids':line_data})
                    line_data = []
                    exit_payroll_id = False
                         
                if result_dict:
                    result_dict.update({'deduction_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict) 
                    line_data = []
                    exit_payroll_id = False
                    result_dict = {}
                    
            #======================== pension_payment ================# 
            if self.type_of_movement == 'pension_payment':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    ben_name = row[2].value
                    payment_method = row[3].value
                    bank_account = row[4].value
                    deposite = row[5].value
                    check_no = row[6].value
                    total_pension = row[7].value
                    
                    if rfc:

                        if exit_payroll_id and line_data:
                            exit_payroll_id.write({'pension_payment_line_ids':line_data})
                            line_data = []
                            exit_payroll_id = False
                            result_dict = {}
                        
                        if result_dict:
                            result_dict.update({'pension_payment_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                            exit_payroll_id = False
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            exit_payroll_id = self.env['employee.payroll.file'].search([('employee_id','=',employee_id.id),('id','in',self.payroll_process_id.payroll_ids.ids)],limit=1)
                            if not exit_payroll_id:                             
                                result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                    'period_start' : self.payroll_process_id.period_start,
                                                    'period_end' : self.payroll_process_id.period_end,
                                                    'fornight' : self.payroll_process_id.fornight,
                                                    'employee_id':employee_id.id,
                                                    'payment_request_type':'direct_employee'})
                    
                    partner_id = False
                    deposite_data = ''
                    check_no_data = ''
                    payment_method_id = False
                    journal_id = False
                    
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

                    if payment_method:         
                        if  type(payment_method) is int or type(payment_method) is float:
                            payment_method = int(payment_method)
                        payment_method_rec = self.env['l10n_mx_edi.payment.method'].search([('name','=',str(payment_method))],limit=1)
                        if payment_method_rec:
                            payment_method_id = payment_method_rec.id

                    if bank_account:
                        if  type(bank_account) is int or type(bank_account) is float:
                            bank_account = int(bank_account)
                        bank_account_rec = self.env['account.journal'].search([('bank_acc_number','=',str(bank_account))],limit=1)
                        if bank_account_rec:
                            journal_id = bank_account_rec.id
                             
                    line_data.append((0,0,{'journal_id':journal_id,'l10n_mx_edi_payment_method_id':payment_method_id,'partner_id':partner_id,'deposit_number':deposite_data,'check_number':check_no_data,'total_pension':total_pension})) 

                if exit_payroll_id and line_data:
                    exit_payroll_id.write({'pension_payment_line_ids':line_data})
                    line_data = []
                    exit_payroll_id = False
                         
                if result_dict:
                    result_dict.update({'pension_payment_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict)
                    line_data = []
                    result_dict = [] 
                    exit_payroll_id = False

            #======================== Additional payments ================# 
            if self.type_of_movement == 'additional_payments':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    job_id = row[1].value
                    amount = row[2].value
                    program_code = row[3].value
                    details = row[4].value
                    
                    if rfc:

                        if exit_payroll_id and line_data:
                            exit_payroll_id.write({'additional_payments_line_ids':line_data})
                            line_data = []
                            exit_payroll_id = False
                            result_dict = {}
                        
                        if result_dict:
                            result_dict.update({'additional_payments_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                            exit_payroll_id = False
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            exit_payroll_id = self.env['employee.payroll.file'].search([('employee_id','=',employee_id.id),('id','in',self.payroll_process_id.payroll_ids.ids)],limit=1)
                            if not exit_payroll_id:                             
                                result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                    'period_start' : self.payroll_process_id.period_start,
                                                    'period_end' : self.payroll_process_id.period_end,
                                                    'fornight' : self.payroll_process_id.fornight,
                                                    'employee_id':employee_id.id,
                                                    'payment_request_type':'direct_employee'})
                    
                    job_data = False
                    program_code_id = False
                    details_data = False
                    
                    if details:
                        if details=='N':
                            details_data = 'N'
                        if details=='U':
                            details_data = 'U'
                    if job_id:
                        job_rec = self.env['hr.job'].search([('name','=',job_id)],limit=1)
                        if job_rec:
                            job_data = job_rec.id
                    
                    if program_code:
                        p_id = self.env['program.code'].search([('program_code','=',program_code)],limit=1)
                        if p_id:
                            program_code_id = p_id.id
                         
                    line_data.append((0,0,{'job_id':job_data,'program_code_id':program_code_id,'details':details_data,'amount':amount})) 

                if exit_payroll_id and line_data:
                    exit_payroll_id.write({'additional_payments_line_ids':line_data})
                    line_data = []
                    exit_payroll_id = False
                    result_dict = {}
                         
                if result_dict:
                    result_dict.update({'additional_payments_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict)
                    result_dict = {} 
                    line_data = []
                    exit_payroll_id = False

            #======================== additional_pension_payments ================# 
            if self.type_of_movement == 'additional_pension_payments':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    ben_name = row[1].value
                    amount = row[2].value
                    
                    if rfc:
                        if exit_payroll_id and line_data:
                            exit_payroll_id.write({'additional_pension_payments_line_ids':line_data})
                            line_data = []
                            exit_payroll_id = False
                            result_dict = {}
                        
                        if result_dict:
                            result_dict.update({'additional_pension_payments_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                            exit_payroll_id = False
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            exit_payroll_id = self.env['employee.payroll.file'].search([('employee_id','=',employee_id.id),('id','in',self.payroll_process_id.payroll_ids.ids)],limit=1)
                            if not exit_payroll_id: 
                                result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                    'period_start' : self.payroll_process_id.period_start,
                                                    'period_end' : self.payroll_process_id.period_end,
                                                    'fornight' : self.payroll_process_id.fornight,
                                                    'employee_id':employee_id.id,
                                                    'payment_request_type':'direct_employee'})
                    
                    partner_id = False
                    
                    if ben_name:
                        per_rec = self.env['res.partner'].search([('name','=',ben_name)],limit=1)
                        if per_rec:
                            partner_id = per_rec.id
                        
                    line_data.append((0,0,{'partner_id':partner_id,'amount':amount})) 

                if exit_payroll_id and line_data:
                    exit_payroll_id.write({'additional_pension_payments_line_ids':line_data})
                    line_data = []
                    exit_payroll_id = False
                    result_dict = {}
                         
                if result_dict:
                    result_dict.update({'additional_pension_payments_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict) 
                    line_data = []
                    exit_payroll_id = False
                    result_dict = {}
                    