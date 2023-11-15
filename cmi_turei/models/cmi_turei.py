# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Departments(models.Model):
    _name = 'cmi_turei.department'
    _description = 'Departments'

    name = fields.Char('Name', required=True)


class Indicator(models.Model):
    _inherit = 'cmi.indicator'

    department_id = fields.Many2one('cmi_turei.department', 'Department')

    @api.model
    def turei_maintenance_cron(self):
        today = datetime.now()
        day1 = today.strftime('%Y-%m-01')
        year = today.strftime('%Y')
        month = today.strftime('%m')
        stage_id = self.env['maintenance.stage'].search([('name', '=', 'Reparado')], limit=1)

        day1_next_month = (today + relativedelta(months=1)).strftime('%Y-%m-01')
        request = self.env['maintenance.request'].search_count(
            [('request_date', '<', day1_next_month), ('request_date', '>=', day1)])
        request_done = self.env['maintenance.request'].search_count(
            [('request_date', '<', day1_next_month), ('request_date', '>=', day1), ('stage_id', '=', stage_id.id)])
        card = self.search([('id', '=', 8)])
        line = self.env['cmi.indicator.line'].search([('year', '=', year), ('month', '=', month), ('indicator_id', '=', card.id)], limit=1)

        if len(line) == 0:
            line = self.env['cmi.indicator.line'].create(
            {'year': year, 'month': month, 'indicator_id': card.id, 'plan': request, 'value': request_done})
        else:
            line.write(
                {'year': year, 'month': month, 'indicator_id': card.id, 'plan': request, 'value': request_done})


