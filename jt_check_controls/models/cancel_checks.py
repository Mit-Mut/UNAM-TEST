from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class CancelChecks(models.Model):

    _name = 'cancel.checks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'check_folio'
    _description = "Cancel Checks"

    check_folio = fields.Integer(string="Check Folio")
    check_status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                               ('Assigned for shipping', 'Assigned for shipping'),
                               ('Available for printing', 'Available for printing'),
                               ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                               ('In transit', 'In transit'), ('Sent to protection', 'Sent to protection'),
                               ('Protected and in transit', 'Protected and in transit'),
                               ('Protected', 'Protected'), ('Detained', 'Detained'),
                               ('Withdrawn from circulation', 'Withdrawn from circulation'),
                               ('Cancelled', 'Cancelled'),
                               ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                               ('On file', 'On file'), ('Destroyed', 'Destroyed'),
                               ('Reissued', 'Reissued'), ('Charged', 'Charged')])
    dependency_id = fields.Many2one('dependency',string="Dependency")
    bank_id = fields.Many2one('account.journal',string="Bank")
    bank_account_id = fields.Many2one('res.partner.bank',string="Bank Account")
    checkbook_no = fields.Char(string="Checkbook")
    observation = fields.Char(string="Observation")
    status = fields.Selection([
    	('draft','Draft'),
    	('approved','Approved'), ('rejected', 'Rejected')
    	],default='draft',string="Status")
    check_log_id = fields.Many2one('check.log')
    lot_folio = fields.Integer(string="Lot Folio")
  
    def action_reject(self):
        self.ensure_one()
        self.status = 'rejected'

    def action_approve(self):
        self.ensure_one()
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'cancel.checks'), ('res_id', '=', self.id)])
        if attachment:
            self.status = 'approved'
            if self.check_log_id:
                self.check_log_id.status = 'Canceled in custody of Finance'
                self.check_status = 'Canceled in custody of Finance'
        else:
            raise ValidationError(_('It is necessary to attach the corresponding document.'))


    def action_generate_batch_folio(self):
      active_ids = self.env.context.get('active_ids')
      if not active_ids:
        return ''

      active_records = self.browse(active_ids)
      seq_ids = self.env['ir.sequence']
      if active_records:
        seq_ids = self.env['ir.sequence'].search([('code', '=', 'batch.folio')], order='company_id')
      number_next = 0
      if seq_ids:
          number_next = seq_ids[0].number_next_actual

      for rec in active_ids:
        check_id = self.browse(rec)
        batch_folio = check_id.lot_folio
        if not batch_folio:
          batch_folio = number_next
          self.lot_folio = batch_folio
  
    def action_request_send_checks(self):
        send_checks = self.env['send.checks']
        for rec in self:
            send_checks.create({
                    'batch_folio':rec.lot_folio,
                    'check_line_ids':[(0,0,{'check_folio':rec.check_folio,'dependency_id':rec.dependency_id.id})] 
                    })