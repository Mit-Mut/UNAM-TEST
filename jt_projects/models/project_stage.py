from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class ProjectCustomStage(models.Model):

    _name = 'project.custom.stage'
    _description = "Project Custom Stage"

    name = fields.Char(string='Stage', size=2)
    description = fields.Text(string='Description')

    @api.constrains('name')
    def _check_name(self):
        if not str(self.name).isnumeric():
            raise ValidationError(_('The Stage must be numeric value'))

class BudgetStage(models.Model):
    
    _inherit = 'stage'
    
    from_project = fields.Boolean('From Project',copy=False,default=False)
    name = fields.Char(string='Stage', size=2)
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.from_project:
                name = rec.name
            else:
                name = rec.stage_identifier
            result.append((rec.id, name))
            
        return result

    