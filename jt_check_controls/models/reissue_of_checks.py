from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ReissueOfChecks(models.Model):
    _name = 'reissue.checks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Reissue Of Checks'
    _rec_name = 'application_folio'
    
    application_folio = fields.Char('Application sheet')
    type_of_request = fields.Selection([('check_reissue','Check Reissue'),('check_cancellation','Check Cancellation')],
                                       string='Type of Request')
    # reissue_type = fields.Selection([('revocation','Revocación'),('reexped','Reexpedición o Reimpresión')],copy=False)
    type_of_request_payroll = fields.Selection(
        [('check_reissue', 'Check Reissue'), ('check_cancellation', 'Check Cancellation'),
         ('check_adjustments', 'Check Adjustments')], string='Type of Request')
    checkbook_req_id = fields.Many2one("checkbook.request", "Checkbook")
    check_log_id = fields.Many2one('check.log','Check Folio')
    check_log_ids = fields.Many2many('check.log','rel_reissue_check_log','log_id','reissue_id',compute="get_check_log_ids")
    
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id, string="Currency")
    check_amount = fields.Monetary(related='check_log_id.check_amount', currency_field='currency_id')
    status = fields.Selection(related='check_log_id.status')
    bank_id = fields.Many2one(related='check_log_id.bank_id')
    bank_account_id = fields.Many2one(related='check_log_id.bank_account_id')
    
    move_id = fields.Many2one('account.move','Payment request')
    folio_against_receipt = fields.Many2one('account.move','Folio against Receipt')
    folio_against_receipt_name = fields.Char(related='folio_against_receipt.folio',string='Folio')
    
    reason_reissue = fields.Text("Reason for Reissue")
    reason_cancellation = fields.Text("Reason for Cancellation")
    reason_rejection = fields.Text("Reason for rejection")
    reason_adjustments = fields.Text("Reason for Adjustment")
    description_layout = fields.Text("Description for Layout")
    
    is_physical_check = fields.Boolean("Do you have the physical check?")
    observations = fields.Text("Observations")
    partner_id = fields.Many2one(related='move_id.partner_id',string='Beneficiary')
    general_status = fields.Selection(related='check_log_id.general_status')
    
    dependence_id = fields.Many2one(related='check_log_id.dependence_id')
    subdependence_id = fields.Many2one(related='check_log_id.subdependence_id')
    date_protection = fields.Date(related='check_log_id.date_protection',string="Expedition date")
    
    state = fields.Selection([('draft','Draft'),('request','Request'),('approved','Approved'),('rejected','Rejected')],default='draft',string='Status')
    type_of_batch = fields.Selection([('supplier','Supplier'),('project','Project'),
                                      ('nominal','Nominal'),('pension','Pension')],string="Type Of Batch")

    type_of_reissue_id = fields.Many2one('type.of.reissue','Reissue type')
    fornight = fields.Selection(related='move_id.fornight',string='Fornight')
    employee_number = fields.Char(string='Employee number',compute='get_employee_number')

    def get_employee_number(self):
        for rec in self:
            emp_no = False
            if rec.partner_id:
                user_id = self.env['res.users'].search([('partner_id','=',rec.partner_id.id)],limit=1)
                if user_id:
                    emp_id = self.env['hr.employee'].search([('user_id','=',user_id.id)],limit=1)
                    if emp_id:
                        emp_no = emp_id.worker_number
            rec.employee_number = emp_no
              
    @api.onchange('move_id')
    def onchange_move_id(self):
        if self.move_id:
            self.folio_against_receipt = self.move_id.id
            self.check_log_id = self.move_id.check_folio_id and self.move_id.check_folio_id.id or False

    @api.onchange('folio_against_receipt')
    def onchange_folio_against_receipt(self):
        if self.folio_against_receipt:
            self.move_id = self.folio_against_receipt.id
            self.check_log_id = self.folio_against_receipt.check_folio_id and self.folio_against_receipt.check_folio_id.id or False

    @api.onchange('check_log_id')
    def onchange_check_log_id(self):
        if self.check_log_id:
            move_id = self.env['account.move'].search([('check_folio_id','=',self.check_log_id.id)],limit=1)
            if move_id:
                self.move_id = move_id.id
                self.folio_against_receipt = move_id.id
            self.checkbook_req_id = self.check_log_id.checklist_id and self.check_log_id.checklist_id.checkbook_req_id and self.check_log_id.checklist_id.checkbook_req_id.id or False 
                        
    @api.depends('type_of_request','checkbook_req_id', 'type_of_request_payroll')
    def get_check_log_ids(self):
        for rec in self:
            log_list = []
            if rec.type_of_request=='check_reissue':
                check_ids = self.env['check.log'].search([('status','in',('Delivered','Protected and in transit',
                                                                          'Cancelled'))])
                if rec.checkbook_req_id:
                    check_ids = check_ids.filtered(lambda x:x.checklist_id.checkbook_req_id.id==rec.checkbook_req_id.id)
                move_ids = self.env['account.move'].search([('check_folio_id','in',check_ids.ids),
                                    ('payment_state','in',('payment_method_cancelled','assigned_payment_method'))])
                if rec.type_of_batch == 'supplier':
                    move_ids = move_ids.filtered(lambda x:x.is_payment_request)
                elif rec.type_of_batch == 'project':
                    move_ids = move_ids.filtered(lambda x:x.is_project_payment)
                elif rec.type_of_batch == 'nominal':
                    move_ids = move_ids.filtered(lambda x:x.is_payroll_payment_request or x.is_different_payroll_request)
                elif rec.type_of_batch == 'pention':
                    move_ids = move_ids.filtered(lambda x:x.is_pension_payment_request)
                
                check_ids = move_ids.mapped('check_folio_id')
                log_list = check_ids.ids
            elif rec.type_of_request_payroll == 'check_reissue':
                check_ids = self.env['check.log'].search([('status', 'in', ('In transit', 'Protected',
                                                                            'Cancelled'))])
                if rec.checkbook_req_id:
                    check_ids = check_ids.filtered(
                        lambda x: x.checklist_id.checkbook_req_id.id == rec.checkbook_req_id.id)
                move_ids = self.env['account.move'].search([('check_folio_id', 'in', check_ids.ids),
                                                            ('payment_state', 'in',
                                                             ('payment_method_cancelled', 'assigned_payment_method'))])
                if rec.type_of_batch == 'nominal':
                    move_ids = move_ids.filtered(
                        lambda x: x.is_payroll_payment_request or x.is_different_payroll_request)
                elif rec.type_of_batch == 'pention':
                    move_ids = move_ids.filtered(lambda x: x.is_pension_payment_request)

                check_ids = move_ids.mapped('check_folio_id')
                log_list = check_ids.ids
            elif rec.type_of_request=='check_cancellation':
                check_ids = self.env['check.log'].search([('status','in',('Protected and in transit','Printed',
                                                                          'Detained','Withdrawn from circulation'))])
                if rec.checkbook_req_id:
                    check_ids = check_ids.filtered(lambda x:x.checklist_id.checkbook_req_id.id==rec.checkbook_req_id.id)
                    move_ids = self.env['account.move'].search([('check_folio_id','in',check_ids.ids)])
                    if rec.type_of_batch == 'supplier':
                        move_ids = move_ids.filtered(lambda x:x.is_payment_request)
                    elif rec.type_of_batch == 'project':
                        move_ids = move_ids.filtered(lambda x:x.is_project_payment)
                    elif rec.type_of_batch == 'nominal':
                        move_ids = move_ids.filtered(lambda x:x.is_payroll_payment_request or x.is_different_payroll_request)
                    elif rec.type_of_batch == 'pention':
                        move_ids = move_ids.filtered(lambda x: x.is_pension_payment_request)

                    check_ids = move_ids.mapped('check_folio_id')
                log_list = check_ids.ids
            elif rec.type_of_request_payroll == 'check_cancellation':
                check_ids = self.env['check.log'].search([('status', 'in', ('Protected', 'Printed',
                                                                        'Detained', 'Withdrawn from circulation'))])
                if rec.checkbook_req_id:
                    check_ids = check_ids.filtered(
                        lambda x: x.checklist_id.checkbook_req_id.id == rec.checkbook_req_id.id)
                    move_ids = self.env['account.move'].search([('check_folio_id', 'in', check_ids.ids)])
                    if rec.type_of_batch == 'nominal':
                        move_ids = move_ids.filtered(
                            lambda x: x.is_payroll_payment_request or x.is_different_payroll_request)
                    elif rec.type_of_batch == 'pention':
                        move_ids = move_ids.filtered(lambda x: x.is_pension_payment_request)

                    check_ids = move_ids.mapped('check_folio_id')
                log_list = check_ids.ids
            elif rec.type_of_request_payroll == 'check_adjustments':
                if rec.checkbook_req_id:
                    check_ids = self.env['check.log'].search([('status', '=', 'Printed')])
                    check_ids = check_ids.filtered(
                        lambda x: x.checklist_id.checkbook_req_id.id == rec.checkbook_req_id.id)
                    if self.type_of_batch == 'nominal':
                        move_ids = self.env['account.move'].search([('check_folio_id', 'in', check_ids.ids),
                                                                    '|', ('is_payroll_payment_request', '=', True),
                                                                    ('is_different_payroll_request', '=', True)])
                        check_ids = move_ids.mapped('check_folio_id')
                    elif self.type_of_batch == 'pension':
                        move_ids = self.env['account.move'].search([('check_folio_id', 'in', check_ids.ids),
                                                                    ('is_pension_payment_request', '=', True)])
                        check_ids = move_ids.mapped('check_folio_id')
                    log_list = check_ids.ids
            rec.check_log_ids= [(6, 0, log_list)]
                
    @api.model
    def create(self, vals):
        res = super(ReissueOfChecks, self).create(vals)
        application_no = self.env['ir.sequence'].next_by_code('reissue.check.folio')
        res.application_folio = application_no
        return res
    
    def action_request(self):
        self.state = 'request'
        check_control_admin_group = self.env.ref('jt_check_controls.group_check_control_admin')
        finance_admin_group = self.env.ref('jt_finance.group_finance_admin')
        check_control_admin_users = check_control_admin_group.users
        finance_admin_users = finance_admin_group.users
        activity_type = self.env.ref('mail.mail_activity_data_todo').id
        summary = "Approve '" + self.application_folio + "' Request for changes to the check"
        if self.type_of_batch == 'supplier':
            summary += " (Suppliers)"
        elif self.type_of_batch == 'project':
            summary += " (Project)"
        elif self.type_of_batch == 'nominal':
            summary += " (Payroll)"
        elif self.type_of_batch == 'pension':
            summary += " (Pension Payment)"
        activity_obj = self.env['mail.activity']
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'reissue.checks')]).id
        user_list = []
        # if self.type_of_reissue_id and self.type_of_reissue_id.name == 'Revocación':
        for user in check_control_admin_users:
            if user.id not  in user_list:
                activity_obj.create({'activity_type_id': activity_type,
                                   'res_model': 'reissue.checks', 'res_id': self.id,
                                   'res_model_id':model_id,
                                   'summary': summary, 'user_id': user.id})
                user_list.append(user.id)
        for user in finance_admin_users:
            if user.id not in user_list:
                activity_obj.create({'activity_type_id': activity_type,
                                   'res_model': 'reissue.checks', 'res_id': self.application_folio,
                                   'res_model_id':model_id,
                                   'summary': summary, 'user_id': user.id})
                user_list.append(user.id)

    
    def action_approve(self):
        self.state = 'approved'
        if self.check_log_id:
            self.check_log_id.status = 'Reissued'
            moves = self.env['account.move'].search([('check_folio_id', '=', self.check_log_id.id)])
            for move in moves:
                payment_ids = self.env['account.payment'].search([('payment_state', '=', 'for_payment_procedure'),
                                                                  ('payment_request_id', '=', move.id)])
                for payment in payment_ids:
                    payment.cancel()
                move.payment_state = 'payment_method_cancelled'
        if self.check_log_id and (self.type_of_request=='check_cancellation' or
                                  self.type_of_request_payroll=='check_cancellation'):
            self.check_log_id.status = 'Cancelled'
            self.check_log_id.date_cancellation = datetime.now().today()
            self.check_log_id.reason_cancellation = self.reason_cancellation
        if self.check_log_id and self.type_of_request_payroll=='check_adjustments':
            self.check_log_id.status = 'Detained'
            self.check_log_id.general_status = 'cancelled'
            self.check_log_id.reason_retention = self.reason_adjustments
        if self.move_id:
            self.move_id.cancel_payment_method()
                
    def action_reject(self):
        return {
            'name': _('Reject Reason'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'reissue.reject.reason.wizard',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_reissue_checks_id': self.id},
        }
    def action_set_reject(self):
        self.state = 'rejected'

    def action_layout_check_cancel(self):
        layout = False
        bank_ids = self.mapped('bank_id.bank_id')
        if bank_ids and len(bank_ids) > 1:
            raise ValidationError(_('Please select same bank for layout'))
        if self:
            if self[0].bank_id and self[0].bank_id.bank_id and self[0].bank_id.bank_id.name:
                if self[0].bank_id.bank_id.name.upper() == 'Banamex'.upper():
                    layout = 'Banamex'
                elif self[0].bank_id.bank_id.name.upper() == 'BBVA Bancomer'.upper():
                    layout = 'BBVA Bancomer'
                elif self[0].bank_id.bank_id.name.upper() == 'Scotiabank'.upper():
                    layout = 'Scotiabank'
                    
        return {
            'name': _('Generate Cancel Check Layout'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'generate.cancel.check.layout',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_reissue_ids': [(6,0,self.ids)],'default_layout':layout},
        }
        