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
    _inherit = 'approve.investment.bal.req'
    
    investment_id = fields.Many2one('investment.investment','First Number:')

    journal_id = fields.Many2one(related='investment_id.journal_id')
    source_ids = fields.Many2many('account.journal','rel_journal_inv_src_approve','journal_id','opt_id',compute="get_journal_ids")
    dest_ids = fields.Many2many('account.journal','rel_journal_inv_dest_approve','journal_id','opt_id',compute="get_journal_ids")

    @api.depends('journal_id','type_of_operation','investment_id.journal_id','investment_id')
    def get_journal_ids(self):
        for rec in self:
            if rec.type_of_operation in ('open_bal','increase','increase_by_closing') :
                rec.source_ids = [(6,0,rec.journal_id.ids)]
            else:
                rec.source_ids = [(6,0,self.env['account.journal'].search([('type','=','bank')]).ids)]

            if rec.type_of_operation in ('retirement','withdrawal','withdrawal_cancellation','withdrawal_closure'):
                rec.dest_ids = [(6,0,rec.journal_id.ids)]
            else:
                rec.dest_ids = [(6,0,self.env['account.journal'].search([('type','=','bank')]).ids)]

    def get_open_balance_vals(self,request):
        vals = super(ApproveInvestmentBalReq,self).get_open_balance_vals(request)
        vals.update({'investment_link_id':self.investment_id and self.investment_id.id or False})
        return vals
        
    def get_investment_line(self,request):
        vals = {
                'investment_id':self.investment_id and self.investment_id.id or False,
                'invoice' : self.invoice,
                'operation_number' : self.operation_number,
                'agreement_number' : self.agreement_number,
                'amount' : self.amount,
                'dependency_id' : self.dependency_id and self.dependency_id.id or False,
                'sub_dependency_id' : self.sub_dependency_id and self.sub_dependency_id.id or False,
                'user_id' : self.user_id and self.user_id.id or False,
                'unit_req_transfer_id' : self.unit_req_transfer_id and self.unit_req_transfer_id.id or False,
                'date_required' : self.date_required,
                'fund_type' : self.fund_type and self.fund_type.id or False,
                'agreement_type_id':self.agreement_type_id and self.agreement_type_id.id or False,
                'base_collabaration_id' : self.base_collabaration_id and self.base_collabaration_id.id or False,
                'investment_fund_id': self.investment_fund_id and self.investment_fund_id.id or False,
                'inc_id':request.id,
                'type_of_operation' : self.type_of_operation,
                'origin_resource_id' : self.origin_resource_id and self.origin_resource_id.id or False,
                'bank_account_id' : self.bank_account_id and self.bank_account_id.id or False,
                'desti_bank_account_id' : self.desti_bank_account_id and self.desti_bank_account_id.id or False,
                'line_state' : 'requested',
                'record_type' : 'automatically'
                }
        return vals
    
    def create_investment_line(self,request):
        vals = self.get_investment_line(request)
        self.env['investment.operation'].create(vals)
        
    def approve(self):
        res = super(ApproveInvestmentBalReq,self).approve()
        request = self.env['request.open.balance.invest'].browse(self.env.context.get('active_id'))
        if request:
            if self.investment_id:
                self.create_investment_line(request)
        return res