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
from odoo.tools.misc import xlsxwriter
import io
import base64

class SummaryofOperationsBankTransactions(models.AbstractModel):
    _name = "jt_finance.summary.of.operations.bank.transactions"
    _inherit = "account.coa.report"
    _description = "Summary of Operations - Bank Transactions"

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
            SummaryofOperationsBankTransactions, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('No.')},
            {'name': _('BANCO RETIRO')},
            {'name': _('CUENTA')},
            {'name': _('INTERBANCARIO')},
            {'name': _('BANCARIO')},
            {'name': _('CHEQUE')},
            {'name': _('BANCO DEPOSITO')},
            {'name': _('CUENTA DEPOSITO')},
            {'name': _('CONCEPTO')},
            {'name': _('ESTATUS')},
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

        lines.append({
                'id': 'hierarchy1_EXPENSE',
                'name': 'COBERTURA DE EGRESOS',
                'columns': [{'name': ''}, {'name': ''},{'name': ''},{'name': ''},{'name': ''},{'name': ''},{'name': ''},{'name': ''},{'name': ''}],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
        bank_transfer_requests = self.env['bank.transfer.request'].search([('application_date', '>=', start), ('application_date', '<=', end),])
        total_amount = 0
        for transfer in bank_transfer_requests:
            total_amount += transfer.amount
            state = dict(transfer._fields['state'].selection).get(transfer.state)
            lines.append({
                    'id': 'hierarchy1_'+str(transfer.id),
                    'name': transfer.name,
                    'columns': [{'name': transfer.origin_bank_id and transfer.origin_bank_id.name or ''}, 
                                {'name': transfer.origin_bank_account_id and transfer.origin_bank_account_id.acc_number or ''},
                                {'name': ''},
                                self._format({'name': transfer.amount},figure_type='float'),
                                {'name': ''},
                                {'name': transfer.bank_id and transfer.bank_id.name or ''},
                                {'name': transfer.bank_account_id and transfer.bank_account_id.acc_number or ''},
                                {'name': transfer.concept},
                                {'name': state}],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                })
        if total_amount:
            lines.append({
                    'id': 'hierarchy_total',
                    'name': '',
                    'columns': [{'name': ''}, 
                                {'name': ''},
                                {'name': ''},
                                self._format({'name': total_amount},figure_type='float'),
                                {'name': ''},
                                {'name': ''},
                                {'name': ''},
                                {'name': ''},
                                {'name': ''}],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                })
    
            lines.append({
                    'id': 'hierarchy_total_movement',
                    'name': '',
                    'columns': [{'name': ''}, 
                                {'name': ''},
                                {'name': ''},
                                {'name': ''},
                                {'name': ''},
                                {'name': ''},
                                {'name': 'TOTAL MOVIMIENTOS:'},
                                self._format({'name': total_amount},figure_type='float'),
                                {'name': ''}],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                })
            
        return lines

    def _get_report_name(self):
        return _("Bank Journal (Summary of Operations - Bank Transactions)")
    
    @api.model
    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 4}

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])
 
        date_default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        currect_date_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'right'})
        currect_date_style.set_border(0)
        super_col_style.set_border(0)
        #Set the first column width to 50
        super_columns = self._get_super_columns(options)
        sheet.set_column(0, 0,15)
        #y_offset = bool(super_columns.get('columns')) and 1 or 0
        #sheet.write(y_offset, 0,'', title_style)
        y_offset = 0
        col = 0
        
        sheet.merge_range(y_offset, col, 6, col, '',super_col_style)
#         if self.env.user and self.env.user.company_id and self.env.user.company_id.header_logo:
#          
#             image_data = io.BytesIO(base64.standard_b64decode(self.env.user.company_id.header_logo))
#             print ("image_data===",image_data)
#             sheet.insert_image('A0', 'logo.png', {'image_data': image_data})
        
        col += 1
        header_title = '''UNIVRSIDAD NACIONAL AUTÓNOMA DE MÉXICO\nPATRONATO UNIVERSITARIO\nDIRECCIÓN GENERAL DE FINANZAS\nSUBDIRECCION DE FINANZAS\nDepartamento de Control Financiero\n%s'''%self._get_report_name()
        sheet.merge_range(y_offset, col, 5, col+8, header_title,super_col_style)
        y_offset += 6
        col=1
        currect_time_msg = "Fecha y hora de impresión: "
        currect_time_msg += datetime.today().strftime('%d/%m/%Y %H:%M')
        sheet.merge_range(y_offset, col, y_offset, col+8, currect_time_msg,currect_date_style)
        y_offset += 1
        
        # Todo in master: Try to put this logic elsewhere
#         x = super_columns.get('x_offset', 0)
#         for super_col in super_columns.get('columns', []):
#             cell_content = super_col.get('string', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
#             x_merge = super_columns.get('merge')
#             if x_merge and x_merge > 1:
#                 sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content, super_col_style)
#                 x += x_merge
#             else:
#                 sheet.write(0, x, cell_content, super_col_style)
#                 x += 1
        for row in self.get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset, x + colspan - 1, header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update({'no_format':True, 'print_mode':True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)
 
        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)
 
        #write all data rows
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style
 
            #write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)
 
            #write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)
 
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file    
