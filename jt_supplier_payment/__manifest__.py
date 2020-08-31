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
    'name': 'Supplier Payment',
    'summary': 'Supplier Payment',
    'version': '13.0.0.1.0',
    'category': 'Invoicing',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': ['jt_payroll_payment','jt_contact_base','l10n_mx_edi'],
    'data': [
        'data/data.xml',
        'data/ir_sequence_data.xml',
        'data/paper_format.xml',
        'security/ir.model.access.csv',
        'views/invoice_view.xml',
        'views/report_receipt_template.xml',
        'views/report_again_receipt.xml',
        'views/payment_request_report.xml',
        'views/account_journal_view.xml',
        'views/payment_management_view.xml',
        'wizard/generate_batch_sheet_view.xml',
        'wizard/bank_balance_check.xml',
        'wizard/message_balance.xml',
        'views/bank_transfer_request.xml',
        'views/account_payment_view.xml',
        'wizard/generate_bank_layout_view.xml',
        'views/res_partner_bank_view.xml',
        'wizard/payment_declined_view.xml',
        'wizard/load_bank_layout_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
