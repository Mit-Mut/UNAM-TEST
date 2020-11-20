from odoo import models, fields, api , _
from datetime import datetime
from odoo.exceptions import UserError


class DistributionOfIncome(models.Model):

    _name = 'distribution.of.income'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Distribution Of Income"
    
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    line_ids = fields.One2many('distribution.of.income.line','distribution_id',string='Lines')
    calculation_line_ids = fields.One2many('distribution.of.income.calculation','distribution_id',string='Lines')
    
    
    all_agreement = fields.Boolean(string='All the Agreement',default=False)
    all_types_of_Agreements = fields.Boolean(string='All Types of Agreements',default=False)
    all_base = fields.Boolean(string='All Bases Of Collaboration',default=False)
    all_dependencies = fields.Boolean(string='All Dependencies',default=False)
    
    fund_ids = fields.Many2many('agreement.fund','fund_dist_inc_link','fund_id','dist_link','By Funds')
    agreement_type_ids = fields.Many2many('agreement.agreement.type','agreement_dist_inc_link','fund_id','dist_link','By Type of Agreements')
    base_ids = fields.Many2many('bases.collaboration','base_co_dist_inc_link','fund_id','dist_link','By Collaboration Base')
    dependency_ids = fields.Many2many('dependency','depen_dist_inc_link','fund_id','dist_link','By Unit')
    reason_rejection = fields.Text("Reason Rejection")
    
    state = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                               ('rejected', 'Rejected'),
                               ('approved', 'Approved'),
                               ('confirmed', 'Confirmed'),
                               ('done', 'Done'),
                               ('canceled', 'Canceled')], string="Status", default="draft")
    

    journal_id = fields.Many2one('account.journal','Bank')
    if_fixed = fields.Boolean("Fixed")
    if_average = fields.Boolean("Average")
    if_variable = fields.Boolean("Variable")

    fixed_rate = fields.Float("Rate")
    average_rate = fields.Float("Rate")
    variable_rate = fields.Float("Rate")

    fixed_extra = fields.Float("Extra Percentage")
    average_extra = fields.Float("Extra Percentage")
    variable_extra = fields.Float("Extra Percentage")
    
    #@api.onchange('start_date','end_date','dependency_ids','agreement_type_ids','base_ids','fund_ids')


    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_('You can delete only draft status data.'))
        return super(DistributionOfIncome, self).unlink()
    
    def action_calculation(self):
        #domain = [('bases_collaboration_id','!=',False)]
        domain = []
        self.line_ids = [(6, 0, [])]
        self.calculation_line_ids = [(6, 0, [])]
        vals = []
        cal_vals = []
        if self.start_date:
            domain.append(('registration_date','>=',self.start_date))
        if self.end_date:
            domain.append(('registration_date','<=',self.end_date))
            
        base_ids = self.env['bases.collaboration'].search(domain)
        #base_ids = requests.mapped('bases_collaboration_id')
        
        if self.dependency_ids and not self.all_dependencies:
            base_ids = base_ids.filtered(lambda x:x.dependency_id.id in self.dependency_ids.ids)
        if self.agreement_type_ids and not self.all_types_of_Agreements:
            base_ids = base_ids.filtered(lambda x:x.agreement_type_id.id in self.agreement_type_ids.ids)
        if self.base_ids and not self.all_base:
            base_ids = base_ids.filtered(lambda x:x.id in self.base_ids.ids)
        if self.fund_ids and not self.all_agreement:
            base_ids = base_ids.filtered(lambda x:x.agreement_type_id.fund_id.id in self.fund_ids.ids)

        
        for base in base_ids:
            requests = self.env['request.open.balance'].search([('bases_collaboration_id','=',base.id),('state','=','confirmed')])
            inc = sum(x.opening_balance for x in requests.filtered(lambda a:a.bases_collaboration_id.id==base.id and a.type_of_operation == 'increase'))
            withdrawal = sum(x.opening_balance for x in requests.filtered(lambda a:a.bases_collaboration_id.id==base.id and a.type_of_operation == 'withdrawal'))
            
#             inc = 0
#             withdrawal = 0
            
  
#             vals.append([0, 0, 
#                         {'fund_id':base.agreement_type_id and base.agreement_type_id.fund_id and base.agreement_type_id.fund_id.id or False,
#                          'agreement_type_id':base.agreement_type_id and base.agreement_type_id.id or False,
#                          'base_id' : base.id,
#                          'dependency_id' : base.dependency_id and base.dependency_id.id or False,
#                          'capital' : base.opening_bal,
#                          'increments' : inc,
#                          'withdrawals' : withdrawal,
#                          'final_balance' : final_balance 
#                          }])

            
            inv_records = self.env['investment.investment'].search([('base_collaboration_id','=',base.id)])
            for inv in inv_records:
                term = 0
                if inv.is_fixed_rate:
                    term = inv.term
                elif inv.is_variable_rate:
                    term = inv.term_variable
                rate = inv.interest_rate + inv.extra_percentage 
                    
                final_balance = inv.amount_to_invest + inc - withdrawal
                income = (((final_balance * rate)/100)/360)*term
                               
                cal_vals.append([0, 0, 
                            {
                             'fund_id':base.agreement_type_id and base.agreement_type_id.fund_id and base.agreement_type_id.fund_id.id or False,
                             'agreement_type_id':base.agreement_type_id and base.agreement_type_id.id or False,
                             'base_id' : base.id,
                             'dependency_id' : inv.dependency_id and inv.dependency_id.id or False,
                             'capital' : inv.amount_to_invest,
                             'increments' : inc,
                             'withdrawals' : withdrawal,
                             'final_balance' : final_balance,
                             'income' : income,
                             'rounded': income,
                             'rate' : rate,
                             'days': term
                             }]) 
 
#         self.line_ids = vals
        self.calculation_line_ids = cal_vals 

    def action_confirm(self):
        today = datetime.today().date()
        user = self.env.user
        employee = self.env['hr.employee'].search(
            [('user_id', '=', user.id)], limit=1)
        fund_type = False
        amount = sum(x.income for x in self.calculation_line_ids)
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.money.market.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_amount': amount,
                'default_date': today,
                'default_employee_id': employee.id if employee else False,
                'default_distribution_id': self.id,
                'default_fund_type': fund_type,
                #'default_bank_account_id' : self.journal_id and self.journal_id.id or False,
                'show_for_supplier_payment': 1,
            }
        }

    def action_requested(self):
        self.state = 'requested'

    def action_approved(self):
        self.state = 'approved'

    def action_confirmed(self):
        self.state = 'confirmed'
        
    def action_reject(self):
        self.state = 'rejected'
        
class DistributionOfIncomeLine(models.Model):
    
    _name = 'distribution.of.income.line'
    _description = "Distribution Of Income Line"
    
    distribution_id = fields.Many2one('distribution.of.income','Distribution') 
    
    fund_id = fields.Many2one('agreement.fund','Fund')
    agreement_type_id = fields.Many2one('agreement.agreement.type','Type Of Agreements')
    base_id = fields.Many2one('bases.collaboration','Name of the B.C')
    dependency_id = fields.Many2one('dependency','Dependency')
    dependency_name = fields.Char(related='dependency_id.dependency',string='Dependency')
    dependency_description = fields.Text(related='dependency_id.description',string='Dependency Description')
    capital = fields.Float("Capital")
    increments = fields.Float("Increments")
    withdrawals = fields.Float("Withdrawals")
    final_balance = fields.Float("Final Balance")
    
class DistributionOfIncomecalculation(models.Model):
    
    _name = 'distribution.of.income.calculation'
    _description = "Distribution Of Income Line"
    
    distribution_id = fields.Many2one('distribution.of.income','Distribution')    

    fund_id = fields.Many2one('agreement.fund','Fund')
    agreement_type_id = fields.Many2one('agreement.agreement.type','Type Of Agreements')
    base_id = fields.Many2one('bases.collaboration','Basis of Collaboration')    
    dependency_id = fields.Many2one('dependency','Dependency')
    dependency_name = fields.Char(related='dependency_id.dependency',string='Dependency')
    dependency_description = fields.Text(related='dependency_id.description',string='Dependency Description')
    capital = fields.Float("Capital")
    increments = fields.Float("Increments")
    withdrawals = fields.Float("Withdrawals")
    final_balance = fields.Float("Final Balance")
    income = fields.Float('Income')
    rounded = fields.Float("Rounded")
    rate = fields.Float("Average Rate")
    days = fields.Integer("Days")
    
    
    