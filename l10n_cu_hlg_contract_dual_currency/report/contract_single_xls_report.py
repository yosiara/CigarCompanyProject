# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ContractSingleXlsReportDual(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        merge_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#C0C0C0', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        merge_format1 = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}, 'bg_color': '#FFFF33', 'font_color': '#000000', 'font_name': 'Calibri', 'text_wrap': True})
        normal_format = workbook.add_format({'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}, 'text_wrap': True})
        head_format = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 12}, 'text_wrap': True})

        worksheet = workbook.add_worksheet(tools.ustr("REGISTRO ÚNICO DE CONTRATO"))
        state = data['state']
        date_start = data['date_start']
        date_end = data['date_end']

        domain = []
        if state:
            domain.append(('state', '=', state))
        if date_start and date_end:
            domain.append(('date_start', '>=', date_start))
            domain.append(('date_start', '<=', date_end))
        flow = data['flow']
        if flow == 'customer':
            aux = 'VENTAS'
        else:
            aux = 'COMPRAS'
        if flow:
            domain.append(('flow', '=', flow))
        contract_ids = self.env['l10n_cu_contract.contract'].search(domain)
        worksheet.merge_range(0, 0, 3, 1, 'FOTO', head_format)
        worksheet.merge_range(0, 2, 3, 7, tools.ustr("REGISTRO ÚNICO DE CONTRATO DE " + aux), head_format)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 30)

        worksheet.write('A5', tools.ustr('Exp No.'), merge_format)
        worksheet.write('B5', tools.ustr('Número'), merge_format)
        if flow == 'customer':
            worksheet.write('C5', tools.ustr('Cliente'), merge_format)
        else:
            worksheet.write('C5', tools.ustr('Proveedor'), merge_format)
        worksheet.write('D5', tools.ustr('Denominación'), merge_format)
        worksheet.write('E5', tools.ustr('Importe CUP'), merge_format)
        worksheet.write('F5', tools.ustr('Importe CUC'), merge_format)
        worksheet.write('G5', tools.ustr('Importe Total'), merge_format)
        worksheet.write('H5', tools.ustr('Fecha Inicio'), merge_format)
        worksheet.write('I5', tools.ustr('Fecha Término'), merge_format)
        worksheet.write('J5', tools.ustr('Especialista'), merge_format)

        x = 5
        for c in contract_ids:
            worksheet.write(x, 0, tools.ustr(c.partner_id.archive_nro if c.partner_id.archive_nro else ''), normal_format)
            worksheet.write(x, 1, tools.ustr(c.number), normal_format)
            worksheet.write(x, 2, tools.ustr(c.partner_id.name), normal_format)
            worksheet.write(x, 3, tools.ustr(c.name), normal_format)
            worksheet.write(x, 4, "{0:.2f}".format(c.total_cup).replace('.', ','), normal_format)
            worksheet.write(x, 5, "{0:.2f}".format(c.total_cuc).replace('.', ','), normal_format)
            worksheet.write(x, 6, "{0:.2f}".format(c.amount_total).replace('.', ','), normal_format)
            worksheet.write(x, 7, c.date_start, normal_format)
            worksheet.write(x, 8, c.date_end, normal_format)
            worksheet.write(x, 9, c.employee_id.name, normal_format)
            x += 1
        x += 2
        worksheet.write(x, 0, tools.ustr("Etapa"), merge_format)
        worksheet.write(x, 1, tools.ustr("Cargo"), merge_format)
        worksheet.merge_range(x,2,x,4, tools.ustr("Nombre y Apellidos"), merge_format)
        worksheet.write(x, 5, tools.ustr("Firma"), merge_format)
        worksheet.write(x, 6, tools.ustr("Fecha"), merge_format)
        x += 1
        worksheet.write(x, 0, tools.ustr("Revisión"), normal_format)
        worksheet.write(x, 1, tools.ustr(" "), normal_format)
        worksheet.merge_range(x,2,x,4, tools.ustr(""), normal_format)
        worksheet.write(x, 5, tools.ustr(" "), normal_format)
        worksheet.write(x, 6, tools.ustr(" "), normal_format)
        x += 1
        worksheet.write(x, 0, tools.ustr("Aprobación"), normal_format)
        worksheet.write(x, 1, tools.ustr(" "), normal_format)
        worksheet.merge_range(x,2,x,4, tools.ustr(""), normal_format)
        worksheet.write(x, 5, tools.ustr(" "), normal_format)
        worksheet.write(x, 6, tools.ustr(" "), normal_format)

ContractSingleXlsReportDual('report.l10n_cu_hlg_contract.contract_single_xls_report_dual.xlsx', 'l10n_cu_contract.print_registry')
