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
import base64
import xlrd
from datetime import datetime
from odoo.modules.module import get_resource_path
from xlrd import open_workbook
from odoo.exceptions import UserError, ValidationError


class ImportAdequaciesLine(models.TransientModel):

    _name = 'import.control.amount.lines'
    _description = 'Import Control Amount Lines'

    folio = fields.Char(string='Folio')
    record_number = fields.Integer(string='Number of records')
    file = fields.Binary(string='File')
    filename = fields.Char(string='File name')
    dwnld_file = fields.Binary(string='Download File')
    dwnld_filename = fields.Char(string='Download File name')
    error_status = fields.Boolean(string='Error Status')
    error_string = fields.Text(string='Error String')

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')

    def download_file(self):
        file_path = get_resource_path(
            'jt_finance', 'static/file/import_line', 'CLC.xlsx')
        file = False
        with open(file_path, 'rb') as file_date:
            file = base64.b64encode(file_date.read())
        self.dwnld_filename = 'import_control_amount_line.xls'
        self.dwnld_file = file
        return {
            'name': 'Download Sample File',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'import.control.amount.lines',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    def import_line(self):
        self.ensure_one()
        control_amount = self.env['calendar.assigned.amounts'].browse(
            self._context.get('active_id'))
        if control_amount.folio != self.folio:
            raise UserError(_('Folio does not match.'))
        elif self.file:
            try:
                data = base64.decodestring(self.file)
                book = open_workbook(file_contents=data or b'')
                sheet = book.sheet_by_index(0)

                total_rows = self.record_number + 1
                if sheet.nrows != total_rows:
                    raise UserError(
                        _('The number of imported lines is not equal to the number of records'))

                headers = []
                for rowx, row in enumerate(map(sheet.row, range(1)), 1):
                    for colx, cell in enumerate(row, 1):
                        headers.append(cell.value)

                result_vals = []
                code_amount_dict = {}
                for rowx, row in enumerate(map(sheet.row, range(1, sheet.nrows)), 1):
                    counter = 0
                    result_dict = {}
                    column = ''
                    for colx, cell in enumerate(row, 1):
                        value = cell.value
                        if headers[counter] == 'PROGRAMA_PRESUPUESTARIO':
                            column = value
                        if headers[counter] == 'ORIGINAL' and column != '':
                            if column not in code_amount_dict:
                                code_amount_dict[column] = float(value)
                            else:
                                vals = code_amount_dict[column]
                                code_amount_dict[column] = vals + float(value)
                        if headers[counter] == 'Start Date':
                            try:
                                start_date = False
                                if type(value) is str:
                                    start_date = datetime.strptime(str(value), '%m/%d/%Y').date()
                                elif type(value) is int or type(value) is float:
                                    start_date = datetime(*xlrd.xldate_as_tuple(value, 0)).date()
                                if start_date:
                                    value = start_date
                                else:
                                    value = False
                            except:
                                pass

                        if headers[counter] == 'End Date':
                            try:
                                end_date = False
                                if type(value) is str:
                                    end_date = datetime.strptime(str(value), '%m/%d/%Y').date()
                                elif type(value) is int or type(value) is float:
                                    end_date = datetime(*xlrd.xldate_as_tuple(value, 0)).date()
                                if end_date:
                                    value = end_date
                                else:
                                    value = False
                            except:
                                pass

                        result_dict.update(
                            {headers[counter]: value})
                        counter += 1
                    result_vals.append((0, 0, result_dict))
                data = result_vals
                if control_amount and control_amount.budget_id:
                    data_dict = {}
                    error_string = ''
                    for budget_line in control_amount.budget_id.success_line_ids:
                        if budget_line.program_code_id and budget_line.program_code_id.budget_program_conversion_id:
                            code = budget_line.program_code_id.budget_program_conversion_id.shcp.name
                            if code not in data_dict:
                                data_dict[code] = float(budget_line.assigned)
                            else:
                                vals = data_dict[code]
                                data_dict[code] = vals + float(budget_line.assigned)
                    for key, value in code_amount_dict.items():
                        if key in data_dict and value != data_dict.get(key):
                            diff = data_dict.get(key) - value
                            error_string += str(key) + ': ' + str(diff) + "\n"
                    vals_amount_control = {
                        'import_date': datetime.today().date(),
                        'diff': error_string,
                        'total_rows': self.record_number,
                    }
                    dict_flag = not bool(code_amount_dict)
                    if dict_flag:
                        raise ValidationError("Please select correct file!")
                    if error_string == '' and not dict_flag:
                        vals_amount_control['file'] = self.file
                        vals_amount_control['filename'] = self.filename
                        self.error_status = False
                    else:
                        self.error_status = True
                        self.error_string = error_string
                    control_amount.write(vals_amount_control)
                    if error_string != '':
                        return {
                            'name': 'Something Went Wrong!',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'view_id': False,
                            'res_model': 'import.control.amount.lines',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'res_id': self.id,
                        }
            except UserError as e:
                raise UserError(e)
