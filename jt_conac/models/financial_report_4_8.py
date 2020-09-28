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

class AnalyticalIncomeStatement(models.AbstractModel):
    _name = "jt_conac.analytical.income.statement.report"
    _inherit = "account.coa.report"
    _description = "Analytical Income Statement"

    def _get_templates(self):
        templates = super(
            AnalyticalIncomeStatement, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Nombre')},
            {'name': _('Estimado')},
            {'name': _('Ampliaciones y Reducciones')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Recaudado')},
            {'name': _('Diferencia')},
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


    def _get_lines(self, options, line_id=None):
        income_obj = self.env['income.statement']
        move_line_obj = self.env['account.move.line']
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            period_list = comparison.get('periods')
            period_list.reverse()
            periods = [period for period in period_list]
        periods.append(options.get('date'))
        posted = 'draft'
        if options.get('unposted_in_period'):
            posted = 'posted'
        
        lines = []
        hierarchy_lines = income_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.name,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = income_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                amt_columns = []
                period_dict = {}

                for period in periods:
                    collected_amount = 0
                    estimated_amount = 0
                    
                    date_start = datetime.strptime(str(period.get('date_from')),
                                                   DEFAULT_SERVER_DATE_FORMAT).date()
                    date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()

                    move_lines = move_line_obj.sudo().search(
                        [('account_id', 'in', level_1_line.accounts_ids.ids),
                         ('move_id.state', '=', posted),
                         ('date', '>=', date_start), ('date', '<=', date_end)])
                    if move_lines:
                        estimated_amount = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))

                    move_lines = move_line_obj.sudo().search(
                        [('account_id', 'in', level_1_line.collected_accounts_ids.ids),
                         ('move_id.state', '=', posted),
                         ('date', '>=', date_start), ('date', '<=', date_end)])
                    if move_lines:
                        collected_amount = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                    
                    if period.get('string') in period_dict:
                        pe_dict = period_dict.get(period.get('string'))
                        period_dict.update({period.get('string'): {'estimated_amount': pe_dict.get('estimated_amount',0.0) + estimated_amount,
                                                                   'collected_amount': pe_dict.get('collected_amount',0.0) + collected_amount,
                                                            }})
                    else:
                        period_dict.update({period.get('string'): {'estimated_amount': estimated_amount,
                                                                   'collected_amount': collected_amount, 
                                                                    }})
                        
                        
                for pe in periods:
                    if pe.get('string') in period_dict.keys():
                        pe_dict = period_dict.get(pe.get('string'))
                        amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': pe_dict.get('collected_amount',0.0)},figure_type='float'))
                        pending_collect = pe_dict.get('estimated_amount',0.0) - pe_dict.get('collected_amount',0.0)
                        amt_columns.append(self._format({'name': pending_collect},figure_type='float'))
                    else:
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.name,
                    'columns':amt_columns,
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })

                level_2_lines = income_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    amt_columns = []
                    period_dict = {}

                    for period in periods:
                        
                        collected_amount = 0
                        estimated_amount = 0
                        
                        date_start = datetime.strptime(str(period.get('date_from')),
                                                       DEFAULT_SERVER_DATE_FORMAT).date()
                        date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()
    
                        move_lines = move_line_obj.sudo().search(
                            [('account_id', 'in', level_2_line.accounts_ids.ids),
                             ('move_id.state', '=', posted),
                             ('date', '>=', date_start), ('date', '<=', date_end)])
                        if move_lines:
                            estimated_amount = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
    
                        move_lines = move_line_obj.sudo().search(
                            [('account_id', 'in', level_2_line.collected_accounts_ids.ids),
                             ('move_id.state', '=', posted),
                             ('date', '>=', date_start), ('date', '<=', date_end)])
                        if move_lines:
                            collected_amount = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                        
                        if period.get('string') in period_dict:
                            pe_dict = period_dict.get(period.get('string'))
                            period_dict.update({period.get('string'): {'estimated_amount': pe_dict.get('estimated_amount',0.0) + estimated_amount,
                                                                       'collected_amount': pe_dict.get('collected_amount',0.0) + collected_amount,
                                                                }})
                        else:
                            period_dict.update({period.get('string'): {'estimated_amount': estimated_amount,
                                                                       'collected_amount': collected_amount, 
                                                                        }})
                            
                            
                    for pe in periods:
                        if pe.get('string') in period_dict.keys():
                            pe_dict = period_dict.get(pe.get('string'))
                            amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': pe_dict.get('collected_amount',0.0)},figure_type='float'))
                            pending_collect = pe_dict.get('estimated_amount',0.0) - pe_dict.get('collected_amount',0.0)
                            amt_columns.append(self._format({'name': pending_collect},figure_type='float'))
                        else:
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                            amt_columns.append(self._format({'name': 0.0},figure_type='float'))

                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.name,
                        'columns': amt_columns,
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    level_3_lines = income_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        amt_columns = []
                        period_dict = {}
    
                        for period in periods:
                            
                            collected_amount = 0
                            estimated_amount = 0
                            
                            date_start = datetime.strptime(str(period.get('date_from')),
                                                           DEFAULT_SERVER_DATE_FORMAT).date()
                            date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()
        
                            move_lines = move_line_obj.sudo().search(
                                [('account_id', 'in', level_3_line.accounts_ids.ids),
                                 ('move_id.state', '=', posted),
                                 ('date', '>=', date_start), ('date', '<=', date_end)])
                            if move_lines:
                                estimated_amount = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
        
                            move_lines = move_line_obj.sudo().search(
                                [('account_id', 'in', level_3_line.collected_accounts_ids.ids),
                                 ('move_id.state', '=', posted),
                                 ('date', '>=', date_start), ('date', '<=', date_end)])
                            if move_lines:
                                collected_amount = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                            
                            if period.get('string') in period_dict:
                                pe_dict = period_dict.get(period.get('string'))
                                period_dict.update({period.get('string'): {'estimated_amount': pe_dict.get('estimated_amount',0.0) + estimated_amount,
                                                                           'collected_amount': pe_dict.get('collected_amount',0.0) + collected_amount,
                                                                    }})
                            else:
                                period_dict.update({period.get('string'): {'estimated_amount': estimated_amount,
                                                                           'collected_amount': collected_amount, 
                                                                            }})
                                
                                
                        for pe in periods:
                            if pe.get('string') in period_dict.keys():
                                pe_dict = period_dict.get(pe.get('string'))
                                amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': pe_dict.get('estimated_amount',0.0)},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': pe_dict.get('collected_amount',0.0)},figure_type='float'))
                                pending_collect = pe_dict.get('estimated_amount',0.0) - pe_dict.get('collected_amount',0.0)
                                amt_columns.append(self._format({'name': pending_collect},figure_type='float'))
                            else:
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                                
                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.name,
                            'columns': amt_columns,
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
                        
        return lines

    def _get_report_name(self):
        return _("Analytical Income Statement")

    @api.model
    def _get_super_columns(self, options):
        # date_cols = options.get('date') and [options['date']] or []
        #  date_cols += (options.get('comparison') or {}).get('periods', [])
        #columns = [{'string': _('Initial Balance')}]
        #print ("date_cols=====",date_cols)
        #columns = reversed(date_cols)
        #print ("columns====",columns)
        return {'columns': {}, 'x_offset': 1, 'merge': 1}
 