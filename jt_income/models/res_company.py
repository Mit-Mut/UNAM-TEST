# -*- coding: utf-8 -*-

from odoo import fields,models,api,_

class company(models.Model):
	_inherit = "res.company"

	header_logo = fields.Binary(string="Header Logo")
	sign = fields.Binary(string="Sign")