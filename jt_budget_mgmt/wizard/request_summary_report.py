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
from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar
from xlrd import *
import xlwt
import base64
from io import BytesIO

class BudgetSummaryReportDownload(models.TransientModel):

    _name = 'summary.report.download'
    _description = 'Budget Summary Report Download'

    state = fields.Selection([('draft', 'Draft'), ('request', 'Request'),
                              ('download', 'Download')], default='draft')
    name = fields.Char("Name")
    report_file = fields.Binary("Download Report", filters='.xls')

    # Date period related fields
    filter_date = fields.Selection([
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Financial Year'),
        ('last_month', 'Last Month'),
        ('last_quarter', 'Last Quarter'),
        ('last_year', 'Last Financial Year'),
        ('custom', 'Custom'),
    ])

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    # Budget Control Related fields
    budget_control_ids = fields.Many2many('budget.control', string='Budget Control')

    # Program Code Section Related fields
    code_section_ids = fields.Many2many('code.structure', string='Programming Code Section')
    program_ids = fields.Many2many('program', string='Program')
    sub_program_ids = fields.Many2many('sub.program', string='Sub-Program')
    dependency_ids = fields.Many2many('dependency', string='Dependency')
    sub_dependency_ids = fields.Many2many('sub.dependency', string='Sub-Dependency')
    item_ids = fields.Many2many('expenditure.item', string='Expense Item')
    origin_ids = fields.Many2many('resource.origin', string='Origin Resource')
    activity_ids = fields.Many2many('institutional.activity', string='Institutional Activity')
    conpp_ids = fields.Many2many('budget.program.conversion', string='Budget Program Conversion (CONPP)')
    conpa_ids = fields.Many2many('departure.conversion', string='SHCP Games (CONPA)')
    expense_type_ids = fields.Many2many('expense.type', string='Type of Expense (TG)')
    location_ids = fields.Many2many('geographic.location', string='Geographic Location (UG)')
    wallet_ids = fields.Many2many('key.wallet', string='Wallet Key (CC)')
    project_type_ids = fields.Many2many('project.type', string='Project Type (TP)')
    stage_ids = fields.Many2many('stage', string='Stage (E)')
    agreement_type_ids = fields.Many2many('agreement.type', string='Type of agreement (TC)')

    @api.onchange('filter_date')
    def onchange_filter(self):
        if self.filter_date:
            date = datetime.now()
            filter_date = self.filter_date
            if filter_date == 'this_month':
                self.start_date = date.replace(day = 1)
                self.end_date = date.replace(day = calendar.monthrange(date.year, date.month)[1])
            elif filter_date == 'this_quarter':
                month = date.month
                if month >= 1 and month <=3:
                    self.start_date = date.replace(month=1, day=1)
                    self.end_date = date.replace(month=3, day=31)
                elif month >= 4 and month <= 6:
                    self.start_date = date.replace(month=4, day=1)
                    self.end_date = date.replace(month=6, day=30)
                elif month >= 7 and month <= 9:
                    self.start_date = date.replace(month=7, day=1)
                    self.end_date = date.replace(month=9, day=30)
                else:
                    self.start_date = date.replace(month=10, day=1)
                    self.end_date = date.replace(month=12, day=31)
            elif filter_date == 'this_year':
                self.start_date = date.replace(month=1, day=1)
                self.end_date = date.replace(month=12, day=31)
            elif filter_date == 'last_month':
                today = datetime.today()
                first = today.replace(day=1)
                last_month_date = first - timedelta(days=1)
                last_month = last_month_date.month
                if last_month == 12:
                    year = date.year - 1
                    self.start_date = date.replace(day=1, month=last_month, year=year)
                    self.end_date = date.replace(day=calendar.monthrange(date.year, last_month)[1], month=last_month,
                                                 year=year)
                else:
                    self.start_date = date.replace(day=1, month=last_month)
                    self.end_date = date.replace(day=calendar.monthrange(date.year, last_month)[1], month=last_month)
            elif filter_date == 'last_quarter':
                month = date.month
                year = date.year
                if month >= 1 and month <=3:
                    self.start_date = date.replace(month=1, day=1, year=year)
                    self.end_date = date.replace(month=12, day=31, year=year)
                elif month >= 4 and month <= 6:
                    self.start_date = date.replace(month=1, day=1)
                    self.end_date = date.replace(month=3, day=31)
                elif month >= 7 and month <= 9:
                    self.start_date = date.replace(month=4, day=1)
                    self.end_date = date.replace(month=6, day=30)
                else:
                    self.start_date = date.replace(month=7, day=1)
                    self.end_date = date.replace(month=9, day=30)
            elif filter_date == 'last_year':
                year = date.year - 1
                self.start_date = date.replace(month=1, day=1, year=year)
                self.end_date = date.replace(month=12, day=31, year=year)

    def request_data(self):
        # Search Programs
        domain = [('state', '=', 'validated')]
        if self.program_ids:
            domain.append(('program_id', 'in', self.program_ids.ids))
        if self.sub_program_ids:
            domain.append(('sub_program_id', 'in', self.sub_program_ids.ids))
        if self.dependency_ids:
            domain.append(('dependency_id', 'in', self.dependency_ids.ids))
        if self.sub_dependency_ids:
            domain.append(('sub_dependency_id', 'in', self.sub_dependency_ids.ids))
        if self.item_ids:
            domain.append(('item_id', 'in', self.item_ids.ids))
        if self.origin_ids:
            domain.append(('resource_origin_id', 'in', self.origin_ids.ids))
        if self.activity_ids:
            domain.append(('institutional_activity_id', 'in', self.activity_ids.ids))
        if self.conpp_ids:
            domain.append(('budget_program_conversion_id', 'in', self.conpp_ids.ids))
        if self.conpa_ids:
            domain.append(('conversion_item_id', 'in', self.conpa_ids.ids))
        if self.expense_type_ids:
            domain.append(('expense_type_id', 'in', self.expense_type_ids.ids))
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        if self.wallet_ids:
            domain.append(('portfolio_id', 'in', self.wallet_ids.ids))
        if self.project_type_ids:
            domain.append(('project_type_id', 'in', self.project_type_ids.ids))
        if self.stage_ids:
            domain.append(('stage_id', 'in', self.stage_ids.ids))
        if self.agreement_type_ids:
            domain.append(('agreement_type_id', 'in', self.wallet_ids.ids))

        programs = self.env['program.code'].search(domain)
        final_codes = []
        code_lines = []
        bud_line_obj = self.env['expenditure.budget.line']
        start = self.start_date
        end = self.end_date
        for code in programs:
            all_b_lines = bud_line_obj.search([('program_code_id', '=', code.id),
                ('expenditure_budget_id.state', '=', 'validate'),('start_date', '>=', start), ('end_date', '<=', end)])
            if all_b_lines:
                final_codes.append(code)
                code_lines.append({code: all_b_lines})

        if code_lines:
            if len(final_codes) <= 5000:
                adequacies_line_obj = self.env['adequacies.lines']
                wb1 = xlwt.Workbook(encoding='utf-8')
                ws1 = wb1.add_sheet('Proforma Summary Report')
                fp = BytesIO()
                header_style = xlwt.easyxf('font: bold 1')

                row = 1
                col = 0
                ws1.write(row, col, "Program Code", header_style)
                for bug_con in self.budget_control_ids:
                    col += 1
                    ws1.write(row, col, bug_con.name, header_style)
                for code_sec in self.code_section_ids:
                    col += 1
                    value = ''
                    if code_sec.section == 'year':
                        value = 'Year'
                    elif code_sec.section == 'pr':
                        value = 'Program'
                    elif code_sec.section == 'sp':
                        value = 'Sub Program'
                    elif code_sec.section == 'dep':
                        value = 'Dependency'
                    elif code_sec.section == 'sd':
                        value = 'Sub Dependency'
                    elif code_sec.section == 'par':
                        value = 'Expenditure Item'
                    elif code_sec.section == 'dv':
                        value = 'Check Digit'
                    elif code_sec.section == 'or':
                        value = 'Source of Resource'
                    elif code_sec.section == 'ai':
                        value = 'Institutional Activity'
                    elif code_sec.section == 'conpp':
                        value = 'Conversion of Budgetary Program'
                    elif code_sec.section == 'conpa':
                        value = 'SHCP items'
                    elif code_sec.section == 'tg':
                        value = 'Type of Expenditure'
                    elif code_sec.section == 'ug':
                        value = 'Geographic Location'
                    elif code_sec.section == 'cc':
                        value = 'Wallet Key'
                    elif code_sec.section == 'tp':
                        value = 'Type of Project'
                    elif code_sec.section == 'np':
                        value = 'Project Number'
                    elif code_sec.section == 'e':
                        value = 'Stage'
                    elif code_sec.section == 'tc':
                        value = 'Type of Agreement'
                    elif code_sec.section == 'nc':
                        value = 'Agreement Number'
                    ws1.write(row, col, value, header_style)

                row += 1
                for code in final_codes:
                    col = 0
                    all_b_lines = bud_line_obj.search([('program_code_id', '=', code.id),
                               ('expenditure_budget_id.state', '=', 'validate'),
                               ('start_date', '>=', start), ('end_date', '<=', end)])
                    if all_b_lines:
                        annual_modified = 0
                        adequacies_lines = adequacies_line_obj.search([('program', '=', code.id),
                                                                       ('adequacies_id.state', '=', 'accepted')])
                        for ad_line in adequacies_lines:
                            if ad_line.line_type == 'increase':
                                annual_modified += ad_line.amount
                            elif ad_line.line_type == 'decrease':
                                annual_modified -= ad_line.amount
                        ws1.write(row, col, code.program_code)
                        for bug_con in self.budget_control_ids:
                            col += 1
                            value = 0
                            if bug_con.name == 'Authorized':
                                value = sum(x.authorized for x in all_b_lines)
                            elif bug_con.name == 'Assigned Total Annual':
                                value = sum(x.assigned for x in all_b_lines)
                            elif bug_con.name == 'Annual Modified':
                                value = annual_modified
                            elif bug_con.name == 'Assigned 1st Trimester':
                                value = sum(x.assigned if x.start_date.month == 1 and \
                                                          x.start_date.day == 1 and x.end_date.month == 3 and x.end_date.day == 31 \
                                                else 0 for x in all_b_lines)
                            elif bug_con.name == 'Assigned 2nd Trimester':
                                value = sum(x.assigned if x.start_date.month == 4 and \
                                                          x.start_date.day == 1 and x.end_date.month == 6 and x.end_date.day == 30 \
                                                else 0 for x in all_b_lines)
                            elif bug_con.name == 'Assigned 3rd Trimester':
                                value = sum(x.assigned if x.start_date.month == 7 and \
                                                          x.start_date.day == 1 and x.end_date.month == 9 and x.end_date.day == 30 \
                                                else 0 for x in all_b_lines)
                            elif bug_con.name == 'Assigned 4th Trimester':
                                value = sum(x.assigned if x.start_date.month == 10 and \
                                                          x.start_date.day == 1 and x.end_date.month == 12 and x.end_date.day == 31 \
                                                else 0 for x in all_b_lines)
                            elif bug_con.name == 'Per Exercise':
                                value = 0
                            elif bug_con.name == 'Committed':
                                value = 0
                            elif bug_con.name == 'Accrued':
                                value = 0
                            elif bug_con.name == 'Exercised':
                                value = 0
                            elif bug_con.name == 'Paid':
                                value = 0
                            elif bug_con.name == 'Available':
                                value = sum(x.available for x in all_b_lines)
                            ws1.write(row, col, value)
                        for code_sec in self.code_section_ids:
                            col += 1
                            value = ''
                            if code_sec.section == 'year':
                                value = code.year.name
                            elif code_sec.section == 'pr':
                                value = code.program_id.key_unam
                            elif code_sec.section == 'sp':
                                value = code.sub_program_id.sub_program
                            elif code_sec.section == 'dep':
                                value = code.dependency_id.dependency
                            elif code_sec.section == 'sd':
                                value = code.sub_dependency_id.sub_dependency
                            elif code_sec.section == 'par':
                                value = code.item_id.item
                            elif code_sec.section == 'dv':
                                value = code.check_digit
                            elif code_sec.section == 'or':
                                value = code.resource_origin_id.key_origin
                            elif code_sec.section == 'ai':
                                value = code.institutional_activity_id.number
                            elif code_sec.section == 'conpp':
                                value = code.budget_program_conversion_id.shcp.name
                            elif code_sec.section == 'conpa':
                                value = code.conversion_item_id.federal_part
                            elif code_sec.section == 'tg':
                                value = code.expense_type_id.key_expenditure_type
                            elif code_sec.section == 'ug':
                                value = code.location_id.state_key
                            elif code_sec.section == 'cc':
                                value = code.portfolio_id.wallet_password
                            elif code_sec.section == 'tp':
                                value = code.project_type_id.project_type_identifier
                            elif code_sec.section == 'np':
                                value = code.project_type_id.number
                            elif code_sec.section == 'e':
                                value = code.stage_id.stage_identifier
                            elif code_sec.section == 'tc':
                                value = code.agreement_type_id.agreement_type
                            elif code_sec.section == 'nc':
                                value = code.agreement_type_id.number_agreement
                            ws1.write(row, col, value)
                        row += 1
                wb1.save(fp)
                out = base64.encodestring(fp.getvalue())
                self.report_file = out
                self.name = 'proforma_summary_report.xls'
                self.state = 'download'
            else:
                req_report = self.env['requested.reports']
                current_time = datetime.now()
                req_rep_vals = {
                    'name': 'Report Request At ' + str(current_time),
                    'requested_by': self.env.user.id,
                    'requested_time': current_time,
                    'filter_date': self.filter_date,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'budget_control_ids': [(4, rec.id) for rec in self.budget_control_ids],
                    'program_ids': [(4, rec.id) for rec in self.program_ids],
                    'sub_program_ids': [(4, rec.id) for rec in self.sub_program_ids],
                    'dependency_ids': [(4, rec.id) for rec in self.dependency_ids],
                    'sub_dependency_ids': [(4, rec.id) for rec in self.sub_dependency_ids],
                    'item_ids': [(4, rec.id) for rec in self.item_ids],
                    'origin_ids': [(4, rec.id) for rec in self.origin_ids],
                    'activity_ids': [(4, rec.id) for rec in self.activity_ids],
                    'conpp_ids': [(4, rec.id) for rec in self.conpp_ids],
                    'conpa_ids': [(4, rec.id) for rec in self.conpa_ids],
                    'expense_type_ids': [(4, rec.id) for rec in self.expense_type_ids],
                    'location_ids': [(4, rec.id) for rec in self.location_ids],
                    'wallet_ids': [(4, rec.id) for rec in self.wallet_ids],
                    'project_type_ids': [(4, rec.id) for rec in self.project_type_ids],
                    'stage_ids': [(4, rec.id) for rec in self.stage_ids],
                    'agreement_type_ids': [(4, rec.id) for rec in self.agreement_type_ids],
                    'program_code_ids':  [(4, rec.id) for rec in final_codes],
                    # 'code_lines': code_lines
                }
                report = req_report.create(req_rep_vals)
                if report:
                    nextcall = current_time + timedelta(seconds=10)
                    cron_vals = {
                        'name': 'Report Request' + str(current_time),
                        'state': 'code',
                        'nextcall': nextcall,
                        'numbercall': -1,
                        'code': "model.download_report(%s)" % report.id,
                        'model_id': self.env.ref('jt_budget_mgmt.model_requested_reports').id,
                        'user_id': self.env.user.id,
                        'req_report_id': req_report
                    }

                    # Final process
                    cron = self.env['ir.cron'].sudo().create(cron_vals)
                    report.cron_id = cron.id
                    self.write({'state': 'request'})
        return {
            'name': 'Report Download Progress',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'summary.report.download',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }