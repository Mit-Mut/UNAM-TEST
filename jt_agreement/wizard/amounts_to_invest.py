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
import base64
from odoo.http import request, content_disposition

class BasesCollaborationAmountstoInvest(models.TransientModel):
    _name = 'bases.collaboration.amounts.invest'
    _description = "Bases of collaboration - Amounts to Invest"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    line_ids = fields.One2many('bases.collaboration.amounts.invest.line', "wizard_id")
    is_hide_button = fields.Boolean(default=False)

    def print_amount_invest_bases_collaboration(self):
        lines = []
        pdf_rec = self.env['bases.collaboration.amounts.invest'].create(
            {'is_hide_button': True, 'start_date': self.start_date, 'end_date': self.end_date})
        for rec in self.env.context.get('active_ids'):
            qr_pdf = self.env.ref('jt_agreement.collaboration_amount_to_invest_report').with_context(
                start_date=self.start_date,end_date=self.end_date).render_qweb_pdf([rec])[0]
            qr_pdf = base64.b64encode(qr_pdf)
            lines.append((0, 0, {'bases_id': rec, 'file': qr_pdf,
                                 'filename': 'bases_collaboration_amouts_to_invest.pdf'}))
        pdf_rec.line_ids = lines

        return {
            'name': 'Download Files',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'bases.collaboration.amounts.invest',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': pdf_rec.id,
            'context': {'active_ids': self.env.context.get('active_ids')}
        }


class AccountStatementLine(models.TransientModel):
    _name = 'bases.collaboration.amounts.invest.line'
    _description = "Bases of collaboration - Amounts to Invest Lines"

    wizard_id = fields.Many2one('bases.collaboration.amounts.invest')
    bases_id = fields.Many2one('bases.collaboration')
    file = fields.Binary(string='File')
    filename = fields.Char(string='File name')

    def download_pdf(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'download',
            'url': "web/content/?model=bases.collaboration.amounts.invest.line&id=" + str(
                self.id) + "&filename_field=filename&field=file&download=true&filename=" + self.filename,
        }

