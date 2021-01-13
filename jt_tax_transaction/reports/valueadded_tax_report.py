from odoo import models, api, fields, _

class ValueaddedTaxReport(models.AbstractModel):

    _name = "jt_tax_transaction.valueadded.report"
    _inherit = "account.generic.tax.report"
    _description = "Report ​ for the determination of Value Added Tax by"