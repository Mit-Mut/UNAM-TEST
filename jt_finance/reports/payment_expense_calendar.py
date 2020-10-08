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

class PaymentExpenseCalendar(models.AbstractModel):
    _name = "jt_finance.payment.expense.calendar"
    _inherit = "account.coa.report"
    _description = "Payment Expense Calendar"

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
            {'name': _('Print Preview'), 'sequence': 1, 'action': 'print_pdf', 'file_export_type': _('PDF')},
            {'name': _('Export (XLSX)'), 'sequence': 2, 'action': 'print_xlsx', 'file_export_type': _('XLSX')},
        ]

    def _get_templates(self):
        templates = super(
            PaymentExpenseCalendar, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Fecha')},
            {'name': _('Egreso')},
            {'name': _('Cuenta Bancaria')},
            {'name': _('Importe')},
            {'name': _('Observaciones')},
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
        lines = []
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        
        account_payment = self.env['account.payment'].search([('payment_date', '>=', start), ('payment_date', '<=', end),('payment_request_type','!=',False),('payment_state','=','for_payment_procedure')])
        for journal in account_payment.mapped("journal_id"):
            total_amount = 0
            lines.append({
                'id': 'hierarchy1_' + str(journal.id),
                'name': journal.name,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            for payment in account_payment.filtered(lambda x:x.journal_id.id==journal.id):
                payment_type = ''
                if payment.payment_request_type == "supplier_payment":
                    payment_type = 'Proveedores'
                elif payment.payment_request_type == "payroll_payment":
                    payment_type = 'Nómina'
                elif payment.payment_request_type == "different_to_payroll":
                    payment_type = 'Diferente a la nómina'
                     
                total_amount += payment.amount
                payment_date = datetime.strftime(payment.payment_date, '%d/%m/%Y')

                lines.append({
                    'id': 'hierarchy2_' + str(payment.id),
                    'name': payment_date,
                    'columns': [{'name': payment_type}, 
                                {'name': payment.payment_issuing_bank_acc_id and payment.payment_issuing_bank_acc_id.acc_number or ''}, 
                                self._format({'name': payment.amount},figure_type='float'), 
                                {'name':''}],
                    'level': 3,
                    'parent_id': 'hierarchy1_' + str(journal.id),
                })

            lines.append({
                'id': 'hierarchy1total_' + str(journal.id),
                'name': "",
                'columns': [{'name': ''}, 
                            {'name': 'TOTAL'}, 
                            self._format({'name': total_amount},figure_type='float'), 
                            {'name':''}],
                'level': 2,
                'parent_id': 'hierarchy1_' + str(journal.id),
            })
            
        return lines

    def _get_report_name(self):
        return _("Payment / Expense Calendar")
    
    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 4}
