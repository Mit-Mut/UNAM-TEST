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
from odoo import models, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
import io
import base64
from odoo.tools import config, date_utils, get_lang
import lxml.html

class WithholdingTaxReport(models.AbstractModel):

    _name = "jt_tax_transaction.withholding.report"
    _inherit = "account.coa.report"
    _description = "​ Withholding tax report"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = None
    filter_all_entries = True
    filter_journals = True
    filter_analytic = None
    filter_unfold_all = None
    filter_cash_basis = None
    filter_hierarchy = None
    filter_unposted_in_period = None
    MAX_LINES = None

    def _get_reports_buttons(self):
        return [
            {'name': _('Print Preview'), 'sequence': 1,
             'action': 'print_pdf', 'file_export_type': _('PDF')},
            {'name': _('Export (XLSX)'), 'sequence': 2,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
        ]

    def _get_templates(self):
        templates = super(
            WithholdingTaxReport, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Name Of The Tax')},
            {'name': ''},
            {'name': ''},
            {'name': _('Net'), 'class': 'number'},
            {'name': _('Tax'), 'class': 'number'}
        ]
    def _format(self, value,figure_type):
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']
        
        if figure_type == 'float':
            currency_id = self.env.company.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number text-muted'
            value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            value['class'] = 'number'
            return value
        if figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            value['class'] = 'number'
            return value
        value['name'] = round(value['name'], 1)
        return value

    def _get_report_name(self):
        return _("Withholding Tax report")

    def _get_lines(self, options, line_id=None):
        lines = []    

        if options.get('all_entries') is False:
            move_state_domain = ('move_id.state', '=', 'posted')
        else:
            move_state_domain = ('move_id.state', '!=', 'cancel')

        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()

        total = 0
        tax_ids = self.env['account.tax'].search([])
        journal_id = False
        journal_rec = self.env['account.journal'].search([('code','=','CBMX')],limit=1)
        if journal_rec:
            journal_id = journal_rec.id
        
        account_ids = self.env['account.account']
         
        account_code_list = ['220.001.001.001','220.001.001.002','220.001.001.003','220.001.002.001',
                             '220.001.002.002','220.001.002.003','220.001.002.004','220.001.002.005',
                             '220.001.003.001','220.001.004.001','220.001.004.002','220.001.004.003',
                             '220.001.004.004','220.001.004.005','220.001.004.006','220.001.005.001',
                             '220.001.005.002'
                             ]
        for a in account_code_list:
            account_id = self.env['account.account'].search([('code','=',a)],limit=1)
            if account_id:
               account_ids = account_ids + account_id
                   

        tax_line_list = []
        for tax in tax_ids:
            total_balance = 0
            total_tax = 0
            move_lines= self.env['account.move.line'].search([('account_id','in',account_ids.ids),('date', '>=', start),('date', '<=', end),('tax_line_id', '=', tax.id),move_state_domain])
            #move_lines = self.env['account.move.line'].search([('date', '>=', start),('date', '<=', end),('move_id.journal_id','=',journal_id),('tax_line_id', '=', tax.id),move_state_domain])
            if move_lines:    
                tax_line_list = []
                tax_account_ids = move_lines.mapped('account_id')
                tax_move_lines = move_lines.filtered(lambda x:x.account_id.id in tax_account_ids.ids)
                
                for account_id in tax_account_ids:
                    net_amount = sum(x.tax_base_amount for x in tax_move_lines.filtered(lambda x:x.account_id.id==account_id.id))
                    tax_amount = sum(x.debit+x.credit for x in tax_move_lines.filtered(lambda x:x.account_id.id==account_id.id))
                    
                    tax_line_list.append({
                        'id': account_id.id,
                        'name' :  account_id.code +" "+ account_id.name, 
                        'columns': [
                                    {'name': ''},
                                    {'name': ''},
                                    self._format({'name': net_amount},figure_type='float'),
                                    self._format({'name': tax_amount},figure_type='float'),
                                    ],
                        'level': 3,
                        'unfolded': True,
                        'parent_id': 'tax_name'+str(tax.id),
                        'caret_options': 'account.account',
                    })
                    total_balance += net_amount
                    total_tax += tax_amount

                tax_list=[{
                    'id': 'tax_name_in'+str(tax.id),
                    'name' : "Total", 
                    'columns': [
                                {'name': ''},
                                {'name': ''},
                                self._format({'name': total_balance},figure_type='float'),
                                self._format({'name': total_tax},figure_type='float'),
                                ],
                    'level': 1,
                    'unfoldable': True,
                    'unfolded': False,
                    'parent_id': 'tax_name'+str(tax.id),
                }]

                tax_list=[{
                    'id': 'tax_name'+str(tax.id),
                    'name' : tax.name, 
                    'columns': [
                                {'name': ''},
                                {'name': ''},
                                self._format({'name': total_balance},figure_type='float'),
                                self._format({'name': total_tax},figure_type='float'),
                                ],
                    'level': 1,
                    'unfoldable': True,
                    'unfolded': False,
                }]
                lines += tax_list + tax_line_list     
        return lines


#         for tax in tax_ids:
#             total_balance = 0
#             total_tax = 0
#             move_lines= self.env['account.move.line'].search([('account_id','in',account_ids.ids),('date', '>=', start),('date', '<=', end),('tax_line_id', '=', tax.id),move_state_domain])
#             #move_lines = self.env['account.move.line'].search([('date', '>=', start),('date', '<=', end),('move_id.journal_id','=',journal_id),('tax_line_id', '=', tax.id),move_state_domain])
#             if move_lines:    
#                 tax_line_list = []
#                 for line in move_lines:
#                     tax_line_list.append({
#                         'id': 'line'+str(line.id),
#                         'name' : line.ref, 
#                         'columns': [
#                                     {'name': line.date},
#                                     {'name': line.move_id.name},
#                                     self._format({'name': line.tax_base_amount},figure_type='float'),
#                                     self._format({'name': line.debit+line.credit},figure_type='float'),
#                                     ],
#                         'level': 3,
#                         'unfolded': True,
#                         'parent_id': 'tax_name'+str(tax.id),
#                     })
#                     total_balance += line.tax_base_amount
#                     total_tax += line.debit+line.credit
# 
#                 tax_list=[{
#                     'id': 'tax_name'+str(tax.id),
#                     'name' : tax.name, 
#                     'columns': [
#                                 {'name': ''},
#                                 {'name': ''},
#                                 self._format({'name': total_balance},figure_type='float'),
#                                 self._format({'name': total_tax},figure_type='float'),
#                                 ],
#                     'level': 1,
#                     'unfoldable': True,
#                     'unfolded': False,
#                 }]
#                 lines += tax_list + tax_line_list     
#         return lines

        #====================================== Direct Account ========#
#         for line in account_ids:
#             move_lines= self.env['account.move.line'].search([('account_id','=',line.id),('date', '>=', start),('date', '<=', end),move_state_domain])
#             amount = sum(x.credit-x.debit for x in move_lines)
#             total += amount
#             tax_line_list.append({
#                 'id': line.id,
#                 'name' : line.code +" "+ line.name, 
#                 'columns': [
#                             {'name': ''},
#                             {'name': ''},
#                             self._format({'name': amount},figure_type='float'),
#                             self._format({'name': 00},figure_type='float'),
#                             ],
#                 'level': 3,
#                 'unfoldable': False,
#                 'class':'text-left',
#                 'caret_options': 'account.account',
#             })
# 
#         lines += tax_line_list     
# 
#         lines.append({
#             'id': 'total',
#             'name' : 'Total', 
#             'columns': [
#                         {'name':''},
#                         {'name':''},
#                          self._format({'name': total},figure_type='float'),
#                         {'name':''},
#                         ],
#             'level': 1,
#             'unfoldable': False,
#             'unfolded': True,
#             'class':'text-left',
#         })

        return lines
