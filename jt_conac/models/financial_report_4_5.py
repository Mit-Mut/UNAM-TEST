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
from odoo import models,api, _


class AnalyticalStatementOfDebtAndOtherLiabilities(models.AbstractModel):
    _name = "jt_conac.analytical.status.of.debts.report"
    _inherit = "account.coa.report"
    _description = "Analytical Statement of Debt and Other Liabilities"

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
            AnalyticalStatementOfDebtAndOtherLiabilities, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {'name': _('Denominación de las Deudas')},
            {'name': _('Moneda de Contratación')},
            {'name': _('Institución o País Acreedor')},
            {'name': _('Saldo Inicial del Periodo')},
            {'name': _('Saldo Final del Periodo')},
        ]
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        columns.extend([{'name': period} for period in periods])

        return columns

    def _get_lines(self, options, line_id=None):
        comparison = options.get('comparison')
        periods = []
        if comparison and comparison.get('filter') != 'no_comparison':
            periods = [period.get('string') for period in comparison.get('periods')]
        debt_obj = self.env['debt.statement']
        lines = []
        hierarchy_lines = debt_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
            level_1_columns.extend([{'name': ''} for period in periods])
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.denomination,
                'columns': level_1_columns,
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = debt_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                level_2_columns.extend([{'name': ''} for period in periods])
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.denomination,
                    'columns': level_2_columns,
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })

                level_2_lines = debt_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                    level_3_columns.extend([{'name': ''} for period in periods])

                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.denomination,
                        'columns': level_3_columns,
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    level_3_lines = debt_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        level_4_columns = [{'name': level_3_line.currency_id.id}, {'name': level_3_line.country_id.id}, {'name': level_3_line.init_balance}, {'name': level_3_line.end_balance}]
                        level_4_columns.extend([{'name': ''} for period in periods])

                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.denomination,
                            'columns': level_4_columns,
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
        return lines
    
    def _get_report_name(self):
        return _("Analytical Statement of Debt and Other Liabilities")

    @api.model
    def _get_super_columns(self, options):
        columns = {}
        return columns 
        