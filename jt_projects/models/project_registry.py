from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import ValidationError, UserError

class ProjectRegistry(models.Model):
    _inherit = 'project.project'
    _description = "CONACYT Project Registry"

    project_type = fields.Selection([('conacyt', 'CONACYT'),
                                     ('concurrent', 'Concurrent'),
                                     ('other', 'Other projects with checkbook')], "Project Type")
    project_type_identifier_id = fields.Many2one(
        'project.type', string="Project Type Identifier")

    proj_start_date = fields.Date("Start Date")
    proj_end_date = fields.Date("End Date")
    visibility = fields.Selection(
        [('due', 'due'), ('expire', 'expire')], 'visibility')
    program_code = fields.Many2one('program.code', string='Program Code')
    rfc = fields.Char("RFC of the person in charge",related="responsible_name.rfc")
    allocated_amount = fields.Monetary("Allocated Amount")
    approved_amount = fields.Monetary("Approved Amount")
    trade_number = fields.Char("Trade Number")
    status = fields.Selection([('open', 'Open'),
                               ('closed', 'Closed')], "Status", default='open')
    check_counts = fields.Integer(compute='compute_count')
    bank_account_id = fields.Many2one("account.journal", "Bank")
    bank_acc_number_id = fields.Many2one(
        "res.partner.bank", related='bank_account_id.bank_account_id', string="Bank Key")
    branch_office = fields.Char(
        related='bank_acc_number_id.branch_number', string="Square")
    ministrations = fields.Integer("Number of ministrations")
    ministering_amount = fields.Monetary("Ministering amount")
    check_project_due = fields.Boolean(
        "Check Project Due", default=True, compute="get_project_due", store=True)
    check_project_expire = fields.Boolean(
        "Check Project expire", default=True, compute="get_project_due", store=True)

    is_papiit_project = fields.Boolean(
        'PAPIIT project', default=False, copy=False)

    is_related_agreement = fields.Boolean(
        'Is It related to agreement?', default=False)

    is_code_create = fields.Boolean('Code Created',copy=False,default=False)
    
    agreement_type_id = fields.Many2one("agreement.type", "Agreement Type")

    resource_type = fields.Selection(
        [('R', 'R (Remnant)'), ('P', 'P (Budget)')], string="Resource Type")
    pre_account_id = fields.Many2one('account.account', 'Previous')
    PAPIIT_project_type = fields.Selection(
        [('PAPIIT', 'PAPIIT'), ('PAPIME', 'PAPIME'), ('INFOCAB', 'INFOCAB')], string="PAPIIT Project Type")
    dependency_id = fields.Many2one('dependency', "Dependency")
    subdependency_id = fields.Many2one('sub.dependency', "Sub Dependency")
    technical_support_id = fields.Many2one('hr.employee', 'Technical support')
    administrative_manager_id = fields.Many2one(
        'hr.employee', 'Administrative Manager')
    exercised_amount = fields.Monetary("Amount exercised")
    final_amount = fields.Monetary(
        string="Final amount", compute='get_final_amount', store=True)
    co_responsible_id = fields.Many2one('hr.employee', 'Co-responsible Name')
    co_responsible_rfc = fields.Char(
        related='co_responsible_id.rfc', string='Co-responsible RFC')
    responsible_name = fields.Many2one('hr.employee', 'Responsible name')
    stage_identifier_id = fields.Many2one('stage', string="Stage")

    project_ministrations_ids = fields.One2many(
        'project.ministrations', 'project_id', string='Project Ministrations')

    custom_stage_id = fields.Many2one('project.custom.stage','Stage')
    custom_stage_description = fields.Text(related='custom_stage_id.description',string="Description Stage")
    custom_project_type_id = fields.Many2one('project.type.custom','Project Type Identifier')
    
    program_code_ids = fields.Many2many('program.code','program_code_project_rel','program_id','project_id',compute="get_program_ids")
    project_status = fields.Selection(
        [('open', 'Open'), ('close', 'Close')], string="Project Status")

    base_id = fields.Many2one('bases.collaboration','Type of Agreement')

    
    @api.onchange('custom_stage_id')
    def onchange_custom_stage_id(self):
        if self.custom_stage_id:
            self.stage_identifier = self.custom_stage_id.name
            self.desc_stage = self.custom_stage_id.description
        else:
            self.stage_identifier = ''
            self.desc_stage = ''

    @api.onchange('custom_project_type_id')
    def onchange_custom_project_type_id(self):
        if self.custom_project_type_id:
            self.project_type_identifier = self.custom_project_type_id.name
        else:
            self.project_type_identifier = ''

    @api.onchange('base_id')
    def onchange_base_id(self):
        if self.base_id:
            self.name_agreement = self.base_id.name
            self.number_agreement = self.base_id.convention_no
            self.agreement_type = self.base_id and self.base_id.agreement_type_id and self.base_id.agreement_type_id.code or ''
        else:
            self.name_agreement = ''
            self.number_agreement = ''
            self.agreement_type = ''
                 
#     agreement_type = fields.Char(related='base_id.name',stringname='Agreement Type', size=2)
#     name_agreement = fields.Text(related='base_id.name',string='Name Agreement')
#     number_agreement = fields.Char(related='base_id.convention_no',string='Number Agreement', size=6)
        
    @api.depends('is_papiit_project')
    def get_program_ids(self):
        for rec in self:
            lines = self.env['adequacies.lines'].search([('line_type','=','increase'),('adequacies_id.state','=','accepted'),('adequacies_id.is_from_project','=',True)])
            if lines:
                rec.program_code_ids = [
                    (6, 0, lines.mapped('program').ids)]
            else:
                rec.program_code_ids = [(6, 0, [])]
    
    # @api.onchange('project_type_identifier_id')
    # def onchange_project_type_identifier_id(self):
    #     if self.project_type_identifier_id:
    #         self.number = self.project_type_identifier_id.number

    @api.constrains('allocated_amount')
    def check_allocated_amount(self):
        if self.allocated_amount == 0 and self.project_type=='conacyt':
            raise UserError(_('Please add allocated amount'))

        if self.allocated_amount == 0 and self.is_papiit_project:
            raise UserError(_('Please add allocated amount'))


    @api.constrains('approved_amount')
    def check_approved_amount(self):
        if self.approved_amount == 0 and self.project_type=='conacyt':
            raise UserError(_('Please add approved amount'))


    @api.constrains('exercised_amount')
    def check_exercised_amount(self):
        if self.exercised_amount == 0 and self.is_papiit_project:
            raise UserError(_('Please add Amount exercised'))

    @api.onchange('stage_identifier_id')
    def onchange_stage_identifier_id(self):
        if self.stage_identifier_id:
            self.desc_stage = self.stage_identifier_id.desc

    @api.onchange('program_code')
    def onchange_program_code(self):
        if self.program_code:
            
            self.custom_stage_id = self.program_code.stage_id and self.program_code.stage_id.project_id and self.program_code.stage_id.project_id.custom_stage_id and self.program_code.stage_id.project_id.custom_stage_id.id or False 
            self.desc_stage = self.program_code.desc_stage
            self.number = self.program_code.project_number
            self.custom_project_type_id = self.program_code.project_type_id and self.program_code.project_type_id.project_id and self.program_code.project_type_id.project_id.custom_project_type_id and self.program_code.project_type_id.project_id.custom_project_type_id.id or False
            self.agreement_type_id = self.program_code.agreement_type_id.id
            self.name_agreement = self.program_code.name_agreement
            self.number_agreement = self.program_code.number_agreement
            self.dependency_id = self.program_code.dependency_id.id
            self.subdependency_id = self.program_code.sub_dependency_id

    @api.depends('exercised_amount', 'allocated_amount')
    def get_final_amount(self):
        for rec in self:
            rec.final_amount = rec.allocated_amount - rec.exercised_amount

    def compute_count(self):
        for record in self:
            record.check_counts = self.env['expense.verification'].search_count(
                [('project_number_id', '=', self.number)])

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
                name = ''
                if project.number:
                    name = project.number
            else:
                name = project.name
            result.append((project.id, name))
        return result

    # @api.onchange('user_id')
    # def onchnage_user_id(self):
    #     if self.user_id:
    #         self.rfc = self.user_id.partner_id.vat

    @api.onchange('bank_account_id')
    def onchnage_bank_account_id(self):
        if self.bank_account_id and self.bank_account_id.bank_account_id:
            self.bank_acc_number_id = self.bank_account_id.bank_account_id
            self.branch_office = self.bank_account_id.branch_number

    def close_project(self):
        #self.status = 'closed'
        return {
            'name': 'Project Close',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'project.close',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_current_id': self.id,
                        'default_project_id':self.id,
                        'default_is_papiit_project' : self.is_papiit_project,
                        'active_ids': self.ids}
        }

    def show_attachment(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        
        }
        action['domain'] = [
            ('res_model', '=', 'project.project'),('res_id', 'in', self.ids)]

        return action

    def count_expense_checks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Checks',
            'view_mode': 'tree,form',
            'res_model': 'expense.verification',
            'domain': [('project_number_id', '=', self.number)],
            'context': "{'create': False}"
        }

    def create_program_code(self):
        stage_id = False
        type_id = False
        stage = self.env['stage'].search([('project_id','=',self.id)],limit=1)
        if stage:
            stage_id = stage.id
            
        project_type_id = self.env['project.type'].search([('project_id','=',self.id)],limit=1)
        if project_type_id:
            type_id = project_type_id.id
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Program Code',
            'view_mode': 'form',
            'res_model': 'project.program.code',
            'target':'new',
            #'domain': [('project_number_id', '=', self.number)],
            'context': {'default_conacyt_project_id': self.id,
                        'default_stage_id':stage_id,
                        'default_project_type_id':type_id,
                        },
        }
        
class ProjectMinistrations(models.Model):

    _name = 'project.ministrations'
    _description = "Project Ministrations"

    project_id = fields.Many2one('project.project', 'Project')
    ministrations = fields.Integer("Number of ministrations")
    ministering_amount = fields.Float("Ministering amount")
