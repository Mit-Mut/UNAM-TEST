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

    def show_conac_move(self):
        for record in self:
            record.conac_line_ids = record.line_ids.filtered(lambda x:x.conac_move)
             
    budget_id = fields.Many2one('expenditure.budget')
    adequacy_id = fields.Many2one('adequacies')
    dependancy_id = fields.Many2one('dependency', string='Dependency')
    sub_dependancy_id = fields.Many2one('sub.dependency', 'Sub Dependency')
    payment_place_id = fields.Many2one('payment.place', 'Name')
    conac_line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',
                                     compute="show_conac_move")


    @api.onchange('dependancy_id','sub_dependancy_id')        
    def onchange_dep_sub_dep(self):
        if self.dependancy_id and self.sub_dependancy_id:
            payment_place_id = self.env['payment.place'].search([('dependancy_id','=',self.dependancy_id.id),('sub_dependancy_id','=',self.sub_dependancy_id.id)])
            if payment_place_id:
                self.payment_place_id = payment_place_id.id
            else:
                self.payment_place_id = False
        else:
            self.payment_place_id = False
            
    def action_register(self):
        for move in self:
            invoice_lines = move.invoice_line_ids.filtered(lambda x:not x.program_code_id)
            if invoice_lines:
                raise ValidationError("Please add program code into invoice lines")
        return super(AccountMove,self).action_register()

        
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
                
#                 invoice_lines = self.env['account.move.line']
#                 invoice_lines_exist = self.env['account.move.line'].search([('program_code_id', '=', line.program_code_id.id),
#                                                                             ('move_id.payment_state', '=', 'approved_payment')
#                                                                            ])
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
#                 if self.invoice_date and invoice_lines_exist: 
#                     invoice_month = self.invoice_date.month
#                     for b_line in invoice_lines_exist:
#                         if b_line.move_id.invoice_date:
#                             b_s_month = b_line.move_id.invoice_date.month
#                             if invoice_month in (1, 2, 3) and b_s_month in (1, 2, 3):
#                                 invoice_lines += b_line
#                             elif invoice_month in (4, 5, 6) and b_s_month in (4, 5, 6):
#                                 invoice_lines += b_line
#                             elif invoice_month in (7, 8, 9) and b_s_month in (7, 8, 8):
#                                 invoice_lines += b_line
#                             elif invoice_month in (10, 11, 12) and b_s_month in (10, 11, 12):
#                                 invoice_lines += b_line
#                     total_assign_budget = sum(x.price_total for x in invoice_lines)
#                     total_available_budget = total_available_budget - total_assign_budget
                    
                                    
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

    def add_budget_available_amount(self): 
        for line in self.invoice_line_ids:
            if line.budget_line_link_ids:
                for b_line in line.budget_line_link_ids:
                    if b_line.budget_line_id:
                        b_line.budget_line_id.available += b_line.amount
                line.budget_line_link_ids.unlink()
                   
    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
        self.button_draft()
        conac_move = self.line_ids.filtered(lambda x:x.conac_move)
        conac_move.sudo().unlink()
        for line in self.line_ids:
            line.coa_conac_id = False 
        
        self.add_budget_available_amount()
    
    def cancel_payment_revers_entry(self):
        revers_list = []
        for line in self.line_ids:
            revers_list.append((0, 0, {
                                     'account_id': line.account_id.id,
                                     'coa_conac_id': line.coa_conac_id and line.coa_conac_id.id or False,
                                     'credit': line.debit,
                                     'debit':line.credit, 
                                     'exclude_from_invoice_tab': True,
                                     'conac_move' : line.conac_move,
                                     'name' : 'Reversa',
                                     'currency_id' : line.currency_id and line.currency_id.id or False,
                                     'amount_currency' : line.amount_currency,
                                 }))
        self.line_ids = revers_list 

    def button_cancel(self):
        for record in self:
            if record.is_payment_request or record.is_payroll_payment_request:
                if record.payment_state == 'cancel':
                    record.cancel_payment_revers_entry()
                    record.add_budget_available_amount()
        return super(AccountMove,self).button_cancel()
    
    def action_cancel_budget(self):
        self.ensure_one()
        self.payment_state = 'cancel'
        self.button_cancel()
        
    def action_reschedule(self):
        res = super(AccountMove,self).action_reschedule()
        for move in self:
            move.add_budget_available_amount()
        return res
              
    def create_journal_line_for_approved_payment(self):
        if self.journal_id and (not self.journal_id.default_credit_account_id or not \
            self.journal_id.default_debit_account_id):
            raise ValidationError(_("Configure Default Debit and Credit Account in %s!" % \
                                    self.journal_id.name))
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
    budget_line_link_ids = fields.One2many('budget.line.move.line.links','account_move_line_id')
    
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

class BudgetLineMoveLinelinks(models.Model):
    
    _name = 'budget.line.move.line.links'
    
    budget_line_id = fields.Many2one('expenditure.budget.line','Budget Line')
    account_move_line_id = fields.Many2one('account.move.line','Budget Line')
    amount = fields.Float('Amount')
       
    
           