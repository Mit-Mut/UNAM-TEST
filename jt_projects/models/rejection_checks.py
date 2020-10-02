from odoo import models, fields, api

class RejectionChecks(models.Model):

    _name = 'rejection.checks'
    _description = "Rejections for CONACYT checks"
    _rec_name = 'key'

    key = fields.Char("Key")
    description = fields.Char("Description")