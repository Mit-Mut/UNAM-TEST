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
    'name': 'Account report design',
    'summary': 'Account Base',
    'version': '13.0.0.1.0',
    'category': 'Invoicing',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'website': 'http://www.jupical.com',
    'license': 'AGPL-3',
    'depends': ['account_accountant', 'l10n_mx','jt_projects'],
    'data': [
        'reports/header.xml',
        'reports/report_menu.xml',
        'reports/income_expenses_header.xml',
        'views/account_request_inherit.xml',
        'views/integration_of_statement_asset_view.xml',
        'views/miles_revenue_view.xml',
        'views/detailed_imcome_statement_view.xml',
        'security/ir.model.access.csv',
    ],

    'application': False,
    'installable': True,
    'auto_install': False,
}
