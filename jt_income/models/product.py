from odoo import models, fields, api

class Product(models.Model):

    _inherit = 'product.template'

    unit_id = fields.Many2one('dependency', string="Dependency")
    sub_dependency_id = fields.Many2one('sub.dependency', string="Subdependency")
    activity_id = fields.Many2one('activity.catalog', string="ID Activity")
    parent_product_id = fields.Many2one('product.product', string="Parent Product")
    sub_product = fields.Boolean("Subproduct")
    do_you_require_password = fields.Boolean("Do you require password?")
    ie_account_id = fields.Many2many('association.distribution.ie.accounts','ie_accounts_product','product_id','ie_account','IE Account')

    _sql_constraints = [('unique_default_code', 'unique(default_code)', 'Internal Reference must be unique.')]
    
    @api.onchange('parent_product_id')
    def onchange_parent_product(self):
        if self.parent_product_id:
            self.sub_product = True
        else:
            self.sub_product = False