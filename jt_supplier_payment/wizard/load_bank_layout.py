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
import base64
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date
import csv
import io

class loadBankLayoutSupplierPayment(models.TransientModel):

    _name = 'load.bank.layout.supplier.payment'
    _description = 'Load Bank Layout Supplier Payment'
    
    journal_id = fields.Many2one('account.journal','Select the file to generate')
    payment_ids = fields.Many2many('account.payment','account_payment_load_bank_layout_rel','load_bank_layout_id','payment_id','Payments')
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Upload File')
    failed_file_name = fields.Char('Failed Filename',default="Failed_Rows.txt")
    failed_file_data = fields.Binary('Failed File')
    success_file_name = fields.Char('Success Filename',default="Success_Rows.txt")
    success_file_data = fields.Binary('Success File')
    is_hide_failed = fields.Boolean('Hide Failed',default=True)
    is_hide_success = fields.Boolean('Hide Success',default=True)
    is_hide_file_upload = fields.Boolean('Hide Success',default=False)
         
    def action_load_bank_layout(self):
        active_ids = self.env.context.get('active_ids')
        for payment in self.env['account.payment'].browse(active_ids):
            if payment.payment_state != 'for_payment_procedure':
                raise UserError(_("You can load Bank Layout only for those payments which are in "
                "'For Payment Procedure'!"))
        if not active_ids:
            return ''
        
        return {
            'name': _('Load Bank Layout'),
            'res_model': 'load.bank.layout.supplier.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_load_bank_layout_supplier_payment_form').id,
            'context': {'default_payment_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
    
    def get_banamex_file(self):
        try:
            failed_content = ''
            success_content = ''
            
            file_data = base64.b64decode(self.file_data)
            data = io.StringIO(file_data.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
            count = 0
            for line in file_reader:
                if count==0:
                    count += 2
                    continue
                account_no = line[8]
                amount = line[16]
                if amount and account_no:
                    first_amount = amount[:-2]
                    last_amount = amount[-2:]

                    act_amount = first_amount+"."+last_amount
                    act_amount = float(act_amount)
                    match_payment =  self.payment_ids.filtered(lambda x:x.amount==act_amount and x.payment_bank_account_id.acc_number==account_no)
                    if match_payment:
                        success_content += str(count)+' : '+ str(line) + "\n"
                        match_payment[0].post()
                    else:
                        failed_content += str(count)+' : '+ str(line) + "\n"
                else:
                    failed_content += str(count)+' : '+ str(line) + "\n"
                count += 1
                
            if failed_content:
                failed_data = base64.b64encode(failed_content.encode('utf-8'))
                self.failed_file_data = failed_data
                self.is_hide_failed = False
                
            if success_content:
                success_data = base64.b64encode(success_content.encode('utf-8'))
                self.success_file_data = success_data
                self.is_hide_success = False
            
        except:
            raise Warning(_("File Format not Valid!"))        

    def get_hsbc_file(self):
        try:
            failed_content = ''
            success_content = ''
            
            file_data = base64.b64decode(self.file_data)
            data = io.StringIO(file_data.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
            count = 0
            for line in file_reader:
                if count==0:
                    count += 2
                    continue
                # account_no = line[1]
                cutomer_ref = line[3]
                amount = line[6]
                if amount and cutomer_ref:
                    act_amount = float(amount)
                    match_payment =  self.payment_ids.filtered(lambda x:x.amount==act_amount and x.hsbc_reference==cutomer_ref)
                    if match_payment:
                        success_content += str(count)+' : '+ str(line) + "\n"                        
                        match_payment[0].post()
                    else:
                        failed_content += str(count)+' : '+ str(line) + "\n"
                else:
                    failed_content += str(count)+' : '+ str(line) + "\n"
                count += 1
                                                            
            if failed_content:
                failed_data = base64.b64encode(failed_content.encode('utf-8'))
                self.failed_file_data = failed_data
                self.is_hide_failed = False
                
            if success_content:
                success_data = base64.b64encode(success_content.encode('utf-8'))
                self.success_file_data = success_data
                self.is_hide_success = False
                                                            
        except:
            raise Warning(_("File Format not Valid!"))
                
                
    def get_santander_file(self):
        try:
            failed_content = ''
            success_content = ''
            
            file_data = base64.b64decode(self.file_data)
            data = io.StringIO(file_data.decode("utf-8")).readlines()
            count = 0
            for line in data:
                count+=1
                sing = line[76]
                amount = line[77:91]
                concept = line[113:152]
                if sing and amount and concept and sing=='-':
                    first_amount = amount[:-2]
                    last_amount = amount[-2:]
                    concept = concept.rstrip()    
                    act_amount = first_amount+"."+last_amount
                    act_amount = float(act_amount)
                    match_payment =  self.payment_ids.filtered(lambda x:x.amount==act_amount and x.santander_payment_concept==concept)
                    if match_payment:
                        success_content += str(count)+' : '+ str(line) + "\n"                        
                        match_payment[0].post()
                    else:
                        failed_content += str(count)+' : '+ str(line) + "\n"
                else:
                    failed_content += str(count)+' : '+ str(line) + "\n"

            if failed_content:
                failed_data = base64.b64encode(failed_content.encode('utf-8'))
                self.failed_file_data = failed_data
                self.is_hide_failed = False
                
            if success_content:
                success_data = base64.b64encode(success_content.encode('utf-8'))
                self.success_file_data = success_data
                self.is_hide_success = False
                                                                
        except:
            raise Warning(_("File Format not Valid!"))        

    def get_jp_morgan_file(self):
        try:

            failed_content = ''
            success_content = ''
            
            file_data = base64.b64decode(self.file_data)
            data = io.StringIO(file_data.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
            count = 0
            for line in file_reader:
                if count==0:
                    count += 2
                    continue
                jp_payment_concept = line[8]
                amount = line[10]
                if amount and jp_payment_concept:
                    act_amount = float(amount)
                    match_payment =  self.payment_ids.filtered(lambda x:x.amount==act_amount and x.jp_payment_concept==jp_payment_concept)
                    if match_payment:
                        success_content += str(count)+' : '+ str(line) + "\n"                        
                        match_payment[0].post()
                    else:
                        failed_content += str(count)+' : '+ str(line) + "\n"
                else:
                    failed_content += str(count)+' : '+ str(line) + "\n"
                count += 1
                
            if failed_content:
                failed_data = base64.b64encode(failed_content.encode('utf-8'))
                self.failed_file_data = failed_data
                self.is_hide_failed = False
                
            if success_content:
                success_data = base64.b64encode(success_content.encode('utf-8'))
                self.success_file_data = success_data
                self.is_hide_success = False
                                            
        except:
            raise Warning(_("File Format not Valid!"))        

    def get_bbva_file(self):
        try:
            failed_content = ''
            success_content = ''
            
            file_data = base64.b64decode(self.file_data)
            data = io.StringIO(file_data.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
            #account_no = ''
            count = 0
            for line in file_reader:
                print ("File===",line)
                count += 1
                #if line[0]=='11':
                    #account_no = line[3]
                #    continue
                if line[0]!='22':
                    continue
                payment_charge = line[7]
                amount = line[8]
                data_line = line[0]
                
                if data_line and data_line=='22' and amount and payment_charge and payment_charge=='1':
                    act_amount = float(amount)
                    
                    match_payment =  self.payment_ids.filtered(lambda x:x.amount==act_amount)
                    if match_payment:
                        success_content += str(count)+' : '+ str(line) + "\n"                        
                        match_payment[0].post()
                    else:
                        failed_content += str(count)+' : '+ str(line) + "\n"
                else:
                    failed_content += str(count)+' : '+ str(line) + "\n"
                
                
            if failed_content:
                failed_data = base64.b64encode(failed_content.encode('utf-8'))
                self.failed_file_data = failed_data
                self.is_hide_failed = False
                
            if success_content:
                success_data = base64.b64encode(success_content.encode('utf-8'))
                self.success_file_data = success_data
                self.is_hide_success = False
                                            
        except:
            raise Warning(_("File Format not Valid!"))        
          
    def load_bank_layout(self):
        diff_payment = self.payment_ids.filtered(lambda x:x.journal_id.load_bank_format != self.journal_id.load_bank_format)
        if diff_payment: 
            raise UserError(_("The selected layout does NOT match the bank of the selected payments"))

        if self.journal_id.load_bank_format == 'banamex':         
            self.get_banamex_file()
        if self.journal_id.load_bank_format == 'hsbc':         
            self.get_hsbc_file()
        if self.journal_id.load_bank_format == 'santander':         
            self.get_santander_file()
        if self.journal_id.load_bank_format == 'jp_morgan':
            self.get_jp_morgan_file()
        if self.journal_id.load_bank_format == 'bbva_bancomer':
            self.get_bbva_file()
        self.is_hide_file_upload = True
        
        return {
            'name': _('Load Bank Layout'),
            'res_model': 'load.bank.layout.supplier.payment',
            'res_id' : self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_load_bank_layout_supplier_payment_form').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
