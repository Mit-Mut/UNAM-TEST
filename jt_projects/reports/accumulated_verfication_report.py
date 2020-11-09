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


class AccumulatedVerficationRecorded(models.AbstractModel):

    _name = "jt_projects.accumulated.verification.recorded"
    _inherit = "account.coa.report"
    _description = "Accumulated verification recorded in Income / Expense"

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
            AccumulatedVerficationRecorded, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('Entry')},
            {'name': _('443 IE REC expenses.Concurrent CONACYT')},
            {'name': _('448 IE CONACYT Checkbooks Expenses')},
            {'name': _('449 IE Expenses Other Projects with checkbook')},
            {'name': _('Total 443,448 and 449 [Horizontal sum]')},
            {'name': _('Countable balance')},
            {'name': _('Accounting account of various debtors')},
            {'name': _('Total of (Number of projects)')},
            {'name': _('Concept')},
            {'name': _('Accumulated [Start month-End    month Stages]')},
            {'name': _(
                'Stage [N of Stage] Accumulated [Months of consultation]')},
            {'name': _('Total [Vertical]')},
            {'name': _('Total checked [Horizontal]')},
        ]

    def _get_report_name(self):
        return _("Accumulated verification recorded in Income / Expense")
