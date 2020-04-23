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
import base64
import io
import re
from datetime import datetime
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ExpenditureBudget(models.Model):

    _name = 'expenditure.budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expenditure Budget'
    _rec_name = 'budget_name'

    def _get_count(self):
        for record in self:
            record.record_number = len(record.line_ids)
            record.import_record_number = len(
                record.line_ids.filtered(lambda l: l.imported == True))

    budget_name = fields.Text(string='Budget name', required=True, tracking=True, states={
                              'validate': [('readonly', True)]})
    responsible_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True, states={
                                     'validate': [('readonly', True)]})

    # Date Periods
    from_date = fields.Date(string='From', states={
                            'validate': [('readonly', True)]})
    to_date = fields.Date(string='To', states={
                          'validate': [('readonly', True)]})

    def _compute_total_budget(self):
        for budget in self:
            budget.total_budget = sum(budget.line_ids.mapped('assigned'))

    total_budget = fields.Float(string='Total budget', tracking=True, compute="_compute_total_budget")
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    import_record_number = fields.Integer(
        string='Number of imported records', readonly=True, compute='_get_count')
    allow_upload = fields.Boolean(string='Allow Update XLS File?')

    # Budget Lines
    line_ids = fields.One2many(
        'expenditure.budget.line', 'expenditure_budget_id',
        string='Expenditure Budget Lines', states={'validate': [('readonly', True)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('previous', 'Previous'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('done', 'Done')], default='draft', required=True, string='State', tracking=True)

    def _compute_failed_rows(self):
        for record in self:
            record.failed_rows = 0
            try:
                data = eval(record.failed_row_ids)
                record.failed_rows = len(data)
            except:
                pass

    def _compute_success_rows(self):
        for record in self:
            record.success_rows = 0
            try:
                data = eval(record.success_row_ids)
                record.success_rows = len(data)
            except:
                pass

    budget_file = fields.Binary(string='Uploaded File')
    filename = fields.Char(string='File name')
    import_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], default='draft', copy=False)
    failed_row_file = fields.Binary(string='Failed Rows File')
    fialed_row_filename = fields.Char(
        string='File name', default="Failed_Rows.txt")
    failed_rows = fields.Integer(
        string='Failed Rows', compute="_compute_failed_rows")
    success_rows = fields.Integer(
        string='Success Rows', compute="_compute_success_rows")
    success_row_ids = fields.Text(
        string='Success Row Ids', default="[]", copy=False)
    failed_row_ids = fields.Text(
        string='Failed Row Ids', default="[]", copy=False)
    pointer_row = fields.Integer(
        string='Current Pointer Row', default=1, copy=False)
    total_rows = fields.Integer(string="Total Rows", copy=False)

    @api.constrains('from_date', 'to_date')
    def _check_dates(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError("Please select correct date")

    def import_lines(self):
        return {
            'name': "Import Budget Lines",
            'type': 'ir.actions.act_window',
            'res_model': 'import.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def validate_year(self, year_string):
        if len(str(year_string)) > 3:
            year_str = str(year_string)[:4]
            if str(year_str).isnumeric():
                year = self.env['year.configuration'].search(
                    [('name', '=', year_str)], limit=1)
                if not year:
                    if self._context.get('from_adequacies'):
                        return False
                    year = self.env['year.configuration'].create(
                        {'name': year_str})
                return year
        return False

    def validate_program(self, program_string):
        flag_created = False
        if len(str(program_string)) > 1:
            program_str = str(program_string).zfill(2)
            if program_str.isnumeric():
                program = self.env['program'].search(
                    [('key_unam', '=', program_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if program:
                        return program
                    return False

                if not program:
                    program = self.env['program'].create(
                        {'key_unam': program_str, 'desc_key_unam': 'NA'})
                    flag_created = True
                return [program, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_subprogram(self, subprogram_string, program):
        flag_created = False
        if len(str(subprogram_string)) > 1:
            subprogram_str = str(subprogram_string).zfill(2)
            if subprogram_str.isnumeric():
                subprogram = self.env['sub.program'].search(
                    [('unam_key_id', '=', program.id), ('sub_program', '=', subprogram_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if subprogram:
                        return subprogram
                    return False

                if not subprogram:
                    subprogram = self.env['sub.program'].create(
                        {'unam_key_id': program.id, 'sub_program': subprogram_str, 'desc': 'NA'})
                    flag_created = True
                return [subprogram, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_dependency(self, dependency_string):
        flag_created = False
        if len(str(dependency_string)) > 2:
            dependency_str = str(dependency_string).zfill(3)
            if dependency_str.isnumeric():
                dependency = self.env['dependency'].search(
                    [('dependency', '=', dependency_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if dependency:
                        return dependency
                    return False

                if not dependency:
                    dependency = self.env['dependency'].create(
                        {'dependency': dependency_str, 'description': 'NA'})
                    flag_created = True
                return [dependency, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_subdependency(self, subdependency_string, dependency):
        flag_created = False
        if len(str(subdependency_string)) > 1:
            subdependency_str = str(subdependency_string).zfill(2)
            if subdependency_str.isnumeric():
                subdependency = self.env['sub.dependency'].search(
                    [('dependency_id', '=', dependency.id), ('sub_dependency', '=', subdependency_string)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if subdependency:
                        return subdependency
                    return False

                if not subdependency:
                    subdependency = self.env['sub.dependency'].create(
                        {'dependency_id': dependency.id, 'sub_dependency': subdependency_string, 'description': 'NA'})
                    flag_created = True
                return [subdependency, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_item(self, item_string, typee):
        flag_created = False
        if len(str(item_string)) > 2:
            item_str = str(item_string).zfill(3)
            typee = str(typee).lower()
            if typee not in ['r', 'c', 'd']:
                typee = 'r'
            if item_str.isnumeric():
                item = self.env['expenditure.item'].search(
                    [('item', '=', item_str), ('exercise_type', '=', typee)], limit=1)
                if not item:
                    item = self.env['expenditure.item'].search(
                        [('item', '=', item_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if item:
                        return item
                    return False

                if not item:
                    item = self.env['expenditure.item'].create(
                        {'item': item_str, 'exercise_type': typee, 'description': 'NA'})
                    flag_created = True
                return [item, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_origin_resource(self, origin_resource_string):
        flag_created = False
        if len(str(origin_resource_string)) > 0:
            origin_resource_str = str(origin_resource_string).replace('.', '').zfill(2)

            desc = 'subsidy'
            if origin_resource_str == '00':
                desc = 'subsidy'
            if origin_resource_str == '01':
                desc = 'income'
            if origin_resource_str == '02':
                desc = 'service'
            if origin_resource_str == '03':
                desc = 'financial'
            if origin_resource_str == '04':
                desc = 'other'
            if origin_resource_str == '05':
                desc = 'pef'

            if origin_resource_str.isnumeric():
                origin_resource = self.env['resource.origin'].search(
                    [('key_origin', '=', origin_resource_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if origin_resource:
                        return origin_resource
                    return False

                if not origin_resource:
                    origin_resource = self.env['resource.origin'].create(
                        {'key_origin': origin_resource_str, 'desc': desc})
                    flag_created = True
                return [origin_resource, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_institutional_activity(self, institutional_activity_string):
        flag_created = False
        if len(str(institutional_activity_string)) > 2:
            institutional_activity_str = str(
                institutional_activity_string).zfill(5)
            if institutional_activity_str.isnumeric():
                institutional_activity = self.env['institutional.activity'].search(
                    [('number', '=', institutional_activity_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if institutional_activity:
                        return institutional_activity
                    return False

                if not institutional_activity:
                    institutional_activity = self.env['institutional.activity'].create(
                        {'number': institutional_activity_str, 'description': 'NA'})
                    flag_created = True
                return [institutional_activity, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_shcp(self, shcp_string, program):
        flag_created = False
        if len(str(shcp_string)) > 3:
            shcp_str = str(shcp_string)
            if len(shcp_str) == 4:
                if not (re.match("[A-Z]{1}\d{3}", str(shcp_str).upper())):

                    # To return for adequacies
                    if self._context.get('from_adequacies'):
                        return False

                    return [False, flag_created]
                else:
                    shcp = self.env['budget.program.conversion'].search(
                        [('shcp', '=', shcp_str)], limit=1)

                    # To return for adequacies
                    if self._context.get('from_adequacies'):
                        if shcp:
                            return shcp
                        return False

                    if not shcp:
                        shcp = self.env['budget.program.conversion'].create(
                            {'shcp': shcp_str, 'unam_key_id': program.id, 'desc': 'NA', 'description': 'NA'})
                        flag_created = True
                    return [shcp, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_conversion_item(self, conversion_item_string):
        flag_created = False
        if len(str(conversion_item_string)) > 4:
            conversion_item_str = str(conversion_item_string).zfill(4)
            if conversion_item_str.isnumeric():
                conversion_item = self.env['departure.conversion'].search(
                    [('federal_part', '=', conversion_item_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if conversion_item:
                        return conversion_item
                    return False

                if not conversion_item:
                    conversion_item = self.env['departure.conversion'].create(
                        {'federal_part': conversion_item_str, 'federal_part_desc': 'NA'})
                    flag_created = True
                return [conversion_item, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_expense_type(self, expense_type_string):
        flag_created = False
        if len(str(expense_type_string)) > 1:
            expense_type_str = str(expense_type_string).zfill(2)
            if expense_type_str.isnumeric():
                expense_type = self.env['expense.type'].search(
                    [('key_expenditure_type', '=', expense_type_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if expense_type:
                        return expense_type
                    return False

                if not expense_type:
                    expense_type = self.env['expense.type'].create(
                        {'key_expenditure_type': expense_type_str, 'description_expenditure_type': 'NA'})
                    flag_created = True
                return [expense_type, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_geo_location(self, location_string):
        flag_created = False
        if len(str(location_string)) > 1:
            location_str = str(location_string).zfill(2)
            if location_str.isnumeric():
                location = self.env['geographic.location'].search(
                    [('state_key', '=', location_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if location:
                        return location
                    return False

                if not location:
                    location = self.env['geographic.location'].create(
                        {'state_key': location_str})
                    flag_created = True
                return [location, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_wallet_key(self, wallet_key_string):
        flag_created = False
        if len(str(wallet_key_string)) > 3:
            wallet_key_str = str(wallet_key_string).zfill(4)
            if wallet_key_str.isnumeric():
                wallet_key = self.env['key.wallet'].search(
                    [('wallet_password', '=', wallet_key_str)], limit=1)

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    if wallet_key:
                        return wallet_key
                    return False

                if not wallet_key:
                    wallet_key = self.env['key.wallet'].create(
                        {'wallet_password': wallet_key_str, 'wallet_password_desc': 'NA'})
                    flag_created = True
                return [wallet_key, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_project_type(self, project_type_string, result_dict):
        flag_created = False
        if len(str(project_type_string)) > 1:
            project_type_str = str(project_type_string).zfill(2)
            if project_type_str.isnumeric():

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    project_type = self.env['project.type'].search(
                        [('project_id.project_type_identifier', '=', project_type_str), ('number', '=', result_dict.get('No. de Proyecto'))], limit=1)
                    if project_type:
                        return project_type
                    return False

                # Find Project
                project = self.env['project.project'].sudo().search(
                    [('project_type_identifier', '=', project_type_str)], limit=1)
                if not project:
                    project = self.env['project.project'].sudo().create({
                        'name': "NA",
                        'project_type_identifier': project_type_str,
                        'desc_stage': "NA",
                        'name_agreement': "NA",
                        'number': result_dict.get('No. de Proyecto'),
                        'stage_identifier': result_dict.get('Etapa'),
                        'agreement_type': result_dict.get('Tipo de Convenio'),
                        'number_agreement': result_dict.get('No. de Convenio'),
                    })
                if project:
                    # Find Project Type
                    project_type = self.env['project.type'].search(
                        [('project_id', '=', project.id)], limit=1)
                    if not project_type:
                        project_type = self.env['project.type'].create(
                            {'project_id': project.id})
                        flag_created = True
                    return [project_type, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_project_number(self, project_number_string, project_type):
        if len(str(project_number_string)) > 5:
            project_number_str = str(project_number_string).zfill(6)
            if project_number_str.isnumeric():
                project = project_type.project_id
                if project and project.number == project_number_str:
                    return project_number_str
                else:
                    project1 = self.env['project.project'].sudo().search(
                        [('number', '=', project_number_str)], limit=1)
                    if project1:
                        project_type = self.env['project.type'].search(
                            [('project_id', '=', project1.id)], limit=1)
                        if project_type:
                            return project1.number
                project.number = project_number_str
                return project_number_str
        if self._context.get('from_adequacies'):
            return False
        return False

    def validate_stage(self, stage_string, project):
        flag_created = False
        if len(str(stage_string)) > 1:
            stage_str = str(stage_string).zfill(2)
            if stage_str.isnumeric():

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    stage = self.env['stage'].search(
                        [('project_id.stage_identifier', '=', stage_str)], limit=1)
                    if stage:
                        return stage
                    return False

                if project and project.stage_identifier == stage_str:
                    # Check stage
                    stage = self.env['stage'].search(
                        [('project_id', '=', project.id)], limit=1)
                    if stage:
                        return [stage, flag_created]
                else:
                    project1 = self.env['project.project'].sudo().search(
                        [('stage_identifier', '=', stage_str)], limit=1)
                    if project1:
                        stage = self.env['stage'].search(
                            [('project_id', '=', project1.id)], limit=1)
                        if stage:
                            return [stage, flag_created]
                        else:
                            project = project1
                stage = self.env['stage'].search(
                    [('project_id', '=', project.id)], limit=1)
                if not stage:
                    stage = self.env['stage'].create(
                        {'project_id': project.id})
                    project.stage_identifier = stage_str
                    flag_created = True
                return [stage, flag_created]
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_agreement_type(self, agreement_type_string, project, agreement_number):
        flag_created = False
        if len(str(agreement_type_string)) > 1:
            agreement_type_str = str(agreement_type_string).zfill(2)
            if agreement_type_str.isnumeric():

                # To return for adequacies
                if self._context.get('from_adequacies'):
                    agreement_type = self.env['agreement.type'].search(
                        [('project_id.agreement_type', '=', agreement_type_str), ('number_agreement', '=', agreement_number)], limit=1)
                    if agreement_type:
                        return agreement_type
                    return False

                validated_agreement_number = self.validate_agreement_number(
                    agreement_number, project)
                if project and project.agreement_type == agreement_type_str and project.number_agreement == validated_agreement_number:
                    # Check agreement type
                    agreement_type = self.env['agreement.type'].search(
                        [('project_id', '=', project.id)], limit=1)
                    if agreement_type:
                        return [agreement_type, flag_created]
                else:
                    project1 = self.env['project.project'].sudo().search([('agreement_type', '=', agreement_type_str), (
                        'number_agreement', '=', validated_agreement_number), ('agreement_type', '=', agreement_type_str)], limit=1)
                    if project1:
                        agreement_type = self.env['agreement.type'].search(
                            [('project_id', '=', project1.id), ('number_agreement', '=', validated_agreement_number)], limit=1)
                        if agreement_type:
                            return [agreement_type, flag_created]
                        else:
                            project = project1
                agreement_type = self.env['agreement.type'].search([('project_id', '=', project.id), (
                    'number_agreement', '=', validated_agreement_number), ('agreement_type', '=', agreement_type_str)], limit=1)
                if not agreement_type:
                    agreement_type = self.env['agreement.type'].create(
                        {'project_id': project.id, 'number_agreement': validated_agreement_number, 'agreement_type': agreement_type_str})
                    flag_created = True
                return [agreement_type, flag_created]

            validated_number = self.validate_agreement_number(
                agreement_number, project)
            if validated_number:
                project.number_agreement = validated_number
                project.agreement_type = agreement_type
        if self._context.get('from_adequacies'):
            return False
        return [False, flag_created]

    def validate_agreement_number(self, agreement_number_string, project):
        if len(str(agreement_number_string)) > 5:
            agreement_number_str = str(agreement_number_string).zfill(6)
            if agreement_number_str.isnumeric():
                # project.number_agreement = agreement_number_str
                return agreement_number_str
        return False

    def validate_asigned_amount(self, asigned_amount_string):
        if len(str(asigned_amount_string)) > 0:
            if str(asigned_amount_string).isnumeric() or type(asigned_amount_string) is float or type(asigned_amount_string) is int:
                return float(asigned_amount_string)
        return "False"

    def validate_authorized_amount(self, authorized_amount_string):
        if len(str(authorized_amount_string)) > 0:
            if str(authorized_amount_string).isnumeric() or type(authorized_amount_string) is float or type(authorized_amount_string) is int:
                return float(authorized_amount_string)
        return "False"

    def validate_and_add_budget_line(self):
        if self.budget_file:
            # If user re-scan for failed rows
            re_scan_failed_rows_ids = eval(self.failed_row_ids)

            counter = 0
            cnt = 0
            pointer = self.pointer_row
            success_row_ids = []
            failed_row_ids = []

            data = base64.decodestring(self.budget_file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)

            headers = []
            for rowx, row in enumerate(map(sheet.row, range(1)), 1):
                for colx, cell in enumerate(row, 1):
                    headers.append(cell.value)

            result_vals = []
            lines_to_iterate = self.pointer_row + 10000
            total_sheet_rows = sheet.nrows - 1
            if total_sheet_rows < lines_to_iterate:
                lines_to_iterate = total_sheet_rows + 1
            failed_row = ""

            conditional_list = range(self.pointer_row, lines_to_iterate)
            if self._context.get('re_scan_failed'):
                conditional_list = []
                for row in re_scan_failed_rows_ids:
                    conditional_list.append(row - 1)

            for rowx, row in enumerate(map(sheet.row, conditional_list), 1):
                p_code = ''
                cnt += 1
                pointer = self.pointer_row + cnt
                if self._context.get('re_scan_failed'):
                    pointer = conditional_list[rowx - 1] + 1

                result_dict = {}
                counter = 0
                for colx, cell in enumerate(row, 1):
                    result_dict.update({headers[counter]: cell.value})
                    counter += 1
                result_vals.append(result_dict)

                final_dict = {}
                # Validate year format
                year = self.validate_year(result_dict.get('AÑO', ''))
                if year:
                    final_dict['year'] = year.id
                    p_code += year.name
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Year Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Program(PR)
                program_result = self.validate_program(
                    result_dict.get('Programa', ''))
                program = program_result[0]
                flag_created_program = program_result[1]
                if program:
                    final_dict['program_id'] = program.id
                    p_code += program.key_unam
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Program(PR) Format\n"
                    if program and flag_created_program:
                        program.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Program
                subprogram_result = self.validate_subprogram(
                    result_dict.get('SubPrograma', ''), program)
                subprogram = subprogram_result[0]
                flag_created_subprogram = subprogram_result[1]
                if subprogram:
                    final_dict['sub_program_id'] = subprogram.id
                    p_code += subprogram.sub_program
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SubProgram(SP) Format\n"
                    if subprogram and flag_created_subprogram:
                        subprogram.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validate Dependency
                dependency_result = self.validate_dependency(
                    result_dict.get('Dependencia', ''))
                dependency = dependency_result[0]
                flag_created_dependency = dependency_result[1]
                if dependency:
                    final_dict['dependency_id'] = dependency.id
                    p_code += dependency.dependency
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Dependency(DEP) Format\n"
                    if dependency and flag_created_dependency:
                        dependency.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Dependency
                subdependency_result = self.validate_subdependency(
                    result_dict.get('SubDependencia', ''), dependency)
                subdependency = subdependency_result[0]
                flag_created_subdependency = subdependency_result[1]
                if subdependency:
                    final_dict['sub_dependency_id'] = subdependency.id
                    p_code += subdependency.sub_dependency
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Sub Dependency(DEP) Format\n"
                    if subdependency and flag_created_subdependency:
                        subdependency.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validate Item
                item_result = self.validate_item(result_dict.get(
                    'Partida', ''), result_dict.get('Cve Ejercicio', ''))
                item = item_result[0]
                flag_created_item = item_result[1]
                if item:
                    final_dict['item_id'] = item.id
                    p_code += item.item
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Item(PAR) Format\n"
                    if item and flag_created_item:
                        item.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                if result_dict.get('Digito Verificador'):
                    p_code += str(result_dict.get('Digito Verificador')
                                  )[:1].replace('.', '').zfill(2)

                # Validate Origin Of Resource
                origin_resource_result = self.validate_origin_resource(
                    result_dict.get('Digito Centraliador', ''))
                origin_resource = origin_resource_result[0]
                flag_created_origin_resource = origin_resource_result[1]
                if origin_resource:
                    final_dict['resource_origin_id'] = origin_resource.id
                    p_code += origin_resource.key_origin
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Origin Of Resource(OR) Format\n"
                    if origin_resource and flag_created_origin_resource:
                        origin_resource.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Institutional Activity Number
                institutional_activity_result = self.validate_institutional_activity(
                    result_dict.get('Actividad Institucional', ''))
                institutional_activity = institutional_activity_result[0]
                flag_created_institutional_activity = institutional_activity_result[1]
                if institutional_activity:
                    final_dict['institutional_activity_id'] = institutional_activity.id
                    p_code += institutional_activity.number
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Institutional Activity Number(AI) Format\n"
                    if institutional_activity and flag_created_institutional_activity:
                        institutional_activity.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Conversion Program SHCP
                shcp_result = self.validate_shcp(
                    result_dict.get('Conversion Programa', ''), program)
                shcp = shcp_result[0]
                flag_created_shcp = shcp_result[1]
                if shcp:
                    final_dict['budget_program_conversion_id'] = shcp.id
                    p_code += shcp.shcp
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                    if shcp and flag_created_shcp:
                        shcp.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Federal Item
                conversion_item_result = self.validate_conversion_item(
                    result_dict.get('Conversion Partida', ''))
                conversion_item = conversion_item_result[0]
                flag_created_conversion_item = conversion_item_result[1]
                if conversion_item:
                    final_dict['conversion_item_id'] = conversion_item.id
                    p_code += conversion_item.federal_part
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid SHCP Games(CONPA) Format\n"
                    if conversion_item and flag_created_conversion_item:
                        conversion_item.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                expense_type_result = self.validate_expense_type(
                    result_dict.get('Tipo de gasto', ''))
                expense_type = expense_type_result[0]
                flag_created_expense_type = expense_type_result[1]
                if expense_type:
                    final_dict['expense_type_id'] = expense_type.id
                    p_code += expense_type.key_expenditure_type
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Expense Type(TG) Format\n"
                    if expense_type and flag_created_expense_type:
                        expense_type.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                geo_location_result = self.validate_geo_location(
                    result_dict.get('Ubicación geografica', ''))
                geo_location = geo_location_result[0]
                flag_created_geo_location = geo_location_result[1]
                if geo_location:
                    final_dict['location_id'] = geo_location.id
                    p_code += geo_location.state_key
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Geographic Location (UG) Format\n"
                    if geo_location and flag_created_geo_location:
                        geo_location.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Wallet Key
                wallet_key_result = self.validate_wallet_key(
                    result_dict.get('Clave Cartera', ''))
                wallet_key = wallet_key_result[0]
                flag_created_wallet_key = wallet_key_result[1]
                if wallet_key:
                    final_dict['portfolio_id'] = wallet_key.id
                    p_code += wallet_key.wallet_password
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Wallet Key(CC) Format\n"
                    if wallet_key and flag_created_wallet_key:
                        wallet_key.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Type
                project_type_result = self.validate_project_type(
                    result_dict.get('Tipo de Proyecto', ''), result_dict)
                project_type = project_type_result[0]
                flag_created_project_type = project_type_result[1]
                if project_type:
                    final_dict['project_type_id'] = project_type.id
                    p_code += project_type.project_type_identifier
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Project Type(TP) Format\n"
                    if project_type and flag_created_project_type:
                        project_type.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Number
                project_number = self.validate_project_number(
                    result_dict.get('No. de Proyecto', ''), project_type)
                if not project_number:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Project Number Format\n"
                    failed_row_ids.append(pointer)
                    continue
                else:
                    p_code += project_number

                # Validation Stage
                stage_result = self.validate_stage(
                    result_dict.get('Etapa', ''), project_type.project_id)
                stage = stage_result[0]
                flag_created_stage = stage_result[1]
                if stage:
                    final_dict['stage_id'] = stage.id
                    p_code += stage.stage_identifier
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Stage(E) Format\n"
                    if stage and flag_created_stage:
                        stage.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Number
                agreement_number = self.validate_agreement_number(
                    result_dict.get('No. de Convenio', ''), project_type.project_id)
                if not agreement_number:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Agreement Number Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Type
                agreement_type_result = self.validate_agreement_type(result_dict.get(
                    'Tipo de Convenio', ''), project_type.project_id, result_dict.get('No. de Convenio', ''))
                agreement_type = agreement_type_result[0]
                flag_created_agreement_type = agreement_type_result[1]
                if agreement_type:
                    final_dict['agreement_type_id'] = agreement_type.id
                    p_code += agreement_type.agreement_type
                    p_code += agreement_number
                else:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Agreement Type(TC) Format\n"
                    if agreement_type and flag_created_agreement_type:
                        agreement_type.sudo().unlink()
                    failed_row_ids.append(pointer)
                    continue

                # Validation Importe 1a Asignacion
                asigned_amount = self.validate_asigned_amount(
                    result_dict.get('Importe 1a Asignacion', ''))
                if asigned_amount == "False":
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Asigned Amount Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Authorized Amount
                authorized_amount = self.validate_authorized_amount(
                    result_dict.get('Importe Autorizado', ''))
                if authorized_amount == "False":
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Invalid Authorized Amount Format\n"
                    failed_row_ids.append(pointer)
                    continue

                try:
                    search_program_code = self.env['program.code'].sudo().search(
                        [('program_code_copy', '=', p_code)], limit=1)
                    if search_program_code:
                        1 / 0
                    program_code = self.env['program.code'].sudo().create(
                        final_dict)
                    success_row_ids.append(pointer)

                    if self._context.get('re_scan_failed'):
                        failed_row_ids_eval_refill = eval(self.failed_row_ids)
                        failed_row_ids_eval_refill.remove(pointer)
                        self.write({'failed_row_ids': str(
                            list(set(failed_row_ids_eval_refill)))})

                    line_vals = {
                        'program_code_id': program_code.id,
                        'authorized': authorized_amount,
                        'assigned': asigned_amount,
                        'imported': True,
                    }
                    self.write({'line_ids': [(0, 0, line_vals)]})
                except:
                    failed_row += str(list(result_dict.values())) + \
                        "------>> Row Data Are Not Corrected or Duplicated Program Code Found!"
                    failed_row_ids.append(pointer)

            failed_row_ids_eval = eval(self.failed_row_ids)
            success_row_ids_eval = eval(self.success_row_ids)
            if len(success_row_ids) > 0:
                success_row_ids_eval.extend(success_row_ids)
            if len(failed_row_ids) > 0:
                failed_row_ids_eval.extend(failed_row_ids)

            vals = {
                'failed_row_ids': str(list(set(failed_row_ids_eval))),
                'success_row_ids': str(list(set(success_row_ids_eval))),
                'pointer_row': pointer,
            }

            failed_data = False
            if failed_row != "":
                content = ""
                if self.failed_row_file:
                    file_data = base64.b64decode(self.failed_row_file)
                    content += io.StringIO(file_data.decode("utf-8")).read()
                content += "\n"
                content += "...................Failed Rows " + \
                    str(datetime.today()) + "...............\n"
                content += str(failed_row)
                failed_data = base64.b64encode(content.encode('utf-8'))
                vals['failed_row_file'] = failed_data
            if pointer == sheet.nrows:
                vals['import_status'] = 'done'
            self.write(vals)

            if pointer == sheet.nrows and len(failed_row_ids_eval) > 0:
                self.write({'allow_upload': True})

            if self.failed_row_ids == 0 or len(failed_row_ids_eval) == 0:
                self.write({'allow_upload': False})

            if len(failed_row_ids) == 0:
                return{
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'All rows are imported successfully!',
                        'type': 'rainbow_man',
                    }
                }

    def verify_data(self):
        total = sum(self.line_ids.mapped('assigned'))
        if total <= 0:
            raise ValidationError("Budget amount should be greater than 0")
        if len(self.line_ids.ids) == 0:
            raise ValidationError("Please add budget lines")
        if total != self.total_budget:
            raise ValidationError(
                "Budget amount not match with total lines assigned amount!")
        if self.total_rows > 0 and self.success_rows != self.total_rows:
            raise ValidationError(
                "Please validate all lines or correct failed rows!")
        return True

    def previous_budget(self):
        self.verify_data()
        self.write({'state': 'previous'})

    def confirm(self):
        self.verify_data()
        self.write({'state': 'confirm'})

    def approve(self):
        self.verify_data()
        self.line_ids.mapped('program_code_id').write({'state': 'validated', 'budget_id': self.id})
        self.write({'state': 'validate'})

    def reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reject',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def unlink(self):
        if not self._context.get('from_wizard'):
            for budget in self:
                if budget.state not in ('draft', 'previous'):
                    raise ValidationError(
                        'You can not delete processed budget!')
        return super(ExpenditureBudget, self).unlink()


class ExpenditureBudgetLine(models.Model):

    _name = 'expenditure.budget.line'
    _description = 'Expenditure Budget Line'
    _rec_name = 'program_code_id'

    expenditure_budget_id = fields.Many2one(
        'expenditure.budget', string='Expenditure Budget', ondelete="cascade")
    program_code_id = fields.Many2one('program.code', string='Program code')
    start_date = fields.Date(
        string='Start date', related="expenditure_budget_id.from_date")
    end_date = fields.Date(
        string='End date', related="expenditure_budget_id.to_date")
    authorized = fields.Float(
        string='Authorized')
    assigned = fields.Float(
        string='Assigned')
    available = fields.Float(
        string='Available')

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    imported = fields.Boolean()
    dependency_id = fields.Many2one(
        'dependency', string='Dependency', related="program_code_id.dependency_id")
    sub_dependency_id = fields.Many2one(
        'sub.dependency', string='Sub-Dependency', related="program_code_id.sub_dependency_id")
    program_id = fields.Many2one(
        'program', string='Program', related="program_code_id.program_id")
    item_id = fields.Many2one(
        'expenditure.item', string='Item', related="program_code_id.item_id")

    _sql_constraints = [
        ('uniq_program_code_id', 'unique(program_code_id)',
         'The Program code must be unique!'),
    ]
