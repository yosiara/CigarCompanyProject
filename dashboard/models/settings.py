from odoo import models, fields, api

from datetime import datetime


class DashboardSettings(models.Model):
    _name = 'dashboard.settings'

    def get_default_chart_model(self):
        return self.search([], limit=1, order='id desc').chart_model_id.id

    def get_default_chart_measure_field(self):
        return self.search([], limit=1, order='id desc').chart_measure_field_id.id

    def get_default_chart_date_field(self):
        return self.search([], limit=1, order='id desc').chart_date_field_id.id

    def get_default_lines(self):
        return self.search([], limit=1, order='id desc').line_ids.ids

    def get_default_chart(self):
        return self.search([], limit=1, order='id desc').chart_ids.ids

    name = fields.Char('Name', default="Setting")
    provider_latitude = fields.Char('latitude')
    provider_longitude = fields.Char('ongitude')
    map = fields.Char('ongitude')
    line_ids = fields.One2many('dashboard.settings.line', 'dashboard_id', 'Fields', default=get_default_lines)
    chart_ids = fields.One2many('dashboard.settings.chart', 'dashboard_id', 'Charts', default=get_default_chart)

    # Automatically updates date filter in dashboard settings once a year
    @api.model
    def dashboard_date_filter_cron(self):
        today = datetime.now()
        first_day = today.strftime('%Y-01-01')
        last_day = today.strftime('%Y-12-31')

        date_range = 'opening_date >= "{}" and opening_date <= "{}"'.format(first_day, last_day)

        # Update Work Orders date range
        work_orders_line = self.env['dashboard.settings.line'].search([('id', '=', 4)], limit=1)
        work_orders_line.write({'filter': date_range})

        # Update Work Orders: Planned-Cycle date range
        work_orders_p_c_line = self.env['dashboard.settings.line'].search([('id', '=', 6)], limit=1)
        work_orders_p_c_line.write({'filter': '{} and work_type = "plan_ciclo"'.format(date_range)})

        # Update Work Orders: Planned x ET date range
        work_orders_x_et_line = self.env['dashboard.settings.line'].search([('id', '=', 7)], limit=1)
        work_orders_x_et_line.write({'filter': '{} and work_type = "plan_et"'.format(date_range)})

        # Update Work Orders ANIR date range
        work_orders_anir_line = self.env['dashboard.settings.line'].search([('id', '=', 8)], limit=1)
        work_orders_anir_line.write({'filter': '{} and anir = True'.format(date_range)})

        # Update Planned Maintenance date range
        planned_maintenance_line = self.env['dashboard.settings.line'].search([('id', '=', 9)], limit=1)
        planned_maintenance_line.write({'filter': 'request_date >= "{}" and request_date <= "{}"'.format(first_day, last_day)})



class DashboardSettingsLine(models.Model):
    _name = 'dashboard.settings.line'
    _order = 'sequence'

    sequence = fields.Integer()
    name = fields.Char('Name')
    model_id = fields.Many2one('ir.model', 'Model')
    field_id = fields.Many2one('ir.model.fields', 'Field')
    color = fields.Selection([('red', 'Red'), ('green', 'Green'), ('primary', 'Primary'), ('yellow', 'Yellow')],
                             string='Color')
    icon = fields.Char('Icon')
    filter = fields.Char('Filter')
    type = fields.Selection([('money', 'Money'), ('qty', 'Quantity')], string='Type')
    dashboard_id = fields.Many2one('dashboard.settings', 'Setting')
    display = fields.Boolean('Show/hide', default=True)


class DashboardSettingschart(models.Model):
    _name = 'dashboard.settings.chart'
    _order = 'sequence'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    display_type = fields.Selection([('area', 'Area'), ('bar', 'Bar')], string='Display Type')
    chart_model_id = fields.Many2one('ir.model', 'Chart Model')
    chart_measure_field_id = fields.Many2one('ir.model.fields', 'Chart measure Field')
    chart_date_field_id = fields.Many2one('ir.model.fields', 'Chart date Field')
    filter = fields.Char('Filter')
    type = fields.Selection([('money', 'Money'), ('qty', 'Quantity')], string='Type')
    dashboard_id = fields.Many2one('dashboard.settings', 'Setting')
    display = fields.Boolean('Show/hide', default=True)

    @api.onchange('display_type', 'chart_model_id')
    def _onchange_price(self):
        domain = []
        if self.chart_model_id:
            domain.append(('model_id', '=', self.chart_model_id.id))
        if self.display_type:
            if self.display_type == 'area':
                domain += [(('ttype', 'in', ['date', 'datetime']))]
            else:
                domain += [(('ttype', 'in', ['date', 'datetime', 'many2one']))]
        return {
            'domain': {
                'chart_date_field_id': domain,
            }
        }
