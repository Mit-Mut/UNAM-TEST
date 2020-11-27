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


    def transfer_request(self):

        today = datetime.today().date()
        # fund_ids = self.line_ids.mapped('fund_id')
        # opt_lines = []
        # for fund in fund_ids:
        #     base_ids = self.line_ids.filtered(lambda x:x.fund_id.id==fund.id).mapped('base_collabaration_id')
        #     for base in base_ids:
        #         lines = self.line_ids.filtered(lambda x:x.investment_fund_id.id==fund.id and x.base_collabaration_id.id == base.id and not x.is_request_generated and x.line_state == 'done')
        #         inc = sum(a.amount for a in lines.filtered(lambda x:x.type_of_operation in ('open_bal','increase')))
        #         ret = sum(a.amount for a in lines.filtered(lambda x:x.type_of_operation in ('retirement','withdrawal','withdrawal_cancellation','withdrawal_closure','increase_by_closing')))
        #         balance = inc - ret
        #         if balance > 0:
        #             opt_lines.append((0,0,{'opt_line_ids':[(6,0,lines.ids)],'investment_fund_id':fund.id,'base_collabaration_id':base.id,'agreement_number':base.convention_no,'amount':balance}))

            # lines = self.line_ids.filtered(lambda x:x.investment_fund_id.id==fund.id and not x.base_collabaration_id and x.line_state == 'done')
            # inc = sum(a.amount for a in lines.filtered(lambda x:x.type_of_operation in ('open_bal','increase')))
            # ret = sum(a.amount for a in lines.filtered(lambda x:x.type_of_operation in ('retirement','withdrawal','withdrawal_cancellation','withdrawal_closure','increase_by_closing')))
            # balance = inc - ret
            # if balance > 0:
            #     opt_lines.append((0,0,{'opt_line_ids':[(6,0,lines.ids)],'investment_fund_id':fund.id,'amount':balance}))
                    
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'inv.transfer.request',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_date': today,
                'default_bank_account_id' : self.journal_id and self.journal_id.id or False,
                # 'default_line_ids' : opt_lines,
                'show_for_agreement' : True,
            }
        }


    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_('You can delete only draft status data.'))
        return super(DistributionOfIncome, self).unlink()
    
    def action_calculation(self):
        #domain = [('bases_collaboration_id','!=',False)]
        domain = [('line_state','=','done'),('dependency_id','!=',False)]
        
        self.line_ids = [(6, 0, [])]
        self.calculation_line_ids = [(6, 0, [])]
        vals = []
        cal_vals = []
        if self.start_date:
            domain.append(('date_required','>=',self.start_date))
        if self.end_date:
            domain.append(('date_required','<=',self.end_date))
        
        if self.journal_id:
            domain.append(('investment_id.journal_id','<=',self.journal_id.id))
            
        #base_ids = self.env['bases.collaboration'].search(domain)
        #base_ids = requests.mapped('bases_collaboration_id')
        
        opt_lines = self.env['investment.operation'].search(domain,order='dependency_id')
        
        
        if self.dependency_ids and not self.all_dependencies:
            opt_lines = opt_lines.filtered(lambda x:x.dependency_id.id in self.dependency_ids.ids)
        if self.agreement_type_ids and not self.all_types_of_Agreements:
            opt_lines = opt_lines.filtered(lambda x:x.agreement_type_id.id in self.agreement_type_ids.ids)
        if self.base_ids and not self.all_base:
            opt_lines = opt_lines.filtered(lambda x:x.base_collabaration_id.id in self.base_ids.ids)
        if self.fund_ids and not self.all_agreement:
            opt_lines = opt_lines.filtered(lambda x:x.investment_fund_id.fund_id.id in self.fund_ids.ids)
        
        inv_funds = opt_lines.mapped('investment_fund_id')
        for fund  in inv_funds:
            dependency_ids = opt_lines.filtered(lambda x: x.investment_fund_id.id == fund.id).mapped('dependency_id')
            for dep in dependency_ids: 
                lines = opt_lines.filtered(lambda x:x.investment_fund_id.id == fund.id and x.dependency_id.id==dep.id)
                capital = sum(a.amount for a  in lines.filtered(lambda x:x.type_of_operation == 'open_bal'))
                 
                for line in lines.filtered(lambda x:x.type_of_operation != 'open_bal'):
                    inc = 0
                    withdrawal = 0
                    if line.type_of_operation in ('increase','increase_by_closing'):
                        inc = line.amount
                    elif line.type_of_operation in ('retirement','withdrawal','withdrawal_cancellation','withdrawal_closure'):
                        withdrawal = line.amount
                    
                    inv = line.investment_id
                    
                    term = 0
                    rate = 0
                    if inv.is_fixed_rate:
                        term = inv.term
                        rate = inv.interest_rate + inv.extra_percentage
                        
                    elif inv.is_variable_rate:
                        v_rate = 0
                        term = inv.term_variable
                        if inv.investment_rate_id:
                            other_rate_id = False
                            if not other_rate_id: 
                                if inv.term_variable == 28 and inv.investment_rate_id.rate_days_28:
                                    v_rate = inv.investment_rate_id.rate_days_28
                                    other_rate_id = True
                                else:
                                    other_rate_id = self.env['investment.period.rate'].search([('rate_days_28','>',0),('rate_date','<=',inv.investment_rate_id.rate_date),('product_type','=',inv.investment_rate_id.product_type)],limit=1,order='rate_date desc')
                                    if other_rate_id:
                                        v_rate = other_rate_id.rate_days_28
                                    other_rate_id = True
                                    
                            if not other_rate_id:
                                if inv.term_variable == 91 and inv.investment_rate_id.rate_days_91:
                                    v_rate = inv.investment_rate_id.rate_days_91
                                    other_rate_id = True
                                else:
                                    other_rate_id = self.env['investment.period.rate'].search([('rate_days_91','>',0),('rate_date','<=',inv.investment_rate_id.rate_date),('product_type','=',inv.investment_rate_id.product_type)],limit=1,order='rate_date desc')
                                    if other_rate_id:
                                        v_rate = other_rate_id.rate_days_91
                                    other_rate_id = True
                                    
                            if not other_rate_id:                                    
                                if inv.term_variable == 182 and inv.investment_rate_id.rate_days_182:
                                    v_rate = inv.investment_rate_id.rate_days_182
                                    other_rate_id = True
                                else:
                                    other_rate_id = self.env['investment.period.rate'].search([('rate_days_182','>',0),('rate_date','<=',inv.investment_rate_id.rate_date),('product_type','=',inv.investment_rate_id.product_type)],limit=1,order='rate_date desc')
                                    if other_rate_id:
                                        v_rate = other_rate_id.rate_days_182
                                    other_rate_id = True
                                    
                        rate = v_rate + inv.extra_percentage
                        
                    final_balance = capital + inc - withdrawal
                    income = (((final_balance * rate)/100)/360)*term
                                   
                    cal_vals.append([0, 0, 
                                {
                                 'fund_id':line.investment_fund_id and line.investment_fund_id.fund_id and line.investment_fund_id.fund_id.id or False,
                                 'agreement_type_id':line.agreement_type_id and line.agreement_type_id.id or False,
                                 'base_id' : line.base_collabaration_id and line.base_collabaration_id.id or False,
                                 'dependency_id' : line.dependency_id and line.dependency_id.id or False,
                                 'capital' : capital,
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
    
    
    