# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdProductionHoursToExcel(models.TransientModel):
    _name = 'wzd.production.hours.to.excel'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'process_control_tobacco.production_hours_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
        })

