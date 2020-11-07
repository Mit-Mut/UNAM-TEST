from odoo import models, fields, api
from datetime import date


class ProjectRegistry(models.Model):
    _inherit = 'project.project'
    _description = "CONACYT Project Registry"

    project_type = fields.Selection([('conacyt', 'CONACYT'),
                                     ('concurrent', 'Concurrent'),
                                     ('other', 'Other projects with checkbook')], "Project Type")
    proj_start_date = fields.Date("Start Date")
    proj_end_date = fields.Date("End Date")
    visibility = fields.Selection(
        [('due', 'due'), ('expire', 'expire')], 'visibility')
    program_code = fields.Many2one('program.code', string='Program Code')
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
    check_project_due = fields.Boolean(
        "Check Project Due", default=True, compute="get_project_due", store=True)
    check_project_expire = fields.Boolean(
        "Check Project expire", default=True, compute="get_project_due", store=True)

    def get_project_due_records(self):
        open_project = self.env['project.project'].search(
            [('status', '=', 'open')])
        if open_project:
            open_project.get_project_due()

    @api.depends('proj_end_date', 'status')
    def get_project_due(self):
        for rec in self:
            if rec.proj_end_date and rec.status:
                end_date = rec.proj_end_date
                today = date.today()
                diff = (end_date - today).days
                if end_date < today and rec.status == 'open':
                    rec.check_project_due = True
                else:
                    rec.check_project_due = False
                if diff <= 21 and diff >= 0 and rec.status == 'open':
                    rec.check_project_expire = True
                else:
                    rec.check_project_expire = False
            else:
                rec.check_project_expire = False
                rec.check_project_due = False

    # def calculate_project_next_to_expire(self):

    #     end_date = self.proj_end_date
    #     today = date.today()
    #     days = end_date
    #     diff = (days - today).days
    #     if diff >= 21:
    #         self.visibility = 'expire'

    def calculate_project_overdue(self):
        print("calll")

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
        return {
            'name': 'Project Close',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'project.close',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_current_id': self.id}
        }

    def show_attachment(self):
        action = self.env.ref('base.action_attachment').read()[0]
        return action
