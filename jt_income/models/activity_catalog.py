from odoo import models, fields

class ActivityCatalog(models.Model):

    _name = 'activity.catalog'
    _description = "Activity Catalog"
    _rec_name = 'activity_id'

    activity_id = fields.Char("ID")
    description = fields.Text("Description")