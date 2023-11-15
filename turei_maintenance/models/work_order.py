# -*- coding: utf-8 -*-
import math
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WorkOrder(models.Model):
    _name = 'turei_maintenance.work_order'
    _description = 'turei_maintenance.work_order'
    _rec_name = 'number_new'

    code = fields.Char(required=True, string='Código')
    number = fields.Char(string='Número')
    number_new = fields.Char("Número")

    opening_date = fields.Date(readonly=False, string='Fecha Apertura')
    closing_date = fields.Date(readonly=False, string='Fecha Cierre')

    execute_cost_center_id = fields.Many2one('l10n_cu_base.cost_center', string='Ejecuta', required=True)
    receive_cost_center_id = fields.Many2one('l10n_cu_base.cost_center', string='Recibe', required=True)
    state = fields.Selection(
        [('created', 'Creada'), ('open', 'Abierta'), ('closed', 'Cerrada'), ('cancel', 'Cancelada')], default='created',
        readonly=True, string='Estado (ATM)')
    # type_id = fields.Many2one('atmsys.work_order.type', string='Tipo', required=True, readonly=False)

    creator_id = fields.Many2one('hr.employee', string='Abre', readonly=True)
    emitter_id = fields.Many2one('hr.employee', string='Emite', required=True)
    executor_id = fields.Many2one('hr.employee', string='Ejecuta', required=True)
    shutter_id = fields.Many2one('hr.employee', string='Cierra', readonly=True)

    realized_work_ids = fields.One2many(comodel_name="turei_maintenance.realized_work",
                                        inverse_name="realized_work_order_id",
                                        string="Trabajo Realizado", required=False, ondelete='cascade')
    equipament_id = fields.Many2one('maintenance.equipment', string='Equipo', domain="[('is_industrial', '=', True)]")
    cycle_id = fields.Many2one('turei_maintenance.cycle_maintenance', string='Ciclo',
                               domain="[('equipment_id', '=', equipament_id)]")

    maintenance_request_id = fields.Many2one('maintenance.request', string='Petición de Mantenimiento')
    equipment_or_area = fields.Char(string="Equipo según ATM")
    note = fields.Text(string="Descripción")

    product_order_ids = fields.One2many('turei_maintenance.product_order', inverse_name='work_order_id',
                                        string='Productos...')
    # ESte campo hay que declararlo en Work order de ATM
    # work_order_mtto_id = fields.Many2one('turei_maintenance.work_order', string='WOMTTO')

    anir = fields.Boolean(default=False)
    time = fields.Char(string='Tiempo(Hr)')
    ready_equipment = fields.Selection([('si', 'SI'), ('no', 'NO')], string='Equipo Listo')
    work_type = fields.Selection([('imp-tec', 'Imprevisto-Técnico'), ('imp_ope', 'Imprevisto-Por Operación'),
                                  ('plan_ciclo', 'Planificado-Ciclo'), ('plan_et', 'Planificado x Estado Técnico'),
                                  ('ins_tec', 'Inspección Técnica'), ('fac_part', 'Fabricación de Pieza')],
                                 string='Tipo de Trabajo')
    delivered = fields.Boolean(string="Entregada")
    category_id = fields.Many2one(related='equipament_id.category_id', store=True)
    maintenance_team_id = fields.Many2one(related='equipament_id.maintenance_team_id', store=True)
    line_id = fields.Many2one(related='equipament_id.line_id')
    description_cancel = fields.Char('Motivo')
    user_cancel_id = fields.Many2one('res.users', 'Usuario')
    date_cancel = fields.Datetime('Fecha y Hora')
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)
    period_id = fields.Many2one('l10n_cu_period.period', string='Period Monthly', compute="_compute_period", store=True)
    # todo add request_date for maintenance
    request_date_maintenance = fields.Date(string='Request Date Maintenance',
                                           compute="_compute_request_date_maintenance", store=True)

    @api.multi
    @api.depends('maintenance_request_id')
    def _compute_request_date_maintenance(self):
        for c_model in self:
            if c_model.maintenance_request_id:
                c_model.request_date_maintenance = c_model.maintenance_request_id.request_date


    @api.multi
    @api.depends('opening_date')
    def _compute_year_char(self):
        for c_model in self:
            if c_model.opening_date:
                date = fields.datetime.strptime(c_model.opening_date, DEFAULT_SERVER_DATE_FORMAT)
                c_model.year_char = str(date.year)

    @api.multi
    @api.depends('opening_date')
    def _compute_period(self):
        for c_model in self:
            if c_model.opening_date:
                date = fields.datetime.strptime(c_model.opening_date, DEFAULT_SERVER_DATE_FORMAT)
                period_id = self.env['l10n_cu_period.period'].search([('date_start', '<=', date),
                                                                      ('date_stop', '>=', date),
                                                                      ('annual', '=', False)])
                c_model.period_id = period_id

    @api.multi
    @api.model
    def button_request(self):
        if self.maintenance_request_id:
            self.maintenance_request_id.write({'stage_id': self.env.ref('maintenance.stage_3').id})
            cycle_plan_id = self.env['turei_maintenance.cycle_maintenance_plan']. \
                search([('equipment_id', '=', self.maintenance_request_id.equipment_id.id),
                        ('cycle', '=', self.maintenance_request_id.cycle_id.id),
                        ('date', '=', self.maintenance_request_id.request_date),
                        ('year_char', '=', self.maintenance_request_id.year_char)], limit=1)

            cycle_plan_id.write({
                'stage_id': self.maintenance_request_id.stage_id.id
            })
        else:
            raise ValidationError('Debe añadir una Petición de Mantenimiento a la orden de trabajo.')

    # @api.onchange('equipament_id', 'cycle_id')
    # def _onchange_equipment_cycle_id(self):
    #     year = datetime.today().date().year
    #     mr_ids = self.env['maintenance.request'].search([('equipment_id', '=', self.equipament_id.id), ('cycle_id', '=', self.cycle_id.id), ('year_char', '=', str(year))])
    #     return {
    #         'domain': {
    #             'maintenance_request_id': [('id', 'in', mr_ids.ids)]
    #         }
    #     }

    @api.onchange('equipament_id')
    def _onchange_equipment(self):
        self.maintenance_request_id = False

    @api.onchange('maintenance_request_id')
    def _onchange_maintenance_request_id(self):
        if self.maintenance_request_id and self.maintenance_request_id.cycle_id:
            self.cycle_id = self.maintenance_request_id.cycle_id

    @api.constrains('maintenance_request_id', 'cycle_id')
    def _check_maintenance_cycle(self):
        if self.maintenance_request_id and self.cycle_id:
            if self.maintenance_request_id.cycle_id.id != self.cycle_id.id:
                raise ValidationError(_('Error! Cycle not corresponding with maintenance request !!'))

    # def button_open(self):
    #     self.state = 'open'
    #     self.closing_date = None
    #
    #     if not self.opening_date:
    #         self.opening_date = fields.Date.today()
    #
    #     employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
    #     if len(employees):
    #         self.creator_id = employees[0].id
    #
    # def button_close(self):
    #     self.state = 'closed'
    #     self.closing_date = fields.Date.today()
    #
    #     employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
    #     if len(employees):
    #         self.shutter_id = employees[0].id

    # Estos metodos van en el work order de ATM
    # Hay que declarar un nuevo campo work_order_mtto_id en el work order de ATM
    # @api.model
    # def create(self, vals):
    #     work_order = super(WorkOrder, self).create(vals)
    #     if vals.get('type_id'):
    #         if work_order.type_id.name == 'A' or work_order.type_id.name == 'P':
    #             if vals.get('product_order_ids'):
    #                 list_product = []
    #                 for line in work_order.product_order_ids:
    #                     list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
    #                 vals['product_order_ids'] = list_product
    #             work_order_mtto = self.env['turei_maintenance.work_order'].sudo().create(vals)
    #             work_order.write({'work_order_mtto_id': work_order_mtto.id})
    #     return work_order
    # #
    @api.multi
    def write(self, vals):
        res = super(WorkOrder, self).write(vals)
        print("write_work_order")
        for rec in self:
            if vals.get('maintenance_request_id'):
                if rec.maintenance_request_id.stage_id.name == "Nueva solicitud":
                    mr_id = rec.maintenance_request_id.write(
                        {'stage_id': self.env.ref('maintenance.stage_1').id})
                    print(mr_id)
                    print(rec.maintenance_request_id)
        return res
    #     work_order = self.env['turei_maintenance.work_order'].browse(self.work_order_mtto_id.id)
    #     if vals.get('type_id'):
    #         if work_order.type_id.name == 'A' or work_order.type_id.name == 'P':
    #             if vals.get('product_order_ids'):
    #                 work_order.product_order_ids.unlink()
    #                 list_product = []
    #                 for line in self.product_order_ids:
    #                     list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
    #                 vals['product_order_ids'] = list_product
    #             work_order.write(vals)
    #     return res


class RealizedWork(models.Model):
    _name = 'turei_maintenance.realized_work'
    _description = 'turei_maitenance.realized_work'

    executor_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    code_executor = fields.Char(string='Código', required=True)
    description = fields.Text(string='Trabajo')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipo', required=True)
    type = fields.Selection(
        [('cambio_pieza', 'Cambio de Pieza'), ('reparacion', 'Reparación'), ('ajustes', 'Ajustes'), ('otros', 'Otros')],
        string='Tipo')
    time = fields.Char(string='Tiempo(Hr)')
    time_hr = fields.Float('Tiempo(Hr)')
    ready_service = fields.Selection([('si', 'SI'), ('no', 'NO')], string='Servicio Concluido')
    note = fields.Text(string="Observaciones")
    realized_work_order_id = fields.Many2one(comodel_name="turei_maintenance.work_order", string="Documento",
                                             required=False)
    rate = fields.Float('Tarifa', compute='_compute_rate', store=True)

    @api.onchange('executor_id')
    def onchange_executor_id(self):
        if self.executor_id:
            self.code_executor = self.executor_id.code

    @api.depends('executor_id', 'time_hr')
    def _compute_rate(self):
        for record in self:
            if record.executor_id and record.time_hr:
                scale_salary = record.executor_id.job_id.salary_group_id.scale_salary
                record.rate = (scale_salary / 190.6) * record.time_hr
            else:
                record.rate = 0

    @api.onchange('code_executor')
    def onchange_code_executor(self):
        if self.code_executor:
            employee_id = self.env['hr.employee'].search([('code', '=', self.code_executor)])
            if employee_id:
                self.executor_id = employee_id.id
            else:
                self.executor_id = False

    def float_time_to_hour_minutes(self, float_time):
        time_values = math.modf(float_time)
        hours = int(time_values[1])
        minutes = round(time_values[0] * 60)
        return hours, minutes


class ProductOrder(models.Model):
    _name = 'turei_maintenance.product_order'
    _description = 'turei_maintenance.product_order'

    product_id = fields.Many2one('simple_product.product', string='Producto', required=True)
    quantity = fields.Float(digits=(16, 4), required=True, string='Cantidad')
    work_order_id = fields.Many2one(comodel_name="turei_maintenance.work_order", string="Documento",
                                    required=False)
