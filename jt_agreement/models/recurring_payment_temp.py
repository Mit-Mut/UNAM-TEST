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
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RecurringPaymentTemplate(models.Model):

    _name = 'recurring.payment.template'
    _description = "Recurring Payment Template"

    name = fields.Char("Payment Rule Name")
    payment_number = fields.Char("Recurrence of payment number")
    payment_period = fields.Selection([('monthly', 'Monthly'), ('bimonthly', 'Bimonthly'),
                                       ('quarterly', 'Quarterly'), ('biquarterly', 'Biquarterly'),
                                       ('annual', 'Annual'), ('biannual', 'Biannual')
                                       ], "Recurrence of payment period")
    terms_condition = fields.Text("Terms and Condition")
    journal_id = fields.Many2one('account.journal', "Journal")

    @api.constrains('payment_number')
    def _check_payment_number(self):
        if self.payment_number and not self.payment_number.isnumeric():
            raise ValidationError(_('Recurrence of payment number must be Numeric.'))