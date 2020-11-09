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


class SummaryOfOperationMaturities(models.AbstractModel):
    _name = "jt_investment.summary.of.operation.maturities"
    _inherit = "account.coa.report"
    _description = "Summary of Operation - Maturities"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
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
            SummaryOfOperationMaturities, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Recurso')},
            {'name': _('Institución financiera')},
            {'name': _('Contrato')},
            {'name': _('Cta Bancaria')},
            {'name': _('Inversión')},
            {'name': _('Producto')},
            {'name': _('Plazo')},
            {'name': _('Tasa Interés')},
            {'name': _('Intereses')},
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

        cetes_records = self.env['investment.cetes'].search([('state','=','confirmed'),('date_time','>=',start),('date_time','<=',end)])
        udibonos_records = self.env['investment.udibonos'].search([('state','=','confirmed'),('date_time','>=',start),('date_time','<=',end)])
        bonds_records = self.env['investment.bonds'].search([('state','=','confirmed'),('date_time','>=',start),('date_time','<=',end)])
        will_pay_records = self.env['investment.will.pay'].search([('state','=','confirmed'),('date_time','>=',start),('date_time','<=',end)])
        sale_security_ids = self.env['purchase.sale.security'].search([('state','in',('confirmed','done')),('invesment_date','>=',start),('invesment_date','<=',end)])
        productive_ids = self.env['investment.investment'].search([('state','in',('confirmed','done')),('invesment_date','>=',start),('invesment_date','<=',end)])
                    
#         cetes_records = self.env['investment.cetes'].search([('date_time','>=',start),('date_time','<=',end)])
#         udibonos_records = self.env['investment.udibonos'].search([('date_time','>=',start),('date_time','<=',end)])
#         bonds_records = self.env['investment.bonds'].search([('date_time','>=',start),('date_time','<=',end)])
#         will_pay_records = self.env['investment.will.pay'].search([('date_time','>=',start),('date_time','<=',end)])
#         sale_security_ids = self.env['purchase.sale.security'].search([('invesment_date','>=',start),('invesment_date','<=',end)])
#         productive_ids = self.env['investment.investment'].search([('invesment_date','>=',start),('invesment_date','<=',end)],order='invesment_date')
        
        total_investment = 0

        #==== Sale Security========#        
        for sale in sale_security_ids:
            #total_investment += cetes.nominal_value
            resouce_name = sale.fund_id and sale.fund_id.name or ''
            term = sale.number_of_titles
            total_investment += sale.amount
            
            interest = ((sale.amount*sale.price/100)*term/360)
            lines.append({
                'id': 'hierarchy_sale' + str(sale.id),
                'name' : resouce_name, 
                'columns': [ {'name': sale.journal_id and sale.journal_id.bank_id and sale.journal_id.bank_id.name or ''},
                            {'name': sale.contract_id and sale.contract_id.name or ''}, 
                            {'name': sale.journal_id and sale.journal_id.bank_account_id and sale.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': sale.amount},figure_type='float'),
                            {'name': 'Securities'},
                            {'name': term},
                            self._format({'name': sale.price},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        #==== CETES========#        
        for cetes in cetes_records:
            total_investment += cetes.nominal_value
            resouce_name = cetes.fund_id and cetes.fund_id.name or ''
            term = 0
            if cetes.term:
                term =int(cetes.term)
                 
            interest = ((cetes.nominal_value*cetes.yield_rate/100)*term/360)
            lines.append({
                'id': 'hierarchy_cetes' + str(cetes.id),
                'name' : resouce_name, 
                'columns': [ {'name': cetes.bank_id and cetes.bank_id.name or ''},
                            {'name': cetes.contract_id and cetes.contract_id.name or ''}, 
                            {'name': cetes.journal_id and cetes.journal_id.bank_account_id and cetes.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': cetes.nominal_value},figure_type='float'),
                            {'name': 'CETES'},
                            {'name': cetes.term},
                            self._format({'name': cetes.yield_rate},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        #==== udibonos========#
        for udibonos in udibonos_records:
            total_investment += udibonos.nominal_value
            resouce_name = udibonos.fund_id and udibonos.fund_id.name or ''
            
            interest = ((udibonos.nominal_value*udibonos.interest_rate/100)*udibonos.time_for_each_cash_flow/360)
            lines.append({
                'id': 'hierarchy_udibonos' + str(udibonos.id),
                'name': resouce_name,
                'columns': [ {'name': udibonos.bank_id and udibonos.bank_id.name or ''},
                            {'name': udibonos.contract_id and udibonos.contract_id.name or ''}, 
                            {'name': udibonos.journal_id and udibonos.journal_id.bank_account_id and udibonos.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': udibonos.nominal_value},figure_type='float'),
                            {'name': 'UDIBONOS'},
                            {'name': udibonos.time_for_each_cash_flow},
                            self._format({'name': udibonos.interest_rate},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        #==== bonds========#
        for bonds in bonds_records:
            total_investment += bonds.nominal_value
            resouce_name = bonds.fund_id and bonds.fund_id.name or ''
            
            interest = ((bonds.nominal_value*bonds.interest_rate/100)*bonds.time_for_each_cash_flow/360)
            
            lines.append({
                'id': 'hierarchy_bonds' + str(bonds.id),
                'name': resouce_name,
                'columns': [ {'name': bonds.bank_id and bonds.bank_id.name or ''},
                            {'name': bonds.contract_id and bonds.contract_id.name or ''}, 
                            {'name': bonds.journal_id and bonds.journal_id.bank_account_id and bonds.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': bonds.nominal_value},figure_type='float'),
                            {'name': 'BONOS'},
                            {'name': bonds.time_for_each_cash_flow},
                            self._format({'name': bonds.interest_rate},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        #==== Pay========#
        for pay in will_pay_records:
            total_investment += pay.amount
            resouce_name = pay.fund_id and pay.fund_id.name or ''
            
            interest = ((pay.amount*pay.interest_rate/100)*pay.term_days/360)
            
            lines.append({
                'id': 'hierarchy_bonds' + str(pay.id),
                'name': resouce_name,
                'columns': [ {'name': pay.bank_id and pay.bank_id.name or ''},
                            {'name': pay.contract_id and pay.contract_id.name or ''}, 
                            {'name': pay.journal_id and pay.journal_id.bank_account_id and pay.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': pay.amount},figure_type='float'),
                            {'name': 'PAGARE'},
                            {'name': pay.term_days},
                            self._format({'name': pay.interest_rate},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        #==== Productive Accounts ========#
        
        for pro in productive_ids:
            total_investment += pro.amount_to_invest

            term = 0
            if pro.is_fixed_rate:
                term = pro.term
            if pro.is_variable_rate:
                term = pro.term_variable
            
            resouce_name = pro.fund_id and pro.fund_id.name or ''
            
            interest = ((pro.amount_to_invest * pro.interest_rate/100)*term/360)
            
            lines.append({
                'id': 'hierarchy_pro' + str(pro.id),
                'name': resouce_name,
                'columns': [ {'name': pro.journal_id and pro.journal_id.bank_id and pro.journal_id.bank_id.name or ''},
                            {'name': pro.contract_id and pro.contract_id.name or ''}, 
                            {'name': pro.journal_id and pro.journal_id.bank_account_id and pro.journal_id.bank_account_id.acc_number or ''},
                            self._format({'name': pro.amount_to_invest},figure_type='float'),
                            {'name': 'Productive Accounts'},
                            {'name': term},
                            self._format({'name': pro.interest_rate},figure_type='float'),
                            self._format({'name': interest},figure_type='float'),
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })
        
        lines.append({
            'id': 'hierarchy_res_total',
            'name': '',
            'columns': [{'name': 'Total Recursos'}, 
                        {'name': ''}, 
                        {'name': ''},
                        self._format({'name': total_investment},figure_type='float'),
                        {'name': ''},
                        {'name': ''},
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        
        #===================== Bank Data ==========#

        journal_ids = self.env['res.bank']
        journal_ids += cetes_records.mapped('bank_id')
        journal_ids += udibonos_records.mapped('bank_id')
        journal_ids += bonds_records.mapped('bank_id')
        journal_ids += will_pay_records.mapped('bank_id')
        journal_ids += sale_security_ids.mapped('journal_id.bank_id')
        journal_ids += productive_ids.mapped('journal_id.bank_id')
                
        if journal_ids:
            journals = list(set(journal_ids.ids))
            journal_ids = self.env['res.bank'].browse(journals)
            
        lines.append({
            'id': 'hierarchy_inst' ,
            'name': '',
            'columns': [{'name': 'Institución'}, 
                        {'name': ''}, 
                        {'name': ''},
                        {'name': ''},
                        {'name': ''},
                        {'name': ''},
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        
        total_ins = 0
        for journal in journal_ids:
            amount = 0
            amount += sum(x.nominal_value for x in cetes_records.filtered(lambda x:x.bank_id.id==journal.id))
            amount += sum(x.nominal_value for x in udibonos_records.filtered(lambda x:x.bank_id.id==journal.id))
            amount += sum(x.nominal_value for x in bonds_records.filtered(lambda x:x.bank_id.id==journal.id))
            amount += sum(x.amount for x in will_pay_records.filtered(lambda x:x.bank_id.id==journal.id))
            amount += sum(x.amount for x in sale_security_ids.filtered(lambda x:x.journal_id.bank_id.id==journal.id))
            amount += sum(x.amount_to_invest for x in productive_ids.filtered(lambda x:x.journal_id.bank_id.id==journal.id))                        
            
            total_ins += amount
            lines.append({
                'id': 'hierarchy_jr' + str(journal.id),
                'name': '',
                'columns': [{'name': journal.name}, 
                            {'name': ''}, 
                            {'name': ''},
                            self._format({'name': amount},figure_type='float'),
                            {'name': ''},
                            {'name': ''},
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        lines.append({
            'id': 'hierarchy_inst_total' ,
            'name': '',
            'columns': [{'name': 'Institución'}, 
                        {'name': ''}, 
                        {'name': ''},
                        self._format({'name': total_ins},figure_type='float'),
                        {'name': ''},
                        {'name': ''},
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })

        #================ Origin Data ====================#
        origin_ids = self.env['agreement.fund']

        origin_ids += cetes_records.mapped('fund_id')        
        origin_ids += udibonos_records.mapped('fund_id')        
        origin_ids += bonds_records.mapped('fund_id')
        origin_ids += will_pay_records.mapped('fund_id')
        origin_ids += will_pay_records.mapped('fund_id')
        origin_ids += will_pay_records.mapped('fund_id')

        if origin_ids:
            origins = list(set(origin_ids.ids))
            origin_ids = self.env['agreement.fund'].browse(origins)

        lines.append({
            'id': 'hierarchy_origin_total' ,
            'name': '',
            'columns': [{'name': 'Tipo de recurso'}, 
                        {'name': ''}, 
                        {'name': ''},
                        {'name': ''},
                        {'name': ''},
                        {'name': ''},
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        
        total_ins = 0
        for origin in origin_ids:
            amount = 0
            amount += sum(x.nominal_value for x in cetes_records.filtered(lambda x:x.fund_id.id==origin.id))
            amount += sum(x.nominal_value for x in udibonos_records.filtered(lambda x:x.fund_id.id==origin.id))
            amount += sum(x.nominal_value for x in bonds_records.filtered(lambda x:x.fund_id.id==origin.id))
            amount += sum(x.amount for x in will_pay_records.filtered(lambda x:x.fund_id.id==origin.id))
            amount += sum(x.amount for x in sale_security_ids.filtered(lambda x:x.fund_id.id==origin.id))
            amount += sum(x.amount_to_invest for x in productive_ids.filtered(lambda x:x.fund_id.id==origin.id))                        
            
            
            total_ins += amount
            lines.append({
                'id': 'hierarchy_or' + str(origin.id),
                'name': '',
                'columns': [{'name': origin.name}, 
                            {'name': ''}, 
                            {'name': ''},
                            self._format({'name': amount},figure_type='float'),
                            {'name': ''},
                            {'name': ''},
                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        lines.append({
            'id': 'hierarchy_total_or' ,
            'name': '',
            'columns': [{'name': 'Total'}, 
                        {'name': ''}, 
                        {'name': ''},
                        self._format({'name': total_ins},figure_type='float'),
                        {'name': ''},
                        {'name': ''},
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        
        return lines

    def _get_report_name(self):
        return _("Summary of Operation - Maturities")
    
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
        sheet.set_column(0, 0,20)
        sheet.set_column(1, 1,15)
        sheet.set_column(2, 2,15)
        sheet.set_column(3, 3,15)
        sheet.set_column(4, 4,10)
        sheet.set_column(5, 5,10)
        sheet.set_column(6, 6,10)
        sheet.set_column(7, 7,10)
        super_columns = self._get_super_columns(options)
        y_offset = 0
        col = 0
        
        sheet.merge_range(y_offset, col, 6, col, '',super_col_style)
        if self.env.user and self.env.user.company_id and self.env.user.company_id.header_logo:
            filename = 'logo.png'
            image_data = io.BytesIO(base64.standard_b64decode(self.env.user.company_id.header_logo))
            sheet.insert_image(0,0, filename, {'image_data': image_data,'x_offset':8,'y_offset':3,'x_scale':0.6,'y_scale':0.6})
        
        col += 1
        header_title = '''UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICOO\nUNIVERSITY BOARD\nDIRECCIÓN GENERAL DE FINANZAS\nSUBDIRECCION DE FINANZAS\nRESUMEN DE OPERACIÓN - VENCIMIENTOS'''
        sheet.merge_range(y_offset, col, 5, col+6, header_title,super_col_style)
        y_offset += 6
        col=1
        currect_time_msg = "Fecha y hora de impresión: "
        currect_time_msg += datetime.today().strftime('%d/%m/%Y %H:%M')
        sheet.merge_range(y_offset, col, y_offset, col+6, currect_time_msg,currect_date_style)
        y_offset += 1
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

    def get_pdf(self, options, minimal_layout=True):
        # As the assets are generated during the same transaction as the rendering of the
        # templates calling them, there is a scenario where the assets are unreachable: when
        # you make a request to read the assets while the transaction creating them is not done.
        # Indeed, when you make an asset request, the controller has to read the `ir.attachment`
        # table.
        # This scenario happens when you want to print a PDF report for the first time, as the
        # assets are not in cache and must be generated. To workaround this issue, we manually
        # commit the writes in the `ir.attachment` table. It is done thanks to a key in the context.
        minimal_layout = False
        if not config['test_enable']:
            self = self.with_context(commit_assetsbundle=True)

        base_url = self.env['ir.config_parameter'].sudo().get_param('report.url') or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        rcontext = {
            'mode': 'print',
            'base_url': base_url,
            'company': self.env.company,
        }

        body = self.env['ir.ui.view'].render_template(
            "account_reports.print_template",
            values=dict(rcontext),
        )
        body_html = self.with_context(print_mode=True).get_html(options)

        body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)
        if minimal_layout:
            header = ''
            footer = self.env['ir.actions.report'].render_template("web.internal_layout", values=rcontext)
            spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 10}
            footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
        else:
            rcontext.update({
                    'css': '',
                    'o': self.env.user,
                    'res_company': self.env.company,
                })
            header = self.env['ir.actions.report'].render_template("jt_investment.external_layout_summary_of_operation_maturities", values=rcontext)
            header = header.decode('utf-8') # Ensure that headers and footer are correctly encoded
            spec_paperformat_args = {}
            # Default header and footer in case the user customized web.external_layout and removed the header/footer
            headers = header.encode()
            footer = b''
            # parse header as new header contains header, body and footer
            try:
                root = lxml.html.fromstring(header)
                match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

                for node in root.xpath(match_klass.format('header')):
                    headers = lxml.html.tostring(node)
                    headers = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=headers))

                for node in root.xpath(match_klass.format('footer')):
                    footer = lxml.html.tostring(node)
                    footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))

            except lxml.etree.XMLSyntaxError:
                headers = header.encode()
                footer = b''
            header = headers

        landscape = False
        if len(self.with_context(print_mode=True).get_header(options)[-1]) > 5:
            landscape = True

        return self.env['ir.actions.report']._run_wkhtmltopdf(
            [body],
            header=header, footer=footer,
            landscape=landscape,
            specific_paperformat_args=spec_paperformat_args
        )

    def get_html(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        # Check the security before updating the context to make sure the options are safe.
        self._check_report_security(options)

        # Prevent inconsistency between options and context.
        self = self.with_context(self._set_context(options))

        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        report = {'name': self._get_report_name(),
                'summary': report_manager.summary,
                'company_name': self.env.company.name,}
        report = {}
        #options.get('date',{}).update({'string':''}) 
        lines = self._get_lines(options, line_id=line_id)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
            # we don't know all the visible lines.
            footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})

        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_header(options), 'lines': lines},
                    'options': {},
                    'context': self.env.context,
                    'model': self,
                }
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        if self.env.context.get('analytic_account_ids'):
            rcontext['options']['analytic_account_ids'] = [
                {'id': acc.id, 'name': acc.name} for acc in self.env.context['analytic_account_ids']
            ]

        render_template = templates.get('main_template', 'account_reports.main_template')
        if line_id is not None:
            render_template = templates.get('line_template', 'account_reports.line_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        if self.env.context.get('print_mode', False):
            for k,v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(b'<div class="js_account_report_footnotes"></div>', self.get_html_footnotes(footnotes_to_render))
        return html
