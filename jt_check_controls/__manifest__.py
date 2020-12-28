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
{
    'name': 'Check Control',
    'summary': 'Check Control System for UNAM',
    'version': '13.0.0..1',
    'category': 'Accounting',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': ['jt_budget_mgmt'],
    'data': [
        'views/minimum_checks.xml',
        'views/trades.xml',
        'views/check_authorized_by_dependency.xml',
        'views/checkbook_req.xml',
        'views/blank_check_req_views.xml',
        'views/supplier_payment_req.xml',
        'views/payment_batch_supplier.xml',
        'wizard/confirm_checkbook_req.xml',
        'wizard/approve_blank_check.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_data.xml',
        'reports/check_request_1.xml',
        'reports/check_request_2.xml',
        'reports/check_registration.xml',
        'reports/report_menu.xml',
        'views/cancel_checks.xml',
        'views/reissue_checks.xml',
        'reports/header.xml',
        'reports/blank_check_req_report.xml',
        'views/send_checks.xml',
        'reports/send_check_report.xml',
        'reports/payment_batch_supplier.xml',
        'wizard/confirm_printed_checks.xml',
        'wizard/generate_sup_batch_check_layout.xml',
        'wizard/generate_cancel_check_layout.xml',
        'views/circulation_of_checks.xml',
        'views/expiration_validity_check.xml',
        

    ],
    'demo': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
