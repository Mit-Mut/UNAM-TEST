from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date, get_lang
from babel.dates import format_datetime, format_date


class EmployeePayroll(models.Model):

    _inherit = 'employee.payroll.file'
    
    check_folio_id = fields.Many2one('check.log', "Check Number")
    check_final_folio_id = fields.Many2one('check.log', "Check final number")

    @api.model
    def create(self,vals):
        res = super(EmployeePayroll,self).create(vals)
        check_payment_method = self.env.ref('l10n_mx_edi.payment_method_cheque').id
        if res.check_number and res.check_number.isnumeric() and res.l10n_mx_edi_payment_method_id and res.l10n_mx_edi_payment_method_id.id==check_payment_method:
            rec_check_number = int(res.check_number)  
                          
            check_id = self.env['check.log'].search([('folio','=',rec_check_number)],limit=1)
            if check_id:
                res.check_folio_id = check_id.id
        return res
    
    def write(self,vals):
        result = super(EmployeePayroll,self).write(vals)
        if 'check_number' in vals or 'l10n_mx_edi_payment_method_id' in vals:
            check_payment_method = self.env.ref('l10n_mx_edi.payment_method_cheque').id
            for res in self:
                if res.check_number and res.check_number.isnumeric() and res.l10n_mx_edi_payment_method_id and res.l10n_mx_edi_payment_method_id.id==check_payment_method:
                    rec_check_number = int(res.check_number)  
                                  
                    check_id = self.env['check.log'].search([('folio','=',rec_check_number)],limit=1)
                    if check_id:
                        if not res.check_folio_id:
                            res.check_folio_id = check_id.id
                        elif res.check_folio_id.id != check_id.id:
                            res.check_final_folio_id = check_id.id
                else:
                    res.check_final_folio_id = False     
        return result
        