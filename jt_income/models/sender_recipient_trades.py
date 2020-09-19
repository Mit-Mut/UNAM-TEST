from odoo import models, fields, api

class SenderRecipientTrades(models.Model):

    _name = 'sender.recipient.trades'
    _description = "Sender Recipient Trades"
    _rec_name = 'template'
    
    template = fields.Selection([('application_form_20','Application form 20%'),
                                 ('format_forgiveness','Format Forgiveness'),
                                 ('format_notice_change','Format notice change form of payment to transfer'),
                                 ('2nd application_form_20','2nd Application form 20%'),
                                 ('format_remission_20','Format remission 20%'),
                                 ('reporting_format_returned_check','Reporting format returned check'),
                                 ],string="Template")
    
    
    recipient_emp_id = fields.Many2one('hr.employee','Employee')
    recipient_title = fields.Char(related="recipient_emp_id.emp_title",string='Title')
    recipient_professional_title = fields.Char(related="recipient_emp_id.emp_job_title",string='Professional Title')

    sender_emp_id = fields.Many2one('hr.employee','Employee')
    sender_title = fields.Char(related="sender_emp_id.emp_title",string='Title')
    sender_professional_title = fields.Char(related="sender_emp_id.emp_job_title",string='Professional Title')
    
    employee_ids = fields.Many2many('hr.employee','rel_employee_sender_recipient_trades','sender_id','emp_id','EMPLOYEES COPIED')
    
    