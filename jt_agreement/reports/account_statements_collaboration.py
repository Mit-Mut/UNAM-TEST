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


class AccountStatementsCollaboration(models.AbstractModel):
    _name = "jt_agreement.account.statements.collaboration"
    _inherit = "account.coa.report"
    _description = "Account Statements Collaboration"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = None
    filter_all_entries = None
    filter_journals = None
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
            AccountStatementsCollaboration, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Fecha')},
            {'name': _('Operación')},
            {'name': _('Depósitos')},
            {'name': _('Retiro')},
            {'name': _('Saldo')},
        ]

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
        lines = []
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        
        req_lines = self.env['request.open.balance'].search([('bases_collaboration_id','!=',False),('state','=','confirmed'),('request_date', '>=',start),('request_date', '<=',end)])
        base_ids = req_lines.mapped('bases_collaboration_id')
        lang = self.env.user.lang
        total_final = 0
        for base in base_ids:
            base_line_ids = req_lines.filtered(lambda x:x.bases_collaboration_id.id==base.id)
            req_date = base_line_ids.mapped('request_date')
            
            req_date += base.rate_base_ids.filtered(lambda x:x.interest_date >= start and x.interest_date <= end).mapped('interest_date')

            lines.append({
            'id': 'hierarchy_'+str(base.id),
            'name': 'Convenio :   '+str(base.name),
            'columns': [{'name': 'Num.de Convenio :     '+str(base.convention_no)}, 
                        {'name': ''}, 
                        {'name': ''},
                        {'name': ''}, 
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
            })

            if req_date:
                req_date = list(set(req_date))
                req_date =  sorted(req_date)
            final = 0
            for req in req_date:
                opt_lines = base_line_ids.filtered(lambda x:x.state=='confirmed' and x.request_date == req)
                for line in opt_lines:
                    opt = dict(line._fields['type_of_operation'].selection).get(line.type_of_operation)
                    #opt = line.type_of_operation
                    if lang == 'es_MX':
                        if line.type_of_operation=='open_bal':
                            opt = 'Importe de apertura'
                        elif line.type_of_operation=='increase':
                            opt = 'Incremento'
                        elif line.type_of_operation=='retirement':
                            opt = 'Retiro'
                        elif line.type_of_operation=='withdrawal':
                            opt = 'Retiro por liquidación'
                        elif line.type_of_operation=='withdrawal_cancellation':
                            opt = 'Retiro por cancelación'
                        elif line.type_of_operation=='withdrawal_closure':
                            opt = 'Retiro por cierre'
                        elif line.type_of_operation=='increase_by_closing':
                            opt = 'Incremento por cierre'
                    debit = 0
                    credit = 0  
                    if line.type_of_operation in ('open_bal','increase','increase_by_closing'):         
                        final += line.opening_balance
                        total_final += line.opening_balance
                        debit = line.opening_balance
                    elif line.type_of_operation in ('withdrawal','retirement','withdrawal_cancellation','withdrawal_closure'):
                        final -= line.opening_balance
                        total_final -= line.opening_balance
                        credit = line.opening_balance

                    lines.append({
                    'id': 'Date_'+str(base.id),
                    'name': line.request_date,
                    'columns': [{'name': opt}, 
                                self._format({'name': debit},figure_type='float'), 
                                self._format({'name': credit},figure_type='float'),
                                self._format({'name': final},figure_type='float'), 
                                ],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                    })
                        
    
                for line in base.rate_base_ids.filtered(lambda x:x.interest_date == req):
                    final += line.interest_rate
                    total_final += line.interest_rate
                    lines.append({
                    'id': 'Date_in'+str(base.id),
                    'name': line.interest_date,
                    'columns': [{'name': 'Intereses' if lang == 'es_MX' else 'Interest',}, 
                                self._format({'name': line.interest_rate},figure_type='float'), 
                                self._format({'name': 0.0},figure_type='float'),
                                self._format({'name': final},figure_type='float'), 
                                ],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                    })

        lines.append({
        'id': 'Total',
        'name': 'Total',
        'columns': [{'name': '',}, 
                    {'name': '',}, 
                    {'name': '',},
                    self._format({'name': total_final},figure_type='float'), 
                    ],
        'level': 1,
        'unfoldable': False,
        'unfolded': True,
        })
                            
        return lines
    
    def _get_report_name(self):
        return _("Account Statements")

    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 4}
