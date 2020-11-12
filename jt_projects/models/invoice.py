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
from odoo import models, fields


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
    is_project_payment = fields.Boolean('Is Project Payment', default=True)
    line = fields.Integer("Line")
    previous = fields.Monetary('Previous')

    # More info Tab
    zone = fields.Integer("Zone")
    rate = fields.Monetary("Rate")
    days = fields.Integer("Days")
    responsible_category_key = fields.Char("Responsible category key")
    responsible_rfc = fields.Char(
        'VAT', related='responsible_id.rfc', store=True)
    responsible_job_position = fields.Many2one(
        'hr.job', 'Responsible job position')

    # def generate_folio(self):
    #     folio = ''
    #     if self.upa_key and self.upa_key.organization:
    #         folio += self.upa_key.organization + "/"
    #     if self.upa_document_type and self.upa_document_type.document_number:
    #         folio += self.upa_document_type.document_number + "/"
    #     folio += self.env['ir.sequence'].next_by_code('payment.folio')
    #     self.folio = folio

    def action_cancel_budget(self):
        self.ensure_one()
        self.payment_state = 'cancel'
        self.button_cancel()

    def button_cancel(self):
        for record in self:
            if record.is_payment_request or record.is_payroll_payment_request:
                if record.payment_state == 'cancel':
                    record.cancel_payment_revers_entry()
                    record.add_budget_available_amount()
        return super(AccountMove, self).button_cancel()

    def action_draft_budget(self):
        self.ensure_one()
        self.payment_state = 'draft'
        self.button_draft()
        conac_move = self.line_ids.filtered(lambda x: x.conac_move)
        conac_move.sudo().unlink()
        for line in self.line_ids:
            line.coa_conac_id = False

        self.add_budget_available_amount()

    def cancel_payment_revers_entry(self):
        revers_list = []
        for line in self.line_ids:
            revers_list.append((0, 0, {
                'account_id': line.account_id.id,
                'coa_conac_id': line.coa_conac_id and line.coa_conac_id.id or False,
                'credit': line.debit,
                'debit': line.credit,
                'exclude_from_invoice_tab': True,
                'conac_move': line.conac_move,
                'name': 'Reversa',
                'currency_id': line.currency_id and line.currency_id.id or False,
                'amount_currency': line.amount_currency,
            }))
        self.line_ids = revers_list

    def action_register(self):
        for move in self:
            move.generate_folio()
            move.payment_state = 'registered'


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    concept = fields.Char('Concept')
    bill = fields.Many2one('account.account')
    programatic_code_id = fields.Many2one(
        'program.code', string='Programmatic Code')
    egress_key_id = fields.Many2one("egress.keys", string="Egress Key")
    type_of_bussiness_line = fields.Char("Type Of Bussiness Line")
    vat = fields.Char('Vat')
    retIVA = fields.Char('RetIVA')
    turn_type = fields.Char("Turn type")
    other_amounts = fields.Monetary("Other Amounts")
    # price_payment = fields.Monetary("Price")
