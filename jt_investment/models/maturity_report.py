from odoo import models, fields, api
from odoo.addons.base.models.res_partner import _tz_get

class MaturityReport(models.Model):

    _name = 'maturity.report'
    _description = "Maturity Report"

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner')
    date = fields.Date("Date")
    fund_id = fields.Many2one('investment.funds', "Fund")
    po_sale_security_id = fields.Many2one('purchase.sale.security', "Purchase/Sale of Securities")
    investment_id = fields.Many2one('investment.investment', "Investment")
    cetes_id = fields.Many2one('investment.cetes', "CETES")
    udibonos_id = fields.Many2one('investment.udibonos', "Udibonos")
    bonds_id = fields.Many2one('investment.bonds', "Bonds")
    will_pay_id = fields.Many2one("investment.will.pay", "I Will Pay")
    non_business_day = fields.Boolean("Non Business Day")
    type = fields.Selection([('non_business_day', 'Non Business Day'),
                             ('business_day', 'Business Day')], default='business_day')

    user_id = fields.Many2one('res.users', 'Owner', states={'done': [('readonly', True)]},
                              default=lambda self: self.env.user)
    start_date = fields.Date("Starting At")
    stop_date = fields.Date("Ending At")
    allday = fields.Boolean("All Day")
    start_datetime = fields.Datetime("Starting At")
    event_tz = fields.Selection('_event_tz_get', string='Timezone',
                                default=lambda self: self.env.context.get('tz') or self.user_id.tz)
    duration = fields.Float("Duration")
    description = fields.Text("Description")
    categ_ids = fields.Many2many('calendar.event.type', 'rel_maturity_report_event_type',
                                 'maturity_report_id', 'rel_report_event_id', "Tags")
    alarm_ids = fields.Many2many('calendar.alarm', 'calendar_alarm_maturity_report_rel', string='Reminders',
                                 ondelete="restrict", copy=False)
    location = fields.Char("Location")
    recurrency = fields.Boolean("Recurrent")
    interval = fields.Integer("Interval")
    rrule_type = fields.Selection([('daily', 'Days'), ('weekly', 'Weeks'),
                                   ('monthly', 'Months'), ('yearly', 'yearly')])
    end_type = fields.Selection([('count', "Number of Repetation"),
                                 ('end_Date', 'End Date')])
    final_date = fields.Date("Final Date")
    count = fields.Integer("Count")
    privacy = fields.Selection([('public', 'Evety One'),
                    ('private', 'Only Me'), ('confidencial', 'Only Internal Users')], string="Privacy")
    show_as = fields.Selection([('free', 'Free'), ('busy', 'Busy')], string="Show As")
    mo = fields.Boolean("Mon")
    tu = fields.Boolean("Tue")
    we = fields.Boolean("Wed")
    th = fields.Boolean("Thu")
    fr = fields.Boolean("Fri")
    sa = fields.Boolean("Sat")
    su = fields.Boolean("Sun")
    month_by = fields.Selection([('date', "Date of Month"),
                                 ('day', "Day of Month")], "Day of Month")
    day = fields.Integer("Day")
    byday = fields.Selection([('1', 'First'),
                              ('2', 'Second'),
                              ('3', 'Third'),
                              ('4', 'Forth'),
                              ('5', 'Fifth'),
                              ('-1', 'Last'),
                              ])
    week_list = fields.Selection([('MO', 'Monday'),
                                  ('TU', 'Tuesday'),
                                  ('WE', 'Wednesday'),
                                  ('Th', 'Thrusday'),
                                  ('FR', 'Friday'),
                                  ('ST', 'Saturday'),
                                  ('SU', 'Sunday')])

    @api.model
    def _event_tz_get(self):
        return _tz_get(self)

class CalendarPaymentRegistration(models.Model):

    _inherit = 'calendar.payment.regis'

    @api.model
    def create(self, vals):
        res = super(CalendarPaymentRegistration, self).create(vals)
        maturity_obj = self.env['maturity.report']
        if res.type_pay == 'Non Business Day' and res.date:
            mat_rec = maturity_obj.search([('date', '=', res.date),
                                           ('non_business_day', '=', True)], limit=1)
            if not mat_rec:
                maturity_obj.create({
                    'name': 'Non Business Day',
                    'non_business_day': True,
                    'date': res.date,
                    'type': 'non_business_day'
                })
        return res

    def write(self, vals):
        res = super(CalendarPaymentRegistration, self).write(vals)
        maturity_obj = self.env['maturity.report']
        for rec in self:
            if vals.get('type_pay') and vals.get('type_pay') == 'Non Business Day' and rec.date:
                mat_rec = maturity_obj.search([('date', '=', rec.date),
                                               ('non_business_day', '=', True)], limit=1)
                if not mat_rec:
                    maturity_obj.create({
                        'name': 'Non Business Day',
                        'non_business_day': True,
                        'date': rec.date,
                        'type': 'non_business_day'
                    })
            elif vals.get('type_pay') and vals.get('type_pay') == 'Payment schedule' and rec.date:
                mat_rec = maturity_obj.search([('date', '=', rec.date),
                                               ('non_business_day', '=', True)], limit=1)
                if mat_rec:
                    mat_rec.unlink()
        return res

    def unlink(self):
        maturity_obj = self.env['maturity.report']
        for rec in self:
            if rec.type_pay == 'Non Business Day' and rec.date:
                mat_rec = maturity_obj.search([('date', '=', rec.date),
                                               ('non_business_day', '=', True)], limit=1)
                if mat_rec:
                    mat_rec.unlink()
        return super(CalendarPaymentRegistration, self).unlink()

    def create_maturity_report(self):
        maturity_obj = self.env['maturity.report']
        for rec in self:
            if rec.type_pay == 'Non Business Day' and rec.date:
                mat_rec = maturity_obj.search([('date', '=', rec.date),
                                     ('non_business_day', '=', True)], limit=1)
                if not mat_rec:
                    maturity_obj.create({
                        'name': 'Non Business Day',
                        'non_business_day': True,
                        'date': rec.date,
                        'type': 'non_business_day'
                    })

