from odoo import models, fields, api,_
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

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
            if record.journal_id:
                journal = record.journal_id
                if not journal.default_debit_account_id or not journal.default_credit_account_id \
                        or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
                    if self.env.user.lang == 'es_MX':
                        raise ValidationError(_("Por favor configure la cuenta UNAM y CONAC en diario!"))
                    else:
                        raise ValidationError(_("Please configure UNAM and CONAC account in journal!"))

                today = datetime.today().date()
                user = self.env.user
                partner_id = user.partner_id.id
                amount = self.amount

                unam_move_val = {'ref': self.folio,  'conac_move': True,
                                 'date': today, 'journal_id': journal.id, 'company_id': self.env.user.company_id.id,
                                 'line_ids': [(0, 0, {
                                     'account_id': journal.default_credit_account_id.id,
                                     'coa_conac_id': journal.conac_credit_account_id.id,
                                     'credit': amount,
                                     'partner_id': partner_id,
                                     'commision_profit_id': self.id,
                                     }),
                                     (0, 0, {
                                     'account_id': journal.default_debit_account_id.id,
                                     'coa_conac_id': journal.conac_debit_account_id.id,
                                     'debit': amount,
                                     'partner_id': partner_id,
                                     'commision_profit_id': self.id,
                                     }),
                                 ]}
                move_obj = self.env['account.move']
                unam_move = move_obj.create(unam_move_val)
                unam_move.action_post()



    

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    commision_profit_id = fields.Many2one('comission.profit','Comission Profit')