from odoo import models, fields, api, _

class PaymentRequest(models.Model):

    _name = 'payment.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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

    @api.depends('beneficiary_id','balance_req_id','balance_req_id.bases_collaboration_id','balance_req_id.bases_collaboration_id.beneficiary_ids')
    def get_bank_ids(self):
        for rec in self:
            partner_ids = []
            if rec.balance_req_id and rec.balance_req_id.bases_collaboration_id and rec.balance_req_id.bases_collaboration_id.beneficiary_ids:
                if self.beneficiary_id:
                    user = self.env['res.users'].sudo().search([('partner_id','=',self.beneficiary_id.id)],limit=1)
                    if user: 
                        emp_id = self.env['hr.employee'].sudo().search([('user_id','=',user.id)],limit=1)
                        if emp_id:
                            beneficiary = self.env['collaboration.beneficiary'].search([
                            ('collaboration_id', '=', rec.balance_req_id.bases_collaboration_id.id), ('employee_id', '=', emp_id.id)])
                            bank_ids = beneficiary.mapped('bank_id')
                            if bank_ids:
                                partner_ids =  bank_ids.ids
                                
            rec.bank_ids = [(6,0,partner_ids)]

    bank_ids = fields.Many2many('res.partner.bank','payment_req_bank_id','bank_id','payment_id',compute="get_bank_ids")
    
    @api.onchange('bank_id')
    def onchage_bank(self):
        if self.bank_id:
            self.account_number = self.bank_id.acc_number

    def request(self):
        self.state = 'requested'
        
    @api.model
    def create(self,vals):
        res = super(PaymentRequest,self).create(vals)
        if res.amount and res.date and res.payment_method_id and res.beneficiary_id:
            folio_rec = ''
            payment_ids = self.env['account.move'].search([('is_payment_request', '=', True),('partner_id','=',res.beneficiary_id.id),('l10n_mx_edi_payment_method_id','=',res.payment_method_id.id),('amount_total','=',res.amount)])
            for payment in payment_ids:
                if payment.date_receipt and payment.date_receipt.date()== res.date:
                    folio_rec = payment.folio 
            res.counter_receipt_sheet = folio_rec
        return res
    
    def write(self,vals):
        result = super(PaymentRequest,self).write(vals)
        if 'counter_receipt_sheet' not in vals:
            for res in self:
                if res.amount and res.date and res.payment_method_id and res.beneficiary_id:
                    folio_rec = ''
                    payment_ids = self.env['account.move'].search([('is_payment_request', '=', True),('partner_id','=',res.beneficiary_id.id),('l10n_mx_edi_payment_method_id','=',res.payment_method_id.id),('amount_total','=',res.amount)])
                    for payment in payment_ids:
                        if payment.date_receipt and payment.date_receipt.date()== res.date:
                            folio_rec = payment.folio 
                    res.counter_receipt_sheet = folio_rec
        return result
    
    def action_validates_payment_request(self):
        for res in self:
            if res.amount and res.date and res.payment_method_id and res.beneficiary_id:
                folio_rec = ''
                payment_ids = self.env['account.move'].search([('is_payment_request', '=', True),('partner_id','=',res.beneficiary_id.id),('l10n_mx_edi_payment_method_id','=',res.payment_method_id.id),('amount_total','=',res.amount)])
                for payment in payment_ids:
                    if payment.date_receipt and payment.date_receipt.date()== res.date:
                        folio_rec = payment.folio 
                res.counter_receipt_sheet = folio_rec

    def action_validates_payment_request_auto(self):
        records = self.env['payment.request'].search(['|',('counter_receipt_sheet','=',False),('counter_receipt_sheet','=','')])
        for res in records:
            if res.amount and res.date and res.payment_method_id and res.beneficiary_id:
                folio_rec = ''
                payment_ids = self.env['account.move'].search([('is_payment_request', '=', True),
                                                               ('partner_id','=',res.beneficiary_id.id),
                                        ('l10n_mx_edi_payment_method_id','=',res.payment_method_id.id),
                                                               ('amount_total','=',res.amount)])
                for payment in payment_ids:
                    if payment.date_receipt and payment.date_receipt.date()== res.date:
                        folio_rec = payment.folio 
                res.counter_receipt_sheet = folio_rec            