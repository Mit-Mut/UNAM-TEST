from odoo import models, fields, api
from datetime import datetime

class Investment(models.Model):

    _name = 'investment.investment'
    _description = "Productive Accounts Investment"
    _rec_name = 'contract_id'
     
    invesment_date = fields.Datetime("Investment Date")
    journal_id = fields.Many2one("account.journal","Bank")
    contract_id = fields.Many2one('investment.contract','Contract')
    amount_to_invest = fields.Float("Amount to invest")
    is_fixed_rate = fields.Boolean('Fixed Rate',default=False)
    is_variable_rate = fields.Boolean('Variable Rate',default=False)
    interest_rate = fields.Float("Interest rate")
    extra_percentage = fields.Float("Extra percentage")
    term = fields.Integer("Fixed Term")
    term_variable = fields.Integer("Variable Term")
    capitalizable = fields.Integer("Days of capitalization")
    frequency = fields.Integer("Frequency of interest payments")
    currency_id = fields.Many2one("res.currency","Currency")
    currency_rate = fields.Float(related="currency_id.rate",string="Exchange rate")
    
    investment_rate_id = fields.Many2one("investment.period.rate","Exchange rate")
    observations = fields.Text("Observations")    
    file_data = fields.Binary("Supporting document")
    file_name = fields.Char("File Name")
    
    state = fields.Selection([('draft','Draft'),('requested','Requested'),('rejected','Rejected'),('approved','Approved'),('confirmed','Confirmed'),('done','Done'),('canceled','Canceled')],string="Status",default='draft')

    fund_type_id = fields.Many2one('fund.type', "Type Of Fund")
    agreement_type_id = fields.Many2one('agreement.agreement.type', 'Agreement Type')
    fund_id = fields.Many2one('agreement.fund','Fund') 
    fund_key = fields.Char(related='fund_id.fund_key',string="Password of the Fund")
    base_collaboration_id = fields.Many2one('bases.collaboration','Name Of Agreements')
    investment_fund_id = fields.Many2one('investment.funds','Investment Funds')
    
    dependency_id = fields.Many2one('dependency', "Dependency")
    sub_dependency_id = fields.Many2one('sub.dependency', "Subdependency")
    reason_rejection = fields.Text("Reason Rejection")
    
    #=====Profit==========#
    estimated_interest = fields.Float(string="Estimated Interest",compute="get_estimated_interest",store=True)
    estimated_profit = fields.Float(string="Estimated Profit",compute="get_estimated_profit",store=True)
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float(string="Real Profit")
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)

    #====== Accounting Fields =========#

    investment_income_account_id = fields.Many2one('account.account','Income Account')
    investment_expense_account_id = fields.Many2one('account.account','Expense Account')
    investment_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    

    return_income_account_id = fields.Many2one('account.account','Income Account')
    return_expense_account_id = fields.Many2one('account.account','Expense Account')
    return_price_diff_account_id = fields.Many2one('account.account','Price Difference Account')    
    sub_origin_resource = fields.Many2one('sub.origin.resource', "Origin of the resource")
    expiry_date = fields.Date(string="Expiration Date")

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        if self.contract_id:
            self.fund_type_id = self.contract_id.fund_type_id and self.contract_id.fund_type_id.id or False 
            self.agreement_type_id = self.contract_id.agreement_type_id and self.contract_id.agreement_type_id.id or False
            self.fund_id = self.contract_id.fund_id and self.contract_id.fund_id.id or False
            self.base_collaboration_id = self.contract_id.base_collabaration_id and self.contract_id.base_collabaration_id.id or False
        else:
            self.fund_type_id = False
            self.agreement_type_id = False
            self.fund_id = False
            self.base_collaboration_id = False
        
    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation =  rec.real_profit - rec.estimated_profit

    @api.depends('is_fixed_rate','is_variable_rate','amount_to_invest','interest_rate','extra_percentage','term_variable','term')
    def get_estimated_interest(self):
        for rec in self:
            term = 0
            if rec.is_fixed_rate:
                term = rec.term
            elif rec.is_variable_rate:
                term = rec.term_variable
            
            rec.estimated_interest =  (((rec.amount_to_invest*(rec.interest_rate+rec.extra_percentage))/100)/360)*term

    @api.depends('estimated_interest','amount_to_invest')
    def get_estimated_profit(self):
        for rec in self:
            rec.estimated_profit =  rec.estimated_interest + rec.amount_to_invest

    @api.onchange('is_fixed_rate')
    def onchange_is_fixed_rate(self):
        if self.is_fixed_rate:
            self.is_variable_rate = False

    @api.onchange('is_variable_rate')
    def onchange_is_variable_rate(self):
        if self.is_variable_rate:
            self.is_fixed_rate = False
                
    def action_confirm(self):
        today = datetime.today().date()
        return {
            'name': 'Approve Request',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'approve.money.market.bal.req',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_amount': self.amount_to_invest,
                'default_date': today,
                'default_investment_id' : self.id,
                'default_fund_type' : self.fund_type_id and self.fund_type_id.id or False,
                'default_bank_account_id' : self.journal_id and self.journal_id.id or False,
                'show_for_supplier_payment':1,
                'default_agreement_type' : self.agreement_type_id and self.agreement_type_id.id or False,
                'default_base_collabaration_id' : self.base_collaboration_id and self.base_collaboration_id.id or False
            }
        }


    def action_reject(self):
        self.state = 'rejected'


    def action_requested(self):
        self.state = 'requested'
        if self.investment_fund_id and self.investment_fund_id.state != 'requested':
            self.investment_fund_id.action_requested()

    def action_approved(self):
        self.state = 'approved'
        if self.investment_fund_id and self.investment_fund_id.state != 'approved':
            self.investment_fund_id.action_approved()

    def action_confirmed(self):
        self.state = 'confirmed'
        if self.investment_fund_id and self.investment_fund_id.state != 'confirmed':
            self.investment_fund_id.action_confirmed()

 
    def action_canceled(self):
        self.state = 'canceled'
        if self.investment_fund_id and self.investment_fund_id.state != 'canceled':
            self.investment_fund_id.action_canceled()
        