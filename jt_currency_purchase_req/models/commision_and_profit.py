from odoo import models, fields, api,_
from datetime import datetime, timedelta

class CommisionAndProfit(models.Model):

    _name = 'comission.profit'
    _description = "Commision And Profit"
    _rec_name = 'folio'

    folio = fields.Char(string='Folio',tracking=True)
    bank_account_id = fields.Many2one('res.partner.bank',string="Bank Account")
    type_of_record = fields.Selection([('commision','Comission'),('interest','Interest')],string='Type Of Record')
    type_of_comission  = fields.Selection([('check_paid_per_window','Check paid per Window'),('transfer','Transfers')],string='Type Of Commision')
    journal_id = fields.Many2one('account.journal',string="Daily")
    programmatic_code_id = fields.Many2one('program.code',string="Programmatic Code")
    amount = fields.Char('Amount')
    move_line_ids = fields.One2many(
        'account.move.line', 'commision_profit_id', string="Journal Items")
    description = fields.Char('Description')
    status = fields.Selection([('draft', 'Draft'),
                               ('approved', 'Approved'),
                               ], string="Status", default="draft")


    def approve(self):

        for record in self:

            record.status = 'approved'


    

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    commision_profit_id = fields.Many2one('comission.profit','Comission Profit')