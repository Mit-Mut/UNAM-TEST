from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ImportPayrollCheckIssue(models.Model):

    _name = 'import.payroll.check.issue'
    _description = "Import Payroll Check Issue"
    _rec_name = 'case'
    
    case = fields.Selection([('R','R'),('F','F'),('H','H'),('C','C')],string='Case')
    original_check_id = fields.Many2one('check.log','Original check number')
    original_bank_code = fields.Char('Original bank code')
    
    new_check_id = fields.Many2one('check.log','New check number')
    new_bank_code = fields.Char('New bank code')
    employee_id = fields.Many2one("hr.employee",'Employee number')
    original_fortnight = fields.Char('Original fortnight')
    new_fortnight = fields.Char('New fortnight')
    rfc = fields.Char('RFC')
    original_amount = fields.Float('Original amount')
    new_amount = fields.Float('New amount')
    upload_date = fields.Date(string="File Upload Date",default=datetime.today())
    
    def action_update_check_and_amount(self):
        for rec in self:
            if rec.new_amount > 0:
                if rec.original_check_id:
                    move_id = self.env['account.move'].search([('check_folio_id','=',rec.original_check_id.id)],limit=1)
                    if move_id: 
                        move_id.action_draft()
#                         if move_id.invoice_line_ids:
#                             move_id.invoice_line_ids[0].price_unit = rec.new_amount
#                             move_id.invoice_line_ids[0]._get_price_total_and_subtotal(price_unit=rec.new_amount)
#                             move_id.invoice_line_ids[0]._onchange_price_subtotal()
#                             move_id.invoice_line_ids[0]._onchange_balance()
#                             move_id.invoice_line_ids[0]._onchange_recompute_dynamic_lines()
#                             move_id._onchange_invoice_line_ids()
                        move_id.action_register()
                        if rec.new_check_id:
                            move_id.check_folio_id = rec.new_check_id.id
                            rec.new_check_id.status = 'Printed'
                    rec.original_check_id.status = 'Reissued'
            if rec.new_amount==0:
                if rec.original_check_id:
                    move_id = self.env['account.move'].search([('check_folio_id','=',rec.original_check_id.id)],limit=1)
                    if move_id: 
                        if rec.new_check_id:
                            move_id.check_folio_id = rec.new_check_id.id
                            rec.new_check_id.status = 'Printed'
                    rec.original_check_id.status = 'Reissued'
                