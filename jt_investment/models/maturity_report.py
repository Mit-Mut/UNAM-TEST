from odoo import models, fields, api

class MaturityReport(models.Model):

    _name = 'maturity.report'
    _description = "Maturity Report"

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner')
    date = fields.Date("Date")
    fund_id = fields.Many2one('investment.funds', "Fund")
    po_sale_security_id = fields.Many2one('purchase.sale.security', "Purchase/Sale of Securities")
    investment_id = fields.Many2one('investment.investment', "Investment")
    cetes_id = fields.Many2one('investment.cetes', "CETES")
    udibonos_id = fields.Many2one('investment.udibonos', "Udibonos")
    bonds_id = fields.Many2one('investment.bonds', "Bonds")
    will_pay_id = fields.Many2one("investment.will.pay", "I Will Pay")