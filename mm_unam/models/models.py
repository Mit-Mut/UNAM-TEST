# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mm_unam(models.Model):
#     _name = 'mm_unam.mm_unam'
#     _description = 'mm_unam.mm_unam'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
