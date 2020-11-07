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

class InvestmentFunds(models.Model):

    _name = 'investment.funds'
    _description = "Investment Funds"
    _rec_name = 'fund_id'
     
    fund_id = fields.Many2one('agreement.fund','Fund Name')
    fund_key = fields.Char(related='fund_id.fund_key',string="Fund Code")
    
    fund_type_id = fields.Many2one('fund.type','Type of Fund')
    type_of_agreement_id = fields.Many2one('agreement.agreement.type','Type of Agreement')
    bases_collaboration_id = fields.Many2one('bases.collaboration','Name of Agreement')
    is_fund = fields.Boolean(default=False,string="Fund")
    state = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                               ('rejected', 'Rejected'),
                               ('approved', 'Approved'),
                               ('confirmed', 'Confirmed'),
                              ('done', 'Done'),
                               ('canceled', 'Canceled')], string="Status", default="draft")


    fund_request_date = fields.Date('Request')
    dependency_id = fields.Many2one('dependency', "Dependency")
    subdependency_id = fields.Many2one('sub.dependency', "Sub Dependency")
    dependency_holder = fields.Char("Dependency Holder")
    responsible_user_id = fields.Many2one('res.users',string='Responsible')
    type_of_resource = fields.Char("Type Of Resource")

    journal_id = fields.Many2one('account.journal','Bank')
    bank_account_id = fields.Many2one(related='journal_id.bank_account_id',string="Account Number")
    
    request_office = fields.Char("Request Office")
    permanent_instructions =fields.Text("Permanent Instructions")
    fund_observation = fields.Text("Observations")
    
    contract_id = fields.Many2one('investment.contract','Contract')

    request_date = fields.Date("Request Date")
    trade_number = fields.Char("Trade Number")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    opening_balance = fields.Monetary("Opening Amount")
    observations = fields.Text("Observations")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id,
                              string="Requesting User")
    
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    cbc_format = fields.Binary("CBC Format")
    cbc_shipping_office = fields.Binary("CBC Shipping Office")
    liability_account_id = fields.Many2one('account.account', "Liability Accounting Account")
    investment_account_id = fields.Many2one('account.account', "Investment Accounting Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    supporting_documentation = fields.Binary("Supporting Documentation")

    type_of_investment = fields.Selection([('productive_account','Productive Account'),
                                           ('securities','Securities'),('money_market','Money Market')
                                           ],string="Type Of Investment")
    
    type_of_financial_products = fields.Selection([
                                           ('CETES','CETES'),('UDIBONOS','UDIBONOS'),
                                           ('BondsNotes','BondsNotes'),('Promissory','Promissory'),
                                           ],string="Type Of Financial Products")

    
    purchase_sale_ids = fields.One2many('purchase.sale.security','investment_fund_id')
    cetes_ids = fields.One2many('investment.cetes','investment_fund_id')
    udibonos_ids = fields.One2many('investment.udibonos','investment_fund_id')
    bonds_ids = fields.One2many('investment.bonds','investment_fund_id')
    will_pay_ids = fields.One2many('investment.will.pay','investment_fund_id')
    productive_ids = fields.One2many('investment.investment','investment_fund_id')

    request_finance_ids = fields.One2many(
        'request.open.balance.finance', 'investment_fund_id')

    def approve_investment(self):
        today = datetime.today().date()
        user = self.env.user
        employee = self.env['hr.employee'].search(
            [('user_id', '=', user.id)], limit=1)
        fund_type = False
        if self.contract_id and self.contract_id.fund_id:
            fund_type = self.contract_id.fund_id.id
        
        amount = 0
        
        amount += sum(x.amount for x in self.purchase_sale_ids)
        amount += sum(x.amount_invest for x in self.cetes_ids)
        amount += sum(x.amount_invest for x in self.udibonos_ids)
        amount += sum(x.amount_invest for x in self.bonds_ids)
        amount += sum(x.amount_invest for x in self.will_pay_ids)
        amount += sum(x.amount_to_invest for x in self.productive_ids)
        
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.money.market.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_amount': amount,
                'default_date': today,
                'default_employee_id': employee.id if employee else False,
                'default_investment_fund_id': self.id,
                'default_fund_type': fund_type,
                'default_bank_account_id' : self.journal_id and self.journal_id.id or False,
                'show_for_supplier_payment': 1,
            }
        }

    def action_requested(self):
        self.state = 'requested'
        for rec in self.purchase_sale_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False
            rec.action_requested()
        for rec in self.cetes_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False            
            rec.action_requested()
        for rec in self.udibonos_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False            
            rec.action_requested()
        for rec in self.bonds_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False            
            rec.action_requested()
        for rec in self.will_pay_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False            
            rec.action_requested()
        for rec in self.productive_ids.filtered(lambda x:x.state != 'requested'):
            rec.dependency_id = self.dependency_id and self.dependency_id.id or False
            rec.sub_dependency_id = self.subdependency_id and self.subdependency_id.id or False            
            rec.action_requested()

    def action_approved(self):
        self.state = 'approved'
        for rec in self.purchase_sale_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()
        for rec in self.cetes_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()
        for rec in self.udibonos_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()
        for rec in self.bonds_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()
        for rec in self.will_pay_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()
        for rec in self.productive_ids.filtered(lambda x:x.state != 'approved'):
            rec.action_approved()

    def action_confirmed(self):
        self.state = 'confirmed'
        for rec in self.purchase_sale_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()
        for rec in self.cetes_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()
        for rec in self.udibonos_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()
        for rec in self.bonds_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()
        for rec in self.will_pay_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()
        for rec in self.productive_ids.filtered(lambda x:x.state != 'confirmed'):
            rec.action_confirmed()


    def action_canceled(self):
        self.state = 'canceled'
        for rec in self.purchase_sale_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
        for rec in self.cetes_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
        for rec in self.udibonos_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
        for rec in self.bonds_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
        for rec in self.will_pay_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
        for rec in self.productive_ids.filtered(lambda x:x.state != 'canceled'):
            rec.action_canceled()
    
    
    