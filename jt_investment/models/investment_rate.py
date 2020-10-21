from odoo import models, fields, api
from datetime import datetime
import requests
import urllib.request
import json

class InvestmentPeriodRate(models.Model):

    _name = 'investment.period.rate'
    _description = "Investment Rate"
    _rec_name = 'rate_date'
    
    rate_date = fields.Date('Date')
    product_type = fields.Selection([('TIIE','TIIE')],string="Product Type")
    daily_rate = fields.Float(string="Daily Rate",digits=0)
    days_28 = fields.Float(string="28 Days",digits=0)
    days_91 = fields.Float(string="91 Days",digits=0)
    days_182 = fields.Float(string="182 Days",digits=0)

    def create_update_product_rate(self,product_type,series_fields_map,data):
        idSerie = data.get('idSerie',False)
        date_data = data.get('datos',[])
        if idSerie and date_data:
            field_name = series_fields_map.get(idSerie,False)
            
            for line in date_data:
                rec_date = line.get('fecha',False)
                rec_date = datetime.strptime(rec_date, '%d/%m/%Y')
                rate = line.get('dato',0.0)
                exist_rec = self.env['investment.period.rate'].search([('product_type','=',product_type),('rate_date','=',rec_date)],limit=1)
                if exist_rec:
                    exist_rec.write({field_name : rate})
                else:
                    vals = {'product_type':product_type,
                            'rate_date':rec_date,
                            field_name : rate,
                            }
                    self.env['investment.period.rate'].create(vals)
                    
                  
    def get_investment_product_rate(self,token,url):
        series_fields_map = {'SF331451':'daily_rate','SF43783':'days_28','SF43878':'days_91','SF111916':'days_182'}
        series_str = 'SF331451,SF43783,SF43878,SF111916'
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('TIIE', series_fields_map, data)
        
         
    def create_investment_period_rate(self):
        token = 'fccfd1e45c7e54ef7a6896f25f7dcf01d51cfa033424abd345707b6a8d2b59c3'
        url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
        self.get_investment_product_rate(token,url)
        
        