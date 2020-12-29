from odoo import models, fields,_
from odoo.exceptions import UserError, ValidationError
import base64
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date

class GenerateCancelCheckLayout(models.TransientModel):
    _name = 'generate.cancel.check.layout'
    _description = 'Generate Cancel Check Layout'

    layout = fields.Selection([('Banamex', 'Banamex'), ('BBVA Bancomer Net Cash', 'BBVA Bancomer Net Cash'),
                                ('Santander', 'Santander')], string="Layout")
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Download')
    reissue_ids = fields.Many2many('reissue.checks','reissue_checks_bank_layout_rel','check_layout_id','reissue_id','Reissue')

    def banamex_cancel_check_file_format(self):
        file_data = ''
        file_name = 'Banamex.txt'
        
        #===Transaction Type ====#
        file_data += '01'
        #===Branch Account Number ====#
        file_data += '0650'
        #===Destination Account ====#
        file_data += '0000000000007274674'
        #===Client ====#
        file_data += '000008505585'
        #===File Format ====#
        file_data += '0001'
        #===Sequential ====#
        file_data += '000001'
        #===Future use ====#
        file_data += '00000000000'
        file_data +="\n"
        
        total_rec = len(self.reissue_ids)
        total_amount = 0
        
        for check in self.reissue_ids:
            #===Transaction Type ====#
            file_data += '02'
            #===Branch Account Number ====#
            file_data += '0650'
            #===Destination Account ====#
            file_data += '0000000000007274674'
            
            temp_log = ''
            if check.check_log_id and check.check_log_id.folio:
                temp_log =  check.check_log_id.folio
                file_data += str(temp_log).zfill(7)
            else:
                file_data += temp_log.zfill(7)

            #=== Check Status=======#
            file_data += '08'

            #====== Amount Data =========
            amount = round(check.check_amount, 2)
            amount = "%.2f" % check.check_amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(12)
            file_data +=str(amount[1])
            
            total_amount += check.check_amount
            #=====Future use=========#
            file_data += '0000000000'
            file_data +="\n"
        
        #=======TRAILER =======#
        
        #=======Transaction Type =======#
        file_data += '03'
        
        #====== Total Movement ======#
        file_data +=str(total_rec).zfill(6)

        #======Total Amount Data =========
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount            
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(14)
        file_data +=str(amount[1])

        gentextfile = base64.b64encode(bytes(file_data, 'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name

    def BBVA_cancel_check_file_format(self):
        file_data = ''
        file_name = 'BBVA Bancomer Net Cash.txt'
        
        #====== Number of account ==#
        file_data += '1/'
        # ==== bank account ===#
        bank_account = ''
        if self.reissue_ids and self.reissue_ids[0].bank_account_id:
            bank_account = self.reissue_ids[0].bank_account_id.acc_number
            
        bank_account.zfill(18)
        file_data += '/'
        total_rec = len(self.reissue_ids)
        total_amount = sum(x.check_amount for x in self.reissue_ids) 
        
        #====== Total Movement ======#
        file_data +=str(total_rec).zfill(6)
        file_data += '/'
        #======Total Amount Data =========
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount            
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(13)
        file_data +=str(amount[1])
        file_data += '/'

        #====== Current Dat time=========
        currect_time = datetime.today()
        
        file_data +=str(currect_time.year) + "-" 
        file_data +=str(currect_time.month).zfill(2) + "-"
        file_data +=str(currect_time.day).zfill(2)
        
        file_data += '\n'        
               
        for check in self.reissue_ids:
            temp_log = ''
            if check.check_log_id and check.check_log_id.folio:
                temp_log =  check.check_log_id.folio
                file_data += str(temp_log).zfill(7)
            else:
                file_data += temp_log.zfill(7)
            file_data += '/'
                        
            #===== action ======#
            file_data += 'B/'

            #====== Amount Data =========
            amount = round(check.check_amount, 2)
            amount = "%.2f" % check.check_amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +=str(amount[1])
            file_data += '\n'
            
        gentextfile = base64.b64encode(bytes(file_data, 'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
            

    def santander_cancel_check_file_format(self):
        file_data = ''
        file_name = 'Santander.txt'

        #===== Type of Registration =====#
        file_data += 'H'

        #====== Current Dat time=========
        currect_time = datetime.today()
        
        file_data +=str(currect_time.year) 
        file_data +=str(currect_time.month).zfill(2)
        file_data +=str(currect_time.day).zfill(2)
        
        #===== Filler ======#
        filler = ''
        file_data += filler.ljust(140, " ")

        #===== Key movement =====#
        file_data += '1'

        file_data += '\n'
        
        total_amount = 0
        
        for check in self.reissue_ids:
            #===== Registration =====#
            file_data += 'B'
            
            branch_number = ''
            if check.bank_id and check.bank_id.branch_number:
                branch_number = check.bank_id.branch_number
            file_data += branch_number

            #===== Account Currency=====#
            file_data += 'M'
            
            #===== Bank Account ====#
            bank_account = ''
            if check.bank_account_id and check.bank_account_id.acc_number:
                bank_account = check.bank_account_id.acc_number
            
            file_data +=bank_account.zfill(10)
            
            #====== Check Folio ======#
            temp_log = ''
            if check.check_log_id and check.check_log_id.folio:
                temp_log =  check.check_log_id.folio
                file_data += str(temp_log).zfill(10)
            else:
                file_data += temp_log.zfill(10)
            
            total_amount += check.check_amount
            
            #====== Amount Data =========#
            amount = round(check.check_amount, 2)
            amount = "%.2f" % check.check_amount            
            amount = str(amount).split('.')
            file_data +=str(amount[0]).zfill(13)
            file_data +=str(amount[1])
            
            #===== Beneficiary's =====#
            partner_name = ''
            if check.partner_id:
                partner_name = check.partner_id.name
            file_data += partner_name.rjust(60)
            
            #======= Fillrer=====
            file_data += ''.ljust(49)

            #======= Key Movement=====
            file_data += '3'
            
            file_data += '\n'
        
        #====Trailer========#
        
        #=========== Type Of Registration ====#
        file_data += 'P'

        #======= Total highs =====
        file_data += ''.ljust(9)

        #======= Checksum of Check Numbers =====
        file_data += ''.ljust(15)

        #======= Sum Of amounts =====
        file_data += ''.ljust(18)
        
        #======= Total Records =====
        total_rec= len(self.reissue_ids)
        file_data +=str(total_rec).zfill(9)
        
        #===== Checksum (Low) ===#
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount            
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(13)
        file_data +=str(amount[1])

        #===== Sum of amounts (Low) ===#    
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount       
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(16)
        file_data +=str(amount[1])
        
        #===== Total high and lows===#
        file_data +=str(total_rec).zfill(9)

        #===== Checksum (Low) ===#
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount            
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(13)
        file_data +=str(amount[1])

        #===== Sum of amounts (Low) ===#    
        amount = round(total_amount, 2)
        amount = "%.2f" % total_amount       
        amount = str(amount).split('.')
        file_data +=str(amount[0]).zfill(16)
        file_data +=str(amount[1])
        
        #======= Fillrer=====
        file_data += ''.ljust(21)

        #======= Key Movement=====
        file_data += '5'

                
        gentextfile = base64.b64encode(bytes(file_data, 'utf-8'))
        self.file_data = gentextfile
        self.file_name = file_name
            
    def action_generate(self):
        for check in self.reissue_ids:

            if check.state != 'approved' or not check.type_of_request != 'check_cancellation':
                raise ValidationError(_('Confirm that the status of all selected checks is "Approved" and Type of Request is "Check Cancellation", therefore no '
                                        'layout can be generated until the status is not Approved'))
            
            if check.bank_id and check.bank_id.name.upper() != self.layout.upper():
                raise ValidationError(_('The selected layout does NOT match the bank of the selected records" and no '
                                        'layout can be generated until the correct bank is selected.'))

        if self.layout == 'Banamex':
            self.banamex_cancel_check_file_format()
        elif self.layout == 'BBVA Bancomer Net Cash':
            self.BBVA_cancel_check_file_format()
        elif self.layout == 'Santander':
            self.santander_cancel_check_file_format()
                    
        return {
            'name': _('Generate Bank Layout'),
            'res_model': 'generate.cancel.check.layout',
            'res_id' : self.id,
            'view_mode': 'form',
            'target': 'new',
            #'view_id': self.env.ref('jt_supplier_payment.view_generate_payroll_payment_bank_layout').id,
            'type': 'ir.actions.act_window',
        }