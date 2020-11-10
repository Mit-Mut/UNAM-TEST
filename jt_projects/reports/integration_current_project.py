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


class IntegrationOfCurrentResearchProjects(models.AbstractModel):

    _name = "jt_projects.integration.of.curr.resarch.project"
    _inherit = "account.coa.report"
    _description = "Integration of current research projects"

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
            {'name': _('Print Preview'), 'sequence': 1,
             'action': 'print_pdf', 'file_export_type': _('PDF')},
            {'name': _('Export (XLSX)'), 'sequence': 2,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
        ]

    def _get_templates(self):
        templates = super(
            IntegrationOfCurrentResearchProjects, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_lines(self, options, line_id=None):
        lines = []
        print('lines', lines)
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        project_records = self.env['project.project'].search(
            [('status', '=', 'open'), ('proj_start_date', '>=', start), ('proj_end_date', '<=', end)])

        for record in project_records:
            lines.append({
                'id': 'projects' + str(record.id),
                'name': record.name,
                'columns': [{'name': record.stage_identifier + '/' + record.proj_start_date.year or ''},

                            ],
                'level': 3,
                'unfoldable': False,
                'unfolded': True,
            })

        return lines

    def _get_columns_name(self, options):
        return [
            {'name': _('Stage / Year')},
            {'name': _('Active project control system balances')},
            {'name': _('Ministered')},
            {'name': _('Checked')},
            {'name': _('To check')},
            {'name': _('Countable balance')},
            {'name': _('Accounting account of various debtors')},
            {'name': _('Total of (Number of projects)')},
        ]

    def _get_report_name(self):
        return _("Integration of current research projects")