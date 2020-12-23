from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class SendChecks(models.Model):

    _name = 'send.checks'
    _rec_name = 'batch_folio'
    _description = 'Sending Checks To File'

    batch_folio = fields.Integer(string='Batch Folio')
    total_checks = fields.Integer(string="Total Number of Checks")
    responsible = fields.Char(string="Responsible for shipping")
    area_position = fields.Char(string="Area And Position")
    date = fields.Date(string="Date")
    approval_date = fields.Date(string="Approval Date")
    check_line_ids = fields.Many2many('send.checks.line',string="Check Line")
    status = fields.Selection([
    	('draft','Draft'),
    	('approved','Approved'),
    	('reject','Reject'),
        ('destroy','Destroyed')
    	],default='draft',string="Status")

    def action_reject(self):
    	self.status = 'reject'

    def action_approve(self):
        self.status = 'approved'
        approval = datetime.now()
        self.approval_date = approval

    def action_destroy(self):
        self.status = 'destroy'

class SendChecksLines(models.Model):
	_name = 'send.checks.line'

	check_folio = fields.Integer(string="Check Folio")
	dependency_id = fields.Many2one('dependency',string="Dependency")
