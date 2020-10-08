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

class TypeofOperation(models.AbstractModel):
    _name = "jt_finance.type.of.operation"
    _inherit = "account.coa.report"
    _description = "Type of Operation"

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
            TypeofOperation, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Cuenta Bancaria')},
            {'name': _('Descripción')},
            {'name': _('Nómina')},
            {'name': _('Proveedores')},
            {'name': _('Diferentes a nómina')},
            {'name': _('ISSSTE')},
            {'name': _('FOVISSSTE')},
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
        
        account_payment = self.env['account.payment'].search([('payment_date', '>=', start), ('payment_date', '<=', end),('payment_request_type','!=',False),('payment_state','in',('for_payment_procedure','posted','reconciled'))],order="journal_id")
        master_total_amount_supplier = 0
        master_total_amount_payroll = 0
        master_total_amount_different_payroll = 0

        for journal in account_payment.mapped("journal_id"):
            total_amount_supplier = 0
            total_amount_payroll = 0
            total_amount_different_payroll = 0
            lines.append({
                'id': 'hierarchy1_' + str(journal.id),
                'name': journal.name,
                'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}, {'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            payment_accounts = account_payment.filtered(lambda x:x.journal_id.id==journal.id).mapped('payment_issuing_bank_acc_id')
            for payment_account in payment_accounts:
                payment_type_records = account_payment.filtered(lambda x:x.journal_id.id==journal.id and x.payment_issuing_bank_acc_id.id==payment_account.id)
                supplier = sum(x.amount for x in payment_type_records.filtered(lambda x:x.payment_request_type == 'supplier_payment'))
                payroll = sum(x.amount for x in payment_type_records.filtered(lambda x:x.payment_request_type == 'payroll_payment'))
                payroll_diff = sum(x.amount for x in payment_type_records.filtered(lambda x:x.payment_request_type == 'different_to_payroll'))
                
                payment_type_name= ''
                total_amount_supplier += supplier
                master_total_amount_supplier += supplier

                total_amount_payroll += payroll
                master_total_amount_payroll += payroll

                total_amount_different_payroll += payroll_diff
                master_total_amount_different_payroll += payroll_diff
                
                if payroll:
                    payment_type_name = 'Nómina'
                    lines.append({
                        'id': 'hierarchy2_' + str(journal.id) + str(payment_account.id)+'Nómina',
                        'name': payment_account.acc_number,
                        'columns': [{'name': payment_type_name},
                                    self._format({'name': payroll},figure_type='float'), 
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'), 
                                    ],
                        'level': 3,
                        'parent_id': 'hierarchy1_' + str(journal.id),
                    })
                
                if supplier:
                    payment_type_name = 'Proveedores'
                    lines.append({
                        'id': 'hierarchy2_' + str(journal.id) + str(payment_account.id)+'Proveedores',
                        'name': payment_account.acc_number,
                        'columns': [{'name': payment_type_name},
                                    self._format({'name': 0.0},figure_type='float'), 
                                    self._format({'name': supplier},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'), 
                                    ],
                        'level': 3,
                        'parent_id': 'hierarchy1_' + str(journal.id),
                    })

                if payroll_diff:
                    payment_type_name = 'Diferentes a nómina'
                    lines.append({
                        'id': 'hierarchy2_' + str(journal.id) + str(payment_account.id)+'Diferentes_nómina',
                        'name': payment_account.acc_number,
                        'columns': [{'name': payment_type_name},
                                    self._format({'name': 0.0},figure_type='float'), 
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': payroll_diff},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'),
                                    self._format({'name': 0.0},figure_type='float'), 
                                    ],
                        'level': 3,
                        'parent_id': 'hierarchy1_' + str(journal.id),
                    })

            lines.append({
                'id': 'hierarchy1total_' + str(journal.id),
                'name': "TOTAL",
                'columns': [{'name': ''}, 
                            self._format({'name': total_amount_payroll},figure_type='float'),
                            self._format({'name': total_amount_supplier},figure_type='float'),
                            self._format({'name': total_amount_different_payroll},figure_type='float'),
                            self._format({'name': 0.0},figure_type='float'),
                            self._format({'name': 0.0},figure_type='float'), 
                            ],
                'level': 2,
                'parent_id': 'hierarchy1_' + str(journal.id),
            })

        lines.append({
            'id': 'hierarchy1mastertotal',
            'name': "Suma Total",
            'columns': [{'name': ''}, 
                        self._format({'name': master_total_amount_payroll},figure_type='float'),
                        self._format({'name': master_total_amount_supplier},figure_type='float'),
                        self._format({'name': master_total_amount_different_payroll},figure_type='float'),
                        self._format({'name': 0.0},figure_type='float'),
                        self._format({'name': 0.0},figure_type='float'), 
 
                        ],
            'level': 2,
            'parent_id': 'hierarchy1_' + str(journal.id),
        })
            
        return lines

    def _get_report_name(self):
        return _("Type of Operation")
    
    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 4}
