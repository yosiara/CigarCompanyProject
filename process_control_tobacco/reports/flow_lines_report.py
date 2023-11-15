# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class FlowLinesToExcelReport(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet(tools.ustr('Eficiencia, CDT y Flujo de la LTR'))
        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 11}})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 11}})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}})

        tecnolog_control = self.env['process_control_tobacco.tecnolog_control_model'].search([('date','>=',lines.date_start),('date','<=',lines.date_end)], order='date, turn')
        worksheet.merge_range('A1:J1', tools.ustr("REPORTE DE EFICIENCIA, CDT Y FLUJO DE LA LTR  DESDE: %s - HASTA: %s") %(lines.date_start, lines.date_end), head_format)
        worksheet.set_column('A2:D2', 7)
        worksheet.write('A2', tools.ustr('Año'), merge_format)
        worksheet.write('B2', 'Mes', merge_format)
        worksheet.write('C2', tools.ustr('Día'), merge_format)
        worksheet.write('D2', tools.ustr('Turno'), merge_format)
        worksheet.set_column('F2:H2', 25)
        worksheet.write('E2', tools.ustr('Línea'), merge_format)
        worksheet.write('F2', tools.ustr('Eficiencia Real'), merge_format)
        worksheet.write('G2', tools.ustr('Eficiencia Operativa'), merge_format)
        worksheet.write('H2', tools.ustr('Coeficiente de Disponibilidad Técnica Real'), merge_format)
        worksheet.write('I2', tools.ustr('Flujo L100'), merge_format)
        worksheet.write('J2', tools.ustr('Flujo L300'), merge_format)

        x = 2
        for tc in tecnolog_control:
            tpexo, tpend, tti = 0.0, 0.0, 0.0
            worksheet.write(x, 0, tc.date.split('-')[0], normal_format)
            worksheet.write(x, 1, tc.date.split('-')[1], normal_format)
            worksheet.write(x, 2, tc.date.split('-')[2], normal_format)
            worksheet.write(x, 3, tc.turn.turn.name[-1:], normal_format)
            worksheet.write(x, 4, tools.ustr("LTR"), normal_format)
            efficiency_real = (tc.reconstituted_produced / (tc.plan_time * tc.productive_capacity)) * 100
            worksheet.write(x, 5, round(efficiency_real,2), normal_format)
            for it in tc.interruptions:
                tti += it.time
                if it.interruption_type.cause == 'exogena':
                    tpexo += it.time
                if it.interruption_type.cause == 'endogena':
                    tpend += it.time
            efficiency_operative = (tc.reconstituted_produced / ((tc.plan_time -(tpexo / 60)) * tc.productive_capacity)) * 100
            worksheet.write(x, 6, round(efficiency_operative,2), normal_format)
            cdt = ((tc.plan_time-(tti / 60))/tc.plan_time) * 100
            worksheet.write(x, 7, round(cdt,2), normal_format)
            worksheet.write(x, 8, round(tc.quantity_vena_polvo / tc.execution_time_l100, 2) if tc.execution_time_l100 !=0 else 0, normal_format)
            worksheet.write(x, 9, round(tc.quantity_vena_polvo / tc.execution_time_l300, 2) if tc.execution_time_l300 != 0 else 0, normal_format)
            x += 1

FlowLinesToExcelReport('report.process_control_tobacco.flow_lines_report', 'wzd.flow.lines.to.excel')
