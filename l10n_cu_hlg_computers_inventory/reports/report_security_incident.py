# -*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models
from odoo.tools.translate import _


class ReportSecurityIncident(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_security_incident'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_computers_inventory.report_security_incident')
        start_date = data['start_date']
        end_date = data['end_date']
        result = []

        incidents_list = self.env['computers_inventory.security_incident'].search([('detection_date', '>=', start_date),
                                                                                   ('detection_date', '<=', end_date)],
                                                                                  order='create_date')

        for incident in incidents_list:
            res = {}
            res['id_code'] = incident.id_code
            res['equipment_id'] = incident.equipment_id.name
            res['employee_id'] = incident.employee_id.name
            res['department_id'] = incident.department_id.name
            res['datetime_start'] = incident.datetime_start
            res['datetime_end'] = incident.datetime_end
            res['incident'] = incident.incident
            res['detection_date'] = incident.detection_date
            res['detector'] = incident.detector.name
            res['observations'] = incident.observations
            res['provisions_applied'] = incident.provisions_applied
            result.append(res)

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': result,
            'elaborates_id': self.env['hr.employee'].search([('id', '=', data['elaborates_id'])]),
            'approved_id': self.env['hr.employee'].search([('id', '=', data['approved_id'])]),
        }
        return report_obj.render('l10n_cu_hlg_computers_inventory.report_security_incident', docargs)
