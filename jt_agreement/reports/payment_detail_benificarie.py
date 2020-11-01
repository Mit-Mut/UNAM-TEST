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


class PaymentDetailsBeneficiaries(models.AbstractModel):
    _name = "jt_agreement.payment_details_beneficiaries"
    _inherit = "account.coa.report"
    _description = "Payment Detail Beneficiaries"

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

    def _get_templates(self):
        templates = super(
            PaymentDetailsBeneficiaries, self)._get_templates()
        templates[
            'main_table_header_template'] = 'account_reports.main_table_header'
        templates['main_template'] = 'account_reports.main_template'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name': _('FOLIO')},
            {'name': _('FECHA INICIO')},
            {'name': _('FECHa FINAL')},
            {'name': _('ESTATUS')},
            {'name': _('MONTO')},
        ]

    def _get_report_name(self):
        return _("Payment Detail Beneficiaries")

    def _get_lines(self, options, line_id=None):
        lines = []
        record = options['date']
        start = record.get('date_from')
        end = record.get('date_to')

        base_ids = self.env['bases.collaboration'].search([('beneficiary_ids','!=',False)])
        
        for base in base_ids:
            base_no = ''
            if base.convention_no:
                base_no = base.convention_no
                
            lines.append({
                'id': 'hierarchy_base' + str(base.id),
                'name': 'CATEDRA:' + base_no,
                'columns': [{'name': base.name}, 
                            {'name': ''}, 
                            {'name': ''},
                            {'name': ''},
                            ],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            employee_ids =  base.beneficiary_ids.mapped('employee_id')
            for emp in employee_ids:
                lines.append({
                    'id': 'hierarchy_emp' + str(base.id) + str(emp.id),
                    'name': emp.rfc,
                    'columns': [{'name': emp.name}, 
                                {'name': ''}, 
                                {'name': ''},
                                {'name': ''},
                                ],
                    'level': 2,
                    'unfoldable': False,
                    'unfolded': True,
                })
                
                ben_ids =  base.beneficiary_ids.filtered(lambda x:x.employee_id.id==emp.id)
                for ben in ben_ids:
                    lines.append({
                        'id': 'hierarchy_ben' + str(ben.id),
                        'name': '',
                        'columns': [
                                    {'name': ben.validity_start}, 
                                    {'name': ben.validity_final_beneficiary},
                                    {'name': base.state},
                                    {'name': ben.amount},
                                    ],
                        'level': 3,
                        'unfoldable': False,
                        'unfolded': True,
                    })
                    
                
        return lines
