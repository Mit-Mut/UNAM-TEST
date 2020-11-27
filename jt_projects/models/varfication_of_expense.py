from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import datetime


class VerficationOfExpense(models.Model):

    _name = 'expense.verification'
    _description = 'Verification Of Expense'

    status = fields.Selection([('eraser', 'Eraser'),
                               ('approve', 'Approved'),
                               ('reject', 'Rejected')], string="Status", default="eraser")
    project_id = fields.Many2one('project.project', string='Project Code')
    project_number_id = fields.Char(
        related='project_id.number', string="Project Number")
    stage_id = fields.Many2one('stage', string='Stage')
    exercise = fields.Text('Exercise')
    exchange_rate = fields.Float('Exchange Rate')
    expense_journal_id = fields.Many2one(
        'account.journal', string="Expense Journal")
    dependence = fields.Many2one('dependency', string="Dependency")
    subdependence = fields.Many2one('sub.dependency', string='Sub Dependence')
    upa_code = fields.Many2one('policy.keys', string='UPA Code')
    type_of_operation = fields.Many2one(
        'operation.type', string='Type Of Operation')
    doc_type = fields.Many2one(
        'upa.document.type', string='Document Type')
    number = fields.Text(
        rejected='project_id.stage_identifier', string='Number')
    type_of_currency = fields.Selection(
        [('national', 'National Currency'),
            ('foreign', 'Foreign currency')
         ], string="Type Of Currency", default='national')
    administrative_forum = fields.Text('Administrative Forms')
    Vouchers = fields.Binary('Vouchers')
    reg_date = fields.Date('Registration Date')
    application_approval_date = fields.Date('Application Approval Date')
    beneficiary_name = fields.Many2one(
        'res.partner', string='Beneficiary Name')
    rfc = fields.Char(related='beneficiary_name.vat', string='RFC')
    invoice_vault_folio = fields.Text('Invoice vault folio')
    uuid_invoice = fields.Text('UUID Invoice')
    invoice_series = fields.Text('Invoice Series')
    invoice_folio = fields.Text('Invoice Folio')
    type_of_aggrement = fields.Many2one(
        'agreement.agreement.type', string='Type Of Agreement')
    currency_id = fields.Many2one(
        'res.currency', help='The currency used to enter statement', string="Currency",default=lambda self: self.env.user.company_id.currency_id)
    agreement_number = fields.Many2one(
        'bases.collaboration', string='Agreement Number')
    agreement_name = fields.Char(
        related='agreement_number.name', string='Agreement Name')
    tech_support = fields.Many2one('hr.employee', string='Technical Support')
    admin_manager = fields.Many2one(
        'hr.employee', string='Administrative manager')
    ext_sponsor = fields.Text('External sponsor')
    observation = fields.Text('Observations')
    move_line_ids = fields.One2many(
        'account.move.line', 'expense_id', string="Journal Items")
    reason_for_rejection = fields.Char('Reason for rejection')
    verifcation_expense_ids = fields.One2many(
        'verification.expense.line', 'verification_expense_id', string='Verfication Expense Line')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
        compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
        compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
        compute='_compute_amount',)

    @api.depends('verifcation_expense_ids','verifcation_expense_ids.price','verifcation_expense_ids.tax_ids')
    def _compute_amount(self):
        for rec in self:
            rec.amount_untaxed = sum(x.price for x in rec.verifcation_expense_ids)
            rec.amount_tax = sum(x.amount_tax for x in rec.verifcation_expense_ids)
            rec.amount_total = rec.amount_untaxed + rec.amount_tax 
            

    def action_approve(self):

        self.status = 'approve'
        if self.expense_journal_id:
            journal = self.expense_journal_id
            if not journal.default_debit_account_id or not journal.default_credit_account_id \
                    or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
                if self.env.user.lang == 'es_MX':
                    raise ValidationError(
                        _("Por favor configure la cuenta UNAM y CONAC en diario!"))
                else:
                    raise ValidationError(
                        _("Please configure UNAM and CONAC account in journal!"))

            today = datetime.today().date()
            user = self.env.user
            partner_id = user.partner_id.id
            if self.beneficiary_name:
                partner_id = self.beneficiary_name.id
                
            amount = self.amount_total

            unam_move_val = {'ref': self.display_name,  'conac_move': True,
                             'date': today, 'journal_id': journal.id, 'company_id': self.env.user.company_id.id,
                             'line_ids': [(0, 0, {
                                 'account_id': journal.default_credit_account_id.id,
                                 'coa_conac_id': journal.conac_credit_account_id.id,
                                 'credit': amount,
                                 'partner_id': partner_id,
                                 'expense_id': self.id,
                             }),
                                 (0, 0, {
                                     'account_id': journal.default_debit_account_id.id,
                                     'coa_conac_id': journal.conac_debit_account_id.id,
                                     'debit': amount,
                                     'partner_id': partner_id,
                                     'expense_id': self.id,
                                 }),
                             ]}
            move_obj = self.env['account.move']
            unam_move = move_obj.create(unam_move_val)
            unam_move.action_post()


class VerificationOfExpenseLine(models.Model):

    _name = 'verification.expense.line'
    _description = 'Verification Expense Line'

    row = fields.Text('Row')
    verification_expense_id = fields.Many2one(
        'expense.verification', string='Verification Expense')
    program_code = fields.Many2one('program.code', string='Program Code')
    price = fields.Monetary('Price')
    subtotal = fields.Monetary(string='Subtotal',compute='get_price_subtotal',store=True)
    amount_tax = fields.Monetary(string='Tax Amount',compute='get_tax_amount',store=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Selection(
        [('mn_amount', 'MN amount'),
            ('amount_me', 'Amount ME')
         ], string="Amount")
    tax_ids = fields.Many2many('account.tax', string="Taxes")

    @api.depends('price','tax_ids','amount_tax')
    def get_price_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price + rec.amount_tax
  
    @api.depends('price','tax_ids')
    def get_tax_amount(self):
        for rec in self:
            rec.amount_tax = 0.0 

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    expense_id = fields.Many2one('expense.verification')
