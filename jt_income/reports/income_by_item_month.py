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

class IncomeByItemMonthReport(models.Model):
    
    _name = 'income.by.item.month.report'
    _description = 'Income By Item Month Report'
    _order = 'year,month'
    _auto = False

    
    year = fields.Char('Year')
    month = fields.Integer('Month No')
#    month_name = fields.Char('Month')
    enrollment_and_tuition = fields.Float('Enrollment And Tuition')
    selection_contest = fields.Float("Selection Contest")
    incorporation_and_revalidation = fields.Float("Incorporation And Revalidation")
    extraordinary_income = fields.Float("Extraordinary Income")
    patrimonial_income = fields.Float("Patrimonial Income")
    financial_products = fields.Float("Financial Products")
    total_other_income = fields.Float(string="Total",compute="get_total_other_income")
    nomina = fields.Float("Nomina")
    suppliers = fields.Float("Suppliers")
    other_benefits = fields.Float("Other Benefits")
    major_maintenance_fund = fields.Float("Major Maintenance Fund")
    fif_funds = fields.Float("FIF Funds")
    total_other_expense = fields.Float(string="Total",compute="get_total_other_expense")
       
    def get_total_other_income(self):
        for rec in self:
            rec.total_other_income = rec.enrollment_and_tuition + rec.selection_contest+rec.incorporation_and_revalidation+rec.extraordinary_income+rec.patrimonial_income+rec.financial_products

    def get_total_other_expense(self):
        for rec in self:
            rec.total_other_expense = rec.major_maintenance_fund + rec.fif_funds+rec.nomina+rec.suppliers+rec.other_benefits

#TO_CHAR(TO_DATE((extract(month from am.date))::text,'MM'),'Month') as month_name,
            
    def init(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                select max(am.id) as id,
                Cast((extract(year from am.date)) as Text) as year,
                (extract(month from am.date)) as month,
                sum(case when am.type_of_revenue_collection = 'dgoae_trades' then abs(am.amount_total_signed) else 0 end) enrollment_and_tuition,
                sum(case when am.type_of_revenue_collection = 'dgae_ref' then abs(am.amount_total_signed) else 0 end) selection_contest,
                sum(case when am.income_type = 'own' then abs(am.amount_total_signed) else 0 end) incorporation_and_revalidation,
                sum(case when am.type_of_revenue_collection = 'deposit_cer' and am.income_type = 'extra' then abs(am.amount_total_signed) else 0 end) extraordinary_income,
                sum(case when am.income_type = 'own' then abs(am.amount_total_signed) else 0 end) patrimonial_income,
                sum(case when am.income_type = 'extra' then abs(am.amount_total_signed) else 0 end) financial_products,
                sum(case when am.is_payroll_payment_request = True and am.payment_state='for_payment_procedure' then abs(am.amount_total_signed) else 0 end) nomina,
                sum(case when am.is_payment_request = True and am.payment_state='for_payment_procedure' then abs(am.amount_total_signed) else 0 end) suppliers,
                0 as major_maintenance_fund,
                0 as fif_funds,
                0 as other_benefits
                from account_move am
                where am.state='posted' 
                group by year,month
                            )'''% (self._table,) 
        )    

