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
from odoo.tools import config, date_utils, get_lang
from odoo.tools.misc import xlsxwriter
import base64
import lxml.html
import io

class StateOfVariation(models.AbstractModel):
    _name = "jt_conac.state.of.variation.report"
    _inherit = "jt_conac.coa.conac.report"
    _description = "State of Variation in the Public Treasury"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = False
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_unposted_in_period = False
    MAX_LINES = None


    def _get_columns_name(self, options):
        return [
            {'name': _('Concepto')},
            {'name': _('Hacienda Pública / Patrimonio Contribuido')},
            {'name': _('Patrimonio Generado de Ejercicios Anteriores')},
            {'name': _('Patrimonio Generado del Ejercicio')},
            {'name': _('Exceso o Insuficiencia en la Actualización de la Hacienda Pública / Patrimonio')},
            {'name': _('Total')},
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
                    'columns': [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''},{'name': ''}],
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
                    level_1_col_5 = level_1_col_2 + level_1_col_3

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
                            level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''},{'name': ''}]
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
                                    level_3_col_4 = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                    level_2_col_4 += level_3_col_4 
                                    level_1_col_4 += level_3_col_4
                                    total_col4 += level_3_col_4
                                    
                                level_3_columns = [{'name': ''}, {'name': ''}, {'name': ''},
                                                    self._format({'name': level_3_col_4},figure_type='float'),self._format({'name': level_3_col_4},figure_type='float')]

                            elif level_3_line.code == '3.1.1.0' or level_3_line.code == '3.1.2.0' or level_3_line.code == '3.1.3.0':
                                if move_lines:
                                    level_3_col_1 = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                    level_2_col_1 += level_3_col_1 
                                    level_1_col_1 += level_3_col_1
                                    total_col1 += level_3_col_1
                                    
                                level_3_columns = [self._format({'name': level_3_col_1},figure_type='float'),
                                                   {'name': ''}, {'name': ''}, {'name': ''},self._format({'name': level_3_col_1},figure_type='float')]

                            elif level_3_line.code == '3.2.1.0':
                                if move_lines:
                                    level_3_col_3 = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                    level_2_col_3 += level_3_col_3 
                                    level_1_col_3 += level_3_col_3
                                    total_col3 += level_3_col_3
                                    
                                level_3_columns = [{'name': ''}, {'name': ''},self._format({'name': level_3_col_3},figure_type='float'),
                                                    {'name': ''},self._format({'name': level_3_col_3},figure_type='float')]

                            elif level_2_line.code == '3.2.2.0' or level_2_line.code == '3.2.3.0' or level_2_line.code == '3.2.4.0' or level_2_line.code == '3.2.5.0':
                                if move_lines:
                                    level_3_col_2 = (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                    level_2_col_2 += level_3_col_2 
                                    level_1_col_2 += level_3_col_2
                                    total_col2 += level_3_col_2
                                    
                                level_3_columns = [{'name': ''}, self._format({'name': level_3_col_2},figure_type='float'),{'name': ''},
                                                    {'name': ''},self._format({'name': level_3_col_2},figure_type='float')]
                                
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
                        
                        level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''},{'name': ''}]
                        if level_2_line.code == '3.3.0.0':
                            level_2_columns = [{'name': ''}, {'name': ''}, {'name': ''}, 
                                               self._format({'name': level_2_col_4},figure_type='float'),self._format({'name': level_2_col_4},figure_type='float')]
                            
                        elif level_2_line.code == '3.3.1.0' or level_2_line.code == '3.3.2.0':
                            if move_lines:
                                level_2_col_4 += (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                total_col4 += level_2_col_4
                                level_1_col_4 += level_2_col_4
                            level_2_columns = [
                                               {'name': ''}, {'name': ''}, {'name': ''},self._format({'name': level_2_col_4},figure_type='float'),self._format({'name': level_2_col_4},figure_type='float')]

                        elif level_2_line.code == '3.1.1.0' or level_2_line.code == '3.1.2.0' or level_2_line.code == '3.1.3.0':
                            if move_lines:
                                level_2_col_1 += (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                total_col1 += level_2_col_1
                                level_1_col_1 += level_2_col_1
                            level_2_columns = [self._format({'name': level_2_col_1},figure_type='float'),
                                                {'name': ''}, {'name': ''}, {'name': ''},self._format({'name': level_2_col_1},figure_type='float')]

                        elif level_2_line.code == '3.2.1.0':
                            if move_lines:
                                level_2_col_3 += (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                total_col3 += level_2_col_3
                                level_1_col_3 += level_2_col_3
                            level_2_columns = [{'name': ''}, {'name': ''},self._format({'name': level_2_col_3},figure_type='float'),
                                                 {'name': ''},self._format({'name': level_2_col_3},figure_type='float')]

                        elif level_2_line.code == '3.2.2.0' or level_2_line.code == '3.2.3.0' or level_2_line.code == '3.2.4.0' or level_2_line.code == '3.2.5.0':
                            if move_lines:
                                level_2_col_2 += (sum(move_lines.mapped('credit')) - sum(move_lines.mapped('debit')))
                                total_col2 += level_2_col_2
                                level_1_col_2 += level_2_col_2
                            level_2_columns = [{'name': ''}, self._format({'name': level_2_col_2},figure_type='float'),{'name': ''},
                                                 {'name': ''},self._format({'name': level_2_col_2},figure_type='float')]
                        
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

                    level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, {'name': ''},{'name': ''}]
                    if level_1_line.code == '3.3.0.0':
                        level_1_columns = [{'name': ''}, {'name': ''}, {'name': ''}, 
                                           self._format({'name': level_1_col_4},figure_type='float'),self._format({'name': level_1_col_4},figure_type='float')]

                    elif level_1_line.code == '3.1.0.0':
                        level_1_columns = [self._format({'name': level_1_col_1},figure_type='float'),
                                           {'name': ''}, {'name': ''}, {'name': ''},self._format({'name': level_1_col_1},figure_type='float') ]

                    elif level_1_line.code == '3.2.0.0':
                        level_1_columns = [{'name': ''},
                                           self._format({'name': level_1_col_2},figure_type='float'),
                                           self._format({'name': level_1_col_3},figure_type='float'), 
                                            {'name': ''}, self._format({'name': level_1_col_5},figure_type='float'),]


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
                                self._format({'name': total_col4},figure_type='float'),
                                {'name': ''},]

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
        body_html = self.with_context(print_mode=True,get_sign_col=True).get_html(options)
        body_html = body_html.replace(b'<div class="o_account_reports_header">',b'<div>')

        body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)
        if minimal_layout:
            header = ''
            footer = self.env['ir.actions.report'].render_template("web.internal_layout", values=rcontext)
            spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 10}
            footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
        else:
            start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
            end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
            rcontext.update({
                    'css': '',
                    'o': self.env.user,
                    'res_company': self.env.company,
                    'start' : start,
                    'end' : end
                })
            header = self.env['ir.actions.report'].render_template("jt_conac.external_layout_of_state_variation", values=rcontext)
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

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        currect_date_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'right'})
        currect_date_style.set_border(0)
        super_col_style.set_border(0)
        # Set the first column width to 50
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 17)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 12)
        super_columns = self._get_super_columns(options)
        y_offset = 0
        col = 0

        sheet.merge_range(y_offset, col, 6, col, '', super_col_style)
        if self.env.user and self.env.user.company_id and self.env.user.company_id.header_logo:
            filename = 'logo.png'
            image_data = io.BytesIO(base64.standard_b64decode(
                self.env.user.company_id.header_logo))
            sheet.insert_image(0, 0, filename, {
                               'image_data': image_data, 'x_offset': 8, 'y_offset': 3, 'x_scale': 0.6, 'y_scale': 0.6})

        col += 1
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        header_title = _('''NATIONAL AUTONOMOUS UNIVERSITY OF MEXICO\nSTATE OF VARIATION IN THE PUBLIC TREASURY''')
        header_title += "\n"
        header_title += str(start.strftime(' %d %B'))
        header_title += _(" OF ")
        header_title += str(start.strftime(' %Y'))
        header_title += _(" AND ")
        header_title += str(end.strftime(' %d %B'))
        header_title += _(" OF ")
        header_title += str(end.strftime(' %Y'))
        sheet.merge_range(y_offset, col, 5, col + 6,
                          header_title, super_col_style)
        y_offset += 6
        col = 1
        currect_time_msg = "Fecha y hora de impresión: "
        currect_time_msg += datetime.today().strftime('%d/%m/%Y %H:%M')
        sheet.merge_range(y_offset, col, y_offset, col + 6,
                          currect_time_msg, currect_date_style)
        y_offset += 1
        for row in self.get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace(
                    '<br/>', ' ').replace('&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset,
                                      x + colspan - 1, header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update({'no_format': True, 'print_mode': True,
                    'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        # write all data rows
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
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the
            # indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(
                    y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(
                    lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(
                        y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(
                        y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file

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
                    'options': options,
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
    
    
