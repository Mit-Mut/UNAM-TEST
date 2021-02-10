# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import copy
import ast
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

    
class ReportAccountFinancialReport(models.Model):
    _name = "jt_account_module_design.financial.report"
    _description = "jt Account Report (HTML)"
    _inherit = "account.financial.html.report"


    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_journals = True
    filter_program_code_section = True
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}

    def _get_templates(self):
        """Get this template for better fit of columns"""
        templates = super(ReportAccountFinancialReport, self)._get_templates()
        templates['main_template'] = 'jt_account_module_design.financial_statement_main_template'
        templates.update({'custom_line_template_right':'jt_account_module_design.custom_line_template_right','custom_line_template_left':'jt_account_module_design.custom_line_template_left'})
        
        return templates

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

    def _get_lines(self, options, line_id=None):
        lines = []

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
         
        report_id = self.env.ref('account_reports.account_financial_report_balancesheet0')
        
        if  report_id:
            #======= Side Data ======#
            print ("lines=====",line_id)
            line_obj = report_id.line_ids
            if line_id:
                line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
            if options.get('comparison') and options.get('comparison').get('periods'):
                line_obj = line_obj.with_context(periods=options['comparison']['periods'])
            if options.get('ir_filters'):
                line_obj = line_obj.with_context(periods=options.get('ir_filters'))
    
            currency_table = report_id._get_currency_table()
            domain, group_by = report_id._get_filter_info(options)
    
            if group_by:
                options['groups'] = {}
                options['groups']['fields'] = group_by
                options['groups']['ids'] = report_id._get_groups(domain, group_by)
    
            amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
            amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
            linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]
            
            left_line_obj = self.env['account.financial.html.report.line']
            right_line_obj = line_obj
            left_line_id = self.env.ref('account_reports.account_financial_report_total_assets0')
            if left_line_id and left_line_id.id in line_obj.ids:
                left_line_obj = left_line_id
                right_line_obj = right_line_obj - left_line_id
            
            if is_add_fiter:
                lines = left_line_obj.with_context(
                        filter_domain=domain,custom_account_ids=[('account_id','in',program_codes_account_ids)]
                    )._get_lines(self, currency_table, options, linesDicts)
                for l in lines:
                    l.update({'side':'left'})

                right_lines = right_line_obj.with_context(
                        filter_domain=domain,custom_account_ids=[('account_id','in',program_codes_account_ids)]
                    )._get_lines(self, currency_table, options, linesDicts)
                for l in right_lines:
                    l.update({'side':'right'})
                    
                lines += right_lines
                #lines = report_id.with_context(custom_account_ids=[('account_id','in',program_codes_account_ids)])._get_lines(options, line_id=line_id)
            else:
                lines = left_line_obj.with_context(
                        filter_domain=domain
                    )._get_lines(self, currency_table, options, linesDicts)
                for l in lines:
                    l.update({'side':'left'})
                    
                right_lines = right_line_obj.with_context(
                        filter_domain=domain
                    )._get_lines(self, currency_table, options, linesDicts)
                    
                for l in right_lines:
                    l.update({'side':'right'})
                
                lines+=right_lines
        return lines
    
    def get_custom_lines(self,lines,side):
        return lines

    def _get_report_name(self):
        return ("Statement Of Financial Position")

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

        render_template = templates.get('main_template', 'jt_account_module_design.financial_statement_main_template')
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
    
class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"
     
    def _get_aml_domain(self):
        domain = super(AccountFinancialReportLine,self)._get_aml_domain()
        if domain:
            domain += (self._context.get('custom_account_ids') or [])
        else:
             domain = (self._context.get('custom_account_ids') or [])
        return domain