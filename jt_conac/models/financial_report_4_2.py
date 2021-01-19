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

class StatusOfActivities(models.AbstractModel):
    _name = "jt_conac.status.of.activities.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "Status of Activities"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = False
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_unposted_in_period = False
    MAX_LINES = None

    def _get_templates(self):
        templates = super(StatusOfActivities, self)._get_templates()
        templates['main_table_header_template'] = 'jt_budget_mgmt.template_statement_financial_position_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        columns = [{'name': _('Account Name')}]
        if options.get('comparison') and options['comparison'].get('periods'):
            comparison = options.get('comparison')
            period_list = comparison.get('periods')
            period_list.reverse()
            columns += [
                           {'name': _('Amount')}
                       ] * (len(period_list) + 1)
        else:
            columns = [
                {'name': _('Account Name')}, {'name': _('Amount')}
            ]
        return columns

    @api.model
    def _get_filter_journals(self):
        # OVERRIDE to filter only bank / cash journals.
        return []

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
        move_line_obj = self.env['account.move.line']
        conac_obj = self.env['coa.conac']

        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            period_list = comparison.get('periods')
            period_list.reverse()
            periods = [period for period in period_list]
        periods.append(options.get('date'))

        lines = []
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        if options.get('all_entries') is False:
            move_state_domain = ('move_id.state', '=', 'posted')
        else:
            move_state_domain = ('move_id.state', '!=', 'cancel')

        last_total_dict = {}
        for line in hierarchy_lines:
            if line.code in ('4.0.0.0', '5.0.0.0'):
                
                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': [{'name': ''}] * len(periods),
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                for level_1_line in level_1_lines:
                    main_balance_dict = {}
                    lines.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': [{'name': ''}] * len(periods),
                        'level': 2,
                        'unfoldable': False,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

                    level_2_lines = conac_obj.search([('parent_id', '=', level_1_line.id)])
                    for level_2_line in level_2_lines:
                        amt_columns = []
                        period_dict = {}

                        for period in periods:
                            
                            date_start = datetime.strptime(str(period.get('date_from')),
                                                           DEFAULT_SERVER_DATE_FORMAT).date()
                            date_end = datetime.strptime(str(period.get('date_to')), DEFAULT_SERVER_DATE_FORMAT).date()

                            move_lines = move_line_obj.sudo().search(
                                [('coa_conac_id', '=', level_2_line.id),
                                 move_state_domain,
                                 ('date', '>=', date_start), ('date', '<=', date_end)])
                            if move_lines:
                                balance = 0
                                if line.code in ('4.0.0.0'):
                                    balance += (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                else:
                                    balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                if period.get('string') in period_dict:
                                    period_dict.update(
                                        {period.get('string'): period_dict.get(period.get('string')) + balance})
                                else:
                                    period_dict.update({period.get('string'): balance})

                        level_3_lines = conac_obj.search([('parent_id', '=', level_2_line.id)])
                        for level_3_line in level_3_lines:
                            for period in periods:
                                
                                date_start = datetime.strptime(str(period.get('date_from')),
                                                               DEFAULT_SERVER_DATE_FORMAT).date()
                                date_end = datetime.strptime(str(period.get('date_to')),
                                                             DEFAULT_SERVER_DATE_FORMAT).date()

                                move_lines = move_line_obj.sudo().search([('coa_conac_id', '=', level_3_line.id),
                                                                          move_state_domain,
                                                                          ('date', '>=', date_start),
                                                                          ('date', '<=', date_end)])
                                if move_lines:
                                    balance = 0
                                    if line.code in ('4.0.0.0'):
                                        balance += (sum(move_lines.mapped('credit'))-sum(move_lines.mapped('debit')))
                                    else:
                                        balance += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    if period.get('string') in period_dict:
                                        period_dict.update(
                                            {period.get('string'): period_dict.get(period.get('string')) + balance})
                                    else:
                                        period_dict.update({period.get('string'): balance})

                        for pd, bal in period_dict.items():
                            if pd in main_balance_dict.keys():
                                main_balance_dict.update({pd: main_balance_dict.get(pd) + bal})
                            else:
                                main_balance_dict.update({pd: bal})
                            if line.code in ('4.0.0.0'):
                                if pd in last_total_dict.keys():
                                    last_total_dict.update({pd: last_total_dict.get(pd) + bal})
                                else:
                                    last_total_dict.update({pd: bal})
                            else:
                                if pd in last_total_dict.keys():
                                    last_total_dict.update({pd: last_total_dict.get(pd) - bal})
                                else:
                                    last_total_dict.update({pd: -bal})
                                
                        for pe in periods:
                            if pe.get('string') in period_dict.keys():
                                amt_columns.append(self._format({'name': period_dict.get(pe.get('string'))},figure_type='float'))
                            else:
                                amt_columns.append(self._format({'name': 0.0},figure_type='float'))
                        lines.append({
                            'id': 'level_two_%s' % level_2_line.id,
                            'name': level_2_line.display_name,
                            'columns': amt_columns,
                            'level': 3,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })

                    total_col = []
                    for pe in periods:
                        if pe.get('string') in main_balance_dict.keys():
                            total_col.append(self._format({'name': main_balance_dict.get(pe.get('string'))},figure_type='float'))
                        else:
                            total_col.append(self._format({'name': 0.00},figure_type='float'))
                    lines.append({
                        'id': 'total_%s' % level_1_line.id,
                        'name': 'Total',
                        'columns': total_col,
                        'level': 2,
                        'title_hover': level_1_line.display_name,
                        'unfoldable': False,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })

        main_total_col = []
        
        for pe in periods:
            if pe.get('string') in last_total_dict.keys():
                temp_total = self._format({'name': last_total_dict.get(pe.get('string'))},figure_type='float')
                main_total_col.append(temp_total)
            else:
                main_total_col.append(self._format({'name': 0.00},figure_type='float'))
                
        if self.env.user.lang == 'es_MX':
            lines.append({
                'id': 'total_%s' % level_1_line.id,
                'name': 'Gran Total',
                'columns': main_total_col,
                'level': 2,
                'title_hover': level_1_line.display_name,
                'unfoldable': False,
                'unfolded': True,
            })
        else:
            lines.append({
                'id': 'total_%s' % level_1_line.id,
                'name': 'Main Total',
                'columns': main_total_col,
                'level': 2,
                'title_hover': level_1_line.display_name,
                'unfoldable': False,
                'unfolded': True,
            })

        return lines
    def _get_report_name(self):
        return _("Status of Activities")

    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        #columns = [{'string': _('Initial Balance')}]
        #print ("date_cols=====",date_cols)
        columns = reversed(date_cols)
        #print ("columns====",columns)
        return {'columns': columns, 'x_offset': 1, 'merge': 1}
    
