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

    liability_account_id = fields.Many2one('account.account', "Liability Accounting Account")
    investment_account_id = fields.Many2one('account.account', "Investment Accounting Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    state = fields.Selection([('draft', 'Draft'),
                               ('valid', 'Valid')], "Status", default='draft')
    total_operations = fields.Integer("Operations", compute="compute_operations")

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

    def compute_operations(self):
        operation_obj = self.env['request.open.balance']
        for rec in self:
            if rec.name:
                operations = operation_obj.search([('name', '=', self.name)])
                rec.total_operations = len(operations)

    # def action_operations(self):
    #     operation_obj = self.env['request.open.balance']
    #     operations = operation_obj.search([('bases_collaboration_id', '=', self.id)])
        # print ("dfdsfsdfsd", self.env.ref('jt_agreement.action_req_open_balance').read()[0])
        # context = {'default_bases_collaboration_id': self.id,
        #             'default_apply_to_basis_collaboration': True,
        #             'default_opening_balance': self.opening_bal,
        #             'default_cbc_format': self.cbc_format,
        #             'default_cbc_shipping_office': self.cbc_shipping_office,
        #             'default_name': self.name,
        #             'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
        #             else False,
        #             'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
        #             else False,
        #             'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
        #             else False,
        #             'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
        #             else False
        #             }
        # return self.env.ref('jt_agreement.action_req_open_balance').read()[0]
        # if operations:
        #     return {
        #         'name': 'Operations',
        #         # 'view_type': 'form',
        #         # 'view_id': self.env.ref('jt_agreement.view_req_open_balance_tree').id,
        #         'view_mode': 'tree,form',
        #         'view_ids': [self.env.ref("jt_agreement.view_req_open_balance_tree").id,
        #                       self.env.ref("jt_agreement.view_req_open_balance_form").id],
        #         'res_model': 'request.open.balance',
        #         'domain': [('bases_collaboration_id', '=', self.id)],
        #         'type': 'ir.actions.act_window',
        #         'context': {'default_bases_collaboration_id': self.id,
        #                     'default_apply_to_basis_collaboration': True,
        #                     'default_opening_balance': self.opening_bal,
        #                     'default_cbc_format': self.cbc_format,
        #                     'default_cbc_shipping_office': self.cbc_shipping_office,
        #                     'default_name': self.name,
        #                     'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
        #                             else False,
        #                     'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
        #                             else False,
        #                     'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
        #                     else False,
        #                     'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
        #                     else False
        #                     }
        #     }
        # else:
        #     return {
        #         'name': 'Operations',
        #         # 'view_type': 'form',
        #         'view_mode': 'form',
        #         'view_id': self.env.ref('jt_agreement.view_req_open_balance_form').id,
        #         'view_ids': [self.env.ref("jt_agreement.view_req_open_balance_form").id],
        #         'res_model': 'request.open.balance',
        #         'domain': [('bases_collaboration_id', '=', self.id)],
        #         'type': 'ir.actions.act_window',
        #         'context': {'default_bases_collaboration_id': self.id,
        #                     'default_apply_to_basis_collaboration': True,
        #                     'default_opening_balance': self.opening_bal,
        #                     'default_name': self.name,
        #                     'default_cbc_format': self.cbc_format,
        #                     'default_cbc_shipping_office': self.cbc_shipping_office,
        #                     'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
        #                     else False,
        #                     'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
        #                     else False,
        #                     'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
        #                     else False,
        #                     'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
        #                     else False
        #                     }
        #     }

    def confirm(self):
        self.state = 'valid'

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

class RequestOpenBalance(models.Model):

    _name = 'request.open.balance'
    _description = "Request to Open Balance"
    _rec_name = 'bases_collaboration_id'

    name = fields.Char("Name")
    bases_collaboration_id = fields.Many2one('bases.collaboration', "Bases Collaboration")
    operation_number = fields.Integer("Operation Number")
    opening_bal = fields.Boolean('Opening Balance')
    increase = fields.Boolean('Increase')
    retirement = fields.Boolean('Retirement')
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

    reason_rejection = fields.Text("Reason for Rejection")
    passed_from_investment = fields.Boolean("Passed From Investment")

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

    def request(self):
        self.state = 'requested'

    def approve_investment(self):
        self.state = 'confirmed'
        self.passed_from_investment = True

    def approve_finance(self):
        self.state = 'approved'
