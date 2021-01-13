from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError

class SupplierPaymentRequest(models.Model):
    _inherit = 'account.move'

    payment_state = fields.Selection(selection_add=[('payment_method_cancelled', 'Payment method cancelled'),
                                                    ('rotated','Rotated'),
                                                    ('assigned_payment_method','Assigned Payment Method')])
    check_folio_id = fields.Many2one('check.log', "Check Sheet")
    related_check_folio_ids = fields.Many2many('check.log','rel_move_check_log','check_id','move_id',string="Related Check Sheets")
    related_check_history = fields.Char("Related Check Sheet")
    check_status = fields.Selection([('Checkbook registration', 'Checkbook registration'),
                          ('Assigned for shipping', 'Assigned for shipping'),
                          ('Available for printing', 'Available for printing'),
                          ('Printed', 'Printed'), ('Delivered', 'Delivered'),
                          ('In transit', 'In transit'), ('Sent to protection','Sent to protection'),
                          ('Protected and in transit','Protected and in transit'),
                          ('Protected', 'Protected'), ('Detained','Detained'),
                          ('Withdrawn from circulation','Withdrawn from circulation'),
                          ('Cancelled', 'Cancelled'),
                          ('Canceled in custody of Finance', 'Canceled in custody of Finance'),
                          ('On file','On file'),('Destroyed','Destroyed'),
                          ('Reissued', 'Reissued'),('Charged','Charged')], related='check_folio_id.status')

    def cancel_payment_method(self):
        for payment_req in self:
            if payment_req.is_payment_request == True or payment_req.is_project_payment == True:
                if payment_req.payment_state == 'for_payment_procedure':
                    payment_req.payment_state = 'payment_method_cancelled'
                    payment_req.payment_bank_id = False
                    payment_req.payment_bank_account_id = False
                    payment_req.payment_issuing_bank_id = False
                    payment_req.payment_issuing_bank_account_id = False
                    payment_req.l10n_mx_edi_payment_method_id = False
                    payment_ids = self.env['account.payment'].search([('payment_state','=','for_payment_procedure'),('payment_request_id','=',payment_req.id)])
                    for payment in payment_ids:
                        payment.cancel()
            if payment_req.payment_state == 'rotated' and payment_req.is_payment_request == True:
                payment_req.action_cancel_budget()

    def action_rotated(self):
#         self.ensure_one()
#         self.payment_state = 'registered'
#         self.batch_folio = ''

        return {
            'name': 'Reschecule Request',
            'view_mode': 'form',
            'view_id': self.env.ref('jt_supplier_payment.reschedule_request_form_view').id,
            'res_model': 'reschedule.request',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def write(self, vals):
        res = super(SupplierPaymentRequest, self).write(vals)
        for move in self:
            if move.is_payment_request and vals.get('payment_state') == 'paid' and move.check_folio_id:
                move.check_folio_id.status = 'Charged'
        return res


    @api.depends('name', 'state')
    def name_get(self):
        res = super(SupplierPaymentRequest, self).name_get()
        if self.env.context and self.env.context.get('show_name_and_folio_name', False):
            result = []
            for rec in self:
                if rec.folio:
                    name = ''
                    if rec.name:
                        name = rec.name 
                    name = name + "("+str(rec.folio)+")" or ''
                    result.append((rec.id, name))
                else:
                    result.append(
                        (rec.id, rec._get_move_display_name(show_ref=True)))
            return result and result or res

        elif self.env.context and self.env.context.get('show_folio_name', False):
            result = []
            for rec in self:
                if rec.folio:
                    name = rec.folio
                    result.append((rec.id, name))
                else:
                    result.append(
                        (rec.id, rec._get_move_display_name(show_ref=True)))
            return result and result or res
        
        else:
            return res

    def get_ticket_data(self):
        dependancy_ids = self.mapped('dependancy_id')
        ticket_data = []
        for dep in dependancy_ids:
            sub_inv_ids = self.filtered(lambda x:x.dependancy_id.id==dep.id)
            sub_dep_ids = sub_inv_ids.mapped('sub_dependancy_id')
            for sub in sub_dep_ids:
                inv_ids = self.filtered(lambda x:x.dependancy_id.id==dep.id and x.sub_dependancy_id.id==sub.id)
                dep_name = dep.description+ ' and ' + sub.description
                payment_id = self.env['payment.place'].search([('dependancy_id','=',dep.id),('sub_dependancy_id','=',sub.id)],limit=1)
                clave_no = ''
                if payment_id:
                    clave_no = payment_id.name
                
                    
                folio_min = min(x.check_folio_id.folio for x in inv_ids)
                folio_max = max(x.check_folio_id.folio for x in inv_ids)
                fornight = ''
                if not folio_min:
                    folio_min = ''
                if not folio_max:
                    folio_max = ''
                     
                if inv_ids:
                    fornight_inv_id = inv_ids.filtered(lambda x:x.fornight)
                    if fornight_inv_id:
                        fornight = str(fornight_inv_id[0].fornight)
                        if fornight_inv_id.invoice_date:
                            fornight += "/"+str(fornight_inv_id.invoice_date.year)
                            
                ticket_data.append({'dep_name':dep_name,'clave_no':clave_no,'folio_min':folio_min,'folio_max':folio_max,'fornight':fornight})
                
        return ticket_data
        
        