from odoo import models, fields

class AccountCancel(models.Model):
	_name = 'account.cancel'

	invoice = fields.Text(string="Invoice")
	state = fields.Selection([
		('eraser','Eraser'),
		('request','Request'),
		('approved','Approved'),
		('confirmed','Confirmed'),
		('rejected','Rejected'),
		])
	movement_type = fields.Selection([
        ('account cancel', 'Account Cancelation'),
    ], 'Movement Type', default='account cancel')
	project_num = fields.Many2one('project.project',string="Project Num")
	project_type = fields.Selection([
		('conacyt','Conacyt'),
		('concurrent','Concurrent'),
		('other project with checkbook','Other Projects with checkbook'),],"Project Type")
	amount_of_ministration = fields.Float(string="Amount of Ministration")
	authorized_amount = fields.Float(string="Authorized Amount")
	observations = fields.Text(string="Observations")
	bank_account = fields.Many2one('account.journal',string="Bank Account")
	contract_no = fields.Char(related="bank_account.contract_number",string="Contract No.")
	supporting_docs = fields.Binary(string="Supporting Docs",copy=False)
