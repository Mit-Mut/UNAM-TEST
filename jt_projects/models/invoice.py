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
from odoo import models, fields,api,_


class AccountMove(models.Model):

    _inherit = 'account.move'

    diary = fields.Many2one('account.journal', string='Diary')
    dependence = fields.Many2one('dependency', string="Dependency")
    subdependence = fields.Many2one('sub.dependency', string='Sub Dependence')
    leaves = fields.Integer('Leaves')
    project_code = fields.Char('Project Code')
    exchange_rate = fields.Char('Exchange Rate')
    foreign_currency_amount = fields.Monetary('Foreign currency amount')
    project_number_id = fields.Many2one(
        'project.project', string='Project Number')
    agreement_number = fields.Char(
        related='project_number_id.number_agreement', string='Agreement Number')
    stage = fields.Char(
        related='project_number_id.stage_identifier', string='Stage')
    excercise = fields.Char('excercise')
    project_key = fields.Char('Project Key')
    invoice_vault_folio = fields.Char('Invoice vault folio')
    status = fields.Selection(
        [('accept', 'Accepted'), ('reject', 'Rejected')], string='Status')
    line = fields.Integer("Header")
    previous = fields.Monetary('Previous')

    # More info Tab
    responsible_category_key = fields.Char("Responsible category key")
    responsible_job_position = fields.Many2one(
        'hr.job', 'Responsible job position')
    
class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    concept = fields.Char('Concept')
    bill = fields.Many2one('account.account')
    vat = fields.Char('Vat')
    retIVA = fields.Char('RetIVA')
    line = fields.Integer("Line")
    #other_amounts = fields.Monetary("Other Amounts")
    # price_payment = fields.Monetary("Price")
