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
from odoo import models, _


class StatementOfCashFlows(models.AbstractModel):
    _name = "jt_conac.statement.of.cash.report"
    _inherit = "account.coa.report"
    _description = "Statement of Cash Flows"

    def _get_templates(self):
        templates = super(
            StatementOfCashFlows, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
        ]

    def _get_lines(self, options, line_id=None):
        cash_obj = self.env['cash.statement']
        lines = []
        hierarchy_lines = cash_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.concept,
                'columns': [],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = cash_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })

                level_2_lines = cash_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': [],
                        'level': 3,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

        return lines
