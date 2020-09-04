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
import math
from datetime import datetime, timedelta
from xlrd import open_workbook
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Adequacies(models.Model):
    _name = 'adequacies'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Adequacies'
    _rec_name = 'folio'

    # Function calculate total imported and manufal rows
    def _get_count(self):
        for record in self:
            record.record_number = len(record.adequacies_lines_ids)
            record.imported_record_number = len(
                record.adequacies_lines_ids.filtered(lambda l: l.imported == True))

    # Function to calculate total increase amount and total decrease amount
    def _compute_total_amounts(self):
        for adequacies in self:
            total_decreased = 0
            total_increased = 0
            for line in adequacies.adequacies_lines_ids:
                if line.line_type == 'decrease':
                    total_decreased += line.amount
                if line.line_type == 'increase':
                    total_increased += line.amount
            adequacies.total_decreased = float(total_decreased)
            adequacies.total_decreased = float(total_increased)

    # Total increased and decreased fields
    total_decreased = fields.Float(
        string='Total Decreased Amount', compute="_compute_total_amounts")
    total_increased = fields.Float(
        string='Total Decreased Amount', compute="_compute_total_amounts")

    folio = fields.Char(string='Folio', states={
        'accepted': [('readonly', True)], 'rejected': [('readonly', True)]}, tracking=True)
    budget_id = fields.Many2one('expenditure.budget', string='Budget', states={
        'accepted': [('readonly', True)], 'rejected': [('readonly', True)]}, tracking=True)
    reason = fields.Text(string='Reason for rejection')
    cron_running = fields.Boolean(string='Running CRON?')

    # Total imported or manual rows
    record_number = fields.Integer(
        string='Number of records', compute='_get_count')
    imported_record_number = fields.Integer(
        string='Number of records imported.', compute='_get_count')

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='draft', required=True, string='State')

    observation = fields.Text(string='Observation', tracking=True)
    adaptation_type = fields.Selection(
        [('compensated', 'Compensated Adjustments'), ('liquid', 'Liquid Adjustments')], default='compensated', states={
            'accepted': [('readonly', True)], 'rejected': [('readonly', True)]}, tracking=True)
    adequacies_lines_ids = fields.One2many(
        'adequacies.lines', 'adequacies_id', string='Adequacies Lines',
        states={'accepted': [('readonly', True)], 'rejected': [('readonly', True)]})
    move_line_ids = fields.One2many("account.move.line", 'adequacy_id', string="Journal Items")
    journal_id = fields.Many2one('account.journal', string="Daily")
    date_of_budget_affected = fields.Date("Date Of Budget Affected",default=datetime.today())
    date_of_liquid_adu = fields.Date("Date of Liquid Adjustments",default=datetime.today())

    _sql_constraints = [
        ('folio_uniq', 'unique(folio)', 'The folio must be unique.')]

    @api.constrains('folio')
    def _check_folio(self):
        if not str(self.folio).isnumeric():
            raise ValidationError('Folio Must be numeric value!')

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

    # Import process related fields
    allow_upload = fields.Boolean(string='Allow Update XLS File?')
    budget_file = fields.Binary(string='Uploaded File', states={'accepted': [
        ('readonly', True)], 'rejected': [('readonly', True)]})
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

    @api.model
    def create(self,vals):
        name = self.env['ir.sequence'].next_by_code('adequacies.folio')
        vals.update({'folio':name})
        res = super(Adequacies,self).create(vals)
        return res

    def import_lines(self):
        return {
            'name': _('Import Adequacies'),
            'type': 'ir.actions.act_window',
            'res_model': 'import.adequacies.line',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def validate_and_add_budget_line(self, record_id=False, cron_id=False):
        if record_id:
            self = self.env['adequacies'].browse(int(record_id))

        if self.budget_file:
            # Objects
            year_obj = self.env['year.configuration']
            program_obj = self.env['program']
            subprogram_obj = self.env['sub.program']
            dependancy_obj = self.env['dependency']
            subdependancy_obj = self.env['sub.dependency']
            item_obj = self.env['expenditure.item']
            origin_obj = self.env['resource.origin']
            activity_obj = self.env['institutional.activity']
            shcp_obj = self.env['budget.program.conversion']
            dpc_obj = self.env['departure.conversion']
            expense_type_obj = self.env['expense.type']
            location_obj = self.env['geographic.location']
            wallet_obj = self.env['key.wallet']
            project_type_obj = self.env['project.type']
            stage_obj = self.env['stage']
            agreement_type_obj = self.env['agreement.type']

            cron = False
            if cron_id:
                cron = self.env['ir.cron'].sudo().browse(int(cron_id))

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

            lines_to_iterate = self.pointer_row + 5000
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

                list_result = []
                counter = 0
                for colx, cell in enumerate(row, 1):
                    list_result.append(cell.value)
                    counter += 1

                # Validate year format
                year = year_obj.validate_year(list_result[0])
                if not year:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Year Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Program(PR)
                program = program_obj.validate_program(list_result[1])
                if not program:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Program(PR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Dependency
                dependency = dependancy_obj.validate_dependency(list_result[3])
                if not dependency:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Dependency
                subdependency = subdependancy_obj.validate_subdependency(list_result[4], dependency)
                if not subdependency:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Sub Dependency(DEP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Sub-Program
                subprogram = subprogram_obj.validate_subprogram(list_result[2], program, dependency, subdependency)
                if not subprogram:
                    failed_row += str(list_result) + \
                                  "------>> Invalid SubProgram(SP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validate Item
                item = item_obj.validate_item(list_result[5], list_result[19])
                if not item:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Expense Item(PAR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                if not list_result[6]:
                    failed_row += str(list_result) + \
                                  "------>> Digito Verificador is not added!\n"
                    failed_row_ids.append(pointer)
                    continue

                if list_result[6]:
                    code = str(list_result[6])
                    if '.' in code:
                        code = code.split('.')[0]
                    p_code += code.zfill(2)

                # Validate Origin Of Resource
                origin_resource = origin_obj.validate_origin_resource(list_result[7])
                if not origin_resource:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Origin Of Resource(OR) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Institutional Activity Number
                institutional_activity = activity_obj.validate_institutional_activity(list_result[8])
                if not institutional_activity:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Institutional Activity Number(AI) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Conversion Program SHCP
                shcp = shcp_obj.validate_shcp(list_result[9], program)
                if not shcp:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Conversion Program SHCP(CONPP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Federal Item
                conversion_item = dpc_obj.validate_conversion_item(list_result[10],item.id)
                if not conversion_item:
                    failed_row += str(list_result) + \
                                  "------>> Invalid SHCP Games(CONPA) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                expense_type = expense_type_obj.validate_expense_type(list_result[11])
                if not expense_type:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Expense Type(TG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Expense Type
                geo_location = location_obj.validate_geo_location(list_result[12])
                if not geo_location:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Geographic Location (UG) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Wallet Key
                wallet_key = wallet_obj.validate_wallet_key(list_result[13])
                if not wallet_key:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Wallet Key(CC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Project Type
                project_type = project_type_obj.with_context(from_adjustment=True).validate_project_type(
                    list_result[14], list_result[15])
                if not project_type:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Project Type(TP) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Stage
                stage = stage_obj.validate_stage(list_result[16], project_type.project_id)
                if not stage:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Stage(E) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Agreement Type
                agreement_type = agreement_type_obj.validate_agreement_type(list_result[17],
                                                                            project_type.project_id, list_result[18])
                if not agreement_type:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Agreement Type(TC) Format\n"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Amount
                amount = 0
                try:
                    amount = float(list_result[20])
                    if float(amount) < 10000:
                        failed_row += str(list_result) + \
                                      "------>> Amount should be 10000 or greater than 10000\n"
                        failed_row_ids.append(pointer)
                        continue
                except:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Amount Format or Amount should be greater than or equal to 10000"
                    failed_row_ids.append(pointer)
                    continue

                # Validation Type
                typee = str(list_result[21]).replace(' ', '').lower()
                if typee not in ['increase', 'decrease']:
                    failed_row += str(list_result) + \
                                  "------>> Invalid Type Format\n"
                    failed_row_ids.append(pointer)
                    continue

                try:
                    program_code = False
                    if year and program and subprogram and dependency and subdependency and item and origin_resource \
                            and institutional_activity and shcp and conversion_item and expense_type and geo_location \
                            and wallet_key and project_type and stage and agreement_type:
                        program_code = self.env['program.code'].sudo().search([
                            ('year', '=', year.id),
                            ('program_id', '=', program.id),
                            ('sub_program_id', '=', subprogram.id),
                            ('dependency_id', '=', dependency.id),
                            ('sub_dependency_id', '=', subdependency.id),
                            ('item_id', '=', item.id),
                            ('resource_origin_id', '=', origin_resource.id),
                            ('institutional_activity_id',
                             '=', institutional_activity.id),
                            ('budget_program_conversion_id', '=', shcp.id),
                            ('conversion_item_id', '=', conversion_item.id),
                            ('expense_type_id', '=', expense_type.id),
                            ('location_id', '=', geo_location.id),
                            ('portfolio_id', '=', wallet_key.id),
                            ('project_type_id', '=', project_type.id),
                            ('stage_id', '=', stage.id),
                            ('agreement_type_id', '=', agreement_type.id),
                            ('state', '=', 'validated'),
                        ], limit=1)

                        if program_code:
                            budget_line = self.env['expenditure.budget.line'].sudo().search(
                                [('program_code_id', '=', program_code.id),
                                 ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)
                            if not budget_line:
                                failed_row += str(list_result) + \
                                              "------>> Budget line not found for program code!"
                                failed_row_ids.append(pointer)
                                continue

                            pc = program_code
                            dv_obj = self.env['verifying.digit']
                            if pc.program_id and pc.sub_program_id and pc.dependency_id and \
                                    pc.sub_dependency_id and pc.item_id:
                                vd = dv_obj.check_digit_from_codes(
                                    pc.program_id, pc.sub_program_id, pc.dependency_id, pc.sub_dependency_id,
                                    pc.item_id)
                                if vd and p_code and vd != p_code:
                                    if vd != p_code:
                                        failed_row += str(list_result) + \
                                                      "------>> Digito Verificador is not matched! \n"
                                        failed_row_ids.append(pointer)
                                        continue

                    if not program_code:
                        failed_row += str(list_result) + \
                                      "------>> Program code not found!"
                        failed_row_ids.append(pointer)
                        continue
                    success_row_ids.append(pointer)

                    if self._context.get('re_scan_failed'):
                        failed_row_ids_eval_refill = eval(self.failed_row_ids)
                        failed_row_ids_eval_refill.remove(pointer)
                        self.write({'failed_row_ids': str(
                            list(set(failed_row_ids_eval_refill)))})

                    line_vals = {
                        'program': program_code.id,
                        'line_type': typee,
                        'amount': amount,
                        'creation_type': 'imported',
                        'imported': True,
                    }
                    self.write({'adequacies_lines_ids': [(0, 0, line_vals)]})
                except:
                    failed_row += str(list_result) + \
                                  "------>> Row Data Are Not Corrected or Validated Program Code Not Found!"
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

            if pointer == sheet.nrows and len(failed_row_ids_eval) > 0:
                self.write({'allow_upload': True})

            if self.failed_row_ids == 0 or len(failed_row_ids_eval) == 0:
                self.write({'allow_upload': False})

            if cron:
                next_cron = self.env['ir.cron'].sudo().search([('prev_cron_id', '=', cron.id), ('active', '=', False), (
                'model_id', '=', self.env.ref('jt_budget_mgmt.model_adequacies').id)], limit=1)
                if next_cron:
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)
                    next_cron.write({'nextcall': nextcall, 'active': True})
                else:
                    self.write({'cron_running': False})
                    failed_count = success_count = 0
                    if self.adequacies_lines_ids:
                        success_count = len(self.adequacies_lines_ids)
                    failed_count = self.total_rows - success_count
                    self.send_notification_msg(self.create_uid, failed_count, success_count)
                    self.create_uid.notify_info(message='Adequacies - ' + str(self.folio) +
                                                        ' Lines Validation process completed. Please verify and correct lines, if any failed!',
                                                title="Adequacies", sticky=True)
                    msg = (_("Adequacies Validation Process Ended at %s" % datetime.strftime(
                        datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                    self.env['mail.message'].create({'model': 'adequacies', 'res_id': self.id,
                                                     'body': msg})
            if vals:
                self.write(vals)

            # if len(failed_row_ids) == 0:
            #     return{
            #         'effect': {
            #             'fadeout': 'slow',
            #             'message': 'All rows are imported successfully!',
            #             'type': 'rainbow_man',
            #         }
            #     }

    def send_notification_msg(self, user, failed, successed):
        ch_obj = self.env['mail.channel']
        base_user = self.env.ref('base.user_root')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=adequacies' % (self.id)
        body = (_("Adequacies Validation Process is Completed for \
                    <a href='%s' target='new'>%s</a>" % (url, self.folio)))
        body += (_("<ul><li>Total Successed Lines: %s </li>\
            <li>Total Failed Lines: %s </li></ul>") % (str(successed), str(failed)))
        if user:
            ch = ch_obj.sudo().search([('name', '=', str(base_user.name + ', ' + user.name)),
                                       ('channel_type', '=', 'chat')], limit=1)
            if not ch:
                ch = ch_obj.create({
                    'name': 'OdooBot, ' + user.name,
                    'public': 'private',
                    'channel_type': 'chat',
                    'channel_last_seen_partner_ids': [(0, 0, {'partner_id': user.partner_id.id,
                                                              'partner_email': user.partner_id.email}),
                                                      (0, 0, {'partner_id': base_user.partner_id.id,
                                                              'partner_email': base_user.partner_id.email})
                                                      ]
                })
            ch.message_post(attachment_ids=[], body=body, content_subtype='html',
                            message_type='comment', partner_ids=[], subtype='mail.mt_comment',
                            email_from=base_user.partner_id.email, author_id=base_user.partner_id.id)
        return True

    def remove_cron_records(self):
        crons = self.env['ir.cron'].sudo().search(
            [('model_id', '=', self.env.ref('jt_budget_mgmt.model_adequacies').id)])
        for cron in crons:
            if cron.adequacies_id and not cron.adequacies_id.cron_running:
                try:
                    cron.sudo().unlink()
                except:
                    pass

    def validate_draft_lines(self):
        if self.budget_file:
            # Total CRON to create
            data = base64.decodestring(self.budget_file)
            book = open_workbook(file_contents=data or b'')
            sheet = book.sheet_by_index(0)
            total_sheet_rows = sheet.nrows - 1
            total_cron = math.ceil(total_sheet_rows / 5000)
            msg = (_("Adequacies Validation Process Started at %s" % datetime.strftime(
                datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
            self.env['mail.message'].create({'model': 'adequacies', 'res_id': self.id,
                                             'body': msg})
            if total_cron == 1:
                self.validate_and_add_budget_line()
                msg = (_("Adequacies Validation Process Ended at %s" % datetime.strftime(
                    datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)))
                self.env['mail.message'].create({'model': 'adequacies', 'res_id': self.id,
                                                 'body': msg})
            else:
                self.write({'cron_running': True})
                prev_cron_id = False
                for seq in range(1, total_cron + 1):
                    # Create CRON JOB
                    cron_name = str(self.folio).replace(' ', '') + "_" + str(datetime.now()).replace(' ', '')
                    nextcall = datetime.now()
                    nextcall = nextcall + timedelta(seconds=10)

                    cron_vals = {
                        'name': cron_name,
                        'state': 'code',
                        'nextcall': nextcall,
                        'nextcall_copy': nextcall,
                        'numbercall': -1,
                        'code': "model.validate_and_add_budget_line()",
                        'model_id': self.env.ref('jt_budget_mgmt.model_adequacies').id,
                        'user_id': self.env.user.id,
                        'adequacies_id': self.id
                    }

                    # Final process
                    cron = self.env['ir.cron'].sudo().create(cron_vals)
                    cron.write(
                        {'code': "model.validate_and_add_budget_line(" + str(self.id) + "," + str(cron.id) + ")"})
                    if prev_cron_id:
                        cron.write({'prev_cron_id': prev_cron_id, 'active': False})
                    prev_cron_id = cron.id

    def validate_data(self):
        for adequacies in self:
            total_decreased = 0
            total_increased = 0
            counter_decreased = 0
            counter_increased = 0
            if len(self.adequacies_lines_ids.ids) == 0:
                raise ValidationError("Please select or import any lines!")
            if self.adaptation_type != 'compensated':
                line_types = adequacies.adequacies_lines_ids.mapped('line_type')
                line_types = list(set(line_types))
                if len(line_types) > 1:
                    raise ValidationError(_(
                        "In liquid adjustment, you can only increase or decrease amount of budget!"))
            code_list_decrese = []
            code_list_decrese_msg = ''
            for line in adequacies.adequacies_lines_ids:
                budget_lines_check = self.env['expenditure.budget.line'].sudo().search(
                    [('program_code_id', '=', line.program.id),
                     ('expenditure_budget_id', '=', self.budget_id.id)])
                budget_line_assign = False
                if adequacies.adaptation_type == 'compensated':
                    b_month = adequacies.date_of_budget_affected.month
                else:
                    b_month = adequacies.date_of_liquid_adu.month
                for b_line in budget_lines_check:
                    if b_line.start_date:
                        b_s_month = b_line.start_date.month
                        if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                            budget_line_assign = b_line
                        elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                            budget_line_assign = b_line
                        elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                            budget_line_assign = b_line
                        elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                            budget_line_assign = b_line
#                 if budget_line_assign:
#                     total_assing_amount = sum(x.assigned for x in budget_line_assign)
#                     if total_assing_amount <=0 :
#                         raise ValidationError(_("You are not allowed to adjustments for zero or negative assign amount of program code! %s " % \
#                                             (line.program.program_code)))
                        

                found = False
                for b_check in budget_lines_check:
                    if adequacies.adaptation_type != 'compensated' and adequacies.date_of_liquid_adu and \
                            b_check.start_date and b_check.end_date:
                        if adequacies.date_of_liquid_adu >= b_check.start_date and adequacies.date_of_liquid_adu <= b_check.end_date:
                            found = True
                    elif adequacies.adaptation_type == 'compensated' and adequacies.date_of_budget_affected \
                            and b_check.start_date and b_check.end_date:
                        if adequacies.date_of_budget_affected >= b_check.start_date and \
                                adequacies.date_of_budget_affected <= b_check.end_date:
                            found = True
                if not found:
                    raise ValidationError(_("%s Program code is not available in %s with selected quarter!" % \
                                            (line.program.program_code, adequacies.budget_id.name)))

#                 if line.amount < 10000:
#                     raise ValidationError(_(
#                         "The total amount of the increases/decreases should be greater than or equal to 10000"))
                if line.line_type == 'decrease':
                    budget_line = False
                    if self.date_of_budget_affected and self.adaptation_type == 'compensated':
                        b_month = self.date_of_budget_affected.month
                        budget_lines = self.env['expenditure.budget.line'].sudo().search(
                            [('program_code_id', '=', line.program.id),
                             ('expenditure_budget_id', '=', self.budget_id.id)])
                        for b_line in budget_lines:
                            if b_line.start_date:
                                b_s_month = b_line.start_date.month
                                if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                    budget_line = b_line
                                elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                    budget_line = b_line
                                elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                                    budget_line = b_line
                                elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                    budget_line = b_line
                                    
                    if self.date_of_liquid_adu and self.adaptation_type == 'liquid':
                        b_month = self.date_of_liquid_adu.month
                        budget_lines = self.env['expenditure.budget.line'].sudo().search(
                            [('program_code_id', '=', line.program.id),
                             ('expenditure_budget_id', '=', self.budget_id.id)])
                        for b_line in budget_lines:
                            if b_line.start_date:
                                b_s_month = b_line.start_date.month
                                if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                    budget_line = b_line
                                elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                    budget_line = b_line
                                elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                                    budget_line = b_line
                                elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                    budget_line = b_line
                                    
                    if not budget_line:
                        budget_line = self.env['expenditure.budget.line'].sudo().search(
                            [('program_code_id', '=', line.program.id),
                             ('expenditure_budget_id', '=', self.budget_id.id)], limit=1)

                        
                    if budget_line and budget_line.authorized < line.amount:
                        code_list_decrese.append(budget_line.program_code_id.program_code)
                        if self.env.user.lang == 'es_MX':
                            code_list_decrese_msg += 'Código del programa de:' + str(budget_line.program_code_id.program_code) + '\n' + ' El monto requerido es de $ '+str(line.amount) + ' y el monto disponible es de $ '+str(budget_line.authorized) + '\n'
                        else:
                            code_list_decrese_msg += 'Program Code: ' + str(budget_line.program_code_id.program_code) + '\n' + ' The required amount is $ '+str(line.amount) + ' the available amount is $ '+str(budget_line.authorized)  + '\n'      
                        continue

                    total_decreased += line.amount
                    counter_decreased += 1
                if line.line_type == 'increase':
                    total_increased += line.amount
                    counter_increased += 1
            if code_list_decrese:
                if self.env.user.lang == 'es_MX':
                    raise ValidationError(_("El monto es mayor que el asignado en el presupuesto! \n presupuesto: %s \n %s" % (adequacies.budget_id.name,code_list_decrese_msg)))
                    
                else:
                    raise ValidationError(_("The amount is greater than the one assigned in the budget. \n Budget: %s \n %s" % (adequacies.budget_id.name,code_list_decrese_msg)))
                    
            if adequacies.adaptation_type == 'compensated' and total_decreased != total_increased:
                raise ValidationError(_(
                    "The total amount of the increases and the total amount of the decreases must be equal for compensated adjustments!"))

    def confirm(self):
        self.validate_data()
        self.state = 'confirmed'

    @api.onchange('adaptation_type')
    def onchange_type(self):
        if self.adaptation_type == 'compensated':
            comp_adequacy_jour = self.env.ref('jt_conac.comp_adequacy_jour')
            if comp_adequacy_jour:
                self.journal_id = comp_adequacy_jour.id
        else:
            liq_adequacy_jour = self.env.ref('jt_conac.liq_adequacy_jour')
            if liq_adequacy_jour:
                self.journal_id = liq_adequacy_jour.id

    def accept(self):
        self.validate_data()
        for line in self.adequacies_lines_ids:
            if line.program:
                if self.date_of_budget_affected and self.adaptation_type == 'compensated':
                    b_month = self.date_of_budget_affected.month
                    budget_line = False
                    budget_lines = self.env['expenditure.budget.line'].sudo().search(
                        [('program_code_id', '=', line.program.id),
                         ('expenditure_budget_id', '=', self.budget_id.id)])
                    for b_line in budget_lines:
                        if b_line.start_date:
                            b_s_month = b_line.start_date.month
                            if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                budget_line = b_line
                            elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                budget_line = b_line
                            elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                                budget_line = b_line
                            elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                budget_line = b_line
                    if budget_line:
                        amount = budget_line.assigned
                        authorized_amount = budget_line.authorized
                        
                        if line.line_type == 'decrease':
                            final_amount = amount - line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount - line.amount})
                        if line.line_type == 'increase':
                            final_amount = amount + line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount + line.amount})
                elif self.date_of_liquid_adu and self.adaptation_type == 'liquid':
                    b_month = self.date_of_liquid_adu.month
                    budget_line = False
                    budget_lines = self.env['expenditure.budget.line'].sudo().search(
                        [('program_code_id', '=', line.program.id),
                         ('expenditure_budget_id', '=', self.budget_id.id)])
                    for b_line in budget_lines:
                        if b_line.start_date:
                            b_s_month = b_line.start_date.month
                            if b_month in (1, 2, 3) and b_s_month in (1, 2, 3):
                                budget_line = b_line
                            elif b_month in (4, 5, 6) and b_s_month in (4, 5, 6):
                                budget_line = b_line
                            elif b_month in (7, 8, 9) and b_s_month in (7, 8, 8):
                                budget_line = b_line
                            elif b_month in (10, 11, 12) and b_s_month in (10, 11, 12):
                                budget_line = b_line
                    if budget_line:
                        amount = budget_line.assigned
                        authorized_amount = budget_line.authorized
                        if line.line_type == 'decrease':
                            final_amount = amount - line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount - line.amount})
                        if line.line_type == 'increase':
                            final_amount = amount + line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount + line.amount})
                else:
                    budget_line = self.env['expenditure.budget.line'].sudo().search(
                        [('program_code_id', '=', line.program.id), ('expenditure_budget_id', '=', self.budget_id.id)],
                        limit=1)
                    if budget_line:
                        amount = budget_line.assigned
                        authorized_amount = budget_line.authorized
                        if line.line_type == 'decrease':
                            final_amount = amount - line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount - line.amount})
                        if line.line_type == 'increase':
                            final_amount = amount + line.amount
                            budget_line.write({'assigned': final_amount,'authorized':authorized_amount + line.amount})
        if self.adaptation_type != 'compensated' and self.journal_id:
            move_obj = self.env['account.move']
            journal = self.journal_id
            today = datetime.today().date()
            user = self.env.user
            partner_id = user.partner_id.id
            amount = sum(self.adequacies_lines_ids.mapped('amount'))
            company_id = user.company_id.id
            if not journal.default_debit_account_id or not journal.default_credit_account_id \
                    or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
                raise ValidationError(_("Please configure UNAM and CONAC account in journal!"))
            if self.adequacies_lines_ids[0].line_type == 'increase':
                unam_move_val = {'ref': self.folio, 'adequacy_id': self.id, 'conac_move': True,
                                 'date': today, 'journal_id': journal.id, 'company_id': company_id,
                                 'line_ids': [(0, 0, {
                                     'account_id': journal.default_credit_account_id.id,
                                     'coa_conac_id': journal.conac_credit_account_id.id,
                                     'credit': amount, 'adequacy_id': self.id,
                                     'partner_id': partner_id
                                 }), (0, 0, {
                                     'account_id': journal.default_debit_account_id.id,
                                     'coa_conac_id': journal.conac_debit_account_id.id,
                                     'debit': amount, 'adequacy_id': self.id,
                                     'partner_id': partner_id
                                 })]}
            else:
                unam_move_val = {'ref': self.folio, 'adequacy_id': self.id, 'conac_move': True,
                                 'date': today, 'journal_id': journal.id, 'company_id': company_id,
                                 'line_ids': [(0, 0, {
                                     'account_id': journal.default_credit_account_id.id,
                                     'coa_conac_id': journal.conac_credit_account_id.id,
                                     'debit': amount, 'adequacy_id': self.id,
                                     'partner_id': partner_id
                                 }), (0, 0, {
                                     'account_id': journal.default_debit_account_id.id,
                                     'coa_conac_id': journal.conac_debit_account_id.id,
                                     'credit': amount, 'adequacy_id': self.id,
                                     'partner_id': partner_id
                                 })]}
            unam_move = move_obj.create(unam_move_val)
            unam_move.action_post()
        if self.adaptation_type == 'compensated' and self.journal_id:
            move_obj = self.env['account.move']
            journal = self.journal_id
            today = datetime.today().date()
            user = self.env.user
            partner_id = user.partner_id.id
            company_id = user.company_id.id
            if not journal.default_debit_account_id or not journal.default_credit_account_id \
                    or not journal.conac_debit_account_id or not journal.conac_credit_account_id:
                raise ValidationError(_("Please configure UNAM and CONAC account in journal!"))
            for line in self.adequacies_lines_ids:
                amount = line.amount
                if line.line_type == 'increase':
                    unam_move_val = {'ref': self.folio, 'adequacy_id': self.id, 'conac_move': True,
                                     'date': today, 'journal_id': journal.id, 'company_id': company_id,
                                     'line_ids': [(0, 0, {
                                         'account_id': journal.default_credit_account_id.id,
                                         'coa_conac_id': journal.conac_credit_account_id.id,
                                         'credit': amount, 'adequacy_id': self.id,
                                         'partner_id': partner_id
                                     }), (0, 0, {
                                         'account_id': journal.default_debit_account_id.id,
                                         'coa_conac_id': journal.conac_debit_account_id.id,
                                         'debit': amount, 'adequacy_id': self.id,
                                         'partner_id': partner_id
                                     })]}
                else:
                    unam_move_val = {'ref': self.folio, 'adequacy_id': self.id, 'conac_move': True,
                                     'date': today, 'journal_id': journal.id, 'company_id': company_id,
                                     'line_ids': [(0, 0, {
                                         'account_id': journal.default_credit_account_id.id,
                                         'coa_conac_id': journal.conac_credit_account_id.id,
                                         'debit': amount, 'adequacy_id': self.id,
                                         'partner_id': partner_id
                                     }), (0, 0, {
                                         'account_id': journal.default_debit_account_id.id,
                                         'coa_conac_id': journal.conac_debit_account_id.id,
                                         'credit': amount, 'adequacy_id': self.id,
                                         'partner_id': partner_id
                                     })]}
                unam_move = move_obj.create(unam_move_val)
                unam_move.action_post()
        self.state = 'accepted'

    def reject(self):
        self.state = 'rejected'

    def unlink(self):
        for adequacies in self:
            if adequacies.state not in ('draft'):
                raise ValidationError(
                    'You can not delete confirmed/rejected adjustments!')
        return super(Adequacies, self).unlink()


class AdequaciesLines(models.Model):
    _name = 'adequacies.lines'
    _description = 'Adequacies Lines'
    _rec_name = ''

    line_type = fields.Selection(
        [('increase', 'Increase'), ('decrease', 'Decrease')], string='Type', default='increase')
    amount = fields.Float(string='Amount')
    creation_type = fields.Selection(
        [('manual', 'Manual'), ('imported', 'Imported')],
        string='Creation type', default='manual')
    adequacies_id = fields.Many2one(
        'adequacies', string='Adequacies', ondelete="cascade")
    imported = fields.Boolean(default=False)
    program = fields.Many2one(
        'program.code', string='Program', domain="[('state', '=', 'validated'), ('budget_id', '=', parent.budget_id)]")

    _sql_constraints = [('uniq_program_per_adequacies_id', 'unique(program,adequacies_id)',
                         'The program code must be unique per Adequacies')]
