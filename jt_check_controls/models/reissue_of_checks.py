from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ReissueOfChecks(models.Model):
    _name = 'reissue.checks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Reissue Of Checks'
    _rec_name = 'application_folio'
    
    application_folio = fields.Char('Application sheet')
    type_of_request = fields.Selection([('check_reissue','Check Reissue'),('check_cancellation','Check Cancellation')],string='Type of Request')
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
    description_layout = fields.Text("Description for Layout")
    
    is_physical_check = fields.Boolean("Do you have the physical check?")
    observations = fields.Text("Observations")
    partner_id = fields.Many2one(related='move_id.partner_id',string='Beneficiary')
    general_status = fields.Selection(related='check_log_id.general_status')
    
    dependence_id = fields.Many2one(related='check_log_id.dependence_id')
    subdependence_id = fields.Many2one(related='check_log_id.subdependence_id')
    date_protection = fields.Date(related='check_log_id.date_protection',string="Expedition date")
    
    state = fields.Selection([('draft','Draft'),('request','Request'),('approved','Approved'),('rejected','Rejected')],default='draft',string='Status')

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
                        
    @api.depends('type_of_request')
    def get_check_log_ids(self):
        for rec in self:
            log_list = []
            if rec.type_of_request=='check_reissue':
                check_ids = self.env['check.log'].search([('status','in',('Delivered','Protected and in transit','Cancelled'))])
                move_ids = self.env['account.move'].search([('check_folio_id','in',check_ids.ids),('payment_state','in',('payment_method_cancelled','assigned_payment_method'))])
                check_ids = move_ids.mapped('check_folio_id') 
                log_list = check_ids.ids
            if rec.type_of_request=='check_cancellation':
                check_ids = self.env['check.log'].search([('status','in',('Protected and in transit','Printed','Detained','Withdrawn from circulation'))])
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
    
    def action_approve(self):
        self.state = 'approved'
        if self.check_log_id:
            self.check_log_id.status = 'Reissued'
            moves = self.env['account.move'].search([('check_folio_id', '=', self.check_log_id.id),
                                                   ('is_payment_request', '=', True)])
            for moves in moves:
                moves.payment_state = 'payment_method_cancelled'
            
        if self.check_log_id and self.type_of_request=='check_cancellation':    
            self.check_log_id.status = 'Cancelled'
            
        if self.move_id:
            self.move_id.cancel_payment_method()
                
    def action_reject(self):
        self.state = 'rejected'

    def action_layout_check_cancel(self):
        return {
            'name': _('Generate Cancel Check Layout'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'generate.cancel.check.layout',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_reissue_ids': [(6,0,self.ids)]},
        }
        