from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class ProjectTypeCustom(models.Model):

    _name = 'project.type.custom'
    _description = "Project Type Custom"

    name = fields.Char(string='Identifier', size=2)
    description = fields.Text(string='Description')

class BudgetProjectType(models.Model):
    
    _inherit = 'project.type'
    
    from_project = fields.Boolean('From Project',copy=False,default=False)
    name = fields.Char(string='Identifier', size=2)
    description = fields.Text(string='Description')


    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.from_project:
                name = rec.name
            else:
                name = rec.project_type_identifier
            result.append((rec.id, name))
            
        return result
    