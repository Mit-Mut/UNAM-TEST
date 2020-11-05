from odoo import models, fields, api
from datetime import datetime


class DistributionOfIncome(models.Model):

    _name = 'distribution.of.income'
    _description = "Distribution Of Income"
    
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    line_ids = fields.One2many('distribution.of.income.line','distribution_id',string='Lines')
    
    all_agreement = fields.Boolean(string='All the Agreement',default=False)
    all_types_of_Agreements = fields.Boolean(string='All Types of Agreements',default=False)
    all_base = fields.Boolean(string='All Bases Of Collaboration',default=False)
    all_dependencies = fields.Boolean(string='All Dependencies',default=False)
    
    fund_ids = fields.Many2many('agreement.fund','fund_dist_inc_link','fund_id','dist_link','By Funds')
    agreement_type_ids = fields.Many2many('agreement.agreement.type','agreement_dist_inc_link','fund_id','dist_link','By Type of Agreements')
    base_ids = fields.Many2many('bases.collaboration','base_co_dist_inc_link','fund_id','dist_link','By Collaboration Base')
    dependency_ids = fields.Many2many('dependency','depen_dist_inc_link','fund_id','dist_link','By Unit')
    
    state = fields.Selection([('draft', 'Draft'),
                               ('requested', 'Requested'),
                               ('rejected', 'Rejected'),
                               ('approved', 'Approved'),
                               ('confirmed', 'Confirmed'),
                               ('done', 'Done'),
                               ('canceled', 'Canceled')], string="Status", default="draft")
    

    @api.onchange('start_date','end_date')
    def onchange_data(self):
        domain = [('bases_collaboration_id','!=',False)]
        self.line_ids = [(6, 0, [])]
        vals = []
        if self.start_date:
            domain.append(('request_date','>=',self.start_date))
        if self.end_date:
            domain.append(('request_date','<=',self.end_date))
        requests = self.env['request.open.balance'].search(domain)
        
        base_ids = requests.mapped('bases_collaboration_id')
        
        for base in base_ids:
            inc = sum(x.opening_balance for x in requests.filtered(lambda a:a.bases_collaboration_id.id==base.id and a.type_of_operation == 'increase'))
            withdrawal = sum(x.opening_balance for x in requests.filtered(lambda a:a.bases_collaboration_id.id==base.id and a.type_of_operation == 'withdrawal'))
            final_balance = base.opening_bal + inc - withdrawal  
            
            vals.append([0, 0, 
                        {'fund_id':base.fund_id and base.fund_id.id or False,
                         'agreement_type_id':base.agreement_type_id and base.agreement_type_id.id or False,
                         'base_id' : base.id,
                         'dependency_id' : base.dependency_id and base.dependency_id.id or False,
                         'capital' : base.opening_bal,
                         'increments' : inc,
                         'withdrawals' : withdrawal,
                         'final_balance' : final_balance 
                         }]) 
         
        
        self.line_ids = vals
        
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
      
    
    
    
    