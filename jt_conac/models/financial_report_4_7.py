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
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
import io
import base64
from odoo.tools import config, date_utils, get_lang
import lxml.html

class StatementOfCashFlows(models.AbstractModel):
    _name = "jt_conac.statement.of.cash.report"
    _inherit = "account.coa.report"
    _description = "Statement of Cash Flows"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_journals = True
    filter_all_entries = True
    filter_journals = True
    filter_unfold_all = True
    filter_hierarchy = True
    filter_analytic = None

    def _get_templates(self):
        templates = super(
            StatementOfCashFlows, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):

        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        
        prev_year = start.year - 1 

        columns = [
            {'name': _('Concepto')},
            {'name': str(start.year)},
            #{'name': str(prev_year)},
        ]

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        columns.extend([{'name': period} for period in periods])

        return columns

    def _format(self, value, figure_type):
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']

        if figure_type == 'float':
            currency_id = self.env.company.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number text-muted'
            value['name'] = formatLang(
                self.env, value['name'], currency_obj=currency_id)
            value['class'] = 'number'
            return value
        if figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            value['class'] = 'number'
            return value
        value['name'] = round(value['name'], 1)
        return value

    def _get_lines(self, options, line_id=None):
        move_line_obj = self.env['account.move.line']
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
            
        periods_data = []
        if comparison and comparison.get('filter') != 'no_comparison':
            period_list = comparison.get('periods')
            #period_list.reverse()
            periods_data = [period for period in period_list]
        #periods.append(options.get('date'))
            
        cash_obj = self.env['cash.statement']
        lines = []

        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()

        if options.get('all_entries') is False:
            move_state_domain = ('move_id.state', '=', 'posted')
        else:
            move_state_domain = ('move_id.state', '!=', 'cancel')
        
        hierarchy_lines = cash_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            level_1_columns = [{'name': ''} ]
            level_1_columns.extend([{'name': ''} for period in periods])

            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.concept,
                'columns': level_1_columns,
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = cash_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                level_2_columns = [{'name': ''}]
                level_2_columns.extend([{'name': ''} for period in periods])

                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': level_2_columns,
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })

                level_2_lines = cash_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    current_amount = 0
                    if level_2_line.coa_conac_ids:
                        move_lines = move_line_obj.sudo().search(
                            [('coa_conac_id', 'in', level_2_line.coa_conac_ids.ids),
                             move_state_domain,
                             ('date', '>=', start),('date', '<=', end)])
                        if move_lines:
                            current_amount = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                    
                    level_3_columns = [self._format({'name': current_amount},figure_type='float'), ]
                    for period in periods_data:
                        date_start = datetime.strptime(str(period.get('date_from')),
                                                       DEFAULT_SERVER_DATE_FORMAT).date()
                        date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()
                        per_amount = 0
                        if level_2_line.coa_conac_ids:
                            move_lines = move_line_obj.sudo().search(
                                [('coa_conac_id', 'in', level_2_line.coa_conac_ids.ids),
                                 move_state_domain,
                                 ('date', '>=', date_start),('date', '<=', date_end)])
                            if move_lines:
                                per_amount = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))

                        level_3_columns.extend([self._format({'name': per_amount},figure_type='float'),])

                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': level_3_columns,
                        'level': 3,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

        return lines

    def _get_report_name(self):
        return _("Statement of Cash Flows")

    @api.model
    def _get_super_columns(self, options):
 #       date_cols = options.get('date') and [options['date']] or []
 #       date_cols += (options.get('comparison') or {}).get('periods', [])
        #columns = [{'string': _('Initial Balance')}]
        #print ("date_cols=====",date_cols)
 #       columns = reversed(date_cols)
        #print ("columns====",columns)
        return {'columns': {}, 'x_offset': 1, 'merge': 1}
 
    