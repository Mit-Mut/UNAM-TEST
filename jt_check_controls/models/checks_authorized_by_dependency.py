from odoo import models, fields, api, _

class CheckAuthorizedByDependency(models.Model):

    _name = 'check.authorized.dependency'
    _description = "Check Authorized By Dependency"
    _rec_name = 'dependency_id'

    dependency_id = fields.Many2one('dependency', string="Dependence")
    subdependency_id = fields.Many2one('sub.dependency', string="Subdependence")
    area = fields.Char("Area")
    max_authorized_checks = fields.Integer("Maximum authorized checks")
    checks_authorized_on_previous_app = fields.Integer("Checks authorized on previous applications",
                                                       compute='_compute_checks')
    checks_remaining_to_auth = fields.Integer("Checks remaining to authorize", compute='_compute_checks')

    def _compute_checks(self):
        check_req_obj = self.env['checkbook.request']
        for rec in self:
            check_reqs = check_req_obj.search([('dependence_id', '=', rec.dependency_id.id),
                                               ('are_test_prin_formats_sent', '=', True),
                                                               ('state', '=', 'approved')])
            rec.checks_authorized_on_previous_app = len(check_reqs)
            rec.checks_remaining_to_auth = rec.max_authorized_checks - len(check_reqs)
