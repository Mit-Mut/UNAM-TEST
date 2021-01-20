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
from odoo import models, fields
from datetime import datetime

class BudegtInsufficiencWiz(models.TransientModel):

    _name = 'budget.insufficien.wiz'
    _description = 'Budgetary Insufficienc'

    msg = fields.Text('Message')
    is_budget_suf = fields.Boolean(default=False)
    move_id = fields.Many2one('account.move','Move')
    move_ids = fields.Many2many('account.move', 'rel_wizard_budget_move', 'move_id', 'rel_wiz_move_id')
    
    def action_ok(self):
        move_str_msg_dict = self._context.get('move_str_msg_dict')
        if self.move_ids and not self.move_id:
            for move in self.move_ids:
                move.payment_state = 'rejected'
                move.reason_rejection = move_str_msg_dict.get(str(move.id))
        else:
            self.move_id.payment_state = 'rejected'
            self.move_id.reason_rejection = self.msg
        
    def decrease_available_amount(self):
        for line in self.move_id.invoice_line_ids:
            budget_line_links = []
            if line.program_code_id and line.price_total != 0:
                amount =  0
                if line.debit:
                    amount = line.debit + line.tax_price_cr
                else: 
                    amount = line.credit + line.tax_price_cr
                
                control_amount = 0
                if line.debit:
                    control_amount = line.debit + line.tax_price_cr
                else: 
                    control_amount = line.credit + line.tax_price_cr
                
                budget_lines = self.env['expenditure.budget.line'].sudo().search(
                [('program_code_id', '=', line.program_code_id.id),
                 ('expenditure_budget_id', '=', line.program_code_id.budget_id.id),
                 ('expenditure_budget_id.state', '=', 'validate')])
                
                if self.move_id.invoice_date and budget_lines:
                    b_month = self.move_id.invoice_date.month
                    for b_line in budget_lines:
                        control_assing_line = self.env['control.assigned.amounts.lines'].search([('program_code_id','=',line.program_code_id.id),('assigned_amount_id.budget_id','=',b_line.expenditure_budget_id.id),('assigned_amount_id.state','=','validated')])
                        if b_line.start_date:
                            b_s_month = b_line.start_date.month
                            if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                control_assing_linefilter = control_assing_line.filtered(lambda x:x.start_date.month in (1,2,3))
                                if control_assing_linefilter:
                                    control_assing_linefilter[0].available -= control_amount
                                    control_amount=0  
                                
                                if b_line.available >= amount:
                                    b_line.available -= amount
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':amount}))
                                    break
                                else:
                                    b_line.available = 0
                                    amount -= b_line.available
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':b_line.available}))
                                    
                            elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                control_assing_linefilter = control_assing_line.filtered(lambda x:x.start_date.month in (4,5,6))
                                if control_assing_linefilter:
                                    control_assing_linefilter[0].available -= control_amount  
                                    control_amount = 0
                                    
                                if b_line.available >= amount:
                                    b_line.available -= amount
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':amount}))
                                    break
                                else:
                                    b_line.available = 0
                                    amount -= b_line.available 
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':b_line.available}))
                                    
                            elif b_month in (7, 8, 9) and b_s_month in (7, 8, 9):
                                control_assing_linefilter = control_assing_line.filtered(lambda x:x.start_date.month in (7,8,9))
                                if control_assing_linefilter:
                                    control_assing_linefilter[0].available -= control_amount  
                                control_amount = 0
                                
                                if b_line.available >= amount:
                                    b_line.available -= amount
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':amount}))
                                    break
                                else:
                                    b_line.available = 0
                                    amount -= b_line.available 
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':b_line.available}))
                                    
                            elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                control_assing_linefilter = control_assing_line.filtered(lambda x:x.start_date.month in (10,11,12))
                                if control_assing_linefilter:
                                    control_assing_linefilter[0].available -= control_amount  
                                    control_amount = 0
                                    
                                if b_line.available >= amount:
                                    b_line.available -= amount
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':amount}))
                                    break
                                else:
                                    b_line.available = 0
                                    amount -= b_line.available 
                                    budget_line_links.append((0,0,{'budget_line_id':b_line.id,'account_move_line_id':line.id,'amount':b_line.available}))
            line.budget_line_link_ids = budget_line_links
            
    def action_budget_allocation(self):
        if self.move_ids and not self.move_id:
            for move in self.move_ids:
                move.payment_state = 'approved_payment'
                move.date_approval_request = datetime.today().date()
                move.is_from_reschedule_payment = False
                for line in move.invoice_line_ids:
                    budget_line_links = []
                    if line.program_code_id and line.price_total != 0:
                        amount = 0
                        if line.debit:
                            amount = line.debit + line.tax_price_cr
                        else:
                            amount = line.credit + line.tax_price_cr

                        control_amount = 0
                        if line.debit:
                            control_amount = line.debit + line.tax_price_cr
                        else:
                            control_amount = line.credit + line.tax_price_cr

                        budget_lines = self.env['expenditure.budget.line'].sudo().search(
                            [('program_code_id', '=', line.program_code_id.id),
                             ('expenditure_budget_id', '=', line.program_code_id.budget_id.id),
                             ('expenditure_budget_id.state', '=', 'validate')])

                        if move.invoice_date and budget_lines:
                            b_month = move.invoice_date.month
                            for b_line in budget_lines:
                                control_assing_line = self.env['control.assigned.amounts.lines'].search(
                                    [('program_code_id', '=', line.program_code_id.id),
                                     ('assigned_amount_id.budget_id', '=', b_line.expenditure_budget_id.id),
                                     ('assigned_amount_id.state', '=', 'validated')])
                                if b_line.start_date:
                                    b_s_month = b_line.start_date.month
                                    if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                        control_assing_linefilter = control_assing_line.filtered(
                                            lambda x: x.start_date.month in (1, 2, 3))
                                        if control_assing_linefilter:
                                            control_assing_linefilter[0].available -= control_amount
                                            control_amount = 0

                                        if b_line.available >= amount:
                                            b_line.available -= amount
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': amount}))
                                            break
                                        else:
                                            b_line.available = 0
                                            amount -= b_line.available
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': b_line.available}))

                                    elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                        control_assing_linefilter = control_assing_line.filtered(
                                            lambda x: x.start_date.month in (4, 5, 6))
                                        if control_assing_linefilter:
                                            control_assing_linefilter[0].available -= control_amount
                                            control_amount = 0

                                        if b_line.available >= amount:
                                            b_line.available -= amount
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': amount}))
                                            break
                                        else:
                                            b_line.available = 0
                                            amount -= b_line.available
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': b_line.available}))

                                    elif b_month in (7, 8, 9) and b_s_month in (7, 8, 9):
                                        control_assing_linefilter = control_assing_line.filtered(
                                            lambda x: x.start_date.month in (7, 8, 9))
                                        if control_assing_linefilter:
                                            control_assing_linefilter[0].available -= control_amount
                                        control_amount = 0

                                        if b_line.available >= amount:
                                            b_line.available -= amount
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': amount}))
                                            break
                                        else:
                                            b_line.available = 0
                                            amount -= b_line.available
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': b_line.available}))

                                    elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                        control_assing_linefilter = control_assing_line.filtered(
                                            lambda x: x.start_date.month in (10, 11, 12))
                                        if control_assing_linefilter:
                                            control_assing_linefilter[0].available -= control_amount
                                            control_amount = 0

                                        if b_line.available >= amount:
                                            b_line.available -= amount
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': amount}))
                                            break
                                        else:
                                            b_line.available = 0
                                            amount -= b_line.available
                                            budget_line_links.append((0, 0, {'budget_line_id': b_line.id,
                                                                             'account_move_line_id': line.id,
                                                                             'amount': b_line.available}))
                    line.budget_line_link_ids = budget_line_links
                move.create_journal_line_for_approved_payment()
        else:
            self.move_id.payment_state = 'approved_payment'
            self.move_id.date_approval_request = datetime.today().date()
            self.move_id.is_from_reschedule_payment = False
            self.decrease_available_amount()
            self.move_id.create_journal_line_for_approved_payment()
        #self.move_id.action_post()
