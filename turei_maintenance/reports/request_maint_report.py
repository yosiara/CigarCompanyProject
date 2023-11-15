# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class RequestMaintReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Peticiones de Mantenimiento'))
        head_format = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})
        merge_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})

        # domain = [('opening_date', '>=', lines.date_start), ('opening_date', '<=', lines.date_end), ('cycle_id', '!=', False)]
        domain = []
        if lines.category_id:
            domain.append(('category_id', '=', lines.category_id.id))
        if lines.maintenance_team_id:
            domain.append(('maintenance_team_id', '=', lines.maintenance_team_id.id))

        # year = datetime.today().date().year
        # date_year = fields.Date.from_string(lines.date_start).year
        # if year == date_year:
        #     domain.append(('opening_date', '>=', lines.date_start))
        #     domain.append(('opening_date', '<=', lines.date_end))
        #     domain.append(('cycle_id', '!=', False))
        #     work_order = self.env['turei_maintenance.work_order'].search(domain, order='opening_date asc')
        # else:
        #     domain.append(('request_date', '>=', lines.date_start))
        #     domain.append(('request_date', '<=', lines.date_end))
        #     work_order = self.env['maintenance.request'].search(domain, order='request_date')
        # domain.append(('request_date', '>=', lines.date_start))
        # domain.append(('request_date', '<=', lines.date_end))
        maintenance_obj = self.env['maintenance.request']
        work_order_obj = self.env['turei_maintenance.work_order']

        equip_ments_ids = self.env['maintenance.equipment'].search(domain,order='line_id asc')
        cycles_plans = self.env['turei_maintenance.cycle_maintenance_plan'].search([('date','>=', lines.date_start),
                                                                                    ('date', '<=', lines.date_end),
                                                                                    ('equipment_id','in',equip_ments_ids.ids)
                                                                                    ],order='date asc')

        worksheet.merge_range('A1:I1', tools.ustr("Resumen de Peticiones de Mantenimiento vs Órdenes Planificadas desde: %s  hasta: %s") % (
        lines.date_start, lines.date_end), head_format)

        worksheet.write('A2', tools.ustr('No.'), merge_format)
        worksheet.write('B2', tools.ustr('No. Inventario'), merge_format)
        worksheet.write('C2', tools.ustr('Nombre del Equipo'), merge_format)
        worksheet.write('D2', tools.ustr('STP'), merge_format)
        worksheet.write('E2', tools.ustr('Duración STP(Horas)'), merge_format)
        worksheet.write('F2', tools.ustr('F_PL'), merge_format)
        worksheet.write('G2', tools.ustr('F_OT'), merge_format)
        worksheet.write('H2', tools.ustr('Taller'), merge_format)
        worksheet.write('I2', tools.ustr('Línea'), merge_format)
        worksheet.write('J2', tools.ustr('No. OT'), merge_format)

        x = 2
        c = 1
        for maint in cycles_plans:
            # if year == date_year:
            #     equip = wk.equipament_id
            #     request_date = wk.maintenance_request_id.request_date
            #     opening_date = wk.opening_date
            #     n_ot = wk.number_new
            # else:
            #     equip = wk.equipment_id
            #     request_date = wk.request_date
            #     opening_date = ''
            #     n_ot = ''

            worksheet.write(x, 0, c, normal_format)
            worksheet.write(x, 1, maint.equipment_id.code, normal_format)
            worksheet.write(x, 2, maint.equipment_id.name, normal_format)
            worksheet.write(x, 3, maint.cycle.cycle, normal_format)
            worksheet.write(x, 4, maint.cycle.duration, normal_format)
            worksheet.write(x, 5, maint.date, normal_format)
            mt = maintenance_obj.search([('request_date','=',maint.date),
                                         ('cycle_id','=',maint.cycle.id),
                                         ('year_char','=',maint.year_char),
                                         ('equipment_id','=',maint.equipment_id.id)
                                         ],limit=1)
            print(mt.id)
            wk = work_order_obj.search([('maintenance_request_id', '=', mt.id),
                                        ('work_type', '=', 'plan_ciclo')])
            worksheet.write(x, 6, wk.opening_date or '', normal_format)
            worksheet.write(x, 7, maint.equipment_id.category_id.name, normal_format)
            worksheet.write(x, 8, maint.equipment_id.line_id.name, normal_format)
            worksheet.write(x, 9, wk.number_new or '', normal_format)
            c += 1
            x += 1



        # x = 2
        # c = 1
        # for maint in maintenance_ids:
        #     # if year == date_year:
        #     #     equip = wk.equipament_id
        #     #     request_date = wk.maintenance_request_id.request_date
        #     #     opening_date = wk.opening_date
        #     #     n_ot = wk.number_new
        #     # else:
        #     #     equip = wk.equipment_id
        #     #     request_date = wk.request_date
        #     #     opening_date = ''
        #     #     n_ot = ''
        #
        #     worksheet.write(x, 0, c, normal_format)
        #     worksheet.write(x, 1, maint.equipment_id.code, normal_format)
        #     worksheet.write(x, 2, maint.equipment_id.name, normal_format)
        #     worksheet.write(x, 3, maint.cycle_id.cycle, normal_format)
        #     worksheet.write(x, 4, maint.cycle_id.duration, normal_format)
        #     worksheet.write(x, 5, maint.request_date, normal_format)
        #     wk = work_order_obj.search([('maintenance_request_id','=',maint.id),('work_type','=','plan_ciclo')])
        #     worksheet.write(x, 6, wk.opening_date or '', normal_format)
        #     worksheet.write(x, 7, maint.equipment_id.category_id.name, normal_format)
        #     worksheet.write(x, 8, maint.equipment_id.line_id.name, normal_format)
        #     worksheet.write(x, 9, wk.number or '', normal_format)
        #     c += 1
        #     x += 1

        # request = self.env['maintenance.request'].search(domain, order='request_date')
        # worksheet.merge_range('A1:F1', tools.ustr("Peticiones de Mantenimiento desde: %s - hasta: %s") %(lines.date_start, lines.date_end), head_format)
        # worksheet.set_column('A2:A2', 5)
        # worksheet.write('A2', tools.ustr('No.'), merge_format)
        # worksheet.set_column('B2:B2', 15)
        # worksheet.write('B2', tools.ustr('Fecha'), merge_format)
        # worksheet.set_column('C2:C2', 20)
        # worksheet.write('C2', tools.ustr('Taller'), merge_format)
        # worksheet.set_column('D2:D2', 30)
        # worksheet.write('D2', tools.ustr('Equipo'), merge_format)
        # worksheet.set_column('E2:F2', 15)
        # worksheet.write('E2', tools.ustr('Código-Ciclo'), merge_format)
        # worksheet.write('F2', tools.ustr('Estado'), merge_format)
        #
        # x = 2
        # c = 1
        # for r in request:
        #     worksheet.write(x, 0, c, normal_format)
        #     worksheet.write(x, 1, r.request_date, normal_format)
        #     worksheet.write(x, 2, r.category_id.name, normal_format)
        #     worksheet.write(x, 3, r.equipment_id.name, normal_format)
        #     worksheet.write(x, 4, r.name, normal_format)
        #     worksheet.write(x, 5, r.stage_id.name, normal_format)
        #     c += 1
        #     x += 1

RequestMaintReport('report.turei_maintenance.request_maint_report', 'wzd.request.maint')
