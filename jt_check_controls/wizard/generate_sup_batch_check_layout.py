from odoo import fields, models, api, _
import datetime
from odoo.exceptions import ValidationError
import base64
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class GenerateSupplierCheckLayout(models.TransientModel):
    _name = 'generate.supp.check.layout'
    _description = 'Generate Supplier Check Layout'

    layout = fields.Selection([('Banamex', 'Banamex'), ('BBVA Bancomer', 'BBVA Bancomer'),
                               ('Inbursa', 'Inbursa'), ('Santander', 'Santander'),
                               ('Scotiabank', 'Scotiabank')], string="Layout")
    file_name = fields.Char('Filename')
    file_data = fields.Binary('Download')
    batch_id = fields.Many2one('payment.batch.supplier')

    def action_generate(self):
        batch = self.batch_id
        if batch:
            if batch.payment_issuing_bank_id.name.upper() != self.layout.upper():
                raise ValidationError(_('The selected layout does NOT match the bank of the selected records" and no '
                                        'layout can be generated until the correct bank is selected.'))
            invalid_req = batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status != 'Delivered')
            if invalid_req:
                raise ValidationError(_('Confirm that the status of all selected checks is "Delivered", therefore no '
                                        'layout can be generated until the status is as indicated above'))
            bank = batch.payment_issuing_bank_id
            file_data = ''
            file_name = ''
            if self.layout == 'Banamex':
                file_name = 'banamex.txt'
                file_data += '01'
                file_data += bank.branch_number if bank.branch_number else ''
                file_data += bank.bank_account_id.acc_number.zfill(20) if bank.bank_account_id else '00000000000000000000'
                file_data += '000008505585'
                file_data += '0001'
                file_data += str(self.env['ir.sequence'].next_by_code('sup.batch.banamex.layout'))
                file_data += '000000000000'
                file_data += '\n'
                total_amt = 0
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'):
                    file_data += '02'
                    file_data += bank.branch_number if bank.branch_number else ''
                    file_data += bank.bank_account_id.acc_number.zfill(20) if bank.bank_account_id \
                        else '00000000000000000000'
                    reqs = batch.payment_req_ids.filtered(lambda x: x.check_folio_id != False)
                    if reqs:
                        file_data += str(reqs[0].check_folio_id.folio).zfill(7)
                    else:
                        file_data += '0000000'
                    file_data += '01'
                    line_amt = str(round(line.amount_to_pay, 2)).split('.')
                    file_data += str(line_amt[0]).zfill(12)
                    file_data += str(line_amt[1]) if len(str(line_amt[1])) == 2 else str(line_amt[1]) + '0'
                    file_data += '00000000000'
                    file_data += '\n'
                    total_amt += line.amount_to_pay
                file_data += '03'
                file_data += str(len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'))).zfill(6)
                total_amt = str(round(total_amt, 2)).split('.')
                file_data += str(total_amt[0]).zfill(14)
                file_data += str(total_amt[1]) if len(str(total_amt[1])) == 2 else str(total_amt[1]) + '0'
            elif self.layout == 'BBVA Bancomer':
                file_name = 'bbva.txt'
                file_data += '1'
                file_data += '/'
                file_data += bank.bank_account_id.acc_number.zfill(18) if bank.bank_account_id \
                        and bank.bank_account_id.acc_number else '000000000000000000'
                file_data += '/'
                total_rec = len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                             x.check_status == 'Delivered'))
                file_data += str(total_rec).zfill(6)
                file_data += '/'
                total_amt = sum(
                    line.amount_to_pay for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                                                x.check_status == 'Delivered'))
                file_data += str(round(total_amt, 2)).replace('.', '').zfill(15)
                file_data += '/'
                today_date = datetime.date.today().strftime("%Y-%m-%d")
                file_data += str(today_date)
                file_data += '/'
                file_data += "\n"
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                                     x.check_status == 'Delivered'):
                    file_data += str(line.check_folio_id.folio).zfill(7)
                    file_data += '/'
                    file_data += 'A'
                    file_data += '/'
                    file_data += str(round(line.amount_to_pay,2)).replace('.','').zfill(15)
                    file_data += "\n"
            elif self.layout == 'Santander':
                file_name = 'santander.txt'
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'):
                    file_data += bank.bank_account_id.acc_number.ljust(18) if bank.bank_account_id \
                        else '000000000000000000'
                    file_data += str(line.check_folio_id.folio).ljust(7)
                    file_data += '             '
                    file_data += line.payment_req_id.partner_id.name.ljust(60) if line.payment_req_id.partner_id else \
                    '                                                            '
                    file_data += str(line.amount_to_pay).replace('.','').zfill(14)
                    today_date = datetime.date.today().strftime("%d-%m-%Y")
                    file_data += str(today_date).replace('-','/')
                    check_protection_term = 0
                    if batch.payment_issuing_bank_id.bank_id:
                        check_protection_term = batch.payment_issuing_bank_id.bank_id.check_protection_term
                    payment_deadline = datetime.date.today() + relativedelta(days=check_protection_term)
                    payment_deadline = payment_deadline.strftime("%d-%m-%Y")
                    file_data += str(payment_deadline).replace('-','/')
                    file_data += "\n"
            elif self.layout == 'Inbursa':
                file_name = 'inbursa.txt'
                total_rec = len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'))
                file_data += str(total_rec)
                file_data += '    '
                total_amt = sum(line.amount_to_pay for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'))
                file_data += str(round(total_amt, 2)).zfill(15)
                file_data += '\n'
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'):
                    today_date = datetime.date.today().strftime("%Y-%m-%d")
                    file_data += str(today_date).replace('-', '/')
                    file_data += '    '
                    file_data += batch.payment_issuing_bank_id.bank_account_id.acc_number if \
                        batch.payment_issuing_bank_id.bank_account_id else ''
                    file_data += '    '
                    file_data += str(line.check_folio_id.folio).zfill(13)
                    file_data += '    '
                    file_data += line.payment_req_id.partner_id.name.ljust(45) if line.payment_req_id.partner_id else ''
                    file_data += '    '
                    file_data += str(line.amount_to_pay).zfill(15)
                    file_data += '    '
                    file_data += batch.description_layout if batch.description_layout else ''
                    file_data += '\n'
            elif self.layout == 'Scotiabank':
                file_name = 'scotiabank.txt'
                file_data += 'H'
                today_date = datetime.date.today().strftime("%Y-%m-%d")
                file_data += str(today_date).replace('-', '/')
                file_data += ''.ljust(140)
                file_data += '1'
                file_data += '\n'
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                                     x.check_status == 'Delivered'):
                    file_data += 'A'
                    file_data += bank.branch_number if bank.branch_number else ''
                    file_data += 'M'
                    file_data += str(bank.bank_account_id.acc_number).zfill(10) if bank.bank_account_id and \
                        bank.bank_account_id.acc_number else ''
                    file_data += str(line.check_folio_id.folio).zfill(10)
                    file_data += str(line.amount_to_pay).zfill(15)
                    file_data += line.payment_req_id.partner_id.name.ljust(60) if line.payment_req_id.partner_id else ''
                    file_data += ''.ljust(140)
                    file_data += '3'
                    file_data += '\n'
                file_data += 'P'
                file_data += str(len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                                     x.check_status == 'Delivered'))).zfill(9)
                file_data += str(batch.checkbook_req_id.checkbook_no).zfill(15)
                total = sum(line.amount_to_pay for line in batch.payment_req_ids.filtered(lambda x: x.selected == True \
                                                            and x.check_status == 'Delivered'))
                file_data += str(round(total, 2)).replace('.','').zfill(18)
                file_data += '         '
                file_data += '               '
                file_data += '                  '
                file_data += str(len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                                              x.check_status == 'Delivered'))).zfill(9)
                file_data += str(batch.checkbook_req_id.checkbook_no).zfill(15)
                total = sum(line.amount_to_pay for line in batch.payment_req_ids.filtered(lambda x: x.selected == True \
                                                                        and x.check_status == 'Delivered'))
                file_data += str(round(total, 2)).replace('.','').zfill(18)
                file_data += '                     '
                file_data += '5'
                file_data += '\n'

            gentextfile = base64.b64encode(bytes(file_data, 'utf-8'))
            self.file_data = gentextfile
            self.file_name = file_name
            selected_req = batch.payment_req_ids.filtered(lambda x: x.selected == True)
            for re in selected_req:
                re.selected = False
            return {
                'name': _('Generate Layout'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'generate.supp.check.layout',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': self.id
            }