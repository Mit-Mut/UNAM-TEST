from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo import models, fields, api, tools, _
try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def amount_to_text(self, amount):
        self.ensure_one()

        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang_code = self.env.context.get('lang') or self.env.user.lang
        lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
        amount_words = tools.ustr('{amt_value} {amt_word}').format(
            amt_value=_num2words(integer_value, lang=lang.iso_code),
            amt_word=self.currency_unit_label,
        )

        if fractional_value == 0:
            amount_words += ' 00/100 M.N.'

        if not self.is_zero(amount - integer_value):
            context = self._context
            if 'from_supplier_payment_batch_report' in context and \
                    'lang' in context and (context.get('lang') == 'es_MX' or context.get('lang') == 'es_MX'):
                amount_in_word = amount_words + ' ' + str(fractional_value) + '/100' + ' M.N.'
                amount_words = amount_in_word
            else:
                amount_words += ' ' + _('and') + tools.ustr(' {amt_value} {amt_word}').format(
                    amt_value=_num2words(fractional_value, lang=lang.iso_code),
                    amt_word=self.currency_subunit_label,
                )

        return amount_words


class PaymentBatchSupplier(models.Model):
    _name = 'payment.batch.supplier'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Payment Batch Supplier"
    _rec_name = 'batch_folio'

    batch_folio = fields.Integer("Batch Folio")
    payment_issuing_bank_id = fields.Many2one("account.journal", "Payment Issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one("res.partner.bank", "Payment Issuing Bank Account")
    checkbook_req_id = fields.Many2one("checkbook.request", "Checkbook Number")
    type_of_payment_method = fields.Selection([('handbook', 'Handbook'),
                                               ('checks', 'Checks')], "Type of Payment Method")
    payment_date = fields.Date(string="Payment Date",default=datetime.today())
    amount_of_checkes = fields.Integer("Amount of Checkes", compute='_get_check_data')
    intial_check_folio = fields.Many2one("check.log", compute='_get_check_data')
    final_check_folio = fields.Many2one("check.log", compute='_get_check_data')
    payment_req_ids = fields.One2many('check.payment.req', "payment_batch_id", "Check Payment Requests")
    printed_checks = fields.Boolean("Printed checks")
    description_layout = fields.Text("Description Layout")
    selected = fields.Boolean("Select All")
    type_of_batch = fields.Selection([('supplier','Supplier'),('project','Project'),('nominal','Nominal'),
                                      ('pension','Pension')],string="Type Of Batch")
       
    @api.onchange('select_all')
    def select_lines(self):
        for line in self.payment_req_ids:
            line.selected = True
        self.selected = True

    @api.onchange('deselect_all')
    def deselect_lines(self):
        for line in self.payment_req_ids:
            line.selected = False
        self.selected = False



    def get_date(self):
        date = self.payment_date and self.payment_date or False
        if date:
            day = date.day
            month = date.month
            month_name = ''
            if month == 1:
                month_name = 'Enero'
            elif month == 2:
                month_name = 'Febrero'
            elif month == 3:
                month_name = 'Marzo'
            elif month == 4:
                month_name = 'Abril'
            elif month == 5:
                month_name = 'Mayo'
            elif month == 6:
                month_name = 'Junio'
            elif month == 7:
                month_name = 'Julio'
            elif month == 8:
                month_name = 'Agosto'
            elif month == 9:
                month_name = 'Septiembre'
            elif month == 10:
                month_name = 'Octubre'
            elif month == 11:
                month_name = 'Noviembre'
            elif month == 12:
                month_name = 'Diciembre'
            year = date.year
            return str(day) + ' de ' + month_name + ' de ' + str(year)

    def _get_check_data(self):
        for rec in self:
            req_list = []
            for req in rec.payment_req_ids:
                if req.check_folio_id:
                    req_list.append(req)
            rec.amount_of_checkes = len(req_list)
            reqs = sorted(req_list)
            if reqs:
                rec.intial_check_folio = reqs[0].check_folio_id.id
                rec.final_check_folio = reqs[-1].check_folio_id.id
            else:
                rec.intial_check_folio = False
                rec.final_check_folio = False
                
    def action_protected_checks(self):
        today = datetime.today().date()
        attch = self.env['ir.attachment']
        for rec in self:
            attachment = attch.search([('res_model', '=', 'payment.batch.supplier'), ('res_id', '=', rec.id)])
            if not attachment:
                raise ValidationError(_("The bank's response file for changing status must be attached to the checks"))
            if rec.payment_issuing_bank_id and rec.payment_issuing_bank_id.bank_id and rec.payment_issuing_bank_id.bank_id.check_protection_term==0:
                raise ValidationError(_("The selected bank has not established the validity of check protection, please configure it."))
            
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if line.check_folio_id.status == 'Sent to protection':
                    if rec.type_of_batch in ('supplier', 'project'):
                        line.check_folio_id.status = 'Protected and in transit'
                    else:
                        line.check_folio_id.status = 'Protected'
                    line.check_folio_id.date_protection = today
                    check_protection_term = 0
                    if line.payment_batch_id.payment_issuing_bank_id.bank_id:
                        check_protection_term = line.payment_batch_id.payment_issuing_bank_id.bank_id.check_protection_term
                    line.check_folio_id.date_expiration = today + relativedelta(days=check_protection_term)
                line.selected = False

    def action_send_file_to_protection(self):
        for rec in self:
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if rec.type_of_batch in ('supplier', 'project'):
                    if line.check_folio_id.status == 'Delivered':
                        line.check_folio_id.status = 'Sent to protection'
                else:
                    if line.check_folio_id.status == 'Printed':
                        line.check_folio_id.status = 'Sent to protection'
                line.selected = False
            rec.selected = False

    def action_deliver_checks(self):
        for rec in self:
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if rec.type_of_batch in ('supplier', 'project'):
                    if line.check_folio_id.status == 'Printed':
                        line.check_folio_id.status = 'Delivered'
                else:
                    if line.check_folio_id.status == 'Protected':
                        line.check_folio_id.status = 'In transit'
                line.selected = False
            rec.selected = False

    def action_layout_check_protection(self):
        rec_id = False
        bank_layout = False
        if self:
            rec_id = self[0].id
            if self[0].payment_issuing_bank_id and self[0].payment_issuing_bank_id.bank_id and self[0].payment_issuing_bank_id.bank_id.name:
                if self[0].payment_issuing_bank_id.bank_id.name.upper()== 'Banamex'.upper():
                    bank_layout = 'Banamex'
                elif self[0].payment_issuing_bank_id.bank_id.name.upper()== 'BBVA Bancomer'.upper():
                    bank_layout = 'BBVA Bancomer'
                elif self[0].payment_issuing_bank_id.bank_id.name.upper()== 'Inbursa'.upper():
                    bank_layout = 'Inbursa'
                elif self[0].payment_issuing_bank_id.bank_id.name.upper()== 'Santander'.upper():
                    bank_layout = 'Santander'
                elif self[0].payment_issuing_bank_id.bank_id.name.upper()== 'Scotiabank'.upper():
                    bank_layout = 'Scotiabank'
        return {
            'name': _('Generate Check Layout'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'generate.supp.check.layout',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_batch_id': rec_id,'default_layout':bank_layout}
        }
    def set_related_check_log(self,line):
        if line.check_folio_id:
            previous_data = ''
            if line.payment_req_id:
                for check in line.payment_req_id.related_check_folio_ids:
                    if check.id != line.check_folio_id.id:
                        if previous_data:
                            previous_data += ","+str(check.folio)
                        else:
                            previous_data = str(check.folio)
                    currect_check_data = str(line.check_folio_id.folio)
                    for c in line.payment_req_id.related_check_folio_ids:
                        if c.id != check.id:
                            currect_check_data += ","+str(c.folio)
                    check.related_checks = currect_check_data 
            line.check_folio_id.related_checks = previous_data 
        
    def action_assign_check_folio(self):
        check_log_obj = self.env['check.log']
        check_payment_req_obj = self.env['check.payment.req']
        for rec in self:
            if rec.checkbook_req_id:
                payment_record_assign = rec.payment_req_ids.filtered(lambda x: x.check_status and x.check_status != 'Cancelled' and x.selected == True)
                payment_record_cancel = rec.payment_req_ids.filtered(lambda x: x.check_status and x.check_folio_id and x.check_folio_id.reason_cancellation != 'Error de Impresión' and x.check_status == 'Cancelled' and x.selected == True)
                if payment_record_assign or payment_record_cancel:
                    raise ValidationError(_('Cannot assign a new check folio because they already have one'))
                payment_record = rec.payment_req_ids.filtered(lambda x: x.check_status == 'Printed' and x.selected == True)
                if payment_record :
                    raise ValidationError(_(' A new check folio cannot be assigned to a check that has been confirmed as Printed.'))
                count = rec.payment_req_ids.filtered(lambda x: x.selected == True)
                logs = check_log_obj.search([('checklist_id.checkbook_req_id', '=', rec.checkbook_req_id.id),
                        ('status', '=', 'Available for printing')],order='folio').ids
                exit_logs = check_payment_req_obj.search([('check_folio_id', 'in', logs)]).mapped('check_folio_id').ids
                logs = list(set(logs)^set(exit_logs))
                if len(logs) < len(count):
                    raise ValidationError(_('Not enough check available to assign printing!'))
                counter = 0
                if logs:
                    logs = check_log_obj.search([('id','in',logs)],order='folio')
                    for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                        line.check_folio_id = logs[counter]
                        line.check_folio_id.check_amount = line.amount_to_pay
                        if line.payment_req_id and line.payment_req_id.check_folio_id:
                            previous_data = line.payment_req_id.related_check_history
                            if previous_data:
                                previous_data += ","+str(line.payment_req_id.check_folio_id.folio)
                            else:
                                previous_data = str(line.payment_req_id.check_folio_id.folio)
                                
                            line.payment_req_id.related_check_history = previous_data      
                            line.payment_req_id.related_check_folio_ids =  [(4, line.payment_req_id.check_folio_id.id)]
                            line.payment_req_id.check_folio_id.related_check_folio_id = line.check_folio_id.id
                            line.check_folio_id.related_check_folio_id = line.payment_req_id.check_folio_id.id
                        
                               
                        line.payment_req_id.check_folio_id = line.check_folio_id.id
                        self.set_related_check_log(line)
                        
                        counter += 1
                        line.selected = False
                        if line.payment_req_id.check_folio_id:
                            line.payment_req_id.payment_state = 'assigned_payment_method'
                    rec.printed_checks = True
                if not logs:
                    raise ValidationError(_('No check available to assign!'))
            rec.selected = False

    def confirm_printed_checks(self):
        self.ensure_one()
        line_vals = []
        selected = self.payment_req_ids.filtered(lambda x: x.selected == True)
        if not selected:
            raise ValidationError(_("Select Check Payment Requests to confirm!"))
        for line in self.payment_req_ids:
            if line.selected and line.check_status == 'Available for printing' and line.check_folio_id:
                line_vals.append({
                    'check_folio_id': line.check_folio_id.id if line.check_folio_id else False,
                    'payment_id': line.payment_id.id if line.payment_id else False,
                    'payment_req_id': line.payment_req_id.id if line.payment_req_id else False,
                    'currency_id': line.currency_id.id if line.currency_id else False,
                    'amount_to_pay': line.amount_to_pay,
                    'check_status': line.check_status
                })
        return {
            'name': _('Check Print'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'confirm.printed.check',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_payment_req_ids': [(0, 0, val) for val in line_vals],
                        'default_supplier_batch_id': self.id}
        }


class CheckPaymentRequests(models.Model):
    _name = 'check.payment.req'
    _description = "Check Payment Request"

    payment_batch_id = fields.Many2one('payment.batch.supplier')
    check_folio_id = fields.Many2one('check.log', "Check Folio")
    payment_id = fields.Many2one('account.payment')
    payment_req_id = fields.Many2one('account.move')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")
    amount_to_pay = fields.Monetary("Amount to Pay", currency_field='currency_id')
    selected = fields.Boolean("Select")
    zone = fields.Integer('Zone',compute="get_zone_data")
    is_withdrawn_circulation = fields.Boolean(default=False, copy=False)

    check_status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                                     ('Assigned for shipping', 'Assigned for shipping'),
                                     ('Available for printing', 'Available for printing'),
                                     ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                                     ('In transit', 'In transit'), ('Sent to protection', 'Sent to protection'),
                                     ('Protected and in transit', 'Protected and in transit'),
                                     ('Protected', 'Protected'), ('Detained', 'Detained'),
                                     ('Withdrawn from circulation', 'Withdrawn from circulation'),
                                     ('Cancelled', 'Cancelled'),
                                     ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                                     ('On file', 'On file'), ('Destroyed', 'Destroyed'),
                                     ('Reissued', 'Reissued'), ('Charged', 'Charged')], related='check_folio_id.status',
                                    store=True)


    @api.depends('zone')
    def get_zone_data(self):

        U = "369369369703603603658148148143692692692036936936981471471476925925925369269269214704704709258258258"
        count = 0
        importe = ''
        NumChq = ''
        vl_impaux = ""
        va = ""
        total = ""
        DIG1 = ""
        dig2 = ""
        numchqs = ""
        zone = {}
        for record in self:
            
            importe = str(record.check_folio_id.folio)
            NumChq = str(record.amount_to_pay)
            IJ = str.find(importe, ".")
                # Elimina el . del importe
            if IJ == 0:
                pass
            else:
                vl_txtaux = importe[0:IJ]
                vl_txtaux = vl_txtaux + importe[IJ + 1:11]
                vl_impaux = vl_txtaux

            # Otra vez elimina cualquier punto del importe
            vl_txtaux = ""
            for IJ in range(0, len(vl_impaux)):
                if vl_impaux[IJ] != ".":
                    vl_txtaux = vl_txtaux + vl_impaux[IJ]
          
            # Rellena con ceros a la izquierda hasta que sean 12 dígitos
            for IJ in range(0, 12 - len(vl_txtaux)):
                vl_txtaux = "0" + vl_txtaux

            #justifica con zeros a la izquierda el numchq hasta 8 dígitos
            numchqs = ""
            for IJ in range(1, 8 - len(NumChq) + 1):
                numchqs = "0" + numchqs
          
            # une el número de cheque y el importe
            numchqs = numchqs + NumChq

            # Agrega otro cero a la izquierda. Deben ser 21 caracteres
            va = "0" + numchqs + vl_txtaux 

            # Calcula el primer dígito
            total = 0

            # Revisa con isdigit porque hay comas en la cadena del importe
            # Si hay coma no se suma nada
            if str.isdigit(va[2]):
                total = total + int(va[2])
            if str.isdigit(va[5]):
                total = total + int(va[5])
            if str.isdigit(va[8]):
                total = total + int(va[8])
            if str.isdigit(va[11]):
                total = total + int(va[11])
            if str.isdigit(va[14]):
                total = total + int(va[14])
            if str.isdigit(va[17]):
                total = total + int(va[17])
            if str.isdigit(va[20]):
                total = total + int(va[20])

            #total = int(va[2]) + int(va[5]) + int(va[8]) + int(va[11]) + \
            #        int(va[14]) + int(va[17]) + int(va[20])   
            
            #inicia la suma de pares 1ra parte
            if str.isdigit(va[0:2]) and int(va[0:2]) > 0:
                total = total + int(U[int(va[0:2])-1])

            if str.isdigit(va[3:5]) and int(va[3:5]) > 0:
                total = total + int(U[int(va[3:5])-1])

            if str.isdigit(va[6:8]) and int(va[6:8]) > 0:
                total = total + int(U[int(va[6:8])-1])

            if str.isdigit(va[9:11]) and int(va[9:11]) > 0:
                total = total + int(U[int(va[9:11])-1])

            if str.isdigit(va[12:14]) and int(va[12:14]) > 0:
                total = total + int(U[int(va[12:14])-1])

            if str.isdigit(va[15:17]) and int(va[15:17]) > 0:
                total = total + int(U[int(va[15:17])-1])

            if str.isdigit(va[18:20]) and int(va[18:20]) > 0:
                total = total + int(U[int(va[18:20])-1])

            DIG1 = 10 - int(str(total)[-1])

            if DIG1 == 10:
                DIG1 = 0

            # Calcula el segundo dígito
            va = ""
            total = 0
            va = numchqs + vl_txtaux + str(DIG1)

            if str.isdigit(va[2]):
                total = total + int(va[2])
            if str.isdigit(va[5]):
                total = total + int(va[5])
            if str.isdigit(va[8]):
                total = total + int(va[8])
            if str.isdigit(va[11]):
                total = total + int(va[11])
            if str.isdigit(va[14]):
                total = total + int(va[14])
            if str.isdigit(va[17]):
                total = total + int(va[17])
            if str.isdigit(va[20]):
                total = total + int(va[20])

            #total = int(va[2]) + int(va[5]) + int(va[8]) + int(va[11]) + \
            #        int(va[14]) + int(va[17]) + int(va[20])

            if str.isdigit(va[0:2]) and int(va[0:2]) > 0:
                total = total + int(U[int(va[0:2])-1])

            if str.isdigit(va[3:5]) and int(va[3:5]) > 0:
                total = total + int(U[int(va[3:5])-1])

            if str.isdigit(va[6:8]) and int(va[6:8]) > 0:
                total = total + int(U[int(va[6:8])-1])

            if str.isdigit(va[9:11]) and int(va[9:11]) > 0:
                total = total + int(U[int(va[9:11])-1])

            if str.isdigit(va[12:14]) and int(va[12:14]) > 0:
                total = total + int(U[int(va[12:14])-1])

            if str.isdigit(va[15:17]) and int(va[15:17]) > 0:
                total = total + int(U[int(va[15:17])-1])

            if str.isdigit(va[18:20]) and int(va[18:20]) > 0:
                total = total + int(U[int(va[18:20])-1])

            dig2 = 10 - int(str(total)[-1])
            
            if dig2 == 10:
                dig2 = 0


            # Une los dos dígitos
            digitos = str(DIG1) + str(dig2)
            record.zone = digitos
        return zone


    @api.constrains('check_folio_id')
    def _check_number(self):
        for rec in self:
            if rec.check_folio_id:
                exit_lines = self.env['check.payment.req'].search([('check_folio_id','=',rec.check_folio_id.id),('id','!=',rec.id)])
    #             if self.env.user.lang == 'es_MX':
    #                 raise ValidationError(_('El número de Actividad Institucional debe ser un valor numérico'))
    #             else:
                if exit_lines:
                    raise ValidationError(_('This check folio already assing to other payment request'))

    def select_lines(self):
        for line in self:
            if line.selected:
                line.selected = False
            else:
                line.selected = True

class BankBalanceCheck(models.TransientModel):
    _inherit = 'bank.balance.check'

    def schedule_payment(self):
        res = super(BankBalanceCheck, self).schedule_payment()
        check_payment_method = self.env.ref('l10n_mx_edi.payment_method_cheque').id
        batch_data = {}
        for invoice in self.invoice_ids:
            if invoice.is_payment_request == True and invoice.l10n_mx_edi_payment_method_id \
                    and invoice.l10n_mx_edi_payment_method_id.id == check_payment_method:
                if invoice.batch_folio in batch_data.keys():
                    batch_data.update({
                        invoice.batch_folio: batch_data.get(invoice.batch_folio) + [invoice]
                    })
                else:
                    batch_data.update({invoice.batch_folio: [invoice]})
            if invoice.is_project_payment == True and invoice.l10n_mx_edi_payment_method_id \
                    and invoice.l10n_mx_edi_payment_method_id.id == check_payment_method:
                if invoice.batch_folio in batch_data.keys():
                    batch_data.update({
                        invoice.batch_folio: batch_data.get(invoice.batch_folio) + [invoice]
                    })
                else:
                    batch_data.update({invoice.batch_folio: [invoice]})

            if invoice.is_payroll_payment_request == True and invoice.l10n_mx_edi_payment_method_id \
                    and invoice.l10n_mx_edi_payment_method_id.id == check_payment_method:
                if invoice.batch_folio in batch_data.keys():
                    batch_data.update({
                        invoice.batch_folio: batch_data.get(invoice.batch_folio) + [invoice]
                    })
                else:
                    batch_data.update({invoice.batch_folio: [invoice]})

            if invoice.is_different_payroll_request == True and invoice.l10n_mx_edi_payment_method_id \
                    and invoice.l10n_mx_edi_payment_method_id.id == check_payment_method:
                if invoice.batch_folio in batch_data.keys():
                    batch_data.update({
                        invoice.batch_folio: batch_data.get(invoice.batch_folio) + [invoice]
                    })
                else:
                    batch_data.update({invoice.batch_folio: [invoice]})

            if invoice.is_pension_payment_request == True and invoice.l10n_mx_edi_payment_method_id \
                    and invoice.l10n_mx_edi_payment_method_id.id == check_payment_method:
                if invoice.batch_folio in batch_data.keys():
                    batch_data.update({
                        invoice.batch_folio: batch_data.get(invoice.batch_folio) + [invoice]
                    })
                else:
                    batch_data.update({invoice.batch_folio: [invoice]})


        for folio, moves in batch_data.items():
            batch_folio = folio
            moves_list = []
            bank_id = self.journal_id.id if self.journal_id else False
            bank_acc_id = self.bank_account_id.id if self.bank_account_id else False
            type_of_batch = False
            for move in moves:
                if move.is_payroll_payment_request:
                    type_of_batch = 'nominal'
                        
                    if move.check_folio_id and move.check_folio_id.status not in ('Detained','Cancelled','Reissued','Withdrawn from circulation'):
                        move.check_folio_id.status = 'Printed'
                        move.payment_state = 'assigned_payment_method'
                elif move.is_payment_request:
                    type_of_batch = 'supplier'
                elif move.is_different_payroll_request:
                    type_of_batch = 'nominal'
                elif move.is_project_payment:
                    type_of_batch = 'project'
                elif move.is_pension_payment_request:
                    type_of_batch = 'pension'
                        
                    if move.check_folio_id and move.check_folio_id.status not in ('Detained','Cancelled','Reissued','Withdrawn from circulation'):
                        move.check_folio_id.status = 'Printed'
                        move.payment_state = 'assigned_payment_method'
                        
                moves_list.append(move)
                
            move_val_list = []
            checkbook_req_id = False
            for move in moves_list:
                check_folio_id = False
                if move.check_folio_id:
                    if move.check_folio_id.status not in ('Detained','Cancelled','Reissued','Withdrawn from circulation'):
                        check_folio_id = move.check_folio_id.id
                        move.check_folio_id.check_amount = move.amount_total
                        checkbook_req_id = move.check_folio_id.checklist_id and move.check_folio_id.checklist_id and move.check_folio_id.checklist_id.checkbook_req_id.id or False
                         
                payment = self.env['account.payment'].search([('payment_request_id', '=', move.id)], limit=1)
                move_val_list.append({'payment_req_id': move.id, 'amount_to_pay': move.amount_total,
                                      'payment_id': payment.id,'check_folio_id':check_folio_id})
            self.env['payment.batch.supplier'].create({
                'batch_folio': batch_folio,
                'payment_issuing_bank_id': bank_id,
                'payment_issuing_bank_acc_id': bank_acc_id,
                'type_of_payment_method': 'checks',
                'type_of_batch':type_of_batch,
                'checkbook_req_id' : checkbook_req_id,
                'payment_req_ids': [(0, 0, val) for val in move_val_list]
            })
        return res
