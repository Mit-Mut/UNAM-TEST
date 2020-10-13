from odoo import models, fields, api

class CETES(models.Model):

    _name = 'investment.cetes'
    _description = "Investment CETES"
    _rec_name = 'folio' 
 
    folio = fields.Integer("Folio")
    date_time = fields.Datetime("Date Time")
    journal_id= fields.Many2one("account.journal",'Bank Account')
    bank_id = fields.Many2one(related="journal_id.bank_id")
    amount_invest = fields.Float("Amount to invest")
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_rate_id = fields.Many2one("res.currency.rate","Exchange Rate")
    total_currency_rate = fields.Float(string="Total",compute="get_total_currency_amount",store=True)
    contract_id = fields.Many2one("investment.contract","Contract")
    document_type = fields.Selection([('cetes','CETES'),('udibonos','Udibonos'),('bonds','Bonds'),('promissory_note','Promissory note')],string="Document")
    instrument_it = fields.Selection([('bank','Bank'),('paper_government','Paper Government Paper')],string="Instrument It")
    account_executive = fields.Char("Account Executive")
    UNAM_operator = fields.Char("UNAM Operator")
    is_federal_subsidy_resources = fields.Boolean("Federal Subsidy Resourcesss")
    observations = fields.Text("Observations")
    
    kind_of_product = fields.Selection([('investment','Investment')],string="Kind Of Product",default="investment")
    key = fields.Char("Identification Key")
    start_date = fields.Date('Start Date')
    due_date = fields.Date('Due Date')
    nominal_value = fields.Float("Nominal Value")
    yield_rate = fields.Float("Yield Rate")
    term= fields.Selection([('28','28 Days'),
                                  ('91','91 Days'),
                                  ('182','182 Days'),
                                  ('364','364 Days')
                                  ],string="Term")
    
    
    cetes_price = fields.Float(string="CETES Price",compute="get_cetes_price",store=True)
    cetes_quantity = fields.Float(string="CETES Quantity",compute="get_cetes_quantity",store=True)
    estimated_interest = fields.Float(string="Estimated Interest",compute="get_estimated_interest",store=True)
    estimated_profit = fields.Float(string="Estimated Profit",compute="get_estimated_profit",store=True)
    real_interest = fields.Float("Real Interest")
    real_profit = fields.Float(string="Real Profit",compute="get_real_profit",store=True)
    state = fields.Selection([('draft','Draft'),('in_process','In Process')],string="Status",default="draft")


    @api.depends('amount_invest','currency_rate_id','currency_rate_id.rate')
    def get_total_currency_amount(self):
        for rec in self:
            if rec.amount_invest and rec.currency_rate_id:
                rec.total_currency_rate = rec.amount_invest * rec.currency_rate_id.rate
            else:
                rec.total_currency_rate = 0
            
    @api.depends('term','yield_rate','nominal_value')
    def get_cetes_price(self):
        for rec in self:
            term_value = 0
            if rec.term:
                term_value = int(rec.term)
            rec.cetes_price = (1/(rec.yield_rate*term_value/36000+1))*rec.nominal_value

    @api.depends('nominal_value')
    def get_cetes_quantity(self):
        for rec in self:
            rec.cetes_quantity = rec.nominal_value/10

    @api.depends('nominal_value','yield_rate','term')
    def get_estimated_interest(self):
        for rec in self:
            term_value = 0
            if rec.term:
                term_value = int(rec.term)
            rec.estimated_interest = rec.yield_rate/100*term_value*rec.nominal_value/360

    @api.depends('nominal_value','yield_rate','term','estimated_interest')
    def get_estimated_profit(self):
        for rec in self:
            rec.estimated_profit = rec.nominal_value + rec.estimated_interest

    @api.depends('nominal_value','real_interest')
    def get_real_profit(self):
        for rec in self:
            rec.real_profit = rec.nominal_value + rec.real_interest

    @api.depends('estimated_profit','real_profit')
    def get_profit_variation(self):
        for rec in self:
            rec.profit_variation =  rec.real_profit - rec.estimated_profit
            
    profit_variation = fields.Float(string="Estimated vs Real Profit Variation",compute="get_profit_variation",store=True)
    

    @api.model
    def create(self,vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code('folio.cetes')
        return super(CETES,self).create(vals)
        
    def action_confirm(self):
        self.state='in_process'

    def action_reset_to_draft(self):
        self.state='draft'

    def action_calculation(self):
        return 
    
    def action_reinvestment(self):
        return 
