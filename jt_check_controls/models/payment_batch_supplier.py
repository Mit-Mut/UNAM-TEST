from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PaymentBatchSupplier(models.Model):

    _name = 'payment.batch.supplier'
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

    def _get_check_data(self):
        for rec in self:
            rec.amount_of_checkes = rec.payment_req_ids.filtered(lambda x: x.check_status == 'Printed')
            reqs = rec.payment_req_ids.filtered(lambda x: x.check_folio_id != False)
            if reqs:
                rec.intial_check_folio = reqs[0].check_folio_id.id
                rec.final_check_folio = reqs[-1].check_folio_id.id

    def action_assign_check_folio(self):
        check_log_obj = self.env['check.log']
        for rec in self:
            if rec.checkbook_req_id:
                count = rec.payment_req_ids.filtered(lambda x:x.selected==True)
                logs = check_log_obj.search([('checklist_id.checkbook_req_id', '=', rec.checkbook_req_id.id),
                                             ('status', '=', 'Available for printing')], limit=len(count)).ids
                counter = 0
                if logs:
                    for line in self.payment_req_ids.filtered(lambda x:x.selected==True):
                        line.check_folio_id = logs[counter]
                        counter += 1
                        line.selected = False
                if not logs:
                    raise ValidationError(_('No check available for printing!'))

class CheckPaymentRequests(models.Model):

    _name = 'check.payment.req'
    _dscription = "Check Payment Request"

    payment_batch_id = fields.Many2one('payment.batch.supplier')
    check_folio_id = fields.Many2one('check.log',"Check Folio")
    payment_id = fields.Many2one('account.payment')
    payment_req_id = fields.Many2one('account.move')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")
    amount_to_pay = fields.Monetary("Amount to Pay", currency_field='currency_id')
    selected = fields.Boolean("Select")
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

