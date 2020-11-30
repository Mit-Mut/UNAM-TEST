from odoo import models, fields, api


class RequestAccounts(models.Model):

    _name = 'request.accounts'
    _description = "Request to open account"
    _rec_name = 'invoice'

    invoice = fields.Char("Invoice", readonly=True, copy=False,
                          default='New')
    invoice_cancel = fields.Char("Invoice", readonly=True, copy=False,
                          default='New')
    project_id = fields.Many2one('project.project', "Project Number")
    project_name = fields.Char(
        related='project_id.name', string="Project Name")
    program_code = fields.Many2one('program.code', string='Program Code')
    user_id = fields.Many2one('hr.employee',
                              related='project_id.responsible_name', string="Project Manager")
    project_type_identifier = fields.Many2one(
        related='project_id.project_type_identifier_id', string="Project Type Identifier")
    project_stage_identifier = fields.Many2one(
        related='project_id.stage_identifier_id', string="Number of stages")
    ministrations_amount = fields.Float("Amount of ministrations")
    authorized_amount = fields.Float("Authorized Amount")
    observations = fields.Text("Observations")
    bank_account_id = fields.Many2one(
        "account.journal", string="Bank", domain=[('type', '=', 'bank')])
    bank_acc_number_id = fields.Many2one('res.partner.bank',
                                         related='bank_account_id.bank_account_id', string="Bank Account")
    no_contract = fields.Char(
        related='bank_account_id.contract_number', string='Contract No.')
    customer_number = fields.Char(
        related='bank_account_id.customer_number', string="Contact No.")
    supporting_documentation = fields.Binary("Supporting Documentation")
    supporting_doc_name = fields.Char('supporting documentation name')
    reason_rejection = fields.Selection([('discharge', 'Does not comply with the documentation supporting the discharge')],
                                        string="Reason for rejection")
    rejection_observations = fields.Text("Rejection observation")
    status = fields.Selection([('eraser', 'Eraser'),
                               ('request', 'Request'),
                               ('approved', 'Approved'),
                               ('confirmed', 'Confirmed'),
                               ('rejected', 'Rejected')], default='eraser', copy=False)

    move_type = fields.Selection([
        ('account cancel', 'Account Cancellation'),
        ('account open', 'Account Open'),
    ], 'Move Type')




    def generate_request(self):
        self.status = 'request'

    # @api.model
    # def create(self, vals):
    #     if vals.get('invoice', 'New') == 'New':
    #         vals['invoice'] = self.env['ir.sequence'].next_by_code(
    #             'request.accounts') or 'New'
    #     result = super(RequestAccounts, self).create(vals)
    #     return result


    @api.model
    def create(self, vals):
        result = super(RequestAccounts, self).create(vals)
        if result.move_type == 'account open':
            invoice = self.env['ir.sequence'].next_by_code('request.accounts')
            result.invoice = invoice

        elif result.move_type == 'account cancel':
            cancel = self.env['ir.sequence'].next_by_code('request.accounts.cancel') or 'New'
            result.invoice_cancel = cancel
    
        print("***",vals)
        return result


#     @api.onchange('project_no')
#     def onchage_project_no(self):
#         if self.project_no:
#             project = self.project_no
#             self.project_name = project.name
#             self.user_id = project.user_id if project.user_id else False
#             self.project_type_identifier = project.project_type
#             self.project_stage_identifier = project.stage_identifier

    def approve_account(self):
        self.write({'status': 'approved'})

    def confirm_account(self):
        self.write({'status': 'confirmed'})

    def reject_account(self):
        self.write({'status': 'rejected'})
