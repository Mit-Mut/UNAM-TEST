from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class BasesCollabration(models.Model):

    _inherit = 'request.open.balance.finance'
    
    bonds_id = fields.Many2one('investment.bonds','Bonds',copy=False)
    cetes_id = fields.Many2one('investment.cetes','cetes',copy=False)
    udibonos_id = fields.Many2one('investment.udibonos','Udibonos',copy=False)
    will_pay_id = fields.Many2one('investment.will.pay','Will Pay',copy=False)
    purchase_sale_security_id = fields.Many2one('purchase.sale.security','Purchase Sale Security',copy=False)
    investment_id = fields.Many2one('investment.investment','Investment',copy=False)
    investment_fund_id = fields.Many2one('investment.funds','Investment Funds',copy=False)
    distribution_id = fields.Many2one('distribution.of.income','Distribution Income',copy=False)
    investment_link_id = fields.Many2one('investment.investment','Investment',copy=False)
    investment_operation_id = fields.Many2one('investment.operation','Operation',copy=False)
    line_opt_ids = fields.One2many('request.open.balance.finance.operation','finance_id',copy=False)
    from_opt_transfer = fields.Boolean(default=False,copy=False)
    amount_type = fields.Selection([('increment','Increment'),('withdrawal','Withdrawal')])
    investment_operation_ids = fields.Many2many('investment.operation','rel_operation_finance_dis','line_id','opt_id',copy=False)
    distribution_income_id = fields.Many2one('distribution.of.income','Distribution Income')
    
    def approve_finance(self):
        result = super(BasesCollabration,self).approve_finance()
        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.action_approved()
            
        if self.investment_id:
            self.investment_id.action_approved()

        if self.bonds_id:
            self.bonds_id.action_approved()

        if self.cetes_id:
            self.cetes_id.action_approved()

        if self.udibonos_id:
            self.udibonos_id.action_approved()

        if self.will_pay_id:
            self.will_pay_id.action_approved()
        
        if self.investment_fund_id:
            self.investment_fund_id.action_approved()
            
        if self.distribution_id:
            self.distribution_id.action_approved()

        if self.investment_operation_id:
            self.investment_operation_id.action_approved()
            
        for line in self.investment_operation_ids:
            line.action_approved()
        return result
     
    def confirmed_finance(self):
        result = super(BasesCollabration,self).confirmed_finance()

        if self.purchase_sale_security_id:
            po_so_security_id = self.purchase_sale_security_id
            po_so_security_id.action_confirmed()
            self.env['maturity.report'].create({
                'name': po_so_security_id.first_number,
                'po_sale_security_id': po_so_security_id.id,
                'partner_id': self.env.user.partner_id.id,
                'date': po_so_security_id.expiry_date
            })

        if self.investment_id:
            self.investment_id.action_confirmed()

        if self.bonds_id:
            bonds_id = self.bonds_id
            bonds_id.action_confirmed()
            self.env['maturity.report'].create({
                'name': bonds_id.first_number,
                'bonds_id': bonds_id.id,
                'partner_id': self.env.user.partner_id.id,
                'date': bonds_id.expiry_date
            })

        if self.cetes_id:
            cetes_id = self.cetes_id
            cetes_id.action_confirmed()
            self.env['maturity.report'].create({
                'name': cetes_id.first_number,
                'cetes_id': cetes_id.id,
                'partner_id': self.env.user.partner_id.id,
                'date': cetes_id.expiry_date
            })

        if self.udibonos_id:
            udibonos_id = self.udibonos_id
            self.udibonos_id.action_confirmed()
            self.env['maturity.report'].create({
                'name': udibonos_id.first_number,
                'udibonos_id': udibonos_id.id,
                'partner_id': self.env.user.partner_id.id,
                'date': udibonos_id.expiry_date
            })

        if self.will_pay_id:
            will_pay_id = self.will_pay_id
            will_pay_id.action_confirmed()
            self.env['maturity.report'].create({
                'name': will_pay_id.first_number,
                'will_pay_id': will_pay_id.id,
                'partner_id': self.env.user.partner_id.id,
                'date': will_pay_id.expiry_date
            })

        if self.investment_fund_id:
            self.investment_fund_id.action_confirmed()

        if self.distribution_id:
            self.distribution_id.action_confirmed()
        
        if self.investment_operation_id:
            self.investment_operation_id.action_done()

        for line in self.investment_operation_ids:
            line.action_done()
            
        if self.distribution_income_id:
            self.distribution_income_id.action_confirmed()
            
        return result 
    
    def reject_finance(self):
        
        result = super(BasesCollabration,self).reject_finance()

        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.action_reject()
            self.purchase_sale_security_id.reason_rejection = self.reason_rejection
            
        if self.investment_id:
            self.investment_id.action_reject()
            self.investment_id.reason_rejection = self.reason_rejection 
        if self.bonds_id:
            self.bonds_id.action_reject()
            self.bonds_id.reason_rejection = self.reason_rejection 

        if self.cetes_id:
            self.cetes_id.action_reject()
            self.cetes_id.reason_rejection = self.reason_rejection 

        if self.udibonos_id:
            self.udibonos_id.action_reject()
            self.udibonos_id.reason_rejection = self.reason_rejection 

        if self.will_pay_id:
            self.will_pay_id.action_reject()
            self.will_pay_id.reason_rejection = self.reason_rejection 

        if self.distribution_id:
            self.distribution_id.action_reject()
            self.distribution_id.reason_rejection = self.reason_rejection 
            
        if self.investment_operation_id:
            self.investment_operation_id.action_reject()
    
        return result

    def reset_draft_finance_payment(self):
        #result = super(BasesCollabration,self).approve_finance()
        self.state = 'sent'
        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.action_approved()
            
        if self.investment_id:
            self.investment_id.action_approved()

        if self.bonds_id:
            self.bonds_id.action_approved()

        if self.cetes_id:
            self.cetes_id.action_approved()

        if self.udibonos_id:
            self.udibonos_id.action_approved()

        if self.will_pay_id:
            self.will_pay_id.action_approved()
        
        if self.investment_fund_id:
            self.investment_fund_id.action_approved()
            
        if self.distribution_id:
            self.distribution_id.action_approved()
        
        if self.investment_operation_id:
            self.investment_operation_id.action_approved()

        for line in self.investment_operation_ids:
            line.action_approved()

    def canceled_finance(self):
        result = super(BasesCollabration,self).canceled_finance()

        if self.purchase_sale_security_id:
            self.purchase_sale_security_id.action_draft()
         
        if self.investment_id:
            self.investment_id.action_canceled()
 
        if self.bonds_id:
            self.bonds_id.action_canceled()
 
        if self.cetes_id:
            self.cetes_id.action_canceled()
 
        if self.udibonos_id:
            self.udibonos_id.action_canceled()
 
        if self.will_pay_id:
            self.will_pay_id.action_canceled()
 
        if self.investment_fund_id:
            self.investment_fund_id.action_canceled()
 
        if self.distribution_id:
            self.distribution_id.action_canceled()

        if self.investment_operation_id:
            self.investment_operation_id.action_canceled()

        for line in self.investment_operation_ids:
            line.action_canceled()
 
        return result
    
class ReqFinanceLines(models.Model):
    _name = 'request.open.balance.finance.operation'
    _description = "Inv Transfer Request Line"

    finance_id = fields.Many2one('request.open.balance.finance')
    investment_fund_id = fields.Many2one('investment.funds','Fund')
    base_collabaration_id = fields.Many2one('bases.collaboration','Name Of Agreements')
    agreement_number = fields.Char("Agreement Number")
    amount_to_transfer = fields.Float("Amount")
    opt_line_ids = fields.Many2many('investment.operation','rel_investment_operation_finance_line','opt_id','line_id')
    amount = fields.Float("Amount")
    
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        finance_req_obj = self.env['request.open.balance.finance']
        for payment in self:
            finance_reqs = finance_req_obj.search([('payment_ids', 'in', payment.id)])
            for fin_req in finance_reqs:
                fin_req.reset_draft_finance_payment()
        return res
    
    def cancel(self):
        res = super(AccountPayment, self).cancel()
        finance_req_obj = self.env['request.open.balance.finance']
        for payment in self:
            finance_reqs = finance_req_obj.search([('payment_ids', 'in', payment.id)])
            for fin_req in finance_reqs:
                fin_req.canceled_finance()
        return res
        