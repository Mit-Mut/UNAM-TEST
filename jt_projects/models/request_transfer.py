from odoo import models, fields


class RequestTransfer(models.Model):

    _name = 'request.transfer'
    _description = 'Request for transfer'
    _rec_name = 'invoice'

    invoice = fields.Text('Invoice')
    application_date = fields.Date('Application Date')
    request_area = fields.Text('Area requesting the transfer')
    user_id = fields.Many2one(
        'res.users', string='Requesting User', default=lambda self: self.env.user.id)
    destination_journal_id = fields.Many2one(
        'account.journal', 'Destination Bank')
    destination_bank_id = fields.Many2one(related="destination_journal_id.bank_account_id", string='Destination Bank Account')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id,string="Coin")

    amount_req_tranfer = fields.Monetary(
        string='Amount of the transfer requested', currency_field='currency_id')
    handover_date = fields.Date('Required handover Date', Required=True)
    application_concept = fields.Text('Application Concept')
    origin_journal_id = fields.Many2one(
        'account.journal', 'Origin Bank')
    origin_bank_id = fields.Many2one(related="origin_journal_id.bank_account_id", string='Origin Bank Account')
    aggrement = fields.Text('Agreement or Project reference')
    status = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                               ('rejected', 'Rejected'),
                               ('approved', 'Approved'),
                               ('sent', 'Sent'),
                               ('confirmed', 'Confirmed'),
                               ('done', 'Done'),
                               ('canceled', 'Canceled')], string="Status", default="draft")

    def generate_request(self):
        self.status = 'requested'
        record = {

            'invoice': self.invoice,
            'bank_account_id': self.origin_journal_id.id,
            'desti_bank_account_id': self.destination_journal_id.id,
            'date': self.application_date,
            'user_id': self.user_id.id,
            'state': self.status

        }
        self.env['request.open.balance.finance'].create(record)