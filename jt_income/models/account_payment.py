from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class account_payment(models.Model):
    _inherit = "account.payment"

    sub_origin_resource_id = fields.Many2one('sub.origin.resource', "Extraordinary / Own income")
        
    def action_register_payment(self):
        res = super(account_payment,self).action_register_payment()
        if res:
            active_ids = self.env.context.get('active_ids')
            if len(active_ids) == 1:
                move_id = self.env['account.move'].browse(active_ids)
                context = dict(res.get('context') or {})
                
                context.update({'default_dependancy_id' : move_id.dependancy_id and move_id.dependancy_id.id or False,
                                                  'default_sub_dependancy_id' : move_id.sub_dependancy_id and move_id.sub_dependancy_id.id or False,
                                                  'default_l10n_mx_edi_payment_method_id' : move_id.l10n_mx_edi_payment_method_id and move_id.l10n_mx_edi_payment_method_id.id or False,
                                                  'default_sub_origin_resource_id' : move_id.sub_origin_resource_id and move_id.sub_origin_resource_id.id or False, 
                                                  })
                if move_id.income_bank_journal_id:
                    context.update({'default_journal_id':move_id.income_bank_journal_id.id})
                res.update({'context':context})    
        return res

    def l10n_mx_edi_is_required(self):
        self.ensure_one()
        if self.invoice_ids:
            income_invoices= self.invoice_ids.filtered(lambda x:x.type_of_revenue_collection)
            if len(income_invoices) == len(self.invoice_ids):
                return False
        return super(account_payment,self).l10n_mx_edi_is_required()
    
    
class payment_register(models.TransientModel):
    
    _inherit = 'account.payment.register'
    _description = 'Register Payment'
    
    
    def _prepare_payment_vals(self, invoices):
        res = super(payment_register,self)._prepare_payment_vals(invoices)
        if invoices and len(invoices)==1:
            move_id = invoices[0]
            res.update({'dependancy_id' : move_id.dependancy_id and move_id.dependancy_id.id or False,
                                                  'sub_dependancy_id' : move_id.sub_dependancy_id and move_id.sub_dependancy_id.id or False,
                                                  'l10n_mx_edi_payment_method_id' : move_id.l10n_mx_edi_payment_method_id and move_id.l10n_mx_edi_payment_method_id.id or False,
                                                  'sub_origin_resource_id' : move_id.sub_origin_resource_id and move_id.sub_origin_resource_id.id or False, 
                                                  })
        return res
            
            
            