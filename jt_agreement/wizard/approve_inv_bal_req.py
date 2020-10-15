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

    invoice = fields.Char("Folio")
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
    unit_req_transfer_id = fields.Many2one('dependency', string="Unit requesting the transfer")
    date_required = fields.Date("Date Required")
    fund_type = fields.Many2one('fund.type', "Fondo")

    @api.model
    def default_get(self, fields):
        res = super(ApproveInvestmentBalReq, self).default_get(fields)
        name = self.env['ir.sequence'].next_by_code('approve.bal.invest')
        res.update({'invoice': name})
        return res

    def approve(self):
        request = self.env['request.open.balance.invest'].browse(self.env.context.get('active_id'))
        if request:
            request.state = 'confirmed'
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
                    'unit_req_transfer_id': self.unit_req_transfer_id.id if self.unit_req_transfer_id else False,
                    'date_required': self.date_required,
                    'fund_type': self.fund_type.id if self.fund_type else False,
                    'request_id': request.id,
                    'state': 'requested'
                }
            )
            if request.balance_req_id:
                request.balance_req_id.state = 'approved'

class Dependency(models.Model):

    _inherit = 'dependency'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if 'bal_user_id' in self._context:
            user = self.env['res.users'].browse(self._context.get('bal_user_id'))
            employees = self.env['hr.employee'].search([('user_id', '=', user.id)])
            dependency_ids = []
            for emp in employees:
                if emp.dependancy_id:
                    dependency_ids.append(emp.dependancy_id.id)
            args = [['id', 'in', dependency_ids]]
        res = super(Dependency, self).name_search(name, args=args, operator=operator, limit=limit)
        return res

