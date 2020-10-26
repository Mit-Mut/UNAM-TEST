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
from odoo.exceptions import ValidationError
from datetime import datetime

class BasesCollabration(models.Model):

    _name = 'bases.collaboration'
    _description = "Bases of collaboration"

    name = fields.Char("Agreement Name")
    convention_no = fields.Char("Convention No.")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    opening_bal = fields.Monetary("Opening Balance")
    available_bal = fields.Monetary("Available Balance")
    agreement_type_id = fields.Many2one('agreement.agreement.type', 'Agreement Type')
    fund_type_id = fields.Many2one('fund.type', "Fund Type")
    dependency_obs = fields.Text("Dependency Observations")
    dependency_id = fields.Many2one('dependency', "Unit No.")
    desc_dependency = fields.Text("Description Dependency")
    subdependency_id = fields.Many2one('sub.dependency', "Sub Dependency")
    desc_subdependency = fields.Text("Sub-unit Name")
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    goals = fields.Char("Goals")
    registration_date = fields.Date("Date of registration in the system")
    is_specific = fields.Boolean(string='Specific',default=False) 
    liability_account_id = fields.Many2one('account.account', "Liability Accounting Account")
    investment_account_id = fields.Many2one('account.account', "Investment Accounting Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    state = fields.Selection([('draft', 'Draft'),
                               ('valid', 'Valid'),
                               ('in_force', 'In Force'),
                              ('to_be_cancelled', 'To Be Cancelled'),
                              ('cancelled', 'Cancelled')], "Status", default='draft')
    total_operations = fields.Integer("Operations", compute="compute_operations")
    total_modifications = fields.Integer("Modifications", compute="compute_modifications")

    employee_id = fields.Many2one('hr.employee', 'Holder of the unit')
    job_id = fields.Many2one('hr.job', "Market Stall")
    phone = fields.Char("Telephone of the unit holder")
    administrative_secretary_id = fields.Many2one('hr.employee', "Administrative Secretary")
    administrative_secretary_phone = fields.Char("Administrative Secretary Telephone")
    direct_manager_cbc_id = fields.Many2one("hr.employee", "Direct manager of CBC")
    cbc_responsible_phone = fields.Char("CBC responsible phone number")
    email = fields.Char("Email")
    unit_address = fields.Text("Unit Address")
    additional_observation = fields.Text("Additional observations of the agency")
    cbc_format = fields.Binary("CBC Format")
    cbc_shipping_office = fields.Binary("CBC Shipping Office")
    committe_ids = fields.One2many('committee', 'collaboration_id', string="Committees")

    no_beneficiary_allowed = fields.Integer("Number of allowed beneficiaries")
    beneficiary_ids = fields.One2many('collaboration.beneficiary', 'collaboration_id')
    provider_ids = fields.One2many('collaboration.providers', 'collaboration_id')

    cancel_date = fields.Date("Cancellation date")
    supporing_doc = fields.Binary("Supporting Documentation")
    reason_cancel = fields.Text("Reason for Cancellations")

    fund_name_transfer_id = fields.Many2one('bases.collaboration', 'Fund name for transfers')
    closing_amt = fields.Monetary("Amount")

    _sql_constraints = [
        ('folio_convention_no', 'unique(convention_no)', 'The Convention No. must be unique.')]

    @api.model
    def create(self, vals):
        res = super(BasesCollabration, self).create(vals)
        if res and res.beneficiary_ids:
            if not res.no_beneficiary_allowed or (res.no_beneficiary_allowed and \
                                                  res.no_beneficiary_allowed < len(res.beneficiary_ids)):
                raise ValidationError(_("You can add only %s Beneficiaries which is mentined in "
                                        "'Number of allowed beneficiaries'" % res.no_beneficiary_allowed))
        return res

    def write(self, vals):
        res = super(BasesCollabration, self).write(vals)
        for rec in self:
            if rec and rec.beneficiary_ids:
                if not rec.no_beneficiary_allowed or (rec.no_beneficiary_allowed and \
                                                      rec.no_beneficiary_allowed < len(rec.beneficiary_ids)):
                    raise ValidationError(_("You can add only %s Beneficiaries which is mentined in "
                                            "'Number of allowed beneficiaries'" % rec.no_beneficiary_allowed))
        return res

    def compute_operations(self):
        operation_obj = self.env['request.open.balance']
        for rec in self:
            if rec.name:
                operations = operation_obj.search([('bases_collaboration_id', '=', rec.id)])
                rec.total_operations = len(operations)

    def compute_modifications(self):
        modification_obj = self.env['bases.collaboration.modification']
        for rec in self:
            if rec.name:
                modifications = modification_obj.search([('bases_collaboration_id', '=', rec.id)])
                rec.total_modifications = len(modifications)

    def action_closing_collaboration(self):
        return {
            'name': 'Closing Collaboration',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_agreement.closing_collaboration_form_view').id,
            'res_model': 'closing.collaboration',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }

    def cancel(self):
        return {
            'name': 'Cancel Collaboration',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_agreement.cancel_collaboration_form_view').id,
            'res_model': 'cancel.collaboration',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_operations(self):
        operation_obj = self.env['request.open.balance']
        operations = operation_obj.search([('bases_collaboration_id', '=', self.id)])
        if operations:
            return {
                'name': 'Operations',
                'view_type': 'form',
                # 'view_id': self.env.ref('jt_agreement.view_req_open_balance_tree').id,
                'view_mode': 'tree,form',
                'view_ids': [(5, 0, 0),
                             (0, 0, {self.env.ref("jt_agreement.view_req_open_balance_tree").id}),
                             (0, 0, {self.env.ref("jt_agreement.view_req_open_balance_form").id})],
                'res_model': 'request.open.balance',
                'domain': [('bases_collaboration_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_bases_collaboration_id': self.id,
                            'default_apply_to_basis_collaboration': True,
                            'default_agreement_number': self.convention_no,
                            'default_opening_balance': self.opening_bal,
                            'default_cbc_format': self.cbc_format,
                            'default_supporting_documentation': self.cbc_format,
                            'default_cbc_shipping_office': self.cbc_shipping_office,
                            'default_name': self.name,
                            'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
                                    else False,
                            'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
                                    else False,
                            'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
                            else False,
                            'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
                            else False
                            }
            }
        else:
            return {
                'name': 'Operations',
                # 'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_agreement.view_req_open_balance_form').id,
                'view_ids': [self.env.ref("jt_agreement.view_req_open_balance_form").id],
                'res_model': 'request.open.balance',
                'domain': [('bases_collaboration_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_bases_collaboration_id': self.id,
                            'default_apply_to_basis_collaboration': True,
                            'default_opening_balance': self.opening_bal,
                            'default_agreement_number': self.convention_no,
                            'default_name': self.name,
                            'default_cbc_format': self.cbc_format,
                            'default_supporting_documentation': self.cbc_format,
                            'default_cbc_shipping_office': self.cbc_shipping_office,
                            'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
                            else False,
                            'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
                            else False,
                            'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
                            else False,
                            'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
                            else False
                            }
            }

    def action_modifications(self):
        modification_obj = self.env['bases.collaboration.modification']
        modifications = modification_obj.search([('bases_collaboration_id', '=', self.id)])
        if modifications:
            return {
                'name': 'Modifications',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'bases.collaboration.modification',
                'domain': [('bases_collaboration_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_dependency_id': self.dependency_id and self.dependency_id.id or False,
                            'default_bases_collaboration_id': self.id,
                            'default_current_target': self.goals,
                            'from_modification': True
                            }
            }
        else:
            return {
                'name': 'Modifications',
                'view_mode': 'form',
                'res_model': 'bases.collaboration.modification',
                'domain': [('bases_collaboration_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_dependency_id': self.dependency_id and self.dependency_id.id or False,
                            'default_bases_collaboration_id': self.id,
                            'default_current_target': self.goals,
                            'from_modification': True
                            }
            }


    def confirm(self):
        self.state = 'valid'

    def action_schedule_withdrawal(self):
        req_obj = self.env['request.open.balance']
        for collaboration in self:
            for beneficiary in collaboration.beneficiary_ids:
                partner_id = beneficiary.employee_id and beneficiary.employee_id.user_id and beneficiary.employee_id.user_id.partner_id and beneficiary.employee_id.user_id.partner_id.id or False   
                req_obj.create({
                    'bases_collaboration_id': collaboration.id,
                    'apply_to_basis_collaboration': True,
                    'agreement_number': collaboration.convention_no,
                    'opening_balance': collaboration.available_bal,
                    'supporting_documentation': collaboration.cbc_format,
                    'type_of_operation': 'retirement',
                    'beneficiary_id': partner_id,
                    'name': self.name,
                    'liability_account_id': collaboration.liability_account_id.id if collaboration.liability_account_id
                    else False,
                    'interest_account_id': collaboration.interest_account_id.id if collaboration.interest_account_id
                    else False,
                    'investment_account_id': collaboration.investment_account_id.id if collaboration.investment_account_id
                    else False,
                    'availability_account_id': collaboration.availability_account_id.id if collaboration.availability_account_id
                    else False
                })

            for beneficiary in collaboration.provider_ids:
                partner_id = beneficiary.partner_id and beneficiary.partner_id.id or False    
                req_obj.create({
                    'bases_collaboration_id': collaboration.id,
                    'apply_to_basis_collaboration': True,
                    'agreement_number': collaboration.convention_no,
                    'opening_balance': collaboration.available_bal,
                    'supporting_documentation': collaboration.cbc_format,
                    'type_of_operation': 'retirement',
                    'provider_id': partner_id,
                    'name': self.name,
                    'liability_account_id': collaboration.liability_account_id.id if collaboration.liability_account_id
                    else False,
                    'interest_account_id': collaboration.interest_account_id.id if collaboration.interest_account_id
                    else False,
                    'investment_account_id': collaboration.investment_account_id.id if collaboration.investment_account_id
                    else False,
                    'availability_account_id': collaboration.availability_account_id.id if collaboration.availability_account_id
                    else False
                })

    @api.onchange('direct_manager_cbc_id')
    def onchange_direct_manager_cbc(self):
        if self.direct_manager_cbc_id:
            if self.direct_manager_cbc_id.work_phone:
                self.cbc_responsible_phone = self.direct_manager_cbc_id.work_phone
            if self.direct_manager_cbc_id.work_email:
                self.email = self.direct_manager_cbc_id.work_email

    @api.onchange('administrative_secretary_id')
    def onchange_administrative_secretary(self):
        if self.administrative_secretary_id and self.administrative_secretary_id.work_phone:
            self.administrative_secretary_phone = self.administrative_secretary_id.work_phone

    @api.onchange('employee_id')
    def onchange_emp_id(self):
        if self.employee_id:
            emp = self.employee_id
            if emp.job_id:
                self.job_id = emp.job_id.id
            if emp.work_phone:
                self.phone = emp.work_phone

    @api.constrains('convention_no')
    def _check_convention_no(self):
        if self.convention_no and not self.convention_no.isnumeric():
            raise ValidationError(_('Convention No must be Numeric.'))
        if self.convention_no and len(self.convention_no) != 8:
            raise ValidationError(_('Convention No must be 8 characters.'))
        if self.dependency_id and self.subdependency_id:
            name = self.dependency_id.dependency + self.subdependency_id.sub_dependency
            if not self.convention_no.startswith(name):
                raise ValidationError(_('First 5 character of Convention must be Dependency and Sub Dependency.'))

    @api.onchange('dependency_id', 'subdependency_id')
    def onchange_dep_subdep(self):
        if self.dependency_id or self.subdependency_id:
            self.convention_no = ''
            number = ''
            if self.dependency_id:
                number += self.dependency_id.dependency
                self.desc_dependency = self.dependency_id.description
            if self.subdependency_id:
                number += self.subdependency_id.sub_dependency
                self.desc_subdependency = self.subdependency_id.description
            self.convention_no = number

    @api.onchange('agreement_type_id')
    def onchange_agreement_type_id(self):
        if self.agreement_type_id and self.agreement_type_id.fund_type_id:
            self.fund_type_id = self.agreement_type_id.fund_type_id.id

class Committe(models.Model):

    _name = 'committee'
    _description = "Committee"

    column_id = fields.Many2one('hr.employee', "Column Name")
    column_position_id = fields.Many2one('hr.job', "Position / Appointment column")
    collaboration_id = fields.Many2one('bases.collaboration')


    @api.onchange('column_id')
    def onchange_column_id(self):
        if self.column_id and self.column_id.job_id:
            self.column_position_id = self.column_id.job_id.id

class Providers(models.Model):
    _name = 'collaboration.providers'
    _description = "Collaboration Providers"

    collaboration_id = fields.Many2one('bases.collaboration')
    partner_id = fields.Many2one('res.partner', "Name")
    bank_id = fields.Many2one('res.partner.bank', "Bank")
    account_number = fields.Char("Account Number")

    @api.onchange('bank_id')
    def onchage_bank(self):
        if self.bank_id:
            self.account_number = self.bank_id.acc_number


class Beneficiary(models.Model):
    _name = 'collaboration.beneficiary'
    _description = "Collaboration Beneficiary"

    collaboration_id = fields.Many2one('bases.collaboration')
    employee_id = fields.Many2one('hr.employee', "Name")
    bank_id = fields.Many2one('res.partner.bank', "Bank")
    account_number = fields.Char("Account Number")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary("Payment Amount")
    payment_rule_id = fields.Many2one('recurring.payment.template', "Payment Rule")
    validity_start = fields.Date("Validity of the beneficiary start")
    validity_final_beneficiary = fields.Date("Validity of the Final Beneficiary")
    withdrawal_sch_date = fields.Date("Withdrawal scheduling date")

    @api.onchange('bank_id')
    def onchage_bank(self):
        if self.bank_id:
            self.account_number = self.bank_id.acc_number

class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'
    _rec_name = 'bank_id'

    def name_get(self):
        if 'from_agreement' not in self._context:
            res = []
            for bank in self:
                res.append((bank.id, bank.acc_number))
        else:
            res = super(ResPartnerBank, self).name_get()
        return res

class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if 'from_retier_operation' in self._context and 'collaboration_id' in self._context:
            collaboration = self.env['bases.collaboration'].browse(self._context.get('collaboration_id'))
            partner_ids = []
            if collaboration and collaboration.provider_ids:
                for provider in collaboration.provider_ids:
                    partner_ids.append(provider.partner_id.id)
            args = [['id', 'in', partner_ids]]

#         if 'from_trust_provider' in self._context and 'collaboration_id' in self._context:
#             collaboration = self.env['bases.collaboration'].browse(self._context.get('collaboration_id'))
#             partner_ids = []
#             if collaboration and collaboration.provider_ids:
#                 for provider in collaboration.provider_ids:
#                     partner_ids.append(provider.partner_id.id)
#             args = [['id', 'in', partner_ids]]
            
        res = super(ResPartner, self).name_search(name, args=args, operator=operator, limit=limit)
        return res

class RequestOpenBalance(models.Model):

    _name = 'request.open.balance'
    _description = "Request to Open Balance"

    name = fields.Char("Name")
    bases_collaboration_id = fields.Many2one('bases.collaboration')
    operation_number = fields.Char("Operation Number")
    agreement_number = fields.Char("Agreement Number")
    type_of_operation = fields.Selection([('open_bal', 'Opening Balance'),
                                          ('increase', 'Increase'),
                                          ('retirement', 'Retirement'),
                                          ('withdrawal', 'Withdrawal for settlement'),
                                          ('withdrawal_cancellation', 'Withdrawal Due to Cancellation'),
                                          ('withdrawal_closure', 'Withdrawal due to closure'),
                                          ('increase_by_closing', 'Increase by closing')],
                                         string="Type of Operation")
    apply_to_basis_collaboration = fields.Boolean("Apply to Basis of Collaboration")
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    state = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                              ('approved', 'Approved'),
                               ('rejected', 'Rejected'),
                               ('confirmed', 'Confirmed'),
                               ('canceled', 'Canceled')], string="Status", default="draft")

    request_date = fields.Date("Request Date")
    trade_number = fields.Char("Trade Number")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    opening_balance = fields.Monetary("Opening Amount")
    observations = fields.Text("Observations")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id,
                              string="Requesting User")

    cbc_format = fields.Binary("CBC Format")
    cbc_shipping_office = fields.Binary("CBC Shipping Office")
    liability_account_id = fields.Many2one('account.account', "Liability Accounting Account")
    investment_account_id = fields.Many2one('account.account', "Investment Accounting Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    reason_rejection = fields.Text("Reason for Rejection")
    supporting_documentation = fields.Binary("Supporting Documentation")
    create_payment_request = fields.Boolean("Create Payment Request")
    beneficiary_id = fields.Many2one('res.partner', "Beneficiary")
    provider_id = fields.Many2one('res.partner', "Provider")
    is_cancel_collaboration = fields.Boolean("Operation of cancel collaboration", default=False)

    #==== fields for trust investment =======#
    
    trust_id = fields.Many2one('agreement.trust','Trust')
    
    patrimonial_account_id = fields.Many2one('account.account', "Patrimonial Account")
    investment_account_id = fields.Many2one('account.account', "Investment Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    honorary_account_id = fields.Many2one('account.account', "Honorary Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    liability_account_id = fields.Many2one('account.account', "Liability Account")

    trust_agreement_file = fields.Binary("Trustee Agreement")
    trust_agreement_file_name = fields.Char("Trust Agreement File Name")
    trust_office_file = fields.Binary("Trust Contract Official Letter")
    trust_office_file_name = fields.Char("Trust Office File Name")

    origin_journal_id = fields.Many2one('account.journal','Origin Bank Account')
    destination_journal_id = fields.Many2one('account.journal','Destination Bank Account')
    
    trust_provider_ids = fields.Many2many('res.partner','rel_req_bal_trust_partner','partner_id','req_id',compute="get_trust_provider_ids")
    trust_beneficiary_ids = fields.Many2many('res.partner','rel_req_bal_trust_beneficiary','partner_id','req_id',compute="get_trust_beneficiary_ids")
    bases_collaboration_beneficiary_ids = fields.Many2many('res.partner','rel_req_bal_bases_collaboration_beneficiary','partner_id','req_id',compute="get_bases_collaboration_beneficiary_ids")

    @api.depends('trust_id','trust_id.provider_ids','trust_id.provider_ids.partner_id')
    def get_trust_provider_ids(self):
        for rec in self:
            if rec.trust_id and rec.trust_id.provider_ids:
                rec.trust_provider_ids = [(6,0,rec.trust_id.provider_ids.mapped('partner_id').ids)]
            else:
                rec.trust_provider_ids = [(6,0,[])]
                
    @api.depends('trust_id','trust_id.beneficiary_ids','trust_id.beneficiary_ids.employee_id')
    def get_trust_beneficiary_ids(self):
        for rec in self:
            partner_ids = []
            if rec.trust_id and rec.trust_id.beneficiary_ids:
                
                for emp in rec.trust_id.beneficiary_ids.mapped('employee_id'):
                    if emp.user_id and emp.user_id.partner_id: 
                        partner_ids.append(emp.user_id.partner_id.id)
            rec.trust_beneficiary_ids = [(6,0,partner_ids)]

    @api.depends('bases_collaboration_id','bases_collaboration_id.beneficiary_ids','bases_collaboration_id.beneficiary_ids.employee_id')
    def get_bases_collaboration_beneficiary_ids(self):
        for rec in self:
            partner_ids = []
            if rec.bases_collaboration_id and rec.bases_collaboration_id.beneficiary_ids:
                for emp in rec.bases_collaboration_id.beneficiary_ids.mapped('employee_id'):
                    if emp.user_id and emp.user_id.partner_id: 
                        partner_ids.append(emp.user_id.partner_id.id)
            rec.bases_collaboration_beneficiary_ids = [(6,0,partner_ids)]
                
    @api.model
    def create(self, vals):
        res = super(RequestOpenBalance, self).create(vals)
        if res and res.is_cancel_collaboration and res.type_of_operation != 'withdrawal_cancellation':
            raise ValidationError(_("Type of Operation must be 'Withdrawal Due to Cancellation' for this operation!"))
        if res and not res.is_cancel_collaboration and res.type_of_operation == 'withdrawal_cancellation':
            raise ValidationError(_("Can't create Operation with 'Withdrawal Due to Cancellation' Type of Operation manually!"))
        return res

    def write(self, vals):
        res = super(RequestOpenBalance, self).write(vals)
        for rec in self:
            if rec.is_cancel_collaboration and rec.type_of_operation != 'withdrawal_cancellation':
                raise ValidationError(
                    _("Type of Operation must be 'Withdrawal Due to Cancellation' for this operation!"))
            if not rec.is_cancel_collaboration and rec.type_of_operation == 'withdrawal_cancellation':
                raise ValidationError(
                        _("Can't create Operation with 'Withdrawal Due to Cancellation' Type of Operation manually!"))
        return res

    def action_create_payment_req(self):
        payment_req_obj = self.env['payment.request']
        payment_reqs = payment_req_obj.search([('balance_req_id', '=', self.id)])
        beneficiary = False
        if self.beneficiary_id:
            beneficiary = self.env['collaboration.beneficiary'].search([
            ('collaboration_id', '=', self.bases_collaboration_id.id), ('partner_id', '=', self.beneficiary_id.id)])
        if payment_reqs:
            return {
                'name': 'Payment Requests',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'payment.request',
                'domain': [('balance_req_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                 'context': {'default_balance_req_id': self.id,
                            'default_name': self.name,
                            'default_type_of_operation': 'retirement',
                            'default_operation_number': self.operation_number,
                            'default_amount': self.opening_balance,
                             'default_beneficiary_id': self.beneficiary_id and self.beneficiary_id.id or False,
                             'default_bank_id': beneficiary.bank_id.id if beneficiary and beneficiary.bank_id else False,
                             'default_account_number': beneficiary.account_number if beneficiary else ''
                            }
            }
        else:
            return {
                'name': 'Payment Request',
                'view_mode': 'form',
                'res_model': 'payment.request',
                'domain': [('balance_req_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_balance_req_id': self.id,
                            'default_name': self.name,
                            'default_type_of_operation': 'retirement',
                            'default_operation_number': self.operation_number,
                            'default_amount': self.opening_balance,
                            'default_beneficiary_id': self.beneficiary_id and self.beneficiary_id.id or False,
                            'default_bank_id': beneficiary.bank_id.id if beneficiary and beneficiary.bank_id else False,
                            'default_account_number': beneficiary.account_number if beneficiary else ''
                            }
            }

    @api.constrains('operation_number')
    def _check_operation_number(self):
        if self.operation_number and not self.operation_number.isnumeric():
            raise ValidationError(_('Operation Number must be Numeric.'))

    def request(self):
        self.env['request.open.balance.invest'].create({
            'name': self.name,
            'operation_number': self.operation_number,
            'agreement_number': self.agreement_number,
            'is_cancel_collaboration': True if self.type_of_operation == 'withdrawal_cancellation' else False,
            'type_of_operation': self.type_of_operation,
            'apply_to_basis_collaboration': self.apply_to_basis_collaboration,
            'origin_resource_id': self.origin_resource_id and self.origin_resource_id.id or False,
            'state': 'requested',
            'request_date': self.request_date,
            'trade_number': self.trade_number,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'opening_balance': self.opening_balance,
            'observations': self.observations,
            'user_id': self.user_id and self.user_id.id or False,
            'cbc_format': self.cbc_format,
            'cbc_shipping_office': self.cbc_shipping_office,
            'liability_account_id': self.liability_account_id and self.liability_account_id.id or False,
            'investment_account_id': self.investment_account_id and self.investment_account_id.id or False,
            'interest_account_id': self.interest_account_id and self.interest_account_id.id or False,
            'availability_account_id': self.availability_account_id and self.availability_account_id.id or False,
            'balance_req_id': self.id,
            'patrimonial_account_id' : self.patrimonial_account_id and self.patrimonial_account_id.id or False,
            'investment_account_id' : self.investment_account_id and self.investment_account_id.id or False,
            'interest_account_id' : self.interest_account_id and self.interest_account_id.id or False,
            'honorary_account_id' : self.honorary_account_id and self.honorary_account_id.id or False,
            'availability_account_id' : self.availability_account_id and self.availability_account_id.id or False,
            'liability_account_id' : self.liability_account_id and self.liability_account_id.id or False,
            'trust_agreement_file' : self.trust_agreement_file,
            'trust_agreement_file_name' : self.trust_agreement_file_name,
            'trust_office_file' : self.trust_office_file,
            'trust_office_file_name' : self.trust_office_file_name,
            'trust_id' : self.trust_id and self.trust_id.id or False,
            'origin_journal_id' : self.origin_journal_id and self.origin_journal_id.id or False,
            "destination_journal_id" : self.destination_journal_id and self.destination_journal_id.id or False, 
        })
        self.state = 'requested'
        if self.type_of_operation == 'withdrawal_cancellation' and self.bases_collaboration_id:
            self.bases_collaboration_id.state = 'to_be_cancelled'

class RequestOpenBalanceInvestment(models.Model):

    _name = 'request.open.balance.invest'
    _description = "Request to Open Balance Investment"

    name = fields.Char("Name")
    balance_req_id = fields.Many2one('request.open.balance', "Opening Balance Request")
    operation_number = fields.Char("Operation Number")
    agreement_number = fields.Char("Agreement Number")
    type_of_operation = fields.Selection([('open_bal', 'Opening Balance'),
                                          ('increase', 'Increase'),
                                          ('retirement', 'Retirement'),
                                          ('withdrawal', 'Withdrawal for settlement'),
                                          ('withdrawal_cancellation', 'Withdrawal Due to Cancellation')],
                                            string="Type of Operation")
    apply_to_basis_collaboration = fields.Boolean("Apply to Basis of Collaboration")
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    state = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                               ('rejected', 'Rejected'),
                               ('confirmed', 'Confirmed'),
                              ('approved', 'Approved'),
                              ('done', 'Done'),
                               ('canceled', 'Canceled')], string="Status", default="draft")

    request_date = fields.Date("Request Date")
    trade_number = fields.Char("Trade Number")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    opening_balance = fields.Monetary("Opening Amount")
    observations = fields.Text("Observations")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id,
                              string="Requesting User")

    cbc_format = fields.Binary("CBC Format")
    cbc_shipping_office = fields.Binary("CBC Shipping Office")
    liability_account_id = fields.Many2one('account.account', "Liability Accounting Account")
    investment_account_id = fields.Many2one('account.account', "Investment Accounting Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    supporting_documentation = fields.Binary("Supporting Documentation")

    origin_journal_id = fields.Many2one('account.journal','Origin Bank Account')
    destination_journal_id = fields.Many2one('account.journal','Destination Bank Account')

    patrimonial_account_id = fields.Many2one('account.account', "Patrimonial Account")
    investment_account_id = fields.Many2one('account.account', "Investment Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    honorary_account_id = fields.Many2one('account.account', "Honorary Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    liability_account_id = fields.Many2one('account.account', "Liability Account")

    trust_agreement_file = fields.Binary("Trustee Agreement")
    trust_agreement_file_name = fields.Char("Trust Agreement File Name")
    trust_office_file = fields.Binary("Trust Contract Official Letter")
    trust_office_file_name = fields.Char("Trust Office File Name")

    trust_id = fields.Many2one('agreement.trust','Trust')
    
    reason_rejection = fields.Text("Reason for Rejection")
    is_cancel_collaboration = fields.Boolean("Operation of cancel collaboration", default=False)


    @api.model
    def create(self, vals):
        res = super(RequestOpenBalanceInvestment, self).create(vals)
        if res and res.is_cancel_collaboration and res.type_of_operation != 'withdrawal_cancellation':
            raise ValidationError(_("Type of Operation must be 'Withdrawal Due to Cancellation' for this operation!"))
        if res and not res.is_cancel_collaboration and res.type_of_operation == 'withdrawal_cancellation':
            raise ValidationError(
                _("Can't create Operation with 'Withdrawal Due to Cancellation' Type of Operation manually!"))
        return res

    def write(self, vals):
        res = super(RequestOpenBalanceInvestment, self).write(vals)
        for rec in self:
            if rec.is_cancel_collaboration and rec.type_of_operation != 'withdrawal_cancellation':
                raise ValidationError(
                    _("Type of Operation must be 'Withdrawal Due to Cancellation' for this operation!"))
            if not rec.is_cancel_collaboration and rec.type_of_operation == 'withdrawal_cancellation':
                raise ValidationError(
                    _("Can't create Operation with 'Withdrawal Due to Cancellation' Type of Operation manually!"))
        return res

    @api.constrains('operation_number')
    def _check_operation_number(self):
        if self.operation_number and not self.operation_number.isnumeric():
            raise ValidationError(_('Operation Number must be Numeric.'))

    def reject_request(self):
        return {
            'name': 'Reason for Rejection',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'reason.rejection.open.bal',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def approve_investment(self):
        today = datetime.today().date()
        user = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        collaboration = False
        if self.balance_req_id and self.balance_req_id.bases_collaboration_id:
            collaboration = self.balance_req_id.bases_collaboration_id
        fund_type = False
        if collaboration and collaboration.fund_type_id:
            fund_type = collaboration.fund_type_id.id
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.investment.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_operation_number': self.operation_number,
                'default_agreement_number': self.agreement_number,
                'default_amount': self.opening_balance,
                'default_date': today,
                'default_employee_id': employee.id if employee else False,
                'default_fund_type': fund_type,
                'show_for_agreement':1,
                'default_bank_account_id' : self.origin_journal_id and self.origin_journal_id.id or False,
                'default_desti_bank_account_id' : self.destination_journal_id and self.destination_journal_id.id or False,
            }
        }


class Project(models.Model):
    _inherit = 'project.project'

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.number_agreement and self.env.context and self.env.context.get('from_agreement', True):
                name = rec.number_agreement
            result.append((rec.id, name))
        return result

class RequestOpenBalanceFinance(models.Model):

    _name = 'request.open.balance.finance'
    _description = "Request to Open Balance For Finanace"
    _rec_name = 'invoice'

    request_id = fields.Many2one('request.open.balance.invest', "Request")
    invoice = fields.Char("Invoice")
    operation_number = fields.Char("Operation Number")
    agreement_number = fields.Char("Agreement Number")
    bank_account_id = fields.Many2one('account.journal', "Bank and Origin Account")
    desti_bank_account_id = fields.Many2one('account.journal', "Destination Bank and Account")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary("Amount")
    dependency_id = fields.Many2one('dependency', "Dependency")
    sub_dependency_id = fields.Many2one('sub.dependency', "Subdependency")
    date = fields.Date("Application date")
    concept = fields.Text("Application Concept")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Applicant")
    unit_req_transfer_id = fields.Many2one('dependency', string="Unit requesting the transfer")
    date_required = fields.Date("Date Required")
    fund_type = fields.Many2one('fund.type', "Background")
    reason_rejection = fields.Text("Reason Rejection")
    state = fields.Selection([('draft', 'Draft'),
                              ('requested', 'Requested'),
                              ('rejected', 'Rejected'),
                              ('approved', 'Approved'),
                              ('sent', 'Sent'),
                              ('confirmed', 'Confirmed'),
                              ('done', 'Done'),
                              ('canceled', 'Canceled')], string="Status", default="draft")
    payment_ids = fields.Many2many('account.payment', 'rel_req_payment', 'payment_id', 'payment_request_rel_id',
                                  "Payments")
    payment_count = fields.Integer(compute="count_payment", string="Payments")

    @api.constrains('operation_number')
    def _check_operation_number(self):
        if self.operation_number and not self.operation_number.isnumeric():
            raise ValidationError(_('Operation Number must be Numeric.'))

    def open_payments(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        action['context'] = {}
        if self.payment_ids:
            action['domain'] = [('id', 'in', self.payment_ids.ids)]
        return action

    def count_payment(self):
        for rec in self:
            rec.payment_count = len(self.payment_ids)

    def reject_request(self):
        return {
            'name': 'Reason for Rejection',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'reason.rejection.open.bal',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def approve_finance(self):
        self.state = 'approved'

    def action_schedule_transfers(self):
        payment_obj = self.env['account.payment']
        today = datetime.today().date()
        data = {}
        for rec in self:
            if rec.state == 'approved' and rec.bank_account_id:
                bank_acc = rec.bank_account_id
                if bank_acc not in data.keys():
                    data.update({
                        bank_acc: [rec]
                    })
                else:
                    data.update({
                        bank_acc: data.get(bank_acc) + [rec]
                    })
        for acc, rec_list in data.items():
            dest_acc = {}
            for rec in rec_list:
                if rec.desti_bank_account_id:
                    dest_bank_acc = rec.desti_bank_account_id
                    if dest_bank_acc not in dest_acc.keys():
                        dest_acc.update({
                            dest_bank_acc: [rec]
                        })
                    else:
                        dest_acc.update({
                            dest_bank_acc: dest_acc.get(dest_bank_acc) + [rec]
                        })
            for dest_acc, rec_list in dest_acc.items():
                amt = 0
                for rec in rec_list:
                    amt += rec.amount
                dep_id = False
                sub_dep_id = False
                
                if rec_list:
                    dep_id = rec_list[0].dependency_id and rec_list[0].dependency_id.id or False
                    sub_dep_id = rec_list[0].sub_dependency_id and rec_list[0].sub_dependency_id.id or False  
                    
                payment = payment_obj.create({
                    'payment_type': 'transfer',
                    'amount': amt,
                    'journal_id': acc.id,
                    'destination_journal_id': dest_acc.id,
                    'payment_date': today,
                    'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                    'dependancy_id' : dep_id,
                    'sub_dependancy_id' : sub_dep_id,
                })
                if payment:
                    for rec in rec_list:
                        rec.payment_ids = [(4, payment.id)]
                        rec.state = 'sent'

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def post(self):
        res = super(AccountPayment, self).post()
        finance_req_obj = self.env['request.open.balance.finance']
        for payment in self:
            finance_reqs = finance_req_obj.search([('payment_ids', 'in', payment.id)])
            for fin_req in finance_reqs:
                fin_req.state = 'confirmed'
                if fin_req.request_id:
                    fin_req.request_id.state = 'done'
                    if fin_req.request_id.balance_req_id:
                        balance_req = fin_req.request_id.balance_req_id
                        balance_req.state = 'confirmed'
                        if balance_req.bases_collaboration_id:
                            if balance_req.type_of_operation == 'withdrawal_cancellation':
                                balance_req.bases_collaboration_id.available_bal = 0
                                balance_req.bases_collaboration_id.state = 'cancelled'
                            elif balance_req.type_of_operation == 'withdrawal':
                                balance_req.bases_collaboration_id.available_bal = 0
                                balance_req.bases_collaboration_id.state = 'cancelled'
                            elif balance_req.type_of_operation == 'retirement':
                                balance_req.create_payment_request = True
                            else:
                                balance_req.bases_collaboration_id.available_bal += fin_req.amount
        return res


