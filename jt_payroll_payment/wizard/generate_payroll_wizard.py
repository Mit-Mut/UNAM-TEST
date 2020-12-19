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
                        if result_dict:
                            result_dict.update({'preception_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                             
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
                         
                if result_dict:
                    result_dict.update({'preception_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict) 

            #======================== payroll_deductions ================# 
            if self.type_of_movement == 'payroll_deductions':
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    
                    counter = 0
                    rfc = row[0].value
                    ded_key = row[2].value
                    amount = row[3].value
                    net_salary = row[4].value
                    
                    if rfc:
                        if result_dict:
                            result_dict.update({'deduction_line_ids':line_data})
                            self.env['employee.payroll.file'].create(result_dict)
                            result_dict = {}
                            line_data = []
                             
                        employee_id =self.env['hr.employee'].search([('rfc','=',rfc)],limit=1)
                        if employee_id:
                            result_dict.update({'payroll_processing_id':self.payroll_process_id.id,
                                                'period_start' : self.payroll_process_id.period_start,
                                                'period_end' : self.payroll_process_id.period_end,
                                                'fornight' : self.payroll_process_id.fornight,
                                                'employee_id':employee_id.id,
                                                'payment_request_type':'direct_employee'})
                    
                    if ded_key:
                        if  type(ded_key) is int or type(ded_key) is float:
                            ded_key = int(ded_key)
                        
                        ded_id = self.env['deduction'].search([('key','=',ded_key)],limit=1)
                        if ded_id:
                            line_data.append((0,0,{'deduction_id':ded_id.id,'amount':amount,'net_salary':net_salary})) 
                         
                if result_dict:
                    result_dict.update({'deduction_line_ids':line_data})
                    self.env['employee.payroll.file'].create(result_dict) 
