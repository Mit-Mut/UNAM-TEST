from odoo import models, fields, api, _

class PaymentRequest(models.Model):

    _name = 'payment.request'
    _inherit = 'mail.thread'
    _description = "Payment Request"

    name = fields.Char("Agreement Name")
    operation_number = fields.Char("Operation Number")
    balance_req_id = fields.Many2one("request.open.balance")
    type_of_operation = fields.Selection([('open_bal', 'Opening Balance'),
                                          ('increase', 'Increase'),
                                          ('retirement', 'Retirement'),
                                          ('withdrawal', 'Withdrawal for settlement')], string="Type of Operation")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary("Amount to withdraw")
    payment_method_id = fields.Many2one('l10n_mx_edi.payment.method', string="Payment Method")
    date = fields.Date("Operation Number")
    reference = fields.Char("Reference")
    counter_receipt_sheet = fields.Char("Counter Receipt Sheet")
    beneficiary_id = fields.Many2one('res.partner', "Beneficiary's name")
    bank_id = fields.Many2one("res.partner.bank", "Bank")
    account_number = fields.Char("Beneficiary account number")
    payment_request_number = fields.Char("Payment Request Number")
    state = fields.Selection([('draft', 'Draft'),
                              ('requested', 'Requested')], 'State', default='draft')

    def request(self):
        self.state = 'requested'