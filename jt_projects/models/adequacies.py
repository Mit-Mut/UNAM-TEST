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
import base64
import io
import math
from datetime import datetime, timedelta
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Adequacies(models.Model):
    _inherit = 'adequacies'

    is_from_project = fields.Boolean(string='From Project',copy=False,default=False)
    is_send_request = fields.Boolean(string='Send Request',copy=False,default=False)
    
    def action_send_request(self):
        
        for rec in self:
            vals_list = []
            rec.is_send_request = True
            for line in rec.adequacies_lines_ids:
                budget_line = self.env['expenditure.budget.line'].sudo().search(
                    [('program_code_id', '=', line.program.id),
                     ('expenditure_budget_id', '=', rec.budget_id.id)], limit=1)
                if not budget_line:
                    vals = {
                        'program_code_id': line.program.id,
                        'start_date': rec.budget_id.from_date,
                        'end_date': rec.budget_id.to_date,
                        'authorized': line.amount,
                        'assigned': line.amount,
                        # 'available': line.available,
                        #'imported': line.imported,
                        'imported_sessional': False,
                        'state': 'success',
                        'year': line.program and line.program.year and line.program.year.name or '',
                        'program': line.program and line.program.program_id and line.program.program_id.key_unam or '',
                        'subprogram': line.program and line.program.sub_program_id and line.program.sub_program_id.sub_program or '',
                        'dependency': line.program and line.program.dependency_id and line.program.dependency_id.dependency or '',
                        'subdependency': line.program and line.program.sub_dependency_id and line.program.sub_dependency_id.sub_dependency or '',
                        'item': line.program and line.program.item_id and line.program.item_id.item or '',
                        'dv': line.program and line.program.check_digit or '',
                        #'origin_resource': line.origin_resource,
                        'ai': line.program and line.program.institutional_activity_id and line.program.institutional_activity_id.number or '',
                        'conversion_program': line.program and line.program.budget_program_conversion_id and line.program.budget_program_conversion_id.shcp and line.program.budget_program_conversion_id.shcp.name or '',
                        'departure_conversion': line.program and line.program.conversion_item_id and line.program.conversion_item_id.federal_part or '',
                        'expense_type': line.program and line.program.expense_type_id and line.program.expense_type_id.key_expenditure_type or '',
                        'location': line.program and line.program.location_id and line.program.location_id.state_key or '',
                        'portfolio': line.program and line.program.portfolio_id and line.program.portfolio_id.wallet_password or '',
                        'project_type': line.program and line.program.project_type_id and line.program.project_type_id.number or '',
                        'project_number':line.program and  line.program.project_number,
                        #'stage': line.stage,
                        #'agreement_type': line.agreement_type,
                        'agreement_number': line.program and  line.program.number_agreement,
                        #'exercise_type': line.exercise_type,
                    }
                    vals_list.append((0, 0, vals))
                    
                    
                    q_vals = dict(vals)
                    rec_date = ''
                    if rec.adaptation_type == 'compensated':
                        rec_date = rec.date_of_budget_affected
                    elif rec.adaptation_type == 'liquid':
                        rec_date = rec.date_of_liquid_adu
                    from_date = False
                    to_date = False
                    
                    if rec_date:
                        
                        b_month = rec_date.month
                        if b_month in (1, 2, 3):
                            from_date = rec_date.replace(day=1,month=1)
                            to_date = rec_date.replace(day=31,month=3)
                        elif b_month in (4, 5, 6):
                            from_date = rec_date.replace(day=1,month=4)
                            to_date = rec_date.replace(day=30,month=6)

                        elif b_month in (7, 8, 9):
                            from_date = rec_date.replace(day=1,month=7)
                            to_date = rec_date.replace(day=30,month=9)

                        elif b_month in (10, 11, 12):
                            from_date = rec_date.replace(day=1,month=10)
                            to_date = rec_date.replace(day=31,month=12)


                    q_vals.update({'imported_sessional': True,'start_date':from_date,'end_date':to_date,'authorized':0,'assigned':0})
                    
                    vals_list.append((0, 0, q_vals))
                    line.program.budget_id = rec.budget_id.id
                    line.program.state = 'validated'
                     
            rec.budget_id.write({'success_line_ids': vals_list})
            

class ProgramCode(models.Model):

    _inherit = 'program.code'
    
    parent_program_id = fields.Many2one('program.code','Parent Program Code')
    
    @api.onchange('parent_program_id')
    def onchange_parent_program_id(self):
        if self.parent_program_id:
            self.year = self.parent_program_id.year and self.parent_program_id.year.id or False
            self.program_id = self.parent_program_id.program_id and self.parent_program_id.program_id.id or False
            self.sub_program_id = self.parent_program_id.sub_program_id and self.parent_program_id.sub_program_id.id or False
            self.dependency_id = self.parent_program_id.dependency_id and self.parent_program_id.dependency_id.id or False
            self.sub_dependency_id = self.parent_program_id.sub_dependency_id and self.parent_program_id.sub_dependency_id.id or False
            self.item_id = self.parent_program_id.item_id and self.parent_program_id.item_id.id or False
            self.resource_origin_id = self.parent_program_id.resource_origin_id and self.parent_program_id.resource_origin_id.id or False
            self.institutional_activity_id = self.parent_program_id.institutional_activity_id and self.parent_program_id.institutional_activity_id.id or False
            self.budget_program_conversion_id = self.parent_program_id.budget_program_conversion_id and self.parent_program_id.budget_program_conversion_id.id or False
            self.conversion_item_id = self.parent_program_id.conversion_item_id and self.parent_program_id.conversion_item_id.id or False
            self.expense_type_id = self.parent_program_id.expense_type_id and self.parent_program_id.expense_type_id.id or False
            self.location_id = self.parent_program_id.location_id and self.parent_program_id.location_id.id or False
            self.portfolio_id = self.parent_program_id.portfolio_id and self.parent_program_id.portfolio_id.id or False
            
            
            
            
            
            