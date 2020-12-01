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
from odoo import models, _
from datetime import datetime
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
# from odoo.tools.misc import formatLang
# from odoo.tools.misc import xlsxwriter
# # import io
# # import base64
# from odoo.tools import config, date_utils, get_lang
# import lxml.html


class IntegrationOfRemnants(models.AbstractModel):

    _name = "jt_projects.integration.remnants"
    _inherit = "account.coa.report"
    _description = "Integration of remnants by PAPIIT, PAPIME, INFOCAB Stage"

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
            {'name': _('Print Preview'), 'sequence': 1,
             'action': 'print_pdf', 'file_export_type': _('PDF')},
            {'name': _('Export (XLSX)'), 'sequence': 2,
             'action': 'print_xlsx', 'file_export_type': _('XLSX')},
        ]

    def _get_templates(self):
        templates = super(
            IntegrationOfRemnants, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates


    def get_header(self, options):

        return[
            
            # [
                
            #     {'name': _('INTEGRATION DE REMANENTES PAPIIT, PAPIME, INFOCAB'),'colspan':5},
                

            # ],

            [
                {'name': _('SALDO MES ANTERIOR JUNIO')},
                {'name': _('CUENTA DE PESIVO:221.006.001.002')},
                {'name': _('CUENTA DE PESIVO:221.006.002.002')},
                {'name': _('CUENTA DE PESIVO:221.006.003.002')},
                {'name': _('TOTAL')},
            ]
        ]


    def _get_lines(self, options, line_id=None):
        lines = []
        start = datetime.strptime(
            str(options['date'].get('date_from')), '%Y-%m-%d').date()
        end = datetime.strptime(
            options['date'].get('date_to'), '%Y-%m-%d').date()
        
        return lines

    def _get_report_name(self):
        return _("Integration of remaining resources")
