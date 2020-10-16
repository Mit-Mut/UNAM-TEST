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
    date = fields.Date("Application date")
    concept = fields.Text("Application Concept")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Applicant")
    employee_id = fields.Many2one('hr.employee', string="Unit requesting the transfer")
    date_required = fields.Date("Date Required")
    fund_type = fields.Many2one('fund.type', "Background")

    bonds_id = fields.Many2one('investment.bonds','Bonds')
    cetes_id = fields.Many2one('investment.cetes','cetes')
    udibonos_id = fields.Many2one('investment.udibonos','Udibonos')
    will_pay_id = fields.Many2one('investment.will.pay','Will Pay')
    purchase_sale_security_id = fields.Many2one('purchase.sale.security','Purchase Sale Security')
    
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
                'bonds_id': self.bonds_id and self.bonds_id.id or False,
                'cetes_id': self.cetes_id and self.cetes_id.id or False,
                'udibonos_id': self.udibonos_id and self.udibonos_id.id or False,
                'will_pay_id': self.will_pay_id and self.will_pay_id.id or False,
                'purchase_sale_security_id' : self.purchase_sale_security_id and self.purchase_sale_security_id.id or False,
                'state': 'requested'
            }
        )
        if self.bonds_id:
            self.bonds_id.state = 'confirmed'
        if self.cetes_id:
            self.cetes_id.state = 'confirmed'
        if self.udibonos_id:
            self.udibonos_id.state = 'confirmed'
        if self.will_pay_id:
            self.will_pay_id.state = 'confirmed'
        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.state = 'confirmed'

