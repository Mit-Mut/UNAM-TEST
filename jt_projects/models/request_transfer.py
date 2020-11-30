from odoo import models, fields, api


class RequestTransfer(models.Model):

    _name = 'request.transfer'
    _description = 'Request for transfer'
    _rec_name = 'invoice'

    invoice = fields.Text('Invoice', readonly=True,
                          default='New')
    application_date = fields.Date('Application Date')
    # request_area = fields.Text('Area requesting the transfer')
    request_area = fields.Many2one('dependency')
    user_id = fields.Many2one(
        'res.users', string='Requesting User', default=lambda self: self.env.user.id)
    destination_journal_id = fields.Many2one(
        'account.journal', 'Destination Bank')
    destination_bank_id = fields.Many2one(
        related="destination_journal_id.bank_account_id", string='Destination Bank Account')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Coin")

    amount_req_tranfer = fields.Monetary(
        string='Amount of the transfer requested', currency_field='currency_id')
    handover_date = fields.Date('Required handover Date', Required=True)
    application_concept = fields.Text('Application Concept')
    origin_journal_id = fields.Many2one(
        'account.journal', 'Origin Bank')
    origin_bank_id = fields.Many2one(
        related="origin_journal_id.bank_account_id", string='Origin Bank Account')
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
            'operation_number':self.invoice,
            'bank_account_id': self.origin_journal_id.id,
            'desti_bank_account_id': self.destination_journal_id.id,
            'date': self.application_date,
            'user_id': self.user_id.id,
            'state': self.status,
            'unit_req_transfer_id': self.request_area.id,
            'project_request_id': self.id,
            'amount': self.amount_req_tranfer,
            'date_required': self.handover_date,
            'concept': self.application_concept,
            'agreement_number': self.aggrement,

        }
        self.env['request.open.balance.finance'].create(record)

    @api.model
    def create(self, vals):
        if vals.get('invoice', 'New') == 'New':
            vals['invoice'] = self.env['ir.sequence'].next_by_code(
                'request.transfer') or 'New'
        result = super(RequestTransfer, self).create(vals)
        return result

    def action_approved(self):
        self.status = 'approved'

    def confirmed_finance(self):
        self.status = 'confirmed'

    def reject_finance(self):
        self.status = 'rejected'

    def action_canceled(self):
        self.status = 'canceled'
