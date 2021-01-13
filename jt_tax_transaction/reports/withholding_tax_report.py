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
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
import io
import base64
from odoo.tools import config, date_utils, get_lang
import lxml.html

class WithholdingTaxReport(models.AbstractModel):

    _name = "jt_tax_transaction.withholding.report"
    _inherit = "account.coa.report"
    _description = "​ Withholding tax report"

    filter_date = {'mode': 'range', 'filter': 'last_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True

    def _get_reports_buttons(self):
        return [
            {'name': _('Print Preview'), 'sequence': 1,
             'action': 'print_pdf', 'file_export_type': _('PDF')},
            {'name': _('Export (XLSX)'), 'sequence': 2,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
            {'name': _('Closing Journal Entry'), 'sequence': 3,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
            {'name': _('Save'), 'sequence': 4,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
        ]

    def _get_templates(self):
        templates = super(
            WithholdingTaxReport, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Name Of The Tax')},
            {'name': ''},
            {'name': ''},
            {'name': _('Net'), 'class': 'number'},
            {'name': _('Tax'), 'class': 'number'}
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

    def _get_report_name(self):
        return _("Withholding Tax report")

    def _get_lines(self, options, line_id=None):
        lines = []    

        lines.append({
            'id': 'isr_ret',
            'name' : 'Assimilated ISR retention', 
            'columns': [
                        ],
            'level': 1,
            'unfolded': True,
            'class':'text-left',
        })

        lines.append({
            'id': 'vat_fees',
            'name' : 'VAT Withholding Fees 10.67%', 
            'columns': [
                         
                        ],
            'level': 1,
            'unfolded': True,
            'class':'text-left',
        })

        lines.append({
            'id': 'isr_fees',
            'name' : 'ISR Withholding Fees 10%', 
            'columns': [
                         
                        ],
            'level': 1,
            'unfolded': True,
            'class':'text-left',
        })

        lines.append({
            'id': 'isr_lease',
            'name' : 'ISR Retention Lease 10%', 
            'columns': [
                         
                        ],
            'level': 1,
            'unfolded': True,
            'class':'text-left',
        })

        lines.append({
            'id': 'vat_lease',
            'name' : 'VAT Withholding Lease 10.67%', 
            'columns': [
                         
                        ],
            'level': 1,
            'unfoldable': True,
            'class':'text-left',
        })

        return lines
