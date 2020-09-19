from odoo import models, fields, api

class SubOriginResource(models.Model):

    _name = 'sub.origin.resource'
    _description = "Sub origin of Resource"

    name = fields.Char("Sub origin of Resource")
    resource_id = fields.Many2one('resource.origin', "Source of Resource")
    key = fields.Selection(related="resource_id.key_origin",string='Key origin of the resource')
    is_it_enabled_for_agreement = fields.Boolean("Is it enabled for agreement?")


class ResourceOrigin(models.Model):
    
    _inherit = 'resource.origin'
    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.key_origin or ''
            if rec.desc and self.env.context and self.env.context.get('show_desc_name',False): 
                name = dict(rec._fields['desc'].selection).get(rec.desc)
            result.append((rec.id, name))
        return result    