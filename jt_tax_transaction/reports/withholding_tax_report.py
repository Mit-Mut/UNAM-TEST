from odoo import models, api, fields, _

class WithholdingTaxReport(models.AbstractModel):

    _name = "jt_tax_transaction.withholding.report"
    _inherit = "account.generic.tax.report"
    _description = "​ Withholding tax report"