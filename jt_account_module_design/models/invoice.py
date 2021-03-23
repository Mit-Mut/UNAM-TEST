# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, timedelta


class Provision(models.Model):

    _name = 'provision'
    _description = 'Provision'
    rec_name = 'number'

    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        journal = None
        if 'default_is_payment_request' in self._context:
            journal = self.env.ref('jt_supplier_payment.payment_request_jour')

        return journal


    number = fields.Char("Number")
    baneficiary_id = fields.Many2one(
        'hr.employee', string="Beneficiary of the payment")
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        string='Partner', change_default=True)
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.model
    def _get_default_currency(self):
        ''' Get the default currency from either the journal, either the default journal's company. '''
        journal = self.journal_id
        return journal.currency_id or journal.company_id.currency_id

    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
        states={'draft': [('readonly', False)]},
        string='Currency',
        default=_get_default_currency)

    req_registeration_date = fields.Date('Request Registeration Date')
    payment_state = fields.Selection([('draft', 'Draft'), ('registered', 'Registered'),
                                    ('provision', 'Provisions'),
                                    ('rejected', 'Rejected'),
                                    ('cancel', 'Cancel')], default='draft', copy=False)
    is_from_reschedule_payment = fields.Boolean(
        string="From Reschedule", default=False)
    leaves = fields.Integer('Leaves')
    project_code = fields.Char('Project Code')
    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')
    exchange_rate = fields.Char('Exchange Rate')
    foreign_currency_amount = fields.Monetary('Foreign currency amount')
    project_number_id = fields.Many2one(
        'project.project', string='Project Number')
    is_papiit_project = fields.Boolean(
        related='project_number_id.is_papiit_project', string='Is Papiit Project')
    agreement_number = fields.Char(
        related='project_number_id.number_agreement', string='Agreement Number')
    stage = fields.Many2one(
        related='project_number_id.stage_identifier_id', string='Stage',readonly=False)
    invoice_vault_folio = fields.Char('Invoice vault folio')
    line = fields.Integer("Header")
    req_registration_date = fields.Date('Request Registration Date')
    baneficiary_key = fields.Char(
        'Baneficiary Key', related='partner_id.password_beneficiary', store=True)
    rfc = fields.Char("RFC", related='partner_id.vat', store=True)
    student_account = fields.Char("Student Account")
    transfer_key = fields.Char("Transfer Key")
    category_key = fields.Many2one(
        string="Category Key", related='partner_id.category_key', store=True)
    workstation_id = fields.Many2one(
        'hr.job', "Appointment", related='partner_id.workstation_id',readonly=False)
    folio = fields.Char("Folio against Receipt")
    folio_dependency = fields.Char("Folio Dependency")
    operation_type_id = fields.Many2one('operation.type', "Operation Type")
    date_receipt = fields.Datetime("Date of Receipt")
    date_approval_request = fields.Date("Date Approval Request")
    administrative_forms = fields.Integer("Number of Administrative Forms")
    no_of_document = fields.Integer("Number of Documents")
    sheets = fields.Integer("Sheets")
    payment_method = fields.Selection(
        [('check', 'Check'), ('electronic_transfer', 'Electronic Transfer'), ('cash', 'Cash')])
    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string='Payment Method',
        help='Indicates the way the payment was/will be received, where the '
        'options could be: Cash, Nominal Check, _compute_rejection_messageedit Card, etc.')

    document_type = fields.Selection(
        [('national', 'National Currency'), ('foreign', 'Foreign Currency')])
    upa_key = fields.Many2one('policy.keys', 'UPA Key')
    upa_document_type = fields.Many2one(
        'upa.document.type', string="Document Type UPA")
    provenance = fields.Text("Provenance")
    batch_folio = fields.Integer("Batch Folio")
    vault_folio = fields.Char("Vault folio")
    payment_bank_id = fields.Many2one('res.bank', "Bank of receipt of payment")
    payment_bank_account_id = fields.Many2one(
        'res.partner.bank', "Payment Receipt bank account")
    payment_issuing_bank_id = fields.Many2one(
        'account.journal', "Payment issuing Bank")
    payment_issuing_bank_acc_id = fields.Many2one(
        related="payment_issuing_bank_id.bank_account_id", string="Payment issuing bank Account")
    responsible_id = fields.Many2one(
        'hr.employee', 'Responsible/Irresponsible')
    administrative_secretary_id = fields.Many2one(
        'hr.employee', 'Administrative Secretary')
    holder_of_dependency_id = fields.Many2one(
        'hr.employee', "Holder of the Dependency")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    user_registering_id = fields.Many2one('res.users')
    commitment_date = fields.Date("Commitment Date")
    
    # @api.depends('payment_state')
    # def _compute_rejection_message(self):

    #     for record in self:
    #         if record.payment_state == 'rejected':
    #             record.reason_rejection_req = 'Budget Insufficiency'

    reason_rejection_req = fields.Text(string="Reason for Rejecting Request")
    reason_rejection = fields.Text("Reason for Rejection")
    reason_cancellation = fields.Text("Reason for Cancellation")
    is_payment_request = fields.Boolean("Payment Request")
    # type = fields.Selection(selection_add=[('payment_req', 'Payment Request')])

    # More info Tab
    reason_for_expendiure = fields.Char("Reason for Expenditure/Trip")
    destination = fields.Char("Destination")
    origin_payment = fields.Char("Origin")
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_expend_id = fields.Many2one(
        'hr.employee', "Name of the responsible")
    rf_person = fields.Char("RFC of the person in charge")
    responsible_category_key = fields.Many2one(
        related='manager_job_id.category_key', string="Responsible category key")
    manager_job_id = fields.Many2one(
        'hr.job', related='responsible_expend_id.job_id', string="Manager’s job")
    responsible_rfc = fields.Char(
        'VAT', related='responsible_expend_id.rfc', store=True)
    line_ids = fields.One2many('account.move.line', 'provision_id', string='Journal Items', copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', store=True, readonly=True,
        compute='_compute_commercial_partner_id')

    @api.depends('partner_id')
    def _compute_commercial_partner_id(self):
        for move in self:
            move.commercial_partner_id = move.partner_id.commercial_partner_id



    provision_line_ids = fields.One2many('provision.line', 'provision_id', string='Provision Line')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="[('company_id', '=', company_id)]",default=_get_default_journal)
    company_id = fields.Many2one(string='Company', store=True, readonly=True,
        related='journal_id.company_id', change_default=True, default=lambda self: self.env.company)
    is_show_beneficiary_key = fields.Boolean(
        'Show Beneficiary Key', default=False)
    excercise = fields.Char('excercise')

    is_show_student_account = fields.Boolean(
        'Show Student Account', default=False)
    is_show_category_key = fields.Boolean('Show Category Key', default=False)
    is_show_appointment = fields.Boolean('Show Appointment', default=False)
    is_show_responsible = fields.Boolean('Show Responsible', default=False)
    is_show_holder_of_dependency = fields.Boolean(
        'Show holder_of_dependency', default=False)
    is_show_commitment_date = fields.Boolean(
        'Show Commitmet Date', default=False)
    is_show_turn_type = fields.Boolean('Show Turn Type', default=False)
    is_show_reason_for_expendiure = fields.Boolean(
        'reason_for_expendiure', default=False)
    is_show_destination = fields.Boolean('is_show_destination', default=False)
    is_show_origin = fields.Boolean('is_show_origin', default=False)
    is_zone_res = fields.Boolean('Show Zone Res', default=False)
    is_show_resposible_group = fields.Boolean(
        'Resposible Group', default=False)

    period_start = fields.Date("Period")
    period_end = fields.Date("Period End")
    pension_reference = fields.Char("Reference")

    deposite_number = fields.Char("Deposit number")
    check_number = fields.Char("Check number")
    bank_key = fields.Char("Bank Key")
    previous_number = fields.Char("Previous Number", size=11)
    previous = fields.Monetary('Previous')
    agreement_type_id = fields.Many2one('agreement.type',string="Agreement Type")

    # More info Tab
    # responsible_category_key = fields.Char("Responsible category key")
    responsible_job_position = fields.Many2one(
        'hr.job', 'Responsible job position')
    operation_name = fields.Char(related='operation_type_id.name')
    ############################################################3
    #account total
    amount_untaxed = fields.Monetary(string='Untaxed Amount',compute='_compute_amount', store=True, readonly=True)
    amount_tax = fields.Monetary(string='Tax', store=True,compute='_compute_amount',readonly=True)
    amount_total = fields.Monetary(string='Total', store=True,compute='_compute_amount',readonly=True)

    @api.depends('provision_line_ids','provision_line_ids.price_unit','provision_line_ids.tax_ids')
    def _compute_amount(self):
        for rec in self:
            rec.amount_untaxed = sum(x.price_unit for x in rec.provision_line_ids)
            rec.amount_tax = sum(x.amount_tax for x in rec.provision_line_ids)
            rec.amount_total = rec.amount_untaxed + rec.amount_tax 


    @api.model
    def create(self,vals):
        res = super(Provision, self).create(vals)
        seq_no = self.env['ir.sequence'].next_by_code('provision')
        res.number = seq_no
        return res

    def action_cancel_budget(self):

        for rec in self:

            rec.payment_status = 'cancel'


    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
        # conac_move = self.line_ids.filtered(lambda x:x.conac_move)
        # conac_move.sudo().unlink()
        # for line in self.line_ids:
        #     line.coa_conac_id = False 
        
        # self.add_budget_available_amount()

    def unlink(self):
        for rec in self:
            if rec.payment_state not in ['registered']:
                raise UserError(_('You cannot delete an entry which has been confirmed.'))
        return super(Provision, self).unlink()


    @api.onchange('operation_type_id')
    def onchange_operation_type_id(self):
        if self.operation_type_id and self.operation_type_id.name:
            my_str1 = "Reimbursement to third parties"
            my_str2 = "Airline tickets"
            my_str3 = "Reimbursement to the fixed fund"
            my_str4 = "Reimbursement to third parties, verification of administration"
            my_str5 = "Payment to supplier"
            is_show_turn_type = False
            is_show_reason_for_expendiure = False
            is_show_destination = False
            is_show_origin = False
            is_zone_res = False
            is_show_resposible_group = False
            if self.operation_type_id.name.upper() == my_str1.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str2.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str3.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str4.upper():
                self.is_show_beneficiary_key = True
                is_show_turn_type = True
            elif self.operation_type_id.name.upper() == my_str5.upper():
                self.is_show_beneficiary_key = True
                self.is_show_commitment_date = True
                is_show_turn_type = True
            else:
                self.is_show_beneficiary_key = False

            self.is_show_turn_type = is_show_turn_type
            str_account = "Fellows"
            if self.operation_type_id.name.upper() == str_account.upper():
                self.is_show_student_account = True
            else:
                self.is_show_student_account = False

            str_category1 = "Viaticals"
            str_category2 = "Viatical expenses replacement of resources to the fixed fund"
            if self.operation_type_id.name.upper() == str_category1.upper():
                self.is_show_category_key = True
                self.is_show_appointment = True
                is_show_reason_for_expendiure = True
                is_zone_res = True
            elif self.operation_type_id.name.upper() == str_category2.upper():
                self.is_show_category_key = True
                self.is_show_appointment = True
                is_zone_res = True
            else:
                self.is_show_category_key = False
                self.is_show_appointment = False

            #====For is_show_responsible =====#
            str_responsible1 = "Scholarship recipients"
            str_responsible2 = "Third party reimbursement"
            str_responsible3 = "Airline tickets"
            str_responsible4 = "Accounts payable creation"
            if self.operation_type_id.name.upper() == str_responsible1.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible2.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible3.upper():
                self.is_show_responsible = True
            elif self.operation_type_id.name.upper() == str_responsible4.upper():
                self.is_show_responsible = True
                is_show_resposible_group = True
                is_show_reason_for_expendiure = True
            else:
                self.is_show_responsible = False

            #======is_show_holder_of_dependency =====:
            str_holder1 = "Field work and school practices"
            str_holder2 = "Reimbursement to the fixed fund"
            str_holder3 = "Reimbursement to third parties, proof of administration"
            str_holder4 = "Exchange expenses"
            str_holder5 = "Expenses of per diem replacement of resources to the fixed fund"
            str_holder6 = "Per diem"
            str_holder7 = "Payment to supplier"
            if self.operation_type_id.name.upper() == str_holder1.upper():
                self.is_show_holder_of_dependency = True
                is_show_reason_for_expendiure = True
                is_show_destination = True
                is_show_resposible_group = True
            elif self.operation_type_id.name.upper() == str_holder2.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder3.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder4.upper():
                self.is_show_holder_of_dependency = True
                is_show_reason_for_expendiure = True
                is_show_origin = True
                is_show_resposible_group = True
            elif self.operation_type_id.name.upper() == str_holder5.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder6.upper():
                self.is_show_holder_of_dependency = True
            elif self.operation_type_id.name.upper() == str_holder7.upper():
                self.is_show_holder_of_dependency = True
            else:
                self.is_show_holder_of_dependency = False

            # ===== For the is_show_reason_for_expendiure ====#
            str_expendiure = "Travel expenses replacement of resources to the fixed fund"
            if self.operation_type_id.name.upper() == str_expendiure.upper():
                is_show_reason_for_expendiure = True
                is_show_destination = True
            str_destination = "Travel expenses"
            if self.operation_type_id.name.upper() == str_destination.upper():
                is_show_destination = True

            self.is_show_reason_for_expendiure = is_show_reason_for_expendiure
            self.is_show_destination = is_show_destination
            self.is_show_origin = is_show_origin
            self.is_zone_res = is_zone_res
            self.is_show_resposible_group = is_show_resposible_group

    def action_register(self):

        self.payment_state = 'registered'
        if self.journal_id:
            journal = self.journal_id
            # if not journal.ai_credit_account_id or not journal.conac_ai_credit_account_id \
            #         or not journal.ai_debit_account_id or not journal.conac_ai_debit_account_id:
            #     if self.env.user.lang == 'es_MX':
            #         raise ValidationError(
            #             _("Por favor configure la cuenta UNAM y CONAC en diario!"))
            #     else:
            #         raise ValidationError(
            #             _("Please configure UNAM and CONAC account in journal!"))

            # if not journal.ei_credit_account_id or not journal.conac_ei_credit_account_id \
            #         or not journal.ei_debit_account_id or not journal.conac_ei_debit_account_id:
            #     if self.env.user.lang == 'es_MX':
            #         raise ValidationError(
            #             _("Por favor configure la cuenta UNAM y CONAC en diario!"))
            #     else:
            #         raise ValidationError(
            #             _("Please configure UNAM and CONAC account in journal!"))

            # today = datetime.today().date()
            # user = self.env.user
            # partner_id = user.partner_id.id
            # if self.partner_id:
            #     partner_id = self.partner_id.id
                
            # amount = self.amount_total
            # lines = [(0, 0, {
            #          'account_id': journal.ei_credit_account_id.id,
            #          'coa_conac_id': journal.conac_ei_credit_account_id.id,
            #          'credit': amount,
            #          'partner_id': partner_id,
            #          'provision_id': self.id,
            #         }),
            #          (0, 0, {
            #              'account_id': journal.ei_debit_account_id.id,
            #              'coa_conac_id': journal.conac_ei_debit_account_id.id,
            #              'debit': amount,
            #              'partner_id': partner_id,
            #              'provision_id': self.id,
            #          }),                                 


            # ]
            # item_expense_account_ids = self.provision_line_ids.mapped('program_code.item_id.unam_account_id')
            # for account_id in item_expense_account_ids:
            #     item_amount = sum(x.subtotal for x in self.provision_line_ids.filtered(lambda x:x.program_code and x.program_code.item_id and x.program_code.item_id.unam_account_id and x.program_code.item_id.unam_account_id.id==account_id.id))

            #     lines.append((0, 0, {
            #                      'account_id': journal.ai_credit_account_id.id,
            #                      'coa_conac_id': journal.conac_ai_credit_account_id.id,
            #                      'credit': item_amount,
            #                      'partner_id': partner_id,
            #                      'provision_id': self.id,
            #                  }))                
            #     lines.append((0, 0, {
            #                      'account_id': account_id.id,
            #                      'coa_conac_id': account_id.coa_conac_id and account_id.coa_conac_id.id or False,
            #                      'debit': item_amount,
            #                      'partner_id': partner_id,
            #                      'provision_id': self.id,
            #                  }))
                
            #===================particular Item records ===============#
                #===== Group 511 ======#
            # item_line_ids = self.provision_line_ids.filtered(lambda x:x.program_code and x.program_code.item_id.item in ('511','512','513','514','515','516','517','521','523','524','531'))
            # if item_line_ids:

            #     if not journal.capitalizable_credit_account_id or not journal.conac_capitalizable_credit_account_id \
            #             or not journal.capitalizable_debit_account_id or not journal.conac_capitalizable_debit_account_id:
            #         if self.env.user.lang == 'es_MX':
            #             raise ValidationError(
            #                 _("Por favor configure la cuenta UNAM y CONAC en diario!"))
            #         else:
            #             raise ValidationError(
            #                 _("Please configure UNAM and CONAC account in journal!"))
                
            #     item_amount = sum(x.subtotal for x in item_line_ids)
                     
            #     lines.append((0, 0, {
            #                      'account_id': journal.capitalizable_credit_account_id.id,
            #                      'coa_conac_id': journal.conac_capitalizable_credit_account_id.id,
            #                      'credit': item_amount,
            #                      'partner_id': partner_id,
            #                      'provision_id': self.id,
            #                  }))
                
            #     lines.append((0, 0, {
            #                          'account_id': journal.capitalizable_debit_account_id.id,
            #                          'coa_conac_id': journal.conac_capitalizable_debit_account_id.id,
            #                          'debit': item_amount,
            #                          'partner_id': partner_id,
            #                          'provision_id': self.id,
            #                      }))

            # unam_move_val = {'ref': self.display_name,  'conac_move': True,
            #                  'dependancy_id' : self.dependancy_id and self.dependancy_id.id or False,
            #                  'sub_dependancy_id': self.sub_dependancy_id and self.sub_dependancy_id.id or False,
            #                  'date': today, 'journal_id': journal.id, 'company_id': self.env.user.company_id.id,
            #                  'line_ids': lines}
            
            # move_obj = self.env['account.move']
            # unam_move = move_obj.create(unam_move_val)
            # unam_move.action_post()







class ProvisionLine(models.Model):

    _name = 'provision.line'
    _description = 'Provision Line'

    product_id = fields.Many2one('product.product',"Product")
    provision_id = fields.Many2one('provision', string='Provision')
    program_code = fields.Many2one('program.code', string='Program Code')
    egress_key_id = fields.Many2one("egress.keys", string="Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    other_amounts = fields.Monetary("Other Amounts")
    turn_type = fields.Char("Turn type")
    invoice_uuid = fields.Char("Invoice UUID")
    invoice_series = fields.Char("Invoice Series")
    folio_invoice = fields.Char("Folio Invoice")
    vault_folio = fields.Char("Vault folio")
    account_id = fields.Many2one('account.account', string='Account',
        index=True, ondelete="restrict", check_company=True,
        domain=[('deprecated', '=', False)])

    quantity = fields.Float(string='Quantity',
        default=1.0, digits='Product Unit of Measure',
        help="The optional quantity expressed by this line, eg: number of product sold. "
             "The quantity is not a legal requirement but is very useful for some reports.")


    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    price_unit = fields.Monetary('Price',digits='Product Price')
    subtotal = fields.Monetary(string='Subtotal',compute='get_price_subtotal',store=True)
    amount_tax = fields.Monetary(string='Tax Amount',compute='get_tax_amount',store=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    tax_ids = fields.Many2many('account.tax', string="Taxes")


    @api.depends('price_unit','tax_ids','amount_tax')
    def get_price_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price_unit + rec.amount_tax
  
    @api.depends('price_unit','tax_ids')
    def get_tax_amount(self):
        for rec in self:
            amount = 0
            if rec.tax_ids:
                taxes_res = rec.tax_ids._origin.compute_all(rec.price_unit,quantity=1)
                amount = taxes_res['total_included'] - taxes_res['total_excluded']
            rec.amount_tax = amount 



class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    provision_id = fields.Many2one('provision')
