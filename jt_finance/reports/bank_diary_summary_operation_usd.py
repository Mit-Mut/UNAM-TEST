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
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang

class DiaryOfBankMovementsInDollars(models.AbstractModel):
    _name = "jt_finance.bank.diary.recovery.expenditures.dollars"
    _inherit = "account.coa.report"
    _description = "Summary of Operation - Recovery of Expenditures USD"

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
            DiaryOfBankMovementsInDollars, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Cuenta Bancaria')},
            {'name': _('Reales')},
            {'name': _('Netos')},
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
        previous_end_date = end - timedelta(days=1)
        
        account_payment = self.env['account.payment'].search([('currency_id.name','=','USD'),('payment_date', '>=', start), ('payment_date', '<=', end),('payment_request_type','!=',False),('payment_state','=','for_payment_procedure')])
        for journal in account_payment.mapped("journal_id"):
            total_amount_current = 0
            total_amount_expense = 0
            
            lines.append({
                'id': 'hierarchy1_' + str(journal.id),
                'name': journal.name,
                'columns': [{'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            account_id = journal.default_debit_account_id and journal.default_debit_account_id.id or False
            if account_id:
                values= self.env['account.move.line'].search([('currency_id.name','=','USD'),('account_id', '=', account_id),('move_id.state', '=', 'posted'),('date','<=',previous_end_date)])
                total_amount_current = sum(x.debit-x.credit for x in values)

            payment_accounts = account_payment.filtered(lambda x:x.journal_id.id==journal.id).mapped('payment_issuing_bank_acc_id')
            for account in payment_accounts:
                expense_amount = sum(x.amount for x in account_payment.filtered(lambda x:x.journal_id.id==journal.id and x.payment_issuing_bank_acc_id.id == account.id))
                total_amount_expense += expense_amount


                lines.append({
                    'id': 'hierarchy2_' +str(journal.id) +str(account.id),
                    'name': account.acc_number,
                    'columns': [self._format({'name': total_amount_current},figure_type='float'), 
                                self._format({'name': expense_amount},figure_type='float'), 
                                ],
                    'level': 3,
                    'parent_id': 'hierarchy1_' + str(journal.id),
                })

            lines.append({
                'id': 'hierarchy1total_' + str(journal.id),
                'name': "Suma Total",
                'columns': [ 
                                self._format({'name': total_amount_current},figure_type='float'), 
                                self._format({'name': total_amount_expense},figure_type='float'),
                            ],
                'level': 2,
                'parent_id': 'hierarchy1_' + str(journal.id),
            })
            
        return lines

    def _get_report_name(self):
        return _("Summary of Operation - Recovery of Expenditures USD")
    
    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 4}
