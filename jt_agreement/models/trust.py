# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Trust(models.Model):

    _name = 'agreement.trust'
    _description = "Agreement Trust"

    name = fields.Char("Trust Name")
    bank_id = fields.Many2one('res.bank','Banking institution')
    dependency_id = fields.Many2one('dependency', "Dependency")
    dependency_desc =  fields.Text(related="dependency_id.description")
    opening_balance = fields.Float("Opening balance")
    origin_resource_id = fields.Many2one('sub.origin.resource', "Origin of the resource")
    executive_name = fields.Char("Executive name")
    phone = fields.Char("Phone")
    email = fields.Char("Email")
    home = fields.Char("Home")
    state = fields.Selection([('draft', 'Draft'),
                               ('valid', 'Valid'),
                               ('in_force', 'In Force'),
                              ('to_be_cancelled', 'To Be Cancelled'),
                              ('cancelled', 'Cancelled')], "Status", default='draft')
  
    
    patrimonial_account_id = fields.Many2one('account.account', "Patrimonial Account")
    investment_account_id = fields.Many2one('account.account', "Investment Account")
    interest_account_id = fields.Many2one('account.account', "Interest Accounting Account")
    honorary_account_id = fields.Many2one('account.account', "Honorary Accounting Account")
    availability_account_id = fields.Many2one('account.account', "Availability Accounting Account")
    liability_account_id = fields.Many2one('account.account', "Liability Account")

    trust_agreement_file = fields.Binary("Trust Agreement")
    trust_agreement_file_name = fields.Char("Trust Agreement File Name")
    trust_office_file = fields.Binary("Trust Office")
    trust_office_file_name = fields.Char("Trust Office File Name")
    
    no_beneficiary_allowed = fields.Integer("Number of allowed beneficiaries")
    beneficiary_ids = fields.One2many('collaboration.beneficiary', 'trust_id')
    provider_ids = fields.One2many('collaboration.providers', 'trust_id')

    committe_ids = fields.One2many('committee', 'trust_id', string="Committees")

    request_open_balance_ids = fields.One2many('request.open.balance','trust_id')
    total_operations = fields.Integer("Operations", compute="compute_operations")
     
    def compute_operations(self):
        for rec in self:
            operations = len(rec.request_open_balance_ids)
            rec.total_operations =operations
            
    @api.constrains('phone')
    def _check_phone(self):
        if self.phone and not self.phone.isnumeric():
            raise ValidationError(_('Phone No must be Numeric.'))
    
    
    @api.model
    def create(self, vals):
        res = super(Trust, self).create(vals)
        if res and res.beneficiary_ids:
            if not res.no_beneficiary_allowed or (res.no_beneficiary_allowed and \
                                                  res.no_beneficiary_allowed < len(res.beneficiary_ids)):
                raise ValidationError(_("You can add only %s Beneficiaries which is mentined in "
                                        "'Number of allowed beneficiaries'" % res.no_beneficiary_allowed))
        return res

    def write(self, vals):
        res = super(Trust, self).write(vals)
        for rec in self:
            if rec and rec.beneficiary_ids:
                if not rec.no_beneficiary_allowed or (rec.no_beneficiary_allowed and \
                                                      rec.no_beneficiary_allowed < len(rec.beneficiary_ids)):
                    raise ValidationError(_("You can add only %s Beneficiaries which is mentined in "
                                            "'Number of allowed beneficiaries'" % rec.no_beneficiary_allowed))
        return res
    
    def confirm(self):
        self.state = 'valid'

    def action_operations(self):
        if self.request_open_balance_ids:
            return {
                'name': 'Operations',
                'view_type': 'form',
                # 'view_id': self.env.ref('jt_agreement.view_req_open_balance_tree').id,
                'view_mode': 'tree,form',
                'view_ids': [(5, 0, 0),
                             (0, 0, {self.env.ref("jt_agreement.view_req_open_balance_trust_tree").id}),
                             (0, 0, {self.env.ref("jt_agreement.view_req_open_balance_trust_form").id})],
                'res_model': 'request.open.balance',
                'domain': [('trust_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_trust_id': self.id,
                            'default_apply_to_basis_collaboration': True,
                            'default_origin_resource_id': self.origin_resource_id and self.origin_resource_id.id or False,
                            'default_opening_balance': self.opening_balance,
                            'default_trust_agreement_file': self.trust_agreement_file,
                            'default_trust_agreement_file_name': self.trust_agreement_file_name,
                            'default_trust_office_file': self.trust_office_file,
                            'default_trust_office_file_name': self.trust_office_file_name,
                            'default_name': self.name,
                            'default_patrimonial_account_id': self.patrimonial_account_id.id if self.patrimonial_account_id
                                    else False,
                            'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
                                    else False,
                            'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
                            else False,
                            'default_honorary_account_id': self.honorary_account_id.id if self.honorary_account_id
                            else False,
                            'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
                            else False,
                            'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
                            else False
                            
                            
                            }
            }
        else:
            return {
                'name': 'Operations',
                # 'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('jt_agreement.view_req_open_balance_trust_form').id,
                'view_ids': [self.env.ref("jt_agreement.view_req_open_balance_trust_form").id],
                'res_model': 'request.open.balance',
                'domain': [('trust_id', '=', self.id)],
                'type': 'ir.actions.act_window',
                'context': {'default_trust_id': self.id,
                            'default_apply_to_basis_collaboration': True,
                            'default_origin_resource_id': self.origin_resource_id and self.origin_resource_id.id or False,
                            'default_opening_balance': self.opening_balance,
                            'default_trust_agreement_file': self.trust_agreement_file,
                            'default_trust_agreement_file_name': self.trust_agreement_file_name,
                            'default_trust_office_file': self.trust_office_file,
                            'default_trust_office_file_name': self.trust_office_file_name,
                            'default_name': self.name,
                            'default_patrimonial_account_id': self.patrimonial_account_id.id if self.patrimonial_account_id
                                    else False,
                            'default_investment_account_id': self.investment_account_id.id if self.investment_account_id
                                    else False,
                            'default_interest_account_id': self.interest_account_id.id if self.interest_account_id
                            else False,
                            'default_honorary_account_id': self.honorary_account_id.id if self.honorary_account_id
                            else False,
                            'default_availability_account_id': self.availability_account_id.id if self.availability_account_id
                            else False,
                            'default_liability_account_id': self.liability_account_id.id if self.liability_account_id
                            else False
                            }
            }
    
    
class Beneficiary(models.Model):
    _inherit = 'collaboration.beneficiary'
    
    trust_id = fields.Many2one('agreement.trust','Trust')
    
class Providers(models.Model):
    _inherit = 'collaboration.providers'

    trust_id = fields.Many2one('agreement.trust','Trust')

class Committe(models.Model):

    _inherit = 'committee'
    
    trust_id = fields.Many2one('agreement.trust','Trust')
    