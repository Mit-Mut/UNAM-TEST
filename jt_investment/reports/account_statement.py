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
from datetime import timedelta

class InvestmentAccountStatement(models.AbstractModel):
    _name = "jt_investment.account.statement"
    _inherit = "account.coa.report"
    _description = "Account Statement"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = None
    filter_all_entries = True
    filter_journals = True
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
            InvestmentAccountStatement, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Fecha')},
            {'name':_('Concepto de aplicación')},
            {'name': _('Referencia')},
            {'name': _('Saldo Inicial')},
            {'name': _('Incrementos')},
            {'name': _('Retiros')},
             {'name': _('Saldo Final')},
        ]

    def _format(self, value, figure_type,digit):
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

    @api.model
    def _get_filter_journals(self):
        return self.env['account.journal'].search([('type','=','bank'),
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
        ], order="company_id, name")

    def _get_lines(self, options, line_id=None):
        lines = []
        lang = self.env.user.lang
        if options.get('all_entries') is False:
            domain=[('line_state','in',('confirmed','done'))]
        else:
            domain=[('line_state','not in',('rejected','canceled'))]

        journal = self._get_options_journals_domain(options)
        if journal:
            domain+=journal

        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()

        productive_domain = domain + [('date_required','>=',start),('date_required','<=',end)]
        productive_ids = self.env['investment.operation'].search(productive_domain)
        
        g_total_inc = 0
        g_total_with = 0
        g_total_final = 0

        header_intial = 0
        header_increment = 0
        header_withdrawal = 0
        
        #===== Investment =======#
        journal_ids = productive_ids.mapped('investment_id.journal_id')
        for journal in journal_ids:
            capital = 0
            total_inc = 0
            total_with = 0
            total_final = 0
            final = 0
            
            records = productive_ids.filtered(lambda x:x.investment_id.journal_id.id == journal.id).sorted(key='date_required')
            lines.append({
                'id': 'hierarchy_account' + str(journal.id),
                'name' :journal.name, 
                'columns': [ 
                            {'name': ''},
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
            pre_date = start
            for rec in records:
                invesment_date = ''
                if pre_date != rec.date_required:
                    day_diff = rec.date_required - pre_date
                    day_diff = day_diff.days + 1
                    for r in range(1,day_diff):
                        lines.append({
                            'id': 'hierarchy_account_date' + str(r),
                            'name' :pre_date, 
                            'columns': [
                                        {'name':''},
                                        {'name': ''},
                                        self._format({'name': capital},figure_type='float',digit=2),
                                        self._format({'name': 0.0},figure_type='float',digit=2),
                                        self._format({'name': 0.0},figure_type='float',digit=2),
                                        self._format({'name': final},figure_type='float',digit=2),
                                        ],
                            'level': 3,
                            'unfoldable': False,
                            'unfolded': True,
                        })
                         
                        pre_date = pre_date + timedelta(days=1)
                
                inc = 0 
                withdraw = 0
                if rec.type_of_operation in ('increase','increase_by_closing','open_bal'):
                    inc = rec.amount
                    total_inc += inc
                    g_total_inc += inc
                elif rec.type_of_operation in ('retirement','withdrawal','withdrawal_cancellation','withdrawal_closure'):
                    withdraw = rec.amount
                    total_with += withdraw
                    g_total_with += withdraw
                    
                if rec.date_required:
                    invesment_date = rec.date_required.strftime('%Y-%m-%d') 
                final = capital + inc - withdraw
                total_final += final

                movement = dict(rec._fields['type_of_operation'].selection).get(rec.type_of_operation)
                if movement=='Opening Balance':
                    movement = 'Importe de apertura'
                elif movement=='Increase':
                    movement = 'Incremento'
                elif movement=='Retirement':
                    movement = 'Retiro'
                elif movement=='Withdrawal for settlement':
                    movement = 'Retiro por liquidación'
                elif movement=='Withdrawal Due to Cancellation':
                    movement = 'Retiro por cancelación'
                elif movement=='Withdrawal due to closure':
                    movement = 'Retiro por cierre'
                elif movement=='Increase by closing':
                    movement = 'Incremento por cierre'
                header_intial += capital
                header_increment += inc
                header_withdrawal += withdraw
                lines.append({
                    'id': 'hierarchy_account' + str(rec.id),
                    'name' :invesment_date, 
                    'columns': [
                                {'name':rec.concept},
                                {'name': movement},
                                self._format({'name': capital},figure_type='float',digit=2),
                                self._format({'name': inc},figure_type='float',digit=2),
                                self._format({'name': withdraw},figure_type='float',digit=2),
                                self._format({'name': final},figure_type='float',digit=2),
                                ],
                    'level': 3,
                    'unfoldable': False,
                    'unfolded': True,
                })
                capital = capital + inc - withdraw
                pre_date = rec.date_required + timedelta(days=1)
            
#             if pre_date != start:
#                 pre_date = pre_date + timedelta(days=1)
#             if pre_date == start and records:
#                 pre_date = pre_date + timedelta(days=1)
            if pre_date != end:
                day_diff = end - pre_date
                day_diff = day_diff.days + 2
                for r in range(1,day_diff):
                    lines.append({
                        'id': 'hierarchy_account_date' + str(r),
                        'name' :pre_date, 
                        'columns': [
                                    {'name':''},
                                    {'name': ''},
                                    self._format({'name': capital},figure_type='float',digit=2),
                                    self._format({'name': 0.0},figure_type='float',digit=2),
                                    self._format({'name': 0.0},figure_type='float',digit=2),
                                    self._format({'name': final},figure_type='float',digit=2),
                                    ],
                        'level': 3,
                        'unfoldable': False,
                        'unfolded': True,
                    })
                    pre_date = pre_date + timedelta(days=1)
             
            lines.append({
                'id': 'Total',
                'name' :'Total', 
                'columns': [ 
                            {'name':''},
                            {'name': ''},
                            {'name': ''},
                            self._format({'name': total_inc},figure_type='float',digit=2),
                            self._format({'name': total_with},figure_type='float',digit=2),
                            self._format({'name': final},figure_type='float',digit=2),
                            ],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            g_total_final += final
        lines.append({
            'id': 'g_Total',
            'name' :'Grand Total', 
            'columns': [ 
                        {'name':''},
                        {'name': ''},
                        {'name': ''},
                        self._format({'name': g_total_inc},figure_type='float',digit=2),
                        self._format({'name': g_total_with},figure_type='float',digit=2),
                        self._format({'name': g_total_final},figure_type='float',digit=2),
                        ],
            'level': 1,
            'unfoldable': False,
            'unfolded': True,
        })
        options.update({'intial': header_intial, 'increment': header_increment, 'withdrawal': header_withdrawal})
        return lines
        

    def _get_report_name(self):
        return _("Account Statements")

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
        sheet.set_column(1, 1,17)
        sheet.set_column(2, 2,20)
        sheet.set_column(3, 3,15)
        sheet.set_column(4, 4,10)
        sheet.set_column(5, 5,15)
        sheet.set_column(6, 6,12)
        super_columns = self._get_super_columns(options)
        y_offset = 0
        col = 0
        
        sheet.merge_range(y_offset, col, 6, col, '',super_col_style)
        if self.env.user and self.env.user.company_id and self.env.user.company_id.header_logo:
            filename = 'logo.png'
            image_data = io.BytesIO(base64.standard_b64decode(self.env.user.company_id.header_logo))
            sheet.insert_image(0,0, filename, {'image_data': image_data,'x_offset':8,'y_offset':3,'x_scale':0.6,'y_scale':0.6})
        
        col += 1
        header_title = '''UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICOO\nDIRECCIÓN GENERAL DE FINANZAS\nSUBDIRECCION DE FINANZAS\nCOMITÉ DE INVERSIONES'''
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

    def get_month_name(self, month):
        month_name = ''
        if month == 1:
            month_name = 'Enero'
        elif month == 2:
            month_name = 'Febrero'
        elif month == 3:
            month_name = 'Marzo'
        elif month == 4:
            month_name = 'Abril'
        elif month == 5:
            month_name = 'Mayo'
        elif month == 6:
            month_name = 'Junio'
        elif month == 7:
            month_name = 'Julio'
        elif month == 8:
            month_name = 'Agosto'
        elif month == 9:
            month_name = 'Septiembre'
        elif month == 10:
            month_name = 'Octubre'
        elif month == 11:
            month_name = 'Noviembre'
        elif month == 12:
            month_name = 'Diciembre'

        return month_name.upper()

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
            period_name = ''
            start_date = datetime.strptime(options.get('date').get('date_from'), DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.strptime(options.get('date').get('date_to'), DEFAULT_SERVER_DATE_FORMAT)
            if start_date and end_date:
                period_name += "Del " + str(start_date.day)

                period_name += ' ' + self.get_month_name(start_date.month)
                if start_date.year != end_date.year:
                    period_name += ' ' + str(start_date.year)

                period_name += " al " + str(end_date.day) + " de " + self.get_month_name(end_date.month) + " " \
                               + str(end_date.year)
            header_intial = options.get('intial')
            header_withdrawal = options.get('withdrawal')
            header_increment = options.get('increment')
            actual = (header_increment + header_intial) - header_withdrawal
            rcontext.update({
                'css': '',
                'o': self.env.user,
                'res_company': self.env.company,
                'period_name': period_name,
                'name': 'CUENTAS PRODUCTIVAS',
                'intial': str(self._format({'name': header_intial},figure_type='float',digit=2).get('name')),
                'increment': str(self._format({'name': header_increment},figure_type='float',digit=2).get('name')),
                'withdrawal': str(self._format({'name': header_withdrawal},figure_type='float',digit=2).get('name')),
                'actual': str(self._format({'name': actual},figure_type='float',digit=2).get('name')),
                'extra_data': True
            })
            header = self.env['ir.actions.report'].with_context(period_name=period_name).render_template(
                "jt_investment.external_layout_investment_committee",
                values=rcontext)
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

