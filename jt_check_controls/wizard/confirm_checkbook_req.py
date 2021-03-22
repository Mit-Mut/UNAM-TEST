from odoo import fields, models, api,_
from odoo.exceptions import ValidationError, UserError

class ConfirmCheckBook(models.TransientModel):
    _name = 'confirm.checkbook'
    _description = 'Confirm Checkbook'

    checkbook_no = fields.Char("Checkbook No.")
    received_boxes = fields.Integer("Number of boxes received")
    check_per_box = fields.Integer("Checks per box")
    additional_checks = fields.Integer("Additional checks without cash")
    total_cash = fields.Integer("Total Checks", compute='calculate_total', store=True)

    @api.depends('received_boxes', 'check_per_box', 'additional_checks')
    def calculate_total(self):
        total = (self.received_boxes * self.check_per_box) + self.additional_checks
        self.total_cash = total

#     def validation_check_folio(self,check_req):
#         bank_id = check_req.bank_id and check_req.bank_id.id or False 
#         other_checkbook_ids = self.env['checkbook.request'].search([('state','=','confirmed'),('bank_id','=',bank_id)])
#         for checkbook in other_checkbook_ids:
#             if check_req.intial_folio >= checkbook.intial_folio and  check_req.intial_folio <= checkbook.final_folio:
#                 raise UserError(_('Cannot register folios that are already registered'))
#             if check_req.final_folio >= checkbook.intial_folio and  check_req.final_folio <= checkbook.final_folio:
#                 raise UserError(_('Cannot register folios that are already registered'))
#             if  checkbook.intial_folio >= check_req.intial_folio and  checkbook.final_folio <= check_req.intial_folio:
#                 raise UserError(_('Cannot register folios that are already registered'))
#             if  checkbook.intial_folio >= check_req.final_folio and  checkbook.final_folio <= check_req.final_folio:
#                 raise UserError(_('Cannot register folios that are already registered'))
            
    def apply(self):
        check_req = self.env['checkbook.request'].browse(self._context.get('active_id'))
        if check_req:
            if self.total_cash != check_req.amount_checks:
                raise ValidationError(_('Check total does not match the number of checks requested'))
            
            if check_req.bank_id:
                check_req.bank_id.checkbook_no = self.checkbook_no
                check_req.checkbook_no = self.checkbook_no
            checklist = self.env['checklist'].create({
                'checkbook_no': self.checkbook_no,
                'received_boxes': self.received_boxes,
                'check_per_box': self.check_per_box,
                'additional_checks': self.additional_checks,
                'total_cash': self.total_cash,
                'checkbook_req_id': check_req.id
            })
            check_log_list = [] 
            for folio in range(check_req.intial_folio, check_req.final_folio + 1):
                check_log_list.append((0, 0, {
                    'folio': folio,
                    'status': 'Checkbook registration' if folio != int(check_req.print_sample_folio_number) else \
                            'Cancelled',
                    'bank_id': check_req.bank_id.id if check_req.bank_id else False,
                    'bank_account_id': check_req.bank_account_id.id if check_req.bank_account_id else False,
                    'checkbook_no': check_req.checkbook_no,
                    # 'dependence_id': check_req.dependence_id.id if check_req.dependence_id else False,
                    # 'subdependence_id': check_req.subdependence_id.id if check_req.subdependence_id else False
                }))
            if check_log_list:
                checklist.checklist_lines = check_log_list
                
#                 checklist.checklist_lines = [(0, 0, {
#                     'folio': folio,
#                     'status': 'Checkbook registration' if folio != int(check_req.print_sample_folio_number) else \
#                             'Cancelled',
#                     'bank_id': check_req.bank_id.id if check_req.bank_id else False,
#                     'bank_account_id': check_req.bank_account_id.id if check_req.bank_account_id else False,
#                     'checkbook_no': check_req.checkbook_no,
#                     # 'dependence_id': check_req.dependence_id.id if check_req.dependence_id else False,
#                     # 'subdependence_id': check_req.subdependence_id.id if check_req.subdependence_id else False
#                 })]
            check_req.state = 'confirmed'
