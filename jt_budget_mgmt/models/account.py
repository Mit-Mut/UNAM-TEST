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
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class AccountMove(models.Model):

    _inherit = 'account.move'

    budget_id = fields.Many2one('expenditure.budget')
    adequacy_id = fields.Many2one('adequacies')
    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')

    def action_validate_budget(self):
        self.ensure_one()
        str_msg = "Budgetary Insufficiency For Program Code\n\n"
        is_check = False
        budget_msg = "Budget sufficiency"
        for line in self.invoice_line_ids:
            total_available_budget = 0
            if line.program_code_id:
                budget_line = self.env['expenditure.budget.line']
                budget_lines = self.env['expenditure.budget.line'].sudo().search(
                [('program_code_id', '=', line.program_code_id.id),
                 ('expenditure_budget_id', '=', line.program_code_id.budget_id.id),
                 ('expenditure_budget_id.state', '=', 'validate')])
                if self.invoice_date and budget_lines:
                    b_month = self.invoice_date.month
                    for b_line in budget_lines:
                        if b_line.start_date:
                            b_s_month = b_line.start_date.month
                            if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                budget_line += b_line
                            elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                budget_line += b_line
                            elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                                budget_line += b_line
                            elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                budget_line += b_line
                    
                    total_available_budget = sum(x.available for x in budget_line)
            if total_available_budget < line.price_total:
                is_check = True
                program_name = ''
                if line.program_code_id:
                    program_name = line.program_code_id.program_code
                    str_msg += program_name+" Available Amount Is "+str(total_available_budget)+"\n\n"
                    
        if is_check:
            return {
                        'name': _('Budgetary Insufficiency'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'budget.insufficien.wiz',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context':{'default_msg':str_msg,'default_move_id':self.id,'default_is_budget_suf':False}
                    }
        else:
            return {
                        'name': _('Budget sufficiency'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'budget.insufficien.wiz',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context':{'default_msg':budget_msg,'default_move_id':self.id,'default_is_budget_suf':True}
                    }
            
    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
    
    def action_cancel_budget(self):
        self.ensure_one()
        self.payment_state = 'cancel'

    def create_journal_line(self):
        #self.line_ids = False
        #payble_line = 
        self.line_ids = [(0, 0, {
                                     'account_id': self.journal_id.default_credit_account_id.id,
                                     'coa_conac_id': self.journal_id.conac_credit_account_id.id,
                                     'credit': self.amount_total, 
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 }), 
                        (0, 0, {
                                     'account_id': self.journal_id.default_debit_account_id.id,
                                     'coa_conac_id': self.journal_id.conac_debit_account_id.id,
                                     'debit': self.amount_total,
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : True
                                 })]
          
        self.conac_move = True
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    budget_id = fields.Many2one('expenditure.budget')
    adequacy_id = fields.Many2one('adequacies')
    program_code_id = fields.Many2one('program.code')
    
    @api.onchange('program_code_id')
    def onchange_program_code(self):
        if self.program_code_id and self.program_code_id.item_id and self.program_code_id.item_id.unam_account_id:
            self.account_id = self.program_code_id.item_id.unam_account_id.id
            

    @api.model
    def _get_default_tax_account(self, repartition_line):
        account = super(AccountMoveLine,self)._get_default_tax_account(repartition_line)
        if self.program_code_id and self.program_code_id.item_id and self.program_code_id.item_id.unam_account_id:
            return self.program_code_id.item_id.unam_account_id
        return account
            