from odoo import models, fields


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
    dependence = fields.Many2one('dependency', string="Dependency")
    subdependence = fields.Many2one('sub.dependency', string='Sub Dependence')
    upa_code = fields.Many2one('policy.keys', string='UPA Code')
    type_of_operation = fields.Many2one(
        'operation.type', string='Type Of Operation')
    doc_type = fields.Many2one('upa.document.type', string='Document Type')
    number = fields.Text('Number')
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
    rfc = fields.Text('RFC')
    invoice_vault_folio = fields.Text('Invoice vault folio')
    uuid_invoice = fields.Text('UUID Invoice')
    invoice_series = fields.Text('Invoice Series')
    invoice_folio = fields.Text('Invoice Folio')
    type_of_aggrement = fields.Many2one(
        'agreement.agreement.type', string='Type Of Agreement')
    agreement_number = fields.Many2one(
        'bases.collaboration', string='Agreement Number')
    agreement_name = fields.Char(
        related='agreement_number.name', string='Agreement Name')
    tech_support = fields.Many2one('hr.employee', string='Technical Support')
    admin_manager = fields.Many2one(
        'hr.employee', string='Administrative manager')
    ext_sponsor = fields.Text('External sponsor')
    observation = fields.Text('Observations')
    reason_for_rejection = fields.Many2one(
        'rejection.check', string='Reason for rejection')
    verifcation_expense_ids = fields.One2many(
        'verification.expense.line', 'verification_expense_id', string='Verfication Expense Line')

    def action_approve(self):

        self.state = 'approve'

    def action_reject(self):

        self.state = 'reject'


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
    taxes = fields.Many2one('account.tax', string="Taxes")
