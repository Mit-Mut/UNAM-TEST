from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class Invoice(models.Model):

    _inherit = 'account.move'

    income_type = fields.Selection([('extra', 'Extraordinary'),
                                    ('own', 'Own')], string="Income Type")
    sub_origin_resource_id = fields.Many2one('sub.origin.resource', "Extraordinary / Own income")
    type_of_revenue_collection = fields.Selection([('billing', 'Billing'),
                                                   ('deposit_cer', 'Certificates of deposit'),
                                                   ('dgae_ref', 'Reference of DGAE'),
                                                   ('dgoae_trades', 'Trades DGOAE')], "Type of Revenue Collection")
    income_bank_journal_id = fields.Many2one('account.journal', "Bank")
    income_bank_account = fields.Many2one('account.journal', "Bank Account")
    reception_date = fields.Date("Reception Date")
    deposit_date = fields.Date("Deposit Date")
    cfdi_folio = fields.Char("Folio CFDI")
    range_sheet_used = fields.Char("Range of sheets used")
    income_activity = fields.Selection([('procosion_service', 'Provision of service'),
                                        ('disposal_property', 'Disposal of property'),
                                        ('leasing_real_estate', 'Leasing of real estate'),
                                        ('donations', 'Donations'),
                                        ('conacyt', 'Conacyt')], "Activity")
    voucher_type = fields.Selection([('income', 'Income'),
                                     ('expenditure', 'Expenditure'),
                                     ('payment_supplement', 'Payment Supplement'),
                                     ('transfer', 'Transfer')], "Voucher Type")
    currency_type = fields.Selection([('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    exchange_rate = fields.Monetary("Exchange Rate")
    income_payment_type = fields.Selection([('single_pue', 'Payment in a singlePUE'),
                                            ('ppd_installments', 'Payment in PPD installments')], "Payment Type")
    related_cfdi = fields.Char("Related CFDI")
    income_payment_ref = fields.Char("Payment reference or approval number")
    ieps = fields.Char('IEPS')
    ieps_amount = fields.Monetary("IEPS Amount")
    record_type = fields.Selection([('manual', 'Manual'),
                                    ('automatic', 'Automatic')], 'Record Type')
    exercise = fields.Char("Exercise")
    operation_key_id = fields.Many2one('deposit.certificate.type', "Operation Key")
    concept = fields.Char("Concept")
    folio_upa = fields.Char("Folio UPA")
    exercise_upa = fields.Char("Exercise UPA")
    observations = fields.Char("Observations")
    status_certificate = fields.Selection([('approved', 'Approved'),
                                           ('cancelled', 'Cancelled')], 'Status Certificate')
    cancellation_date = fields.Date("Cancellation Date")
    date_reference = fields.Date('Date of Reference')
    exercise_reference = fields.Char("Exercise of the reference")
    email = fields.Char("Mail")
    certificate_seal = fields.Char("Certificate Seal")
    charge_id = fields.Many2one('hr.job', "Charge")
    base_salary = fields.Monetary("Base Salary")
    emitter = fields.Char("Emitter")
    registry = fields.Char("Registry")
    issuer_dependency_id = fields.Many2one('dependency', "Issuer Dependency")
    cfdi_conacyt_enter = fields.Char("CFDI CONACYT Enter")
    cfdi_conacyt_exercise = fields.Char("CFDI Exercise CONACYT entry")
    amount_cfdi_conacyt_income = fields.Monetary("Amount CFDI CONACYT Income")
    conacyt_project_key = fields.Many2one('project.project', "CONACYT project key")
    cfdi_conacyt_date = fields.Date('CFDI CONACYT Date')
    conacyt_project_name = fields.Char('CONACYT Project Name')
    uuid_cfdi_ps = fields.Char('UUID CFDI PS')
    income_vat = fields.Monetary("VAT")
    income_isr = fields.Monetary("ISR")
    surcharges_ps = fields.Monetary("Surcharges PS")
    legal_number = fields.Char("Legal Number")
    legal_compensation = fields.Char("Legal Compensation")
    number_of_returned_check = fields.Integer('Number of returned check') 
    circular_number = fields.Char('Circular number')
    addressee = fields.Char('Addressee')
    bank_status_account = fields.Char('Bank status account')
    bank_account_statement = fields.Char('Bank account statement')
    number_receipts = fields.Char('Number receipts')
    movement_date = fields.Date('Movement date')
    description_of_the_movement = fields.Char('Description of the movement')
    settlement_date = fields.Date('Settlement date')
    income_id = fields.Char('ID')
    income_branch = fields.Char('Branch')
    reference_plugin = fields.Char('Reference Plugin')
    income_status = fields.Selection([('approved','Approved'),('rejected','Rejected')],string="Income Status")
    adequacies_ids = fields.One2many("adequacies",'invoice_move_id')
    
    @api.depends('adequacies_ids','record_type','type_of_revenue_collection')
    def get_hide_budget_refund(self):
        for record in self:
            is_hide_budget_refund = False
            if record.adequacies_ids:
                is_hide_budget_refund = True
            elif record.record_type != 'manual' or record.type_of_revenue_collection != 'deposit_cer':
                is_hide_budget_refund = True
            record.is_hide_budget_refund = is_hide_budget_refund
            
    is_hide_budget_refund = fields.Boolean('Hide Budget Refund',compute='get_hide_budget_refund',store=True)
    
    @api.constrains('income_id')
    def _check_income_id(self):
        if self.income_id and not str(self.income_id).isnumeric():
            raise ValidationError(_('The ID must be numeric value'))

    @api.constrains('income_branch')
    def _check_income_branch(self):
        if self.income_branch and not str(self.income_branch).isnumeric():
            raise ValidationError(_('The Branch must be numeric value'))
    
 
    def action_budget_refund(self):
        liq_adequacy_jour = self.env.ref('jt_conac.liq_adequacy_jour')
        journal_id = False
        if liq_adequacy_jour:
            journal_id = liq_adequacy_jour.id

        seq_ids = self.env['ir.sequence'].search([('code', '=', 'invoice.adequacies.folio')], order='company_id')
        number_next = 0
        if seq_ids:
            number_next = seq_ids[0].number_next_actual 

        return {
            'name': _('Liquid Adjustments'),
            'res_model': 'liquid.adjustments.manual.deposite',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context' : {'default_journal_id' : journal_id,'default_folio':number_next,'default_move_id':self.id}
        }
        
class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'
    
    @api.depends('product_id')
    def count_sub_produts(self):
        for record in self:
            if record.product_id:
                record.subproduct_count = self.env['product.product'].search_count([('parent_product_id','=',record.product_id.id)])
            else:
                record.subproduct_count = 0
        
    subproduct_count = fields.Integer('Subproduct',compute="count_sub_produts",store=True)
    unidentified_product = fields.Integer('Unidentified product')
    income_sub_account = fields.Char("Income Sub-account")
    income_sub_subaccount = fields.Char("Income Sub-subaccount")
    ddi_office_accounting = fields.Char("DDI Office to general accounting the")
    amount_of_check = fields.Float("Amount of the check")
    deposit_for_check_recovery = fields.Char("Deposit for check recovery")
    cfdi_20 = fields.Char("CFDI 20%")
    
    


