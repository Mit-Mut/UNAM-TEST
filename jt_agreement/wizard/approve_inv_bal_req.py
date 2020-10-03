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
    _name = 'approve.investment.bal.req'
    _description = "Approve Investment Balance request"

    invoice = fields.Char("Invoice")
    operation_number = fields.Integer("Operation Number")
    agreement_number_id = fields.Many2one('project.project', "Agreement Number")
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

    def approve(self):
        request = self.env['request.open.balance'].browse(self.env.context.get('active_id'))
        if request:
            request.state = 'confirmed'
            self.env['request.open.balance.finance'].create(
                {
                    'invoice': self.invoice,
                    'operation_number': self.operation_number,
                    'agreement_number_id': self.agreement_number_id.id if self.agreement_number_id else False,
                    'bank_account_id': self.bank_account_id.id if self.bank_account_id else False,
                    'desti_bank_account_id': self.desti_bank_account_id.id if self.desti_bank_account_id else False,
                    'amount': self.amount,
                    'date': self.date,
                    'concept': self.concept,
                    'employee_id': self.employee_id.id if self.employee_id else False,
                    'date_required': self.date_required,
                    'fund_type': self.fund_type.id if self.fund_type else False,
                    'request_id': request.id,
                    'state': 'requested'
                }
            )



