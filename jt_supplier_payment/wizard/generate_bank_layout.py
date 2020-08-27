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
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date

class GenerateBankLayout(models.TransientModel):

    _name = 'generate.bank.layout'
    _description = 'Generate Bank Layout'
    
    journal_id = fields.Many2one('account.journal','Select the file to generate')
    payment_ids = fields.Many2many('account.payment','account_payment_bank_layout_rel','bank_layout_id','payment_id','Payments')
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Download')

    def action_generate_bank_layout(self):
        active_ids = self.env.context.get('active_ids')
        for payment in self.env['account.payment'].browse(active_ids):
            if payment.payment_state != 'for_payment_procedure':
                raise UserError(_("You can generate Bank Layout only for those payments which are in "
                "'For Payment Procedure'!"))
        if not active_ids:
            return ''
        
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.view_generate_bank_layout').id,
            'context': {'default_payment_ids':[(6,0,active_ids)]},
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def banamex_file_format(self):
        file_data = ''
        file_name = 'banamex.txt'
        
        for payment in self.payment_ids:
            file_data += '03'
            if payment.journal_id.account_type:
                if payment.journal_id.account_type=='check':
                    file_data += '01'
                    if payment.journal_id.branch_number:
                        file_data += payment.journal_id.branch_number.zfill(4)
                    else: 
                        file_data += '0000'                        
                elif payment.journal_id.account_type=='card':
                    file_data += '03'
                    file_data += '0000'
                elif payment.journal_id.account_type=='master':
                    file_data += '06'
                    file_data += '0000'
                else:
                    file_data += '0000'
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(20)
            else:
                temp =''
                file_data +=temp.zfill(20)
            #==== Receipt Bank DATA ===========
            if payment.payment_bank_account_id:
                if payment.payment_bank_account_id.account_type=='checks':
                    file_data += '01'
                    if payment.payment_bank_account_id.branch_number:
                        file_data += payment.payment_bank_account_id.branch_number.zfill(4)
                    else: 
                        file_data += '0000'                        
                elif payment.payment_bank_account_id.account_type=='card':
                    file_data += '03'
                    file_data += '0000'
                elif payment.payment_bank_account_id.account_type=='master_acc':
                    file_data += '06'
                    file_data += '0000'
                else:
                    file_data += '00'
                    file_data += '0000'
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(20)
            else:
                temp =''
                file_data +=temp.zfill(20)
                
            #====== Amount Data =========
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(12)
            file_data +=str(amount[1])
            
            #====== Currency Data =========
            if payment.currency_id:
                if payment.currency_id.name=='USD':
                    file_data +='005'
                elif payment.currency_id.name=='MXN':
                    file_data +='001'
            #====== Description =========
            temp_desc = ''
            if payment.banamex_description:
                temp_desc = payment.banamex_description
            file_data += temp_desc.ljust(24, " ")
    
            #====== banamex_concept =========
            temp_desc = ''
            if payment.banamex_concept:
                temp_desc = payment.banamex_concept
            file_data += temp_desc.ljust(34, " ")
    
            #====== banamex_reference =========
            temp_desc = ''
            if payment.banamex_reference:
                temp_desc = payment.banamex_reference
            file_data += temp_desc.ljust(10, " ")
            
            #====== Currency constant =========
            file_data += "000"
            #====== Current Dat time=========
            currect_time = datetime.today()
            
            file_data +=str(currect_time.day).zfill(2)
            file_data +=str(currect_time.month).zfill(2)
            file_data +=str(currect_time.year)[:2]
            file_data +=str(currect_time.hour).zfill(2)
            file_data +=str(currect_time.minute).zfill(2)
            file_data +="\n"
            
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def bbva_tnn_ptc_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER NET CASH​ (TNN or PTC).txt'
        
        for payment in self.payment_ids:
            #==== Receipt Bank DATA ===========#            
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #======= Bank Issuance of payment ======#    
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #====== Currency Data =========#
            if payment.currency_id:
                if payment.currency_id.name=='USD':
                    file_data +='USD'
                elif payment.currency_id.name=='MXN':
                    file_data += 'MXP'
                else:
                    file_data += payment.currency_id.name
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +='.'
            file_data +=str(amount[1])
            
            #=====reason for payment======#
            reason_payment = 'PAGO'
            if payment.payment_date:
                payment_year = str(payment.payment_date.year)[:2]
                month_name = format_datetime(payment.payment_date, 'MMMM', locale=get_lang(self.env).code)
                if payment.payment_date.month==1:
                    month_name = 'Enero'
                elif payment.payment_date.month==2:
                    month_name = 'Febrero'
                elif payment.payment_date.month==3:
                    month_name = 'Marzo'
                elif payment.payment_date.month==4:
                    month_name = 'Abril'
                elif payment.payment_date.month==5:
                    month_name = 'Mayo'
                elif payment.payment_date.month==6:
                    month_name = 'Junio'
                elif payment.payment_date.month==7:
                    month_name = 'Julio'
                elif payment.payment_date.month==8:
                    month_name = 'Agosto'
                elif payment.payment_date.month==9:
                    month_name = 'Septiembre'
                elif payment.payment_date.month==10:
                    month_name = 'Octubre'
                elif payment.payment_date.month==11:
                    month_name = 'Noviembre'
                elif payment.payment_date.month==12:
                    month_name = 'Diciembre'
                
                reason_payment += " "+month_name+" "+payment_year
            file_data += reason_payment.ljust(30, " ")     
            file_data +="\n"      
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def bbva_tsc_pcs_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER NET CASH​ ​ (TSC or PSC).txt'
        
        for payment in self.payment_ids:
            #==== Receipt Bank DATA ===========#            
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            if payment.journal_id.bank_account_id:
                file_data += payment.journal_id.bank_account_id.acc_number.zfill(18)
            else:
                temp =''
                file_data +=temp.zfill(18)
            #====== Currency Data =========#
            file_data += 'MXP'
#             if payment.currency_id:
#                 file_data += payment.currency_id.name
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +='.'
            file_data +=str(amount[1])

            #=====“Beneficiary”======#
            beneficiary_name=''
            if payment.partner_id:
                beneficiary_name = payment.partner_id.name
            file_data += beneficiary_name.ljust(30, " ")   
            #======= Type of Account ========#
            bank_account_code = '00'
            print ("=====",payment.partner_id.bank_ids)
            if payment.partner_id and payment.partner_id.bank_ids:
                if payment.partner_id.bank_ids[0].account_type=='card':
                    bank_account_code = '03'
                elif payment.partner_id.bank_ids[0].account_type=='clabe_acc':
                    print ("=====",payment.partner_id.bank_ids[0].account_type)
                    bank_account_code = '40'
            file_data +=  bank_account_code
              
#             if payment.payment_bank_account_id:
#                 if payment.payment_bank_account_id.account_type=='card':
#                     file_data += '03'
#                 elif payment.payment_bank_account_id.account_type=='clabe_acc':
#                     file_data += '40'
#                 else:
#                     file_data += '00'
            #======= Bank Code / Key bank ========#
            if payment.payment_bank_id:
                bank_code = ''
                if payment.payment_bank_id.l10n_mx_edi_code:
                    bank_code = payment.payment_bank_id.l10n_mx_edi_code
                file_data += bank_code.zfill(3)
            #=====reason for payment======#
            reason_payment = 'PAGO'
            if payment.payment_date:
                payment_year = str(payment.payment_date.year)[:2]
                month_name = format_datetime(payment.payment_date, 'MMMM', locale=get_lang(self.env).code)
                reason_payment += " "+month_name+" "+payment_year
            file_data += reason_payment.ljust(30, " ")     
            #====== net_cash_reference =======#
            net_cash_reference = ''
            if payment.net_cash_reference:
                net_cash_reference = payment.net_cash_reference
            file_data += net_cash_reference.zfill(7)
            #====== net_cash_availability =======#   
            if payment.net_cash_availability:
                if payment.net_cash_availability=='SPEI':
                    file_data += 'H'
                elif payment.net_cash_availability=='CECOBAN':
                    file_data += 'M'
            file_data +="\n"      
                                     
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def bbva_sit_file_format(self):
        file_data = ''
        file_name = 'BBVA BANCOMER SIT.txt'
        
        #============= Header Data =========#
        file_data += 'H'
        file_data += '000747289'
        
        #========= Current Date =========
        currect_time = datetime.today()
        file_data +=str(currect_time.year)
        file_data +="-"+str(currect_time.month).zfill(2)
        file_data +="-"+str(currect_time.day)
        
        file_data += '01'
        
        #===== sit_file_key ====
        sit_file_key = ''
#         if payment.sit_file_key:
#             sit_file_key = payment.sit_file_key
        file_data +=sit_file_key.ljust(30)
        #======== Response Code =======#
        file_data += '00'
        #======== Response code description =======#
        file_data += ''.ljust(20)
        #======= Channel =======#
        file_data += ''.ljust(3)
        #========= Charge account ==========#
        if self.journal_id.bank_account_id:
            file_data += self.journal_id.bank_account_id.acc_number.zfill(35)
        else:
            temp =''
            file_data +=temp.zfill(35)
        #====== Currency of the agreement =======#
        file_data += ''.ljust(3)
        #======== FILLER =========
        file_data += ''.ljust(1251)
        file_data +="\n"

        #============= Payment  Details =========#              
        for payment in self.payment_ids:

            #=======Registration indicato ========            
            file_data +="D"
            #=======Instruction ========            
            file_data +="A"
            #=======Document type ========            
            file_data +="P"
            #=== Reference  =====
            folio = ''
            if payment.folio:
                folio = payment.folio
            folio_splits = folio.split('/')
            rec_data = ''
            for sp_data in folio_splits:
                rec_data+=sp_data
            file_data += rec_data.ljust(20)
            #===== Provider Password / Beneficiary Password =======#
            pass_beneficiary = ''
            if payment.partner_id and payment.partner_id.password_beneficiary:
                pass_beneficiary = payment.partner_id.password_beneficiary
            file_data += pass_beneficiary.ljust(30)
            #======= Type of Service  =======
            file_data +="PDA"
            
            #======= Operation code  ========#
            sit_operation_code = '0'
            if payment.sit_operation_code:
                if payment.sit_operation_code=='payment_on_account_bancomer':
                    sit_operation_code = '2'
                elif payment.sit_operation_code=='payment_interbank':
                    sit_operation_code = '5'
            file_data +=sit_operation_code
            #======== Charge account  ==========#
            file_data += ''.zfill(20)
            #======== FILLER ========
            file_data += ''.ljust(15)
            #=======Reference numeral ========#
            sit_reference = ''
            if payment.sit_operation_code and payment.sit_operation_code=='payment_interbank' and payment.sit_reference:
                sit_reference = payment.sit_reference
            file_data += sit_reference.ljust(25)
            #=======Reason For Payment ========#
            sit_reason_for_payment = ''
            if payment.sit_operation_code and payment.sit_operation_code=='payment_interbank' and payment.sit_reason_for_payment:
                sit_reason_for_payment = payment.sit_reason_for_payment
            file_data += sit_reason_for_payment.ljust(37)
            #======== FILLER ========
            file_data += ''.ljust(15)
    
            #=======Personalized legend ========#
            sit_reference = ''
            if payment.sit_reference:
                sit_reference = payment.sit_reference
            file_data += sit_reference.ljust(25)
            #======== CIE Concept ========#
            file_data += ''.ljust(37)
            #======Tax receipt =====#
            file_data += "N"
            #======== FILLER ========#
            file_data += ''.ljust(8)
            #======= Account type ======#
            file_data += ''.ljust(2)
            #======= Subscription account ======#
            file_data += ''.ljust(35)
            #======= Name of 1st beneficiary ======#
            file_data += ''.ljust(40)
            #======= Identification code of the 1st beneficiary======#
            file_data += ''.ljust(1)
            #======= Identification number 1st beneficiary======#
            file_data += ''.ljust(30)
            #======= Name of 2nd beneficiary======#
            file_data += ''.ljust(40)
            #======= Identification code of the 2nd beneficiary======#
            file_data += ''.ljust(1)
            #======= Identification number 2nd beneficiary======#
            file_data += ''.ljust(30)
            #====== Currency Data =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += 'MXP'
                else:
                    file_data += payment.currency_id.name
            #====== BIC / SWIFT =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += ''.ljust(11)
                else:
                    if payment.payment_bank_account_id and payment.payment_bank_account_id.bic_swift:
                        file_data += payment.payment_bank_account_id.bic_swift.ljust(11)
                    else:
                        file_data += ''.ljust(11)                         

            #====== ABA =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += ''.ljust(9)
                else:
                    if payment.payment_bank_account_id and payment.payment_bank_account_id.aba:
                        file_data += payment.payment_bank_account_id.aba.zfill(9)
                    else:
                        file_data += ''.zfill(9)                         
        
            #======= Document key ========#
            file_data += 'FA'
            #====== Amount Data =========
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +=str(amount[1])
            #========FILLER==========
            file_data +=''.zfill(15)
            #======= Confirmation Type ========#
            file_data += '01'
            #========== Email ==========#
            email = ''
            if payment.partner_id and payment.partner_id.email:
                email =  payment.partner_id.email
            file_data += email.ljust(50)
            #===== Periodicity interest of ======#
            file_data += 'N'
            #======= FILLER =======#
            file_data +=''.zfill(8)
            #======= FILLER =======#
            file_data +=''.zfill(4)

            #========= Payment Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +="-"+str(payment.payment_date.month).zfill(2)
                file_data +="-"+str(payment.payment_date.day)
            #====== Effective date =======#
            file_data += '0001-01-01'
            #====== Grace Date =======#
            file_data += '0001-01-01'
            #====== Expiration date=======#
            file_data += '0001-01-01'
            #=========Document Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +="-"+str(payment.payment_date.month).zfill(2)
                file_data +="-"+str(payment.payment_date.day)
            #====== Recurring payment indicator =========#
            file_data += 'N'
            #======= FILLER =======#
            file_data += ''.ljust(1) 
            #====== Recurring payment end date=======#
            file_data += '0001-01-01'
            #==== Additional data length or Payment detail =====#
            file_data += '700'
            #======== Additional =======#
            additional = 'PAGO UNAM'
            if payment.folio:
                split_data = payment.folio.split('/')
                if split_data:
                    additional +=" - "+split_data[0]
            if payment.sit_additional_data:
                additional += payment.sit_additional_data
            file_data += additional.ljust(700)
            #======= FILLER =======#
            file_data += ''.ljust(10) 
            #======= FILLER =======#
            file_data += ''.ljust(10)
            #======= Code status of the document =======# 
            file_data += ''.ljust(2)
            #======= Document status code description =======# 
            file_data += ''.ljust(30)
            #====== Date of last document event=======#
            file_data += '0001-01-01'
            file_data +="\n"
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def santander_file_format(self):
        file_name = 'SANTANDER.txt'
        file_data = ''
        for payment in self.payment_ids:
            #========= Charge account ==========#
            if self.journal_id.bank_account_id:
                file_data += self.journal_id.bank_account_id.acc_number.zfill(11)
            else:
                temp =''
                file_data +=temp.zfill(11)
            #====== Spaces ====#
            file_data += ''.ljust(5)
            #===== Bank Account Payment Receiving ========#
            if payment.payment_bank_account_id:
                file_data += payment.payment_bank_account_id.acc_number.zfill(11)
            else:
                temp =''
                file_data +=temp.zfill(11)
            #====== Spaces ====#
            file_data += ''.ljust(5)
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(10)
            file_data +='.'
            file_data +=str(amount[1])
            #======= Payment concept ==========#
            santander_payment_concept = ''
            if payment.santander_payment_concept:
                santander_payment_concept = payment.santander_payment_concept
            file_data += santander_payment_concept.ljust(40)
            
            #==== Payment Date ======
            if payment.payment_date:
                file_data +=str(payment.payment_date.day)
                file_data +=str(payment.payment_date.month).zfill(2)
                file_data +=str(payment.payment_date.year)[:2]
            file_data +="\n"
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
            
    def hsbc_file_format(self):    
        file_name = 'HSBC.csv'
        record_count = 0
        file_data = ''
        for payment in self.payment_ids:
            #==========Sequence ========#
            record_count+=1
            file_data+=str(record_count)

            #==========Bank Account ========#
            if self.journal_id.bank_account_id:
                file_data +=","+self.journal_id.bank_account_id.acc_number.zfill(10)
            else:
                temp =''
                file_data +=","+temp.zfill(10)
            #===== Bank Account Payment Receiving ========#
            if payment.payment_bank_account_id:
                file_data += ","+payment.payment_bank_account_id.acc_number.zfill(10)
            else:
                temp =''
                file_data +=","+temp.zfill(10)            
            #====== Amount Data =========#
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            #print ('Amount=====',x)
            file_data +=","+str(amount[0])
            file_data +='.'
            file_data +=str(amount[1])
            
            #====== Currency Data =========#
            if payment.currency_id:
                if payment.currency_id.name=='MXN':
                    file_data += ','+'1'
                elif payment.currency_id.name=='USD':
                    file_data += ','+'2'
                else:
                    file_data += ','+''
            #===== hsbc_reference ====#
            hsbc_reference = ''
            if payment.hsbc_reference:
                hsbc_reference = payment.hsbc_reference
            file_data +="," + hsbc_reference
            #======= Partner Name ========#
            partner_name = ''
            if payment.partner_id:
                partner_name = payment.partner_id.name
            file_data +="," + partner_name   
            #==== Fiscal Proof  ========#
            file_data +="," + '0'
            #==== RFC Of the beneficiary  ========#
            file_data +=",                  " # 18 Space
            #====VAT  ========#
            file_data +=",             "    # 13 Space 
            
            file_data +="\n"
        
        file_data +=str(record_count+1) + ","+ str(record_count) + ","+'Transfer terceros' 
        
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def jp_morgan_wires_file_format(self):   

        file_name = 'jp_morgan_wires.csv'
        record_count = 0
        total_amount = 0
        file_data = 'HEADER'+","
        #====== Current Dat time=========
        currect_time = datetime.today()
        file_data +=str(currect_time.year)
        file_data +=str(currect_time.month).zfill(2)
        file_data +=str(currect_time.day)
        file_data +=str(currect_time.hour)
        file_data +=str(currect_time.minute)
        file_data +=str(currect_time.second)
        
        file_data += ","+"1.0"
        file_data +="\n"                
        for payment in self.payment_ids:
            record_count += 1
            file_data += "P"
            file_data += ','
            #======== Method ========#
            if payment.jp_method:
                if payment.jp_method == 'WIRES':
                    file_data += 'WIRES'
                    file_data += ','
                if payment.jp_method == 'BOOKTX':
                    file_data += 'BOOKTX'
                    file_data += ','
            else:
                file_data += ','
            
            # ======== BIC /SWIFT ======
            if payment.payment_bank_id:
                bank_code = ''
                if payment.payment_bank_id.bic:
                    bank_code = payment.payment_bank_id.bic
                file_data += bank_code            
            file_data += ','

            #==========Bank Account ========#
            if self.journal_id.bank_account_id:
                file_data +=self.journal_id.bank_account_id.acc_number
            file_data += ','
            # ===== Bank to bank transfer ========#
            if payment.jp_bank_transfer:
                if payment.jp_bank_transfer == 'non_financial_institution':
                    file_data += 'N'
                elif payment.jp_bank_transfer == 'financial_institution':
                    file_data += 'Y'
            file_data += ','

            #====== Currency Data =========#
            if payment.currency_id:
                file_data += payment.currency_id.name
            file_data += ','

            #====== Amount Data =========#
            total_amount += payment.amount
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            #print ('Amount=====',x)
            file_data +=str(amount[0])
            file_data +='.'
            file_data +=str(amount[1])
            file_data += ','
            #===== Equivalent Amount======#
            file_data += ','.ljust(1)
                   
            #===== N / A======#
            file_data += ',,,,'
            #======== Payment Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +=str(payment.payment_date.month).zfill(2)
                file_data +=str(payment.payment_date.day)
            file_data += ','
            
            # ====== ID Type ======#
            if payment.jp_id_type:
                if payment.jp_id_type == 'clabe':
                    file_data += 'CLBE_CODE'
                elif payment.jp_id_type == 'debit_card':
                    file_data += 'DR_CARD'
                elif payment.jp_id_type == 'vostro':
                    file_data += 'VOSTRO_CD'
            file_data += ','

            # ======== CLABE ======
            if payment.payment_bank_account_id:
                bank_clabe = ''
                if payment.payment_bank_account_id.l10n_mx_edi_clabe:
                    bank_code = payment.payment_bank_account_id.l10n_mx_edi_clabe
                file_data += bank_clabe            
            file_data += ','
            
            #======= Partner Name ========#
            partner_name = ''
            if payment.partner_id:
                partner_name = payment.partner_id.name
            file_data +=partner_name   
            file_data += ','            

            #======= Partner Address1 ========#
            address_1 = ''
            if payment.partner_id and payment.partner_id.street:
                address_1 = payment.partner_id.street
            file_data +=address_1   
            file_data += ','            
            

            #======= Partner Address2 ========#
            address_2 = ''
            if payment.partner_id and payment.partner_id.street2:
                address_2 = payment.partner_id.street2
            file_data +=address_2   
            file_data += ','            

            #======= Partner Address3====#
            address_3 = ''
            if payment.partner_id:
                if payment.partner_id.city:
                    address_3 = payment.partner_id.city
                if payment.partner_id.zip:
                    address_3 += " "+payment.partner_id.zip
            file_data +=address_3   
            file_data += ','            
            # ==== Blank =======
            file_data += ','

            # ==== Country Name =======
            country_code = ''
            if payment.partner_id and payment.partner_id.country_id:
                country_code = payment.partner_id.country_id.code or ''
            file_data +=country_code   
            
            file_data += ','
            #====== Blank Value ======
            file_data += ',,'
            file_data += ','
            #======== ID Type Beneficiary Bank ========#
            if payment.jp_id_type_beneficiary_bank:
                if payment.jp_id_type_beneficiary_bank == 'None':
                    file_data += 'None'
                elif payment.jp_id_type_beneficiary_bank == 'SPEI':
                    file_data += 'SPEI'
                elif payment.jp_id_type_beneficiary_bank == 'SWIFT':
                    file_data += 'SWIFT'
            file_data += ','
            #===== Bank Key =======
            if payment.payment_bank_account_id:
                bank_code = ''
                if payment.payment_bank_id.l10n_mx_edi_code:
                    bank_code = payment.payment_bank_id.l10n_mx_edi_code
                file_data += bank_code
            #==== Bank Name=========#
            if payment.payment_bank_id:
                bank_name = ''
                if payment.payment_bank_id.name:
                    bank_name = payment.payment_bank_id.name
                file_data += bank_name            
            file_data += ','
            
            #======= Bank Address1 ========#
            address_1 = ''
            if payment.payment_bank_id:
                address_1 = payment.payment_bank_id.street or ''
            file_data +=address_1   
            file_data += ','            
            

            #======= Bank Address2 ========#
            address_2 = ''
            if payment.payment_bank_id:
                address_2 = payment.payment_bank_id.street2 or ''
            file_data +=address_2   
            file_data += ','            

            #======= Bank Address3====#
            address_3 = ''
            if payment.payment_bank_id and payment.payment_bank_id.state:
                address_3 = payment.payment_bank_id.state.name
                address_3 += " "+payment.payment_bank_id.zip or ''
            file_data +=address_3   
            file_data += ','            

            # ==== Country Name =======
            country_code = ''
            if payment.partner_id and payment.payment_bank_id.country:
                country_code = payment.payment_bank_id.country.code or ''
            file_data +=country_code   
            file_data += ','
            #=====Supplementary ID======#
            file_data += ','
            #=====Supplementary ID Value======#
            file_data += ','            
            #=====N\A======#
            file_data += ',,,,,,,'            
            #=====ID Type======#
            file_data += ','            
            #=====ID Voucher======#
            file_data += ','            
            #=====Bank Name======#
            file_data += ','            
            #=====Address 1======#
            file_data += ','            
            #=====Address 2======#
            file_data += ','
            #=====Address 3======#
            file_data += ','            
            #=====Country======#
            file_data += ','            
            #=====N/A======#
            file_data += ',,'            
            #=====ID Type======#
            file_data += ',,'            
            #=====By Order Name======#
            file_data += ','            
            #=====Address 1======#
            file_data += ','            
            #=====Address 2======#
            file_data += ','
            #=====Address 3======#
            file_data += ','            
            #=====Country======#
            file_data += ','            
            #=====N/A======#
            file_data += ',,,,,,,,,,,,,,,,,'
            #======== Reference Sent with Payment ======#
            file_data += ','
            #======== Interanal Reference  ======#
            file_data += ','
            #======== N/A  ======#
            file_data += ','
            #======== Detail 1  ======#
            file_data += ','
            #======== Detail 2  ======#
            file_data += ','
            #======== Detail 3  ======#
            file_data += ','
            #======== Detail 4  ======#
            file_data += ','
            #======== N/A  ======#
            file_data += ','
            #======== Code  ======#
            file_data += ','
            #======== Country  ======#
            file_data += ','
            #======== Instruction 1  ======#
            file_data += ','
            #======== Instruction 2  ======#
            file_data += ','
            #======== Instruction 3  ======#
            file_data += ','
            #======== Instruction Code1  ======#
            file_data += ','
            #======== Instruction  Text 1 ======#
            file_data += ','
            #======== Instruction Code 2 ======#
            file_data += ','
            #======== Instruction  Text 2 ======#
            file_data += ','
            #======== Instruction Code 3  ======#
            file_data += ','
            #======== Instruction  Text 3 ======#
            file_data += ','

            #======== Sender to Receiver Code 1  ======#
            file_data += ','
            #======== Sender to Receiver Line 1======#
            file_data += ','
            #======== Sender to Receiver Code 2  ======#
            file_data += ','
            #======== Sender to Receiver Line 2 ======#
            file_data += ','
            #======== Sender to Receiver Code 3  ======#
            file_data += ','
            #======== Sender to Receiver Line 3 ======#
            file_data += ','
            #======== Sender to Receiver Code 4  ======#
            file_data += ','
            #======== Sender to Receiver Line 4 ======#
            file_data += ','
            #======== Sender to Receiver Code 5  ======#
            file_data += ','
            #======== Sender to Receiver Line 5 ======#
            file_data += ','
            #======== Sender to Receiver Code 6  ======#
            file_data += ','
            #======== Sender to Receiver Line 6 ======#
            file_data += ','
            #======== Priority ======#
            file_data += ','
            #======== N/A ======#
            file_data += ','
            #======== Charges ======#
           
            #======== ID Type Beneficiary Bank ========#
            if payment.jp_charges:
                if payment.jp_charges == 'shared':
                    file_data += 'AHS'
                elif payment.jp_charges == 'beneficiary':
                    file_data += 'BEN'
                elif payment.jp_charges == 'remitter':
                    file_data += 'OUR'
            file_data += ','
            #======== N/A ======#
            file_data += ','

            #======== Aditional Details ======#
            file_data += ','
            #======== Note ======#
            file_data += ','
            #======== Beneficiary Email ======#
            file_data += ','
            #======== Payroll Indicatorl ======#
            file_data += ','
            #======== Confidential Indicator ======#
            file_data += ','
            #====== Group Name==========#
            file_data += ','
            
            file_data +="\n"    
        file_data += "TRAILER" +","+str(record_count)+","
        amount = "%.2f" % total_amount
        amount = str(amount).split('.')
        file_data +=str(amount[0])
        file_data +='.'
        file_data +=str(amount[1])
                                       
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def jp_morgan_us_drawdowns_file_format(self):
        file_name = 'jp_morgan_us_drawdowns.csv'
        record_count = 0
        total_amount = 0
        file_data = ''
        for payment in self.payment_ids:
            record_count += 1
            #======= Input Type =======
            file_data += "P"
            file_data += ','
            #========= Receipt Method ======
            file_data += "DRWDWN"
            file_data += ','
            # ======== BIC /SWIFT ======
            if payment.payment_bank_id:
                bank_code = ''
                if payment.payment_bank_id.bic:
                    bank_code = payment.payment_bank_id.bic
                file_data += bank_code            
            file_data += ','
            #==========Bank Account ========#
            if self.journal_id.bank_account_id:
                file_data +=self.journal_id.bank_account_id.acc_number
            file_data += ','
            #======= N/A ==========#
            file_data += ','
            #======== Currency =========#
            file_data += "USD"
            file_data += ','
            #====== Amount Data =========#
            total_amount += payment.amount
            amount = round(payment.amount, 2)
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            file_data +=str(amount[0])
            file_data +='.'
            file_data +=str(amount[1])
            file_data += ','
            #======= N/A ==========#
            file_data += ','

            # ===== Drawdown Type ========#
            if payment.jp_drawdown_type:
                if payment.jp_drawdown_type == 'WIRE':
                    file_data += 'WIRE'
                elif payment.jp_drawdown_type == 'BOOK':
                    file_data += 'BOOK'
            file_data += ','
            #======= N/A ==========#
            file_data += ',,,'
            #======== Payment Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +=str(payment.payment_date.month).zfill(2)
                file_data +=str(payment.payment_date.day)
            file_data += ','
            #======= N/A ==========#
            file_data += ',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
            #==========Bank Account ========#
            if payment.payment_bank_account_id:
                file_data +=payment.payment_bank_account_id.acc_number
            file_data += ','
            #======= Partner Name ========#
            partner_name = ''
            if payment.partner_id:
                partner_name = payment.partner_id.name
            file_data +=partner_name
            file_data += ','  
            #====== Address 1 ======# 
            file_data += ','
            #======== N/A =======#
            file_data += ','
            #====== City ======#
            file_data += ','
            #===== Country ======#
            file_data += 'MX'
            file_data += ','
            #===== ID Type =======#
            if payment.jp_drawdown_type and payment.jp_drawdown_type=='Drawdown':
                if payment.payment_bank_id:
                    bank_code = ''
                    if payment.payment_bank_id.bic:
                        bank_code = payment.payment_bank_id.bic
                    file_data += bank_code            
                file_data += ','
            else:
                file_data += ','
            #======== Journal Account =======#
            if payment.jp_drawdown_type and payment.jp_drawdown_type=='Drawdown':
                if self.journal_id.bank_account_id:
                    file_data +=self.journal_id.bank_account_id.acc_number
                file_data += ','
            else:
                file_data += ','

            #======== Bank of receipt of payment =======#
            if payment.jp_drawdown_type and payment.jp_drawdown_type=='Drawdown':
                if payment.payment_bank_id:
                    file_data += payment.payment_bank_id.name
                file_data += ','
            else:
                file_data += ','

            #======== Bank Address 1 =======#
            if payment.jp_drawdown_type and payment.jp_drawdown_type=='Drawdown':
                if payment.payment_bank_id and payment.payment_bank_id.street:
                    file_data += payment.payment_bank_id.street
                file_data += ','
            else:
                file_data += ','
            #===== N/A=======#
            file_data += ','
            #===== City=======#
            file_data += ','
            #=====Country=======#
            file_data += ','
            #===== N/A=======#
            file_data += ','
            #===== Internal Reference=======#
            file_data += ','
            #===== N/A=======#
            file_data += ','
            #===== Details1=======#
            file_data += ','
            #===== Details2=======#
            file_data += ','
            #===== Details3=======#
            file_data += ','
            #===== Details4=======#
            file_data += ','
            #===== N/A=======#
            file_data += ',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
            #===== Note=======#
            file_data += ','
            #===== N/A=======#
            file_data += ','
            file_data += '\n'            
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def jp_morgan_advice_to_receive_file_format(self):
        file_name = 'jp_morgan_advice_to_receive.csv'
        record_count = 0
        total_amount = 0
        file_data = ''
        for payment in self.payment_ids:
            record_count += 1
            #========Input Type=======#
            file_data += 'P'
            file_data += ','
            #========Receipt Method=======#
            file_data += 'ATR'
            file_data += ','
            # ======== BIC /SWIFT ======
            if payment.payment_bank_id:
                bank_code = ''
                if payment.payment_bank_id.bic:
                    bank_code = payment.payment_bank_id.bic
                file_data += bank_code            
            file_data += ','
            #==========Bank Account ========#
            if self.journal_id.bank_account_id:
                file_data +=self.journal_id.bank_account_id.acc_number
            file_data += ','
            #======= N/A=========#
            file_data += ','
            #====== Currency Data =========
            if payment.currency_id:
                file_data += payment.currency_id.name
            file_data += ','
            #====== Amount Data =========#
            amount = "%.2f" % payment.amount
            amount = str(amount).split('.')
            file_data +=str(amount[0])
            file_data +='.'
            file_data +=str(amount[1])
            file_data += ','
            #====== N/A =========#
            file_data += ',,,,,'
            #======== Payment Date =========
            if payment.payment_date:
                file_data +=str(payment.payment_date.year)
                file_data +=str(payment.payment_date.month).zfill(2)
                file_data +=str(payment.payment_date.day)
            file_data += ','
            #======= N/A=========#
            file_data += ',,,,,,,,,,,,,,,,,,,,,,,,,,'
            #===== ID Type =======#
            if payment.jp_drawdown_type and payment.jp_drawdown_type=='Drawdown':
                if payment.payment_bank_id:
                    bank_code = ''
                    if payment.payment_bank_id.bic:
                        bank_code = payment.payment_bank_id.bic
                    file_data += bank_code            
                file_data += ','
            else:
                file_data += ','
            #====== ID Value =======#
            file_data += ','
            #======== Bank of receipt of payment =======#
            if payment.payment_bank_id:
                file_data += payment.payment_bank_id.name
                file_data += ','
            else:
                file_data += ','
            #===== Address 1 ========#
            file_data += ','
            #===== Address 2 ========#
            file_data += ','
            #===== Address 3 ========#
            file_data += ','
            # ==== Country Name =======
            country_code = ''
            if payment.payment_bank_id and payment.payment_bank_id.country:
                country_code = payment.payment_bank_id.country.code or ''
            file_data +=country_code   
            file_data += ','
            #========== N/A=========
            file_data += ',,,,,,,,,'
            #========= Name========3
            file_data += 'UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO'
            file_data += ','
            #====== Address 1 =======#
            file_data += ','
            #====== Address 2 =======#
            file_data += ','
            #====== City =======#
            file_data += ','
            #====== Country =======#
            file_data += ','
            #====== N/A =======#
            file_data += ',,,,,,,,,,,,,'
            #====== N/A =======#
            file_data += ','
            #======Internal Reference =======#
            file_data += ','
            #======N/A =======#
            file_data += ',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
            #======= Note ========#
            file_data += ','
            #======== N/A =======#
            file_data += ','
            file_data += '\n'   
            
        gentextfile = base64.b64encode(bytes(file_data,'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
        
    def generate_bank_layout(self):
        for payment in self.payment_ids:
            if payment.journal_id.id != self.journal_id.id:
                raise UserError(_("The selected layout does NOT match the bank of the selected payments"))
        if self.journal_id.bank_format == 'banamex':
            self.banamex_file_format()
        elif self.journal_id.bank_format == 'bbva_tnn_ptc':
            self.bbva_tnn_ptc_file_format()
        elif self.journal_id.bank_format == 'bbva_tsc_pcs':
            self.bbva_tsc_pcs_file_format()
        elif self.journal_id.bank_format == 'bbva_sit':
            self.bbva_sit_file_format()
        elif self.journal_id.bank_format == 'santander':
            self.santander_file_format()
        elif self.journal_id.bank_format == 'hsbc':
            self.hsbc_file_format()
        elif self.journal_id.bank_format == 'jpmw':
            self.jp_morgan_wires_file_format()
        elif self.journal_id.bank_format == 'jpma':
            self.jp_morgan_advice_to_receive_file_format()
        elif self.journal_id.bank_format == 'jpmu':
            self.jp_morgan_us_drawdowns_file_format()
        else:
            self.file_data = False
            self.file_name = False

        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.bank.layout',
            'res_id' : self.id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }    
    
    
    
    
