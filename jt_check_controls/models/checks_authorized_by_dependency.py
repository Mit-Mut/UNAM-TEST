from odoo import models, fields, api, _

class CheckAuthorizedByDependency(models.Model):

    _name = 'check.authorized.dependency'
    _description = "Check Authorized By Dependency"

    dependency_id = fields.Many2one('dependency', string="Dependence")
    subdependency_id = fields.Many2one('sub.dependency', string="Subdependence")
    area = fields.Char("Area")
    max_authorized_checks = fields.Integer("Maximum authorized checks")
    checks_authorized_on_previous_app = fields.Integer("Checks authorized on previous applications")
    checks_remaining_to_auth = fields.Integer("Checks remaining to authorize")