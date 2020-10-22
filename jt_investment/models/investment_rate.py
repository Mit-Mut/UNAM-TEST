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
    product_type = fields.Selection([('TIIE','TIIE'),('CETES','CETES'),('UDIBONOS','UDIBONOS'),('BONUS','BONUS'),('PAGARE','PAGARE')],string="Product Type")
    rate_daily = fields.Float(string="Daily Rate",digits=0)
    rate_days_28 = fields.Float(string="28 Days",digits=0)
    term_days_28 = fields.Integer(string="Term 28 Days")
    rate_days_91 = fields.Float(string="91 Days",digits=0)
    term_days_91 = fields.Integer(string="Term 91 Days")
    rate_days_182 = fields.Float(string="182 Days",digits=0)
    term_days_182 = fields.Integer(string="Term 182 Days")
    rate_days_364 = fields.Float(string="364 Days",digits=0)
    term_days_364 = fields.Integer(string="Term 364 Days")

    #=====UDIBONOS=====#    
    rate_year_3 = fields.Float(string="3 Year Rate",digits=0)
    term_year_3 = fields.Integer(string="3 Year Term")
    rate_year_5 = fields.Float(string="5 Year Rate",digits=0)
    term_year_5 = fields.Integer(string="5 Year Term")
    rate_year_10 = fields.Float(string="10 Year Rate",digits=0)
    term_year_10 = fields.Integer(string="10 Year Term")
    rate_year_20 = fields.Float(string="20 Year Rate",digits=0)
    term_year_20 = fields.Integer(string="20 Year Term")
    rate_year_30 = fields.Float(string="30 Year Rate",digits=0)
    term_year_30 = fields.Integer(string="30 Year Term")
    
    #========BONUS=====#
    rate_year_7 = fields.Float(string="7 Year Rate",digits=0)
    term_year_7 = fields.Integer(string="7 Year Term")
    
    def create_update_product_rate(self,product_type,series_fields_map,series_fields_type_map,data):
        idSerie = data.get('idSerie',False)
        date_data = data.get('datos',[])
        if idSerie and date_data:
            field_name = series_fields_map.get(idSerie,False)
            field_type = series_fields_type_map.get(idSerie,False)
            
            for line in date_data:
                rec_date = line.get('fecha',False)
                rec_date = datetime.strptime(rec_date, '%d/%m/%Y')
                rate = line.get('dato',0.0)
                if rate.isnumeric():
                    rate = float(rate)
                if rate == 'N/E':
                    rate = str(0)
                if isinstance(rate,str):
                    rate = rate.replace(',','')
                if field_type=='int':
                    rate = int(rate)
                elif field_type=='float':
                    rate = float(rate)
                else:
                    rate = 0
                        
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
        series_fields_map = {'SF331451':'rate_daily','SF43783':'rate_days_28','SF43878':'rate_days_91','SF111916':'rate_days_182'}
        series_fields_type_map = {'SF331451':'float','SF43783':'float','SF43878':'float','SF111916':'float'}
        series_str = 'SF331451,SF43783,SF43878,SF111916'
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('TIIE', series_fields_map,series_fields_type_map, data)

    def get_cetes_product_rate(self,token,url):
        #=======link=======#
        #=====  https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries#    ====#
        series_fields_map = {'SF43935':'term_days_28','SF43936':'rate_days_28',
                             'SF43938':'term_days_91','SF43939':'rate_days_91',
                             'SF43941':'term_days_182','SF43942':'rate_days_182',
                             'SF43944':'term_days_364','SF43945':'rate_days_364'
                             }

        series_fields_type_map = {'SF43935':'int','SF43936':'float',
                             'SF43938':'int','SF43939':'float',
                             'SF43941':'int','SF43942':'float',
                             'SF43944':'int','SF43945':'float'
                             }
        
        series_str = 'SF43935,SF43936,SF43938,SF43939,SF43941,SF43942,SF43944,SF43945'
        
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('CETES', series_fields_map,series_fields_type_map, data)
        

    def get_UDIBONOS_product_rate(self,token,url):
        #=======link=======#
        #=====  https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries#    ====#

        series_fields_map = {'SF61593':'term_year_3','SF61592':'rate_year_3',
                             'SF43926':'term_year_5','SF43927':'rate_year_5',
                             'SF43923':'term_year_10','SF43924':'rate_year_10',
                             'SF46957':'term_year_20','SF46958':'rate_year_20',
                             'SF46960':'term_year_30','SF46961':'rate_year_30',
                             }
        series_fields_type_map = {'SF61593':'int','SF61592':'float',
                             'SF43926':'int','SF43927':'float',
                             'SF43923':'int','SF43924':'float',
                             'SF46957':'int','SF46958':'float',
                             'SF46960':'int','SF46961':'float',
                             }
        
        series_str = 'SF61593,SF61592,SF43926,SF43927,SF43923,SF43924,SF46957,SF46958,SF46960,SF46961'
        
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('UDIBONOS', series_fields_map,series_fields_type_map, data)

    def get_BONUS_product_rate(self,token,url):
        #=======link=======#
        #=====  https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries#    ====#

        series_fields_map = {'SF43882':'term_year_3','SF43883':'rate_year_3',
                             'SF43885':'term_year_5','SF43886':'rate_year_5',
                             'SF44945':'term_year_7','SF44946':'rate_year_7',
                             'SF44070':'term_year_10','SF44071':'rate_year_10',
                             'SF45383':'term_year_20','SF45384':'rate_year_20',
                             'SF60689':'term_year_30','SF60696':'rate_year_30',
                             }
        series_fields_type_map = {'SF43882':'int','SF43883':'float',
                             'SF43885':'int','SF43886':'float',
                             'SF44945':'int','SF44946':'float',
                             'SF44070':'int','SF44071':'float',
                             'SF45383':'int','SF45384':'float',
                             'SF60689':'int','SF60696':'float',
                             }
        
        series_str = 'SF43882,SF43883,SF43885,SF43886,SF44945,SF44946,SF44070,SF44071,SF45383,SF45384,SF60689,SF60696'
        
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('BONUS', series_fields_map,series_fields_type_map, data)   

    def get_PAGARE_product_rate(self,token,url):
        series_fields_map = {'SF43783':'rate_days_28','SF43878':'rate_days_91','SF111916':'rate_days_182'}
        series_fields_type_map = {'SF43783':'float','SF43878':'float','SF111916':'float'}
        series_str = 'SF43783,SF43878,SF111916'
        url +=  series_str+"/datos/oportuno?token=%s"%token

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req).read()
        response = json.loads(response.decode('utf-8'))
        if response.get('bmx',False):
            series_dict = response.get('bmx',False)
            for data in series_dict.get('series',[]):
                self.create_update_product_rate('PAGARE', series_fields_map,series_fields_type_map, data)
                      
    def create_investment_period_rate(self):
        token = 'fccfd1e45c7e54ef7a6896f25f7dcf01d51cfa033424abd345707b6a8d2b59c3'
        url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'
        self.get_investment_product_rate(token,url)
        self.get_cetes_product_rate(token,url)
        self.get_UDIBONOS_product_rate(token,url)
        self.get_BONUS_product_rate(token,url)
        self.get_PAGARE_product_rate(token,url)
        