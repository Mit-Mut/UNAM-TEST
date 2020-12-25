from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import base64

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
                file_data += bank.branch_number
                file_data += bank.bank_account_id.acc_number.zfill(18) if bank.bank_account_id else '000000000000000000'
                file_data += '000008505585'
                file_data += '0001'
                file_data += str(self.env['ir.sequence'].next_by_code('sup.batch.banamex.layout'))
                file_data += '00000000000'
                file_data += '\n'
                total_amt = 0
                for line in batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status == 'Delivered'):
                    file_data += '02'
                    file_data += bank.branch_number
                    file_data += bank.bank_account_id.acc_number.zfill(18) if bank.bank_account_id \
                        else '000000000000000000'
                    reqs = batch.payment_req_ids.filtered(lambda x: x.check_folio_id != False)
                    if reqs:
                        file_data += str(reqs[0].check_folio_id.folio).zfill(7)
                    else:
                        file_data += '0000000'
                    file_data += '01'
                    file_data += str(line.amount_to_pay).replace('.','').zfill(14)
                    file_data += '0000000000'
                    file_data += '\n'
                    total_amt += line.amount_to_pay
                file_data += '03'
                file_data += str(len(batch.payment_req_ids.filtered(lambda x: x.selected == True and \
                                                         x.check_status != 'Delivered'))).zfill(6)
                file_data += str(total_amt).replace('.','').zfill(14)

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