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
from datetime import datetime
from odoo import models, api, _,fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang

class StateOfVariation(models.AbstractModel):
    _name = "jt_conac.state.of.variation.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "State of Variation in the Public Treasury"

    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
            {'name': _('Hacienda Pública / Patrimonio Contribuido')},
            {'name': _('Patrimonio Generado de Ejercicios Anteriores')},
            {'name': _('Patrimonio Generado del Ejercicio')},
            {'name': _('Exceso o Insuficiencia en la Actualización de la Hacienda Pública / Patrimonio')},
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
        conac_obj = self.env['coa.conac']
        move_line_obj = self.env['account.move.line']
        lines = []
        move_state_domain = ('move_id.state', '=', 'posted')
        hierarchy_lines = conac_obj.sudo().search(
            [('parent_id', '=', False)], order='code')

        total_col1 = 0
        total_col2 = 0
        total_col3 = 0
        total_col4 = 0
        
        for line in hierarchy_lines:
            if line.code == '3.0.0.0':
                lines.append({
                    'id': 'hierarchy_' + line.code,
                    'name': line.display_name,
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                    'level': 1,
                    'unfoldable': False,
                    'unfolded': True,
                })

                level_1_lines = conac_obj.search([('parent_id', '=', line.id)])
                first_level = []
                for level_1_line in level_1_lines:
                    level_1_col_1 = 0
                    level_1_col_2 = 0
                    level_1_col_3 = 0
                    level_1_col_4 = 0

                    level_2_lines = conac_obj.search(
                        [('parent_id', '=', level_1_line.id)])
                    second_level = []
                    for level_2_line in level_2_lines:
                        level_2_col_1 = 0
                        level_2_col_2 = 0
                        level_2_col_3 = 0
                        level_2_col_4 = 0


                        level_3_lines = conac_obj.search(
                            [('parent_id', '=', level_2_line.id)])
                        third_level = []
                        for level_3_line in level_3_lines:
                            level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                            level_3_col_1 = 0
                            level_3_col_2 = 0
                            level_3_col_3 = 0
                            level_3_col_4 = 0
                            
                            move_lines = move_line_obj.sudo().search(
                                [('coa_conac_id', '=', level_3_line.id),
                                 move_state_domain,
                                 ])
                            
                            
                            if level_3_line.code == '3.3.1.0' or level_3_line.code == '3.3.2.0':
                                if move_lines:
                                    level_3_col_4 = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    level_2_col_4 += level_3_col_4 
                                    level_1_col_4 += level_3_col_4
                                    total_col4 += level_3_col_4
                                    
                                level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''},
                                                    self._format({'name': level_3_col_4},figure_type='float')]

                            elif level_3_line.code == '3.1.1.0' or level_3_line.code == '3.1.2.0' or level_3_line.code == '3.1.3.0':
                                if move_lines:
                                    level_3_col_1 = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    level_2_col_1 += level_3_col_1 
                                    level_1_col_1 += level_3_col_1
                                    total_col1 += level_3_col_1
                                    
                                level_3_columns = [self._format({'name': level_3_col_1},figure_type='float'),
                                                   {'name': ''}, {'name': ''}, {'name': ''},]

                            elif level_3_line.code == '3.2.1.0':
                                if move_lines:
                                    level_3_col_3 = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    level_2_col_3 += level_3_col_3 
                                    level_1_col_3 += level_3_col_3
                                    total_col3 += level_3_col_3
                                    
                                level_3_columns = [{'name': ''}, {'name': ''},self._format({'name': level_3_col_3},figure_type='float'),
                                                    {'name': ''},]

                            elif level_2_line.code == '3.2.2.0' or level_2_line.code == '3.2.3.0' or level_2_line.code == '3.2.4.0' or level_2_line.code == '3.2.5.0':
                                if move_lines:
                                    level_3_col_2 = (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                    level_2_col_2 += level_3_col_2 
                                    level_1_col_2 += level_3_col_2
                                    total_col2 += level_3_col_2
                                    
                                level_3_columns = [{'name': ''}, self._format({'name': level_3_col_2},figure_type='float'),{'name': ''},
                                                    {'name': ''},]
                                
                            third_level.append({
                                'id': 'level_three_%s' % level_3_line.id,
                                'name': level_3_line.display_name,
                                'columns': level_3_columns,
                                'level': 4,
                                'parent_id': 'level_two_%s' % level_2_line.id,
                            })
                        
                        #====== Level 2 Data===========#
                        move_lines = move_line_obj.sudo().search(
                            [('coa_conac_id', '=', level_2_line.id),
                             move_state_domain,
                             ])
                        
                        level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                        if level_2_line.code == '3.3.0.0':
                            level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, 
                                               self._format({'name': level_2_col_4},figure_type='float')]
                            
                        elif level_2_line.code == '3.3.1.0' or level_2_line.code == '3.3.2.0':
                            if move_lines:
                                level_2_col_4 += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                total_col4 += level_2_col_4
                                level_1_col_4 += level_2_col_4
                            level_2_columns = [
                                               {'name': ''}, {'name': ''}, {'name': ''},self._format({'name': level_2_col_4},figure_type='float'),]

                        elif level_2_line.code == '3.1.1.0' or level_2_line.code == '3.1.2.0' or level_2_line.code == '3.1.3.0':
                            if move_lines:
                                level_2_col_1 += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                total_col1 += level_2_col_1
                                level_1_col_1 += level_2_col_1
                            level_2_columns = [self._format({'name': level_2_col_1},figure_type='float'),
                                                {'name': ''}, {'name': ''}, {'name': ''}]

                        elif level_2_line.code == '3.2.1.0':
                            if move_lines:
                                level_2_col_3 += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                total_col3 += level_2_col_3
                                level_1_col_3 += level_2_col_3
                            level_2_columns = [{'name': ''}, {'name': ''},self._format({'name': level_2_col_3},figure_type='float'),
                                                 {'name': ''}]

                        elif level_2_line.code == '3.2.2.0' or level_2_line.code == '3.2.3.0' or level_2_line.code == '3.2.4.0' or level_2_line.code == '3.2.5.0':
                            if move_lines:
                                level_2_col_2 += (sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit')))
                                total_col2 += level_2_col_2
                                level_1_col_2 += level_2_col_2
                            level_2_columns = [{'name': ''}, self._format({'name': level_2_col_2},figure_type='float'),{'name': ''},
                                                 {'name': ''}]
                        
                        second_level.append({
                            'id': 'level_two_%s' % level_2_line.id,
                            'name': level_2_line.display_name,
                            'columns': level_2_columns,
                            'level': 3,
                            'unfoldable': True,
                            'unfolded': True,
                            'parent_id': 'level_one_%s' % level_1_line.id,
                        })
                        second_level += third_level

                    level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}]
                    if level_1_line.code == '3.3.0.0':
                        level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, 
                                           self._format({'name': level_1_col_4},figure_type='float')]

                    elif level_1_line.code == '3.1.0.0':
                        level_1_columns = [self._format({'name': level_1_col_1},figure_type='float'),
                                           {'name': ''}, {'name': ''}, {'name': ''}, ]

                    elif level_1_line.code == '3.2.0.0':
                        level_1_columns = [{'name': ''},
                                           self._format({'name': level_1_col_2},figure_type='float'),
                                           self._format({'name': level_1_col_3},figure_type='float'), 
                                            {'name': ''}, ]


                    first_level.append({
                        'id': 'level_one_%s' % level_1_line.id,
                        'name': level_1_line.display_name,
                        'columns': level_1_columns,
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': True,
                        'parent_id': 'hierarchy_' + line.code,
                    })
                    first_level += second_level
                    
                lines +=  first_level         
                total_columns = [self._format({'name': total_col1},figure_type='float'),
                                self._format({'name': total_col2},figure_type='float'),
                                self._format({'name': total_col3},figure_type='float'),
                                self._format({'name': total_col4},figure_type='float')]

                lines.append({
                    'id': 'Total',
                    'name': 'Total',
                    'columns': total_columns,
                    'level': 1,
                })
                
        return lines

    def _get_report_name(self):
        return _("State of Variation in the Public Treasury")

    @api.model
    def _get_super_columns(self, options):
        
        columns = [{'string': self._get_report_name()}]
        return {'columns': columns, 'x_offset': 0, 'merge': 1}
    