from odoo import fields, models, api

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

    def apply(self):
        check_req = self.env['checkbook.request'].browse(self._context.get('active_id'))
        if check_req:
            if check_req.bank_id:
                check_req.bank_id.checkbook_no = self.checkbook_no
            checklist = self.env['checklist'].create({
                'checkbook_no': self.checkbook_no,
                'received_boxes': self.received_boxes,
                'check_per_box': self.check_per_box,
                'additional_checks': self.additional_checks,
                'total_cash': self.total_cash,
                'checkbook_req_id': check_req.id
            })
            for folio in range(check_req.intial_folio, check_req.final_folio + 1):
                checklist.checklist_lines = [(0, 0, {
                    'folio': folio,
                    'status': 'Checkbook registration',
                    'bank_id': check_req.bank_id.id if check_req.bank_id else False,
                    'bank_account_id': check_req.bank_account_id.id if check_req.bank_account_id else False,
                    'checkbook_no': check_req.checkbook_no,
                    'dependence_id': check_req.dependence_id.id if check_req.dependence_id else False,
                    'subdependence_id': check_req.subdependence_id.id if check_req.subdependence_id else False
                })]
            check_req.state = 'confirmed'
