from odoo import models, fields


class VerficationOfExpense(models.Model):

    _name = 'expense.verification'
    _description = 'Verification Of Expense'
    
    state = fields.Selection([('draft', 'Draft'),
                              ('approve', 'Approved'),
                              ('reject', 'Rejected')], string="Status", default="draft")
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
    type_of_aggrement = fields.Many2one('agreement.agreement.type')
