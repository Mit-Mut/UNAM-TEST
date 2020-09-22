from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResBank(models.Model):

    _inherit = 'res.partner.bank'

    for_income = fields.Boolean("Income")