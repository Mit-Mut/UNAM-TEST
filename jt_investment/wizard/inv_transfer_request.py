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
from odoo.exceptions import UserError,ValidationError,UserError

class InvTransferRequest(models.TransientModel):
    _name = 'inv.transfer.request'
    _description = "Inv Transfer Request"

    bank_account_id = fields.Many2one('account.journal', "Bank and Origin Account")
    desti_bank_account_id = fields.Many2one('account.journal', "Destination Bank and Account")
    amount = fields.Float("Amount To Transfer")
    date = fields.Date("Application date")
    concept = fields.Text("Application Concept")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Applicant")
    line_ids = fields.One2many('inv.transfer.request.line','wizard_id')
        
    def approve(self):
        line_amount = sum(x.amount_to_transfer for x in self.line_ids.filtered(lambda a:a.check))
        if line_amount != self.amount:
            raise UserError(_('Sum of amount in line is not equal to header amount'))
        opt_lines = []
        for line in self.line_ids.filtered(lambda a:a.check):
            opt_lines.append((0,0,{'investment_fund_id':line.investment_fund_id and line.investment_fund_id.id or False,
                                   'base_collabaration_id' : line.base_collabaration_id and line.base_collabaration_id.id or False,
                                   'agreement_number': line.agreement_number,
                                   'amount_to_transfer' : line.amount_to_transfer,
                                   'amount' : line.amount,
                                   'opt_line_ids' : line.opt_line_ids,
                                   }))
            for opt_line in line.opt_line_ids:
                opt_line.is_request_generated = True
        
        for line in self.line_ids.filtered(lambda a:a.check):
            self.env['investment.operation'].create({
                'investment_id':self.env.context.get('active_id',0),
                'agreement_number': line.agreement_number,
                'bank_account_id' :  self.bank_account_id.id if self.bank_account_id else False,
                'desti_bank_account_id' : self.desti_bank_account_id.id if self.desti_bank_account_id else False,
                'amount' : line.amount_to_transfer,
                'investment_fund_id' : line.investment_fund_id and line.investment_fund_id.id or False,
                'type_of_operation':'retirement',
                'state' : 'done',
                })    
        self.env['request.open.balance.finance'].create(
            {
                'bank_account_id': self.bank_account_id.id if self.bank_account_id else False,
                'desti_bank_account_id': self.desti_bank_account_id.id if self.desti_bank_account_id else False,
                'amount': self.amount,
                'date': self.date,
                'concept': self.concept,
                'state': 'requested',
                'line_opt_ids' : opt_lines,
                'from_opt_transfer' : True
            }
        )
            
class InvTransferRequestLine(models.TransientModel):
    _name = 'inv.transfer.request.line'
    _description = "Inv Transfer Request Line"

    wizard_id = fields.Many2one('inv.transfer.request')
    investment_fund_id = fields.Many2one('investment.funds','Fund')
    base_collabaration_id = fields.Many2one('bases.collaboration','Name Of Agreements')
    agreement_number = fields.Char("Agreement Number")
    amount = fields.Float("Amount")
    amount_to_transfer = fields.Float("Amount To Transfer")
    check = fields.Boolean('Transfer')
    opt_line_ids = fields.Many2many('investment.operation','rel_investment_operation_wizard_line','opt_id','line_id')
    