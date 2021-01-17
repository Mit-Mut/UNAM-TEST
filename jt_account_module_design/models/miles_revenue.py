from odoo import models, fields, api,_

class ProjectCustomStage(models.Model):

    _name = 'miles.revenue'
    _description = "Miles Revenue"

    concept = fields.Char(string='Concept')
    year = fields.Date(string="Year")
    stage = fields.Char(string="Stage")
    project_type = fields.Char(string="Project Type")
    account_ids = fields.Many2many('account.account', string='Account')