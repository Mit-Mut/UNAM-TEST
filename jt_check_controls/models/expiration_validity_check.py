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
from odoo import models, fields, api, _,tools
from datetime import datetime, timedelta,date
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, format_date

class ExpirationValidityCheck(models.Model):
    
    _name = 'expiration.validity.check'
    _description = 'Expiration Validity Check'
    _auto = False
    _rec_name='check_no'
    
    check_folio_id = fields.Many2one('check.log',"Check number")
    check_payment_req_id = fields.Many2one('check.payment.req','Check Payment Request')
    payment_req_id = fields.Many2one('account.move')
    payment_name = fields.Char(related='payment_req_id.name',string='Application number')
    check_no = fields.Integer(related='check_folio_id.folio',string='Check number')
    currency_id = fields.Many2one(related='payment_req_id.currency_id')
    
    dependence_id = fields.Many2one(related='check_folio_id.dependence_id')
    subdependence_id = fields.Many2one(related='check_folio_id.subdependence_id')
    
    partner_id = fields.Many2one(related='payment_req_id.partner_id',string='Beneficiary')
    amount = fields.Monetary(related='payment_req_id.amount_total')

    date_printing = fields.Date(related='check_folio_id.date_printing',string='Check issue date')
    date_expiration = fields.Date(related='check_folio_id.date_expiration',string='Effective date')
    
    status = fields.Selection(related='check_folio_id.status',string='Check status')
    check_validity = fields.Integer(related='check_folio_id.bank_id.bank_id.check_validity',string='Days of validity')
    
    payment_method_name = fields.Char('Payment Name')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                select line.id as id,
                line.id as check_payment_req_id,
                line.check_folio_id as check_folio_id,
                line.payment_req_id as payment_req_id
                from check_payment_req line,
                account_move am,
                check_log cl                
                where line.is_withdrawn_circulation IS FALSE
                AND am.payment_state = 'assigned_payment_method'
                AND am.id=line.payment_req_id 
                AND cl.status = 'Protected and in transit'
                AND cl.id = line.check_folio_id
                            )'''% (self._table) 
        )    
    
    def action_withdrawn_from_circulation(self):
        if self.payment_req_id:
            self.payment_req_id.payment_state = 'payment_method_cancelled'
        if self.check_folio_id:
            self.check_folio_id.status = 'Withdrawn from circulation'
            self.check_payment_req_id.is_withdrawn_circulation = True         
                    