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


class AnalyticalStatusOfTheExpenditureBudgetExercise(models.AbstractModel):
    _name = "jt_conac.status.of.expenditure.report"
    _inherit = "account.coa.report"
    _description = "Analytical Status of the Expenditure Budget Exercise"

    def _get_templates(self):
        templates = super(
            AnalyticalStatusOfTheExpenditureBudgetExercise, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
            {'name': _('Aprobado')},
            {'name': _('Ampliaciones/ (Reducciones)')},
            {'name': _('Modificado')},
            {'name': _('Devengado')},
            {'name': _('Pagado')},
            {'name': _('Subejercicio')},
        ]

    def _get_lines(self, options, line_id=None):
        exp_obj = self.env['status.expen']
        bud_obj = self.env['expenditure.budget']
        adeq_obj = self.env['adequacies']
        item_obj = self.env['expenditure.item']
        budgets = bud_obj.search([('state', '=', 'validate')])
        adequacies = adeq_obj.search([('state', '=', 'accepted')])
        item_dict_auth = {'111-199': [{}], '211-285': [{}], '321-361': [{}], '411-431': [{}], '511-531': [{}],
                          '611-623': [{}], '721-734': [{}]}
        item_dict_adeq = {}
        for budget in budgets:
            for line in budget.success_line_ids:
                item = int(line.item_id.item)
                if item >= 111 and item <= 199:
                    main_dict = item_dict_auth.get('111-199')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 211 and item <= 285:
                    main_dict = item_dict_auth.get('211-285')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 321 and item <= 361:
                    main_dict = item_dict_auth.get('321-361')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 411 and item <= 431:
                    main_dict = item_dict_auth.get('411-431')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 511 and item <= 531:
                    main_dict = item_dict_auth.get('511-531')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 611 and item <= 623:
                    main_dict = item_dict_auth.get('611-623')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
                elif item >= 721 and item <= 731:
                    main_dict = item_dict_auth.get('721-734')[0]
                    if item in main_dict.keys():
                        amt = main_dict.get(item) + line.authorized
                        main_dict.update({item: amt})
                    else:
                        main_dict.update({item: line.authorized})
        for ade in adequacies:
            for line in ade.adequacies_lines_ids:
                if line.program:
                    item = line.program.item_id.item
                    if item in item_dict_adeq.keys():
                        if line.line_type == 'increase':
                            item_dict_adeq.update({item: item_dict_adeq.get(item) + line.amount})
                        else:
                            item_dict_adeq.update({item: item_dict_adeq.get(item) - line.amount})
                    else:
                        if line.line_type == 'increase':
                            item_dict_adeq.update({item: line.amount})
                        else:
                            item_dict_adeq.update({item: -line.amount})
        lines = []
        hierarchy_lines = exp_obj.sudo().search(
            [('parent_id', '=', False)], order='id')

        for line in hierarchy_lines:
            lines.append({
                'id': 'hierarchy_' + str(line.id),
                'name': line.concept,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })

            level_1_lines = exp_obj.search([('parent_id', '=', line.id)])
            for level_1_line in level_1_lines:
                lines.append({
                    'id': 'level_one_%s' % level_1_line.id,
                    'name': level_1_line.concept,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'parent_id': 'hierarchy_' + str(line.id),
                })
                if level_1_line.concept == 'Remuneraciones al Personal de Carácter Permanente':
                    item_dict_111 = dict(sorted(item_dict_auth.get('111-199')[0].items()))
                    for item, authorized in item_dict_111.items():
                        item = item_obj.search([('item', '=', item)])
                        name = item.item
                        if item.description:
                            name += ' '
                            name += item.description
                        adeq_amt = item_dict_adeq.get(item.item) if item_dict_adeq.get(item.item) else 0
                        modi_amt = authorized + adeq_amt
                        lines.append({
                            'id': 'level_two_%s' % item.id,
                            'name': name,
                            'columns': [{'name': authorized}, {'name': adeq_amt}, {'name': modi_amt}, {'name': ''},
                                        {'name': ''}, {'name': modi_amt}],
                            'level': 3,
                            'unfoldable': False,
                            'unfolded': False,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })
                elif level_1_line.concept == 'Materias Primas y Materiales de Producción y Comercialización':
                    item_dict_111 = dict(sorted(item_dict_auth.get('211-285')[0].items()))
                    for item, authorized in item_dict_111.items():
                        item = item_obj.search([('item', '=', item)])
                        name = item.item
                        if item.description:
                            name += ' '
                            name += item.description
                        adeq_amt = item_dict_adeq.get(item.item) if item_dict_adeq.get(item.item) else 0
                        modi_amt = authorized + adeq_amt
                        lines.append({
                            'id': 'level_two_%s' % item.id,
                            'name': name,
                            'columns': [{'name': authorized}, {'name': adeq_amt}, {'name': modi_amt}, {'name': ''},
                                        {'name': ''}, {'name': modi_amt}],
                            'level': 3,
                            'unfoldable': False,
                            'unfolded': False,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })

                level_2_lines = exp_obj.search(
                    [('parent_id', '=', level_1_line.id)])
                for level_2_line in level_2_lines:
                    lines.append({
                        'id': 'level_two_%s' % level_2_line.id,
                        'name': level_2_line.concept,
                        'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                        'level': 3,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'level_one_%s' % level_1_line.id,
                    })

                    level_3_lines = exp_obj.search(
                        [('parent_id', '=', level_2_line.id)])
                    for level_3_line in level_3_lines:
                        lines.append({
                            'id': 'level_three_%s' % level_3_line.id,
                            'name': level_3_line.concept,
                            'columns': [{'name': level_3_line.approved}, {'name': level_3_line.ext_and_red}, {'name': level_3_line.modified}, {'name': level_3_line.accrued}, {'name': level_3_line.paid_out}, {'name': level_3_line.sub_exercise}],
                            'level': 4,
                            'parent_id': 'level_two_%s' % level_2_line.id,
                        })
        return lines
