from odoo import models, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools.misc import xlsxwriter
import io
import base64
from odoo.tools import config, date_utils, get_lang
import lxml.html

class ValueaddedTaxReport(models.AbstractModel):

    _name = "jt_tax_transaction.valueadded.report"
    _inherit = "account.generic.tax.report"
    _description = "Report ​ for the determination of Value Added Tax by"
    
    is_sale = False
    is_purchase = False
    def convert_string_to_float(self,values):
        amount = 0
        amount = values.replace('$','')
        amount = amount.replace(',','')
        amount = float(amount)
        return amount

    def _format(self, value,figure_type):
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']
        
        if figure_type == 'float':
            currency_id = self.env.company.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number text-muted'
            value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            value['class'] = 'number'
            return value
        if figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            value['class'] = 'number'
            return value
        value['name'] = round(value['name'], 1)
        return value
    
    def _get_lines(self, options, line_id=None):
        lines = super(ValueaddedTaxReport,self)._get_lines(options,line_id)
        col_list = []
        columns= []
        new_lines = []
        
        for line in lines:
            print ("line=",line)
            if not col_list:
                for l in line.get('columns'):
                    col_list.append(0)
                
            if line.get('id','')=='sale':
                is_sale = True
                is_purchase = False
                new_lines.append(line)
                
            elif line.get('id','')=='purchase':
                is_sale = False
                is_purchase = True
                new_lines.append(line)
            else:
                tax = self.env['account.tax'].browse(line.get('id',0))
                if tax and tax.amount > 0:
                    new_lines.append(line)
                else:
                    continue
                
            count = 0
            for data in line.get('columns'):
                if data.get('name',False):
                    
                    if is_sale:
                        float_amount = self.convert_string_to_float(data.get('name',0))
                        col_list[count] += float_amount
                    if is_purchase:
                        float_amount = self.convert_string_to_float(data.get('name',0))
                        col_list[count] -= float_amount
                        
                    count += 1
        if col_list:
            for col in col_list:
                columns.append(self._format({'name': col},figure_type='float'))
            print ("columns==",columns)   
            new_lines.append({'id': 'tax_charge_favor', 'name': 'Tax in Charge / Favor', 
                           'unfoldable': False, 
                           'columns': columns,
                           'level': 1, 
                           }           
                )
        return new_lines   