from odoo import models, fields, api


class ProjectRegistry(models.Model):
    _inherit = 'project.project'
    _description = "CONACYT Project Registry"

    project_type = fields.Selection([('conacyt', 'CONACYT'),
                                     ('concurrent', 'Concurrent'),
                                     ('other', 'Other projects with checkbook')], "Project Type")
    proj_start_date = fields.Date("Start Date")
    proj_end_date = fields.Date("End Date")
    rfc = fields.Char("RFC of the person in charge")
    allocated_amount = fields.Monetary("Allocated Amount")
    approved_amount = fields.Monetary("Approved Amount")
    trade_number = fields.Char("Trade Number")
    status = fields.Selection([('open', 'Open'),
                               ('closed', 'Closed')], "Status", default='open')
    bank_account_id = fields.Many2one("account.journal", "Bank Accounts")
    bank_acc_number_id = fields.Many2one("res.partner.bank", "Bank Key")
    branch_office = fields.Char("Square")
    ministrations = fields.Integer("Number of ministrations")
    ministering_amount = fields.Monetary("Ministering amount")


    def name_get(self):
        result = []
        for project in self:
            if 'from_conacyt' in self._context:
                name = project.number
            else:
                name = project.name
            result.append((project.id, name))
        return result


    @api.onchange('user_id')
    def onchnage_user_id(self):
        if self.user_id:
            self.rfc = self.user_id.partner_id.vat


    @api.onchange('bank_account_id')
    def onchnage_bank_account_id(self):
        if self.bank_account_id and self.bank_account_id.bank_account_id:
            self.bank_acc_number_id = self.bank_account_id.bank_account_id
            self.branch_office = self.bank_account_id.branch_office


    def close_project(self):
        self.status = 'closed'
