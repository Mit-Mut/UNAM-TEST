from odoo import models, fields, api, _

class MinimumCheck(models.Model):

    _name = 'minimum.checks'
    _description = "Minimum of Checks"

    name = fields.Char("Name")
    checkbook_id = fields.Many2one('res.partner.bank', "Checkbook")
    bank_id = fields.Many2one('account.journal', "Bank")
    minimum_of_checks = fields.Integer("Mimimum of Checks")
    reorder_point = fields.Integer("Reorder Point")