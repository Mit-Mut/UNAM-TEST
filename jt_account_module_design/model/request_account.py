from odoo import models, fields, api,_


class RequestAccounts(models.Model):

    _inherit = 'request.accounts'
    _description = "Request to open account"
    
    bank_id = fields.Many2one('res.bank','Bank')
