from odoo import models, fields


class RemainingResource(models.Model):
    _name = 'remaining.resource'
    _description = "Integration of remaining resources"
    _rec_name = 'concept'

    concept = fields.Char('Concept')
    stage = fields.Integer("Stage")
    year = fields.Integer("Year")
    project_type = fields.Selection(
        [('papit', 'PAPIIT'), ('papime', 'PAPIME'), ('infocab', 'INFOCAB')], string='Project Type')
    account_id = fields.Many2one('account.account')
