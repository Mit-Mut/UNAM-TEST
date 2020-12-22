from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class CancelChecks(models.Model):

    _name = 'cancel.checks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'check_folio'
    _description = "Cancel Checks"

    check_folio = fields.Integer(string="Check Folio")
    check_status = fields.Char(string="Check Status")
    dependency = fields.Many2one('dependency',string="dependency")
    bank_id = fields.Many2one('res.bank',string="Bank")
    bank_account_id = fields.Many2one('account.journal',string="Bank Account")
    checkbook = fields.Char(string="checkbook")
    observation = fields.Char(string="Observation")
    status = fields.Selection([
    	('draft','Draft'),
    	('approved','Approved'),
    	],default='draft',string="Status")

