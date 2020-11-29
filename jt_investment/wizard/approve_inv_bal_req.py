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

class ApproveInvestmentBalReq(models.TransientModel):
    _name = 'approve.money.market.bal.req'
    _description = "Approve Money Market Balance request"

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
    employee_id = fields.Many2one('hr.employee', string="Unit requesting the transfer")
    date_required = fields.Date("Date Required")
    fund_type = fields.Many2one('fund.type', "Type Of Funds")
    fund_id = fields.Many2one('agreement.fund','Funds')
    
    bonds_id = fields.Many2one('investment.bonds','Bonds')
    cetes_id = fields.Many2one('investment.cetes','cetes')
    udibonos_id = fields.Many2one('investment.udibonos','Udibonos')
    will_pay_id = fields.Many2one('investment.will.pay','Will Pay')
    purchase_sale_security_id = fields.Many2one('purchase.sale.security','Purchase Sale Security')
    investment_id = fields.Many2one('investment.investment','Investment')
    investment_fund_id = fields.Many2one('investment.funds','Investment Funds')
    distribution_id = fields.Many2one('distribution.of.income','Distribution Income')
    
    agreement_type = fields.Many2one('agreement.agreement.type',string="Agreement Type")
    base_collabaration_id = fields.Many2one('bases.collaboration','Name Of Agreements')
    amount_type = fields.Selection([('increment','Increment'),('withdrawal','Withdrawal')])
    
    def approve(self):
        self.env['request.open.balance.finance'].create(
            {
                'invoice': self.invoice,
                'operation_number': self.operation_number,
                'agreement_number': self.agreement_number,
                'bank_account_id': self.bank_account_id.id if self.bank_account_id else False,
                'desti_bank_account_id': self.desti_bank_account_id.id if self.desti_bank_account_id else False,
                'amount': self.amount,
                'date': self.date,
                'concept': self.concept,
                'fund_type': self.fund_type.id if self.fund_type else False,
                'agreement_type_id' : self.agreement_type and self.agreement_type.id or False,
                'base_collabaration_id' : self.base_collabaration_id and self.base_collabaration_id.id or False,
                'dependency_id' : self.dependency_id and self.dependency_id.id or False,
                'sub_dependency_id' : self.sub_dependency_id and self.sub_dependency_id.id or False,
                'bonds_id': self.bonds_id and self.bonds_id.id or False,
                'cetes_id': self.cetes_id and self.cetes_id.id or False,
                'udibonos_id': self.udibonos_id and self.udibonos_id.id or False,
                'will_pay_id': self.will_pay_id and self.will_pay_id.id or False,
                'investment_id' : self.investment_id and self.investment_id.id or False,
                'distribution_id' : self.distribution_id and self.distribution_id.id or False,
                'purchase_sale_security_id' : self.purchase_sale_security_id and self.purchase_sale_security_id.id or False,
                'state': 'requested',
                'fund_id' : self.fund_id and self.fund_id.id or False,
                'amount_type' : self.amount_type,
            }
        )
        if self.bonds_id:
            self.bonds_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.bonds_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            if self.env.context and not self.env.context.get('edit_amount_field'):
                self.bonds_id.concept = self.concept 
            self.bonds_id.action_requested()
            
        if self.cetes_id:
            self.cetes_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.cetes_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            if self.env.context and not self.env.context.get('edit_amount_field'):
                self.cetes_id.concept = self.concept 
            
            self.cetes_id.action_requested()
        if self.udibonos_id:
            if self.env.context and not self.env.context.get('edit_amount_field'):
                self.udibonos_id.concept = self.concept 
            
            self.udibonos_id.action_requested()
            self.udibonos_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.udibonos_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            
        if self.will_pay_id:
            self.will_pay_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.will_pay_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            if self.env.context and not self.env.context.get('edit_amount_field'):
                self.will_pay_id.concept = self.concept 
            self.will_pay_id.action_requested()
            
        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.purchase_sale_security_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            self.purchase_sale_security_id.journal_id = self.bank_account_id and self.bank_account_id.id or False
            if self.env.context and not self.env.context.get('edit_amount_field'):
                self.purchase_sale_security_id.concept = self.concept 
            self.purchase_sale_security_id.action_requested()
            
        if self.investment_id:
            self.investment_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.investment_id.sub_dependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            self.investment_id.action_requested()
        if self.investment_fund_id:
            self.investment_fund_id.dependency_id = self.dependency_id and self.dependency_id.id or False
            self.investment_fund_id.subdependency_id = self.sub_dependency_id and self.sub_dependency_id.id or False
            self.investment_fund_id.journal_id = self.bank_account_id and self.bank_account_id.id or False
            self.investment_fund_id.action_requested()
            
        if self.distribution_id:
            self.distribution_id.action_requested()
            
