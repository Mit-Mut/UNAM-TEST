from odoo import models, fields, api

class SubOriginResource(models.Model):

    _name = 'sub.origin.resource'
    _description = "Sub origin of Resource"

    name = fields.Char("Sub origin of Resource")
    resource_id = fields.Many2one('resource.origin', "Source of Resource")
    key = fields.Selection(related="resource_id.key_origin",string='Key origin of the resource')
    is_it_enabled_for_agreement = fields.Boolean("Is it enabled for agreement?")
    income_type = fields.Selection([('extra', 'Extraordinary'),
                                    ('own', 'Own')], string="Income Type")
    report_name = fields.Char(string="Report",compute="get_report_display_name",store=True,copy=False)
    
    @api.depends('name')
    def get_report_display_name(self):
        for rec in self:
            if rec.name:
                if rec.name=='Servicios de educación Bancos (INS-RINS)':
                    rec.report_name = 'SERV. EDUC. BANCOS (INS-RINS)'
                elif rec.name=='Servicios de educación Caja Gral.':
                    rec.report_name = 'SERV. EDUC. CAJA GRAL.'
                elif rec.name=='Aspirantes':
                    rec.report_name = 'ASPIRANTES-LIC.'
                elif rec.name=='D.B.I.N.':
                    rec.report_name = 'D.B.I.N.'
                elif rec.name=='D.P.Y.D.':
                    rec.report_name = 'D.P.Y.D.'
                elif rec.name=='Venta almacén':
                    rec.report_name = 'VTA. ALMAC.'
                elif rec.name=='Licenciatarios':
                    rec.report_name = 'LICENCIATARIOS'
                elif rec.name=='DEP en garantia':
                    rec.report_name = 'DEP EN GARANTIA'
                elif rec.name=='DGIRE-bancos':
                    rec.report_name = 'DGIRE-BANCOS'
                elif rec.name=='DGIRE-caja':
                    rec.report_name = 'DGIRE-CAJA'
                else:
                    rec.report_name = rec.name
    
    

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