from odoo import models, fields

class DepositCertificateType(models.Model):

    _name = 'deposit.certificate.type'
    _description = "Type of Deposit Certificate"

    name = fields.Char("Name")
    description = fields.Text("General Description")