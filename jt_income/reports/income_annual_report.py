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

class IncomeAnnualReport(models.Model):
    
    _name = 'income.annual.report'
    _description = 'Income Annual Report'
    _order = 'year'
    _auto = False

    sub_origin_resource_id = fields.Many2one('sub.origin.resource', "Name")
    year = fields.Char('Year')
    january = fields.Float('January')
    february = fields.Float('February')
    march = fields.Float('March')
    april = fields.Float('April')
    may = fields.Float('May')
    june = fields.Float('June')
    july = fields.Float('July')
    august = fields.Float('August')
    september = fields.Float('September')
    october = fields.Float('October')
    november = fields.Float('November')
    december = fields.Float('December')
    total = fields.Float('Total')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                select max(ap.id) as id,ap.sub_origin_resource_id as sub_origin_resource_id,
                Cast((extract(year from payment_date)) as Text) as year,
                sum(case when extract(month from payment_date) = 1 then amount else 0 end) january,
                sum(case when extract(month from payment_date) = 2 then amount else 0 end) february,
                sum(case when extract(month from payment_date) = 3 then amount else 0 end) march,
                sum(case when extract(month from payment_date) = 4 then amount else 0 end) april,
                sum(case when extract(month from payment_date) = 5 then amount else 0 end) may,
                sum(case when extract(month from payment_date) = 6 then amount else 0 end) june,
                sum(case when extract(month from payment_date) = 7 then amount else 0 end) july,
                sum(case when extract(month from payment_date) = 8 then amount else 0 end) august,
                sum(case when extract(month from payment_date) = 9 then amount else 0 end) september,
                sum(case when extract(month from payment_date) = 10 then amount else 0 end) october,
                sum(case when extract(month from payment_date) = 11 then amount else 0 end) november,
                sum(case when extract(month from payment_date) = 12 then amount else 0 end) december,
                sum(amount) as total
                from account_payment ap
                where ap.sub_origin_resource_id IS NOT NULL and ap.state in ('posted','reconciled') 
                and ap.partner_type='customer' and ap.payment_type = 'inbound'
                group by sub_origin_resource_id,year
                            )'''% (self._table,) 
        )    

# group by item_id_first,item_id_second