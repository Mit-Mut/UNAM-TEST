from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    payment_date = fields.Date("Payment Date")
    amount_of_checkes = fields.Integer("Amount of Checkes", compute='_get_check_data')
    intial_check_folio = fields.Many2one("check.log", compute='_get_check_data')
    final_check_folio = fields.Many2one("check.log", compute='_get_check_data')
    payment_req_ids = fields.One2many('check.payment.req', "payment_batch_id", "Check Payment Requests")
    printed_checks = fields.Boolean("Printed checks")
    description_layout = fields.Text("Description Layout")

    def get_date(self):
        today = datetime.today().date()
        day = today.day
        month = today.month
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
        year = today.year
        return str(day) + ' de ' + month_name + ' de ' + str(year)

    def _get_check_data(self):
        for rec in self:
            rec.amount_of_checkes = len(rec.payment_req_ids.filtered(lambda x: x.check_status == 'Printed'))
            reqs = rec.payment_req_ids.filtered(lambda x: x.check_folio_id != False)
            if reqs:
                rec.intial_check_folio = reqs[0].check_folio_id.id
                rec.final_check_folio = reqs[-1].check_folio_id.id

    def action_protected_checks(self):
        today = datetime.today().date()
        attch = self.env['ir.attachment']
        for rec in self:
            attachment = attch.search([('res_model', '=', 'payment.batch.supplier'), ('res_id', '=', rec.id)])
            if not attachment:
                raise ValidationError(_("The bank's response file for changing status must be attached to the checks"))
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if line.check_folio_id.status == 'Sent to protection':
                    line.check_folio_id.status = 'Protected and in transit'
                    line.check_folio_id.date_protection = today
                    check_protection_term = 0
                    if line.payment_batch_id.payment_issuing_bank_id.bank_id:
                        check_protection_term = line.payment_batch_id.payment_issuing_bank_id.bank_id.check_protection_term
                    line.check_folio_id.date_expiration = today + relativedelta(days=check_protection_term)
                line.selected = False

    def action_send_file_to_protection(self):
        for rec in self:
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if line.check_folio_id.status == 'Delivered':
                    line.check_folio_id.status = 'Sent to protection'
                line.selected = False

    def action_deliver_checks(self):
        for rec in self:
            for line in rec.payment_req_ids.filtered(lambda x: x.selected == True):
                if line.check_folio_id.status == 'Printed':
                    line.check_folio_id.status = 'Delivered'
                line.selected = False

    def action_layout_check_protection(self):
        return {
            'name': _('Generate Check Layout'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'generate.supp.check.layout',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_batch_id': self.id}
        }

    def action_assign_check_folio(self):
        check_log_obj = self.env['check.log']
        for rec in self:
            if rec.checkbook_req_id:
                count = rec.payment_req_ids.filtered(lambda x:x.selected==True)
                logs = check_log_obj.search([('checklist_id.checkbook_req_id', '=', rec.checkbook_req_id.id),
                                             ('status', '=', 'Available for printing')], limit=len(count)).ids
                if len(logs) != len(count):
                    raise ValidationError(_('No available for printing!'))
                counter = 0
                if logs:
                    for line in rec.payment_req_ids.filtered(lambda x:x.selected==True):
                        line.check_folio_id = logs[counter]
                        counter += 1
                        line.selected = False
                    rec.printed_checks = True
                if not logs:
                    raise ValidationError(_('No check available for printing!'))

    def confirm_printed_checks(self):
        self.ensure_one()
        line_vals = []
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
    check_folio_id = fields.Many2one('check.log',"Check Folio")
    payment_id = fields.Many2one('account.payment')
    payment_req_id = fields.Many2one('account.move')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")
    amount_to_pay = fields.Monetary("Amount to Pay", currency_field='currency_id')
    selected = fields.Boolean("Select")
    is_withdrawn_circulation = fields.Boolean(default=False,copy=False)
    
    check_status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                          ('Assigned for shipping', 'Assigned for shipping'),
                          ('Available for printing', 'Available for printing'),
                          ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                          ('In transit', 'In transit'), ('Sent to protection','Sent to protection'),
                          ('Protected and in transit','Protected and in transit'),
                          ('Protected', 'Protected'), ('Detained','Detained'),
                          ('Withdrawn from circulation','Withdrawn from circulation'),
                          ('Cancelled', 'Cancelled'),
                          ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                          ('On file','On file'),('Destroyed','Destroyed'),
                          ('Reissued', 'Reissued'),('Charged','Charged')], related='check_folio_id.status', store=True)

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

        for folio, moves in batch_data.items():
            batch_folio = folio
            moves_list = []
            bank_id = self.journal_id.id if self.journal_id else False
            bank_acc_id = self.bank_account_id.id if self.bank_account_id else False
            for move in moves:
                moves_list.append(move)
            move_val_list = []
            for move in moves_list:
                payment = self.env['account.payment'].search([('payment_request_id', '=', move.id)], limit=1)
                move_val_list.append({'payment_req_id': move.id, 'amount_to_pay': move.amount_total,
                                      'payment_id': payment.id})
            self.env['payment.batch.supplier'].create({
                'batch_folio': batch_folio,
                'payment_issuing_bank_id': bank_id,
                'payment_issuing_bank_acc_id': bank_acc_id,
                'type_of_payment_method': 'checks',
                'payment_req_ids': [(0, 0, val) for val in move_val_list]
            })
        return res

