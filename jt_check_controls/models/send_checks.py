from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class SendChecks(models.Model):
    _name = 'send.checks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'batch_folio'
    _description = 'Sending Checks To File'

    batch_folio = fields.Integer(string='Batch Folio')
    total_checks = fields.Integer(string="Total Number of Checks")
    responsible = fields.Char(string="Responsible for shipping")
    area_position = fields.Char(string="Area And Position")
    date = fields.Date(string="Date")
    approval_date = fields.Date(string="Approval Date")
    check_line_ids = fields.Many2many('send.checks.line', string="Check Line")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        ('destroy', 'Destroyed')
    ], default='draft', string="Status")

    def action_reject(self):
        self.status = 'reject'

    def action_approve(self):
        self.status = 'approved'
        approval = datetime.today().date()
        self.approval_date = approval
        for rec in self.check_line_ids:
            rec.check_log_id.status = 'On file'
        for res in self:
            if res.status == 'approved' and res.approval_date:
                res._send_notification_msg()

    def _send_notification_msg(self):

        for res in self:
            if res.status == 'approved' and res.approval_date:
                five_yrs_ago = (datetime.today().date() -
                                relativedelta(years=5))

                if res.approval_date == five_yrs_ago:

                    activity = self.env['mail.activity'].sudo().create({
                        'activity_type_id': self.env.ref('jt_check_controls.mail_act_send_checks').id,
                        'note': _('5 years old on file and can be destroyed'),
                        'res_id': res.id,
                        'user_id': self.env.user.id,
                        'res_model_id': self.env.ref('jt_check_controls.model_send_checks').id,
                    })
                    activity._onchange_activity_type_id()

    # def _write(self, vals):

    #     if self.env.context.get('mail_activity_automation_skip'):
    #         return super(SendChecks, self)._write()

    #     if 'approved' in self.status:
    #         if self.status == 'approved':
    #             filtered_self = self.search([('id', 'in', self.ids),
    #                                          ('user_id', '!=', False),
    #                                          ('status', '!=', 'approved')])
    #             filtered_self.activity_unlink(
    #                 ['jt_check_controls.mail_act_send_checks'])
    #             for check in filtered_self:
    #                 check.activity_schedule(
    #                     'jt_check_controls.mail_act_send_checks',
    #                     user_id=check.user_id.id,
    #                     note=_("5 years old on file and can be destroyed"))

    #     return super(SendChecks, self)._write()

    def action_destroy(self):
        self.status = 'destroy'
        for rec in self.check_line_ids:
            rec.check_log_id.status = 'Destroyed'


class SendChecksLines(models.Model):
    _name = 'send.checks.line'

    check_log_id = fields.Many2one('check.log', string="Check Folio")
    dependency_id = fields.Many2one('dependency', string="Dependency")
