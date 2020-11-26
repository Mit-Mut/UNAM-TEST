from odoo import models, fields, api


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
        'res.currency', help='The currency used to enter statement', string="Currency")
    agreement_number = fields.Many2one(
        'bases.collaboration', string='Agreement Number')
    agreement_name = fields.Char(
        related='agreement_number.name', string='Agreement Name')
    tech_support = fields.Many2one('hr.employee', string='Technical Support')
    admin_manager = fields.Many2one(
        'hr.employee', string='Administrative manager')
    ext_sponsor = fields.Text('External sponsor')
    observation = fields.Text('Observations')
    reason_for_rejection = fields.Char('Reason for rejection')
    verifcation_expense_ids = fields.One2many(
        'verification.expense.line', 'verification_expense_id', string='Verfication Expense Line')

    # untax_amount = fields.Monetary(
    #     'Subtotal', compute='_compute_subtotal_amount', currency_field='currency_id')
    # tax_group_by = fields.Text('Taxes', compute='_compute_tax_amount')
    # total = fields.Monetary(
    #     'Total(Price)', compute='_compute_total_amount', currency_field='currency_id')

    # def _compute_subtotal_amount(self):

    #     subtotal = 0.0
    #     for record in self.verifcation_expense_ids:
    #         subtotal += record.subtotal
    #     record.untax_amount = subtotal

    # def _compute_tax_amount(self):

    #     for record in self.verifcation_expense_ids:
    #         tax_amount = 0.0
    #         tax_amount = record.taxes.amount * record.subtotal
    #         record.tax_group_by = tax_amount

    # def _compute_total_amount(self):

    #     total = 0
    #     for record in self.verifcation_expense_ids:
    #         tax_amount = record.taxes.amount * record.subtotal
    #         print(tax_amount)
    #         record.total = record.untax_amount

    def action_approve(self):

        self.status = 'approve'


class VerificationOfExpenseLine(models.Model):

    _name = 'verification.expense.line'
    _description = 'Verification Expense Line'

    row = fields.Text('Row')
    verification_expense_id = fields.Many2one(
        'verification.expense', string='Verification Expense')
    program_code = fields.Many2one('program.code', string='Program Code')
    subtotal = fields.Monetary('Subtotal(Price)')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Selection(
        [('mn_amount', 'MN amount'),
            ('amount_me', 'Amount ME')
         ], string="Amount")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
