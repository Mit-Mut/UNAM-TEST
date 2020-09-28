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

class ReportCalendarAmountAssign(models.Model):
    
    _name = 'report.calendar.amount.assign.line'
    _description = 'Report Calendar Amount Assign Line'
    _auto = False
    _order = 'item_first,item_second'
    
    item_first = fields.Char('Grouping by Object of Expenditure First')
    item_second = fields.Char('Grouping by Object of Expenditure')
    line_id = fields.Many2one('calendar.assigned.amounts.lines',"Lines")
    
    january = fields.Float(string='January')
    amount_deposite_january = fields.Float(string='Amount deposited January')
    pending_january = fields.Float(string='Receivable January')
    february = fields.Float(string='February')
    amount_deposite_february = fields.Float(string='Amount deposited February')
    pending_february = fields.Float(string='Receivable February')
    march = fields.Float(string='March')
    amount_deposite_march = fields.Float(string='Amount deposited March')
    pending_march = fields.Float(string='Receivable March')
    april = fields.Float(string='April')
    amount_deposite_april = fields.Float(string='Amount deposited April')
    pending_april = fields.Float(string='Receivable April')
    may = fields.Float(string='May')
    amount_deposite_may = fields.Float(string='Amount deposited May')
    pending_may = fields.Float(string='Receivable May')
    june = fields.Float(string='June')
    amount_deposite_june = fields.Float(string='Amount deposited June')
    pending_june = fields.Float(string='Receivable June')
    july = fields.Float(string='July')
    amount_deposite_july = fields.Float(string='Amount deposited July')
    pending_july = fields.Float(string='Receivable July')
    august = fields.Float(string='August')
    amount_deposite_august = fields.Float(string='Amount deposited August')
    pending_august = fields.Float(string='Receivable August')
    september = fields.Float(string='September')
    amount_deposite_september = fields.Float(string='Amount deposited September')
    pending_september = fields.Float(string='Receivable September')
    october = fields.Float(string='October')
    amount_deposite_october = fields.Float(string='Amount deposited October')
    pending_october = fields.Float(string='Receivable October')
    november = fields.Float(string='November')
    amount_deposite_november = fields.Float(string='Amount deposited November')
    pending_november = fields.Float(string='Receivable November')
    december = fields.Float(string='December')
    amount_deposite_december = fields.Float(string='Amount deposited December')
    pending_december = fields.Float(string='Receivable December')
    
    annual_amount = fields.Float(string='Annual Amount')

    clc_january = fields.Char('CLC January',compute="get_clc_folio",compute_sudo=True)
    clc_february = fields.Char('CLC February',compute="get_clc_folio",compute_sudo=True)
    clc_march = fields.Char('CLC March',compute="get_clc_folio",compute_sudo=True)
    clc_april = fields.Char('CLC April',compute="get_clc_folio",compute_sudo=True)
    clc_may = fields.Char('CLC May',compute="get_clc_folio",compute_sudo=True)
    clc_june = fields.Char('CLC June',compute="get_clc_folio",compute_sudo=True)
    clc_july = fields.Char('CLC July',compute="get_clc_folio",compute_sudo=True)
    clc_august = fields.Char('CLC August',compute="get_clc_folio",compute_sudo=True)
    clc_september = fields.Char('CLC September',compute="get_clc_folio",compute_sudo=True)
    clc_october = fields.Char('CLC October',compute="get_clc_folio",compute_sudo=True)
    clc_november = fields.Char('CLC November',compute="get_clc_folio",compute_sudo=True)
    clc_december = fields.Char('CLC December',compute="get_clc_folio",compute_sudo=True)
 
    def get_clc_folio(self):
        for line in self:
            line.clc_january = ''
            line.clc_february = ''
            line.clc_march = ''
            line.clc_april = ''
            line.clc_may = ''
            line.clc_june = ''
            line.clc_july = ''
            line.clc_august = ''
            line.clc_september = ''
            line.clc_october = ''
            line.clc_november = ''
            line.clc_december = ''
            
            assing_lines = self.env['calendar.assigned.amounts.lines'].search([('item_id_first','=',line.item_first),('item_id_second','=',line.item_second)])
            if assing_lines:
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',1)])
                if recived_lines:
                    line.clc_january = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',2)])
                if recived_lines:
                    line.clc_february = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',3)])
                if recived_lines:
                    line.clc_march = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',4)])
                if recived_lines:
                    line.clc_april = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',5)])
                if recived_lines:
                    line.clc_may = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',6)])
                if recived_lines:
                    line.clc_june = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',7)])
                if recived_lines:
                    line.clc_july = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',8)])
                if recived_lines:
                    line.clc_august = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',9)])
                if recived_lines:
                    line.clc_september = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',10)])
                if recived_lines:
                    line.clc_october = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',11)])
                if recived_lines:
                    line.clc_november = str(recived_lines.mapped('folio_clc')).strip('[]')
                recived_lines = self.env['control.amounts.received.line'].search([('calendar_assigned_amount_line_id','in',assing_lines.ids),('month_no','=',12)])
                if recived_lines:
                    line.clc_december = str(recived_lines.mapped('folio_clc')).strip('[]')
    
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
            select max(id) as id,item_id_first as item_first,item_id_second as item_second,max(id) as line_id,
                sum(annual_amount) as annual_amount,sum(january) as january,sum(amount_deposite_january) as amount_deposite_january,(sum(january-amount_deposite_january)) as pending_january,
                sum(february) as february,sum(amount_deposite_february) as amount_deposite_february,(sum(february-amount_deposite_february)) as pending_february,
                sum(march) as march,sum(amount_deposite_march) as amount_deposite_march,(sum(march-amount_deposite_march)) as pending_march,
                sum(april) as april,sum(amount_deposite_april) as amount_deposite_april,(sum(april-amount_deposite_april)) as pending_april,
                sum(may) as may,sum(amount_deposite_may) as amount_deposite_may,(sum(may-amount_deposite_may)) as pending_may,
                sum(june) as june,sum(amount_deposite_june) as amount_deposite_june,(sum(june-amount_deposite_june)) as pending_june,
                sum(july) as july,sum(amount_deposite_july) as amount_deposite_july,(sum(july-amount_deposite_july)) as pending_july,
                sum(august) as august,sum(amount_deposite_august) as amount_deposite_august,(sum(august-amount_deposite_august)) as pending_august,
                sum(september) as september,sum(amount_deposite_september) as amount_deposite_september,(sum(september-amount_deposite_september)) as pending_september,
                sum(october) as october,sum(amount_deposite_october) as amount_deposite_october,(sum(october-amount_deposite_october)) as pending_october,
                sum(november) as november,sum(amount_deposite_november) as amount_deposite_november,(sum(november-amount_deposite_november)) as pending_november,
                sum(december) as december,sum(amount_deposite_december) as amount_deposite_december,(sum(december-amount_deposite_december)) as pending_december 
            from calendar_assigned_amounts_lines
            group by item_id_first,item_id_second
            )'''% (self._table,) 
        )    
    
    
    
    
    
    
    
    
    
    