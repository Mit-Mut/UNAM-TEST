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

from lxml import etree
from lxml.objectify import fromstring

from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.xml_utils import _check_with_xsd


from odoo import models, api, _, fields, tools
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
import io
import base64
from odoo.tools import config, date_utils, get_lang
import lxml.html


class StatusProgramReport(models.AbstractModel):

    _name = "jt_account_module_design.general.ledger.inherit"
    _inherit = "account.report"
    _description = "Trial Balance"

    filter_program_code_section = True
    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = True
    #filter_analytic = True
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    MAX_LINES = None
    
    
#     def _get_reports_buttons(self):
#         return [
#             {'name': _('Print Preview'), 'sequence': 1,
#              'action': 'print_pdf', 'file_export_type': _('PDF')},
#             {'name': _('Export (XLSX)'), 'sequence': 2,
#              'action': 'print_xlsx', 'file_export_type': _('XLSX')},
#         ]

#     @api.model
#     def _get_templates(self):
#         templates = super(StatusProgramReport, self)._get_templates()
#         templates['line_template'] = 'account_reports.line_template_general_ledger_report'
#         return templates
# 
# 
#     @api.model
#     def _get_columns_name(self, options):
#         return [
#             {'name': ''},
#             {'name': _('Date'), 'class': 'date'},
#             {'name': _('Communication')},
#             {'name': _('Partner')},
#             {'name': _('Currency'), 'class': 'number'},
#             {'name': _('Debit'), 'class': 'number'},
#             {'name': _('Credit'), 'class': 'number'},
#             {'name': _('Balance'), 'class': 'number'}
#         ]

    @api.model
    def _init_filter_program_code_section(self, options, previous_options=None):
        options['code_sections'] = previous_options and previous_options.get(
            'code_sections') or []
        program_fields_ids = [int(acc) for acc in options['code_sections']]
        selected_program_fields = program_fields_ids \
                                  and self.env['report.program.fields'].browse(program_fields_ids) \
                                  or self.env['report.program.fields']
        options['selected_program_fields'] = selected_program_fields.mapped(
            'name')

        # Program Section filter
        options['section_program'] = previous_options and previous_options.get(
            'section_program') or []
        program_ids = [int(acc) for acc in options['section_program']]
        selected_programs = program_ids \
                            and self.env['program'].browse(program_ids) \
                            or self.env['program']
        options['selected_programs'] = selected_programs.mapped('key_unam')

        # Sub Program Section filter
        options['section_sub_program'] = previous_options and previous_options.get(
            'section_sub_program') or []
        sub_program_ids = [int(acc) for acc in options['section_sub_program']]
        selected_sub_programs = sub_program_ids \
                                and self.env['sub.program'].browse(sub_program_ids) \
                                or self.env['sub.program']
        options['selected_sub_programs'] = selected_sub_programs.mapped(
            'sub_program')

        # Dependency Section filter
        options['section_dependency'] = previous_options and previous_options.get(
            'section_dependency') or []
        dependency_ids = [int(acc) for acc in options['section_dependency']]
        selected_dependency = dependency_ids \
                              and self.env['dependency'].browse(dependency_ids) \
                              or self.env['dependency']
        options['selected_dependency'] = selected_dependency.mapped(
            'dependency')

        # Sub Dependency Section filter
        options['section_sub_dependency'] = previous_options and previous_options.get(
            'section_sub_dependency') or []
        sub_dependency_ids = [int(acc)
                              for acc in options['section_sub_dependency']]
        selected_sub_dependency = sub_dependency_ids \
                                  and self.env['sub.dependency'].browse(sub_dependency_ids) \
                                  or self.env['sub.dependency']
        options['selected_sub_dependency'] = selected_sub_dependency.mapped(
            'sub_dependency')

        # Expense Item filter
        options['section_expense_item'] = previous_options and previous_options.get(
            'section_expense_item') or []
        item_ids = [int(acc) for acc in options['section_expense_item']]
        selected_items = item_ids \
                         and self.env['expenditure.item'].browse(item_ids) \
                         or self.env['expenditure.item']
        options['selected_items'] = selected_items.mapped('item')

        # Origin Resource filter
        options['section_or'] = previous_options and previous_options.get(
            'section_or') or []
        or_ids = [int(acc) for acc in options['section_or']]
        selected_origins = or_ids \
                           and self.env['resource.origin'].browse(or_ids) \
                           or self.env['resource.origin']
        options['selected_or'] = selected_origins.mapped('key_origin')


    def _get_templates(self):
        """Get this template for better fit of columns"""
        templates = super(StatusProgramReport, self)._get_templates()
        templates['main_table_header_template'] = 'l10n_mx_reports.template_coa_table_header'
        return templates


#     @api.model
#     def _get_templates(self):
#         templates = super(StatusProgramReport, self)._get_templates()
#         templates['main_table_header_template'] = 'account_reports.template_coa_table_header'
#         return templates

    def _get_columns_name(self, options):
        """Get more specific columns to use in SAT report"""
        columns = [{'name': ''}, {'name': _('Initial Balance'), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for period in options['comparison']['periods']:
                columns += [
                    {'name': _('Debit'), 'class': 'number'},
                    {'name': _('Credit'), 'class': 'number'},
                    ]
        return columns + [
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
            {'name': _('Total'), 'class': 'number'},
        ]

    def _post_process(self, grouped_accounts, initial_balances, options, comparison_table):
        afrl_obj = self.env['account.financial.html.report.line']
        lines = []
        n_cols = len(comparison_table) * 2 + 2
        total = [0.0] * n_cols
        afr_lines = afrl_obj.search([
            ('parent_id', '=', False),
            ('code', 'ilike', 'MX_COA_%')], order='code')
        for line in afr_lines:
            childs = self._get_lines_second_level(
                line.children_ids, grouped_accounts, initial_balances, options, comparison_table)
            if not childs:
                continue
            cols = ['']
            if not options.get('coa_only'):
                cols = cols * n_cols
                child_cols = [c['columns'] for c in childs if c.get('level') == 2]
                total_line = []
                for col in range(n_cols):
                    total_line += [sum(a[col] for a in child_cols)]
                    total[col] += total_line[col]
                for child in childs:
                    child['columns'] = [{'name': self.format_value(v)} for v in child['columns']]
            lines.append({
                'id': 'hierarchy_' + line.code,
                'name': line.name,
                'columns': [{'name': v} for v in cols],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            lines.extend(childs)
            if not options.get('coa_only'):
                lines.append({
                    'id': 'total_%s' % line.code,
                    'name': _('Total %s') % line.name[2:],
                    'level': 0,
                    'class': 'hierarchy_total',
                    'columns': [{'name': self.format_value(v)} for v in total_line],
                })
        if not options.get('coa_only'):
            lines.append({
                'id': 'hierarchy_total',
                'name': _('Total'),
                'level': 0,
                'class': 'hierarchy_total',
                'columns': [{'name': self.format_value(v)} for v in total],
            })
        return lines

    @api.model
    def _get_lines_second_level(self, lines_child, grouped_accounts,
                                initial_balances, options, comparison_table):
        """Return list of tags found in the second level"""
        lines = []
        sorted_childs = sorted(lines_child, key=lambda a: a.name)
        for child in sorted_childs:
            account_lines = self._get_lines_third_level(
                child, grouped_accounts, initial_balances, options,
                comparison_table)
            if not account_lines:
                continue
            cols = [{'name': ''}]
            if not options.get('coa_only'):
                n_cols = len(comparison_table) * 2 + 2
                child_cols = [c['columns'] for c in account_lines if c.get('level') == 3]
                cols = []
                for col in range(n_cols):
                    cols += [sum(a[col] for a in child_cols)]
            lines.append({
                'id': 'level_one_%s' % child.id,
                'name': child.name,
                'columns': cols,
                'level': 2,
                'class': 'hierarchy_total' if not options.get('coa_only') else '',
                'unfoldable': True,
                'unfolded': True,
            })
            lines.extend(account_lines)
        return lines


    @api.model
    def _get_lines_third_level(self, line, grouped_accounts, initial_balances,
                               options, comparison_table):
        """Return list of accounts found in the third level"""
        lines = []
        company_id = self.env.context.get('company_id') or self.env.company
        domain = safe_eval(line.domain or '[]')
        domain += [
            ('deprecated', '=', False),
            ('company_id', '=',company_id.id),
        ]
        basis_account_ids = self.env['account.tax'].search_read(
            [('cash_basis_base_account_id', '!=', False)], ['cash_basis_base_account_id'])
        basis_account_ids = [account['cash_basis_base_account_id'][0] for account in basis_account_ids]
        domain.append((('id', 'not in', basis_account_ids)))
        account_ids = self.env['account.account'].search(domain, order='code')
        tags = account_ids.mapped('tag_ids').filtered(
            lambda r: r.color == 4).sorted(key=lambda a: a.name)
        for tag in tags:
            accounts = account_ids.search([
                ('tag_ids', 'in', [tag.id]),
                ('id', 'in', account_ids.ids),
            ])
            name = tag.name
            name = name[:63] + "..." if len(name) > 65 else name
            cols = [{'name': ''}]
            childs = self._get_lines_fourth_level(accounts, grouped_accounts, initial_balances, options, comparison_table)
            if not childs:
                continue
            if not options.get('coa_only'):
                n_cols = len(comparison_table) * 2 + 2
                child_cols = [c['columns'] for c in childs]
                cols = []
                for col in range(n_cols):
                    cols += [sum(a[col] for a in child_cols)]
            lines.append({
                'id': 'level_two_%s' % tag.id,
                'parent_id': 'level_one_%s' % line.id,
                'name': name,
                'columns': cols,
                'level': 3,
                'unfoldable': True,
                'unfolded': True,
                'tag_id': tag.id,
            })
            lines.extend(childs)
        return lines

    def _get_lines_fourth_level(self, accounts, grouped_accounts, initial_balances, options, comparison_table):
        lines = []
        company_id = self.env.context.get('company_id') or self.env.company
        is_zero = company_id.currency_id.is_zero
        for account in accounts:
            # skip accounts with all periods = 0 (debit and credit) and no initial balance
            if not options.get('coa_only'):
                non_zero = False
                for period in range(len(comparison_table)):
                    if account in grouped_accounts and (
                        not is_zero(initial_balances.get(account, 0)) or
                        not is_zero(grouped_accounts[account][period]['debit']) or
                        not is_zero(grouped_accounts[account][period]['credit'])
                    ):
                        non_zero = True
                        break
                if not non_zero:
                    continue
            name = account.code + " " + account.name
            name = name[:63] + "..." if len(name) > 65 else name
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            if len(tag) > 1:
                raise UserError(_(
                    'The account %s is incorrectly configured. Only one tag is allowed.'
                ) % account.name)
            nature = dict(tag.fields_get()['nature']['selection']).get(tag.nature, '')
            cols = [{'name': nature}]
            if not options.get('coa_only'):
                cols = self._get_cols(initial_balances, account, comparison_table, grouped_accounts)
            lines.append({
                'id': account.id,
                'parent_id': 'level_two_%s' % tag.id,
                'name': name,
                'level': 4,
                'columns': cols,
                'caret_options': 'account.account',
            })
        return lines

    def _get_cols(self, initial_balances, account, comparison_table, grouped_accounts):
        cols = [initial_balances.get(account, 0.0)]
        total_periods = 0
        for period in range(len(comparison_table)):
            amount = grouped_accounts[account][period]['balance']
            total_periods += amount
            cols += [grouped_accounts[account][period]['debit'],
                        grouped_accounts[account][period]['credit']]
        cols += [initial_balances.get(account, 0.0) + total_periods]
        return cols

    def _l10n_mx_edi_add_digital_stamp(self, path_xslt, cfdi):
        """Add digital stamp certificate attributes in XML report"""
        company_id = self.env.company
        certificate_ids = company_id.l10n_mx_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            return cfdi
        tree = fromstring(cfdi)
        xslt_root = etree.parse(tools.file_open(path_xslt))
        cadena = str(etree.XSLT(xslt_root)(tree))
        sello = certificate_id.sudo().get_encrypted_cadena(cadena)
        tree.attrib['Sello'] = sello
        tree.attrib['noCertificado'] = certificate_id.serial_number
        tree.attrib['Certificado'] = certificate_id.sudo().get_data()[0]
        return etree.tostring(tree, pretty_print=True,
                              xml_declaration=True, encoding='UTF-8')

    def get_bce_dict(self, options):
        company = self.env.company
        xml_data = self._get_lines(options)
        accounts = []
        account_lines = [l for l in xml_data
                         if l.get('level') in [2, 3] and l.get('show', True)]
        for line in account_lines:
            cols = line.get('columns', [])
            initial, debit, credit, end = (
                cols[0].get('name', 0.0),
                cols[-3].get('name', 0.0),
                cols[-2].get('name', 0.0),
                cols[-1].get('name', 0.0))
            accounts.append({
                'number': line.get('name').split(' ', 1)[0],
                'initial': "%.2f" % (initial),
                'debit': "%.2f" % (debit),
                'credit': "%.2f" % (credit),
                'end': "%.2f" % (end),
            })
        date = fields.Date.from_string(self.env.context['date_from'])
        chart = {
            'vat': company.vat or '',
            'month': str(date.month).zfill(2),
            'year': date.year,
            'accounts': accounts,
            'type': 'N',
        }
        return chart

    @api.model
    def _get_lines(self, options, line_id=None):
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.

        domain = []
        is_add_fiter = False          
        if len(options['selected_programs']) > 0:
            domain.append(('program_id.key_unam', 'in', options['selected_programs']))
            is_add_fiter = True
        if len(options['selected_sub_programs']) > 0:
            domain.append(('sub_program_id.sub_program', 'in', options['selected_sub_programs']))
            is_add_fiter = True
        if len(options['selected_dependency']) > 0:
            domain.append(('dependency_id.dependency', 'in', options['selected_dependency']))
            is_add_fiter = True
        if len(options['selected_sub_dependency']) > 0:
            domain.append(('sub_dependency_id.sub_dependency', 'in', options['selected_sub_dependency']))
            is_add_fiter = True
        if len(options['selected_items']) > 0:
            domain.append(('item_id.item', 'in', options['selected_items']))
            is_add_fiter = True
        if len(options['selected_or']) > 0:
            domain.append(('resource_origin_id.key_origin', 'in', options['selected_or']))
            is_add_fiter = True
            
        program_code_obj = self.env['program.code']
        program_codes = program_code_obj.search(domain)
        
        program_codes_account_ids = program_codes.mapped('item_id.unam_account_id')
        program_codes_account_ids = program_codes_account_ids.ids
        
        new_options = options.copy()
        new_options['unfold_all'] = True
        options_list = self._get_options_periods_list(new_options)
        accounts_results, taxes_results = self.env['account.general.ledger']._do_query(options_list, fetch_lines=False)

        grouped_accounts = {}
        initial_balances = {}
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods') or []
        for account, periods_results in accounts_results:
            if is_add_fiter and not account.id in program_codes_account_ids:
                continue
            grouped_accounts.setdefault(account, [])
            for i, res in enumerate(periods_results):
                if i == 0:
                    initial_balances[account] = res.get('initial_balance', {}).get('balance', 0.0)
                grouped_accounts[account].append({
                    'balance': res.get('sum', {}).get('balance', 0.0),
                    'debit': res.get('sum', {}).get('debit', 0.0),
                    'credit': res.get('sum', {}).get('credit', 0.0),
                })
        
        return self._post_process(grouped_accounts, initial_balances, options, comparison_table)

    @api.model
    def get_xml(self, options):
        qweb = self.env['ir.qweb']
        version = '1.3'
        ctx = self._set_context(options)
        if not ctx.get('date_to'):
            return False
        ctx['no_format'] = True
        values = self.with_context(ctx).get_bce_dict(options)
        cfdicoa = qweb.render(CFDIBCE_TEMPLATE, values=values)
        for key, value in MX_NS_REFACTORING.items():
            cfdicoa = cfdicoa.replace(key.encode('UTF-8'),
                                      value.encode('UTF-8') + b':')
        cfdicoa = self._l10n_mx_edi_add_digital_stamp(
            CFDIBCE_XSLT_CADENA % version, cfdicoa)

        with tools.file_open(CFDIBCE_XSD % version, "rb") as xsd:
            _check_with_xsd(cfdicoa, xsd)
        return cfdicoa

    def get_html(self, options, line_id=None, additional_context=None):
        return super(StatusProgramReport, self.with_context(
            self._set_context(options))).get_html(
                options, line_id, additional_context)

    def get_report_filename(self, options):
        return super(StatusProgramReport, self.with_context(
            self._set_context(options))).get_report_filename(options).upper()

    def _get_report_name(self):
        """The structure to name the Trial Balance reports is:
        VAT + YEAR + MONTH + ReportCode
        ReportCode:
        BN - Trial balance with normal information
        BC - Trial balance with with complementary information. (Now is
        not suportes)"""
        context = self.env.context
        date_report = fields.Date.from_string(context['date_from']) if context.get(
                'date_from') else fields.Date.today()
        return '%s%s%sBN' % (
            self.env.company.vat or '',
            date_report.year,
            str(date_report.month).zfill(2))

    def open_journal_items(self, options, params):
        new_params = params.copy()
        new_params.pop('financial_group_line_id', False)
        return super(StatusProgramReport, self).open_journal_items(
            options, new_params)

    def view_all_journal_items(self, options, params):
        if not params.get('id') or 'hierarchy' in params.get('id'):
            return super(StatusProgramReport, self).view_all_journal_items(
                options, params)
        ctx = self._set_context(options)
        lines = self.with_context(**ctx)._get_lines(options)
        new_params = params.copy()
        new_params.pop('id', False)
        accounts = self._get_accounts_journal_items([params.get('id')], lines)
        ctx = {'search_default_account': 1}
        res = super(StatusProgramReport, self.with_context(
            **ctx)).view_all_journal_items(options, new_params)
        res.get('domain', []).append(('account_id', 'in', accounts))
        return res

    def _get_accounts_journal_items(self, params, lines):
        levels = [
            l.get('level') for l in lines if l.get('parent_id') in params]
        if levels and levels[0] == 4:
            return [
                l.get('id') for l in lines if l.get('parent_id') in params]
        params = [
            l.get('id') for l in lines if l.get('parent_id') in params]
        return self._get_accounts_journal_items(params, lines)


    def get_pdf(self, options, minimal_layout=True,line_id=None):
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
        body_html = body_html.replace(b'<div class="o_account_reports_header">',b'<div>')
        #<div class="o_account_reports_header">
        body = body.replace(b'<body class="o_account_reports_body_print">', b'<body class="o_account_reports_body_print">' + body_html)
        if minimal_layout:
            header = ''
            footer = self.env['ir.actions.report'].render_template("web.internal_layout", values=rcontext)
            spec_paperformat_args = {'data-report-margin-top': 10, 'data-report-header-spacing': 20}
            footer = self.env['ir.actions.report'].render_template("web.minimal_layout", values=dict(rcontext, subst=True, body=footer))
        else:
            lines = self._get_lines(options, line_id=line_id)
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
            header = self.env['ir.actions.report'].render_template("jt_account_module_design.external_layout_fianancial_statement_report", values=rcontext)
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
