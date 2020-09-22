from odoo import models, fields

class ActivityCatalog(models.Model):

    _name = 'activity.catalog'
    _description = "Activity Catalog"
    _rec_name = 'activity_id'

    activity_id = fields.Char("ID")
    description = fields.Text("Description")
    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.activity_id or ''
            if rec.description: 
                name += ' ' + rec.description
            result.append((rec.id, name))
        return result