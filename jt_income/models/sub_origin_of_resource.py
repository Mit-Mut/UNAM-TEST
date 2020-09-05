from odoo import models, fields, api

class SubOriginResource(models.Model):

    _name = 'sub.origin.resource'
    _description = "Sub origin of Resource"

    name = fields.Char("Sub origin of Resource")
    resource_id = fields.Many2one('resource.origin', "Source of Resource")
    key = fields.Integer(string='Key origin of the resource')
    is_it_enabled_for_agreement = fields.Boolean("Is it enabled for agreement?")


    @api.onchange('resource_id')
    def onchange_resource_id(self):
        if self.resource_id and self.resource_id.key_origin:
            self.key = self.resource_id.key_origin
        else:
            self.key = 0