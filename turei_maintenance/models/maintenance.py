# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.name + '-' + record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result

    category_id = fields.Many2one('maintenance.equipment.category', string='Taller',
                                  track_visibility='onchange', group_expand='_read_group_category_ids')
    location = fields.Many2one('l10n_cu_base.cost_center', string='Usado en la ubicación')
    state = fields.Selection(
        [('bueno', 'Bueno'), ('regular', 'Regular'), ('malo', 'Malo'), ('fuera_servicio', 'Fuera Servicio'),
         ('conservacion', 'Conservación'), ('baja', 'Baja')], string='Estado')
    year_production = fields.Char(string='Año de Fabricación')
    brand = fields.Char(string='Marca')
    country = fields.Char(string='País')
    christism = fields.Char(string='Criticidad')
    equipment_parts_ids = fields.One2many(compute="_compute_equipment_parts",
                                          comodel_name='turei_maintenance.equipment_parts')
    # equipment_parts_ids = fields.One2many(comodel_name='turei_maintenance.equipment_parts', inverse_name='equipment_id', string='Piezas')
    # equipment_parts_count = fields.Integer(string='Piezas', compute='_compute_equipment_parts_count')
    # equipment_electric_motor_ids = fields.One2many(comodel_name='turei_maintenance.equipment_electric_motor', inverse_name='equipment_id', string='Motores Electricos')
    # equipment_electric_motor_count = fields.Integer(string='Motores', compute='_compute_equipment_electric_motor_count')
    equipment_electric_motor_ids = fields.One2many(compute="_compute_equipment_electric_motor",
                                                   comodel_name='turei_maintenance.equipment_electric_motor')
    cycle_maintenance_ids = fields.One2many(comodel_name='turei_maintenance.cycle_maintenance',
                                            inverse_name='equipment_id', string='Ciclos de mantenimiento')
    cycle_maintenance = fields.Char(string='Ciclo de Mantenimiento', compute='_compute_cycle_maintenance')
    cycle_time = fields.Integer('Duración Ciclo Mantenimeinto (Horas)')
    start_time = fields.Float('Hora de inicio', default='08.00', required=True)
    work_time = fields.Integer('Tiempo de Explotación Diario')
    config_maintenance = fields.Boolean(string='Comienza el Plan (Ciclo y Fecha)?', default=False)
    config_date = fields.Date('Fecha Inicio')
    config_cycle = fields.Many2one('turei_maintenance.cycle_maintenance', string='Ciclo',
                                   domain="[('equipment_id', '=', id)]")
    cycle_maintenance_plan_ids = fields.One2many(comodel_name='turei_maintenance.cycle_maintenance_plan',
                                                 inverse_name='equipment_id', string='Ciclo Mantenimiento Plan')
    code = fields.Char(string='Código')
    parent_id = fields.Many2one('maintenance.equipment', string='Parent', index=True, ondelete='cascade')
    child_ids = fields.One2many('maintenance.equipment', 'parent_id', string='Child Types')
    line_id = fields.Many2one('turei_maintenance.line', string='Línea')
    sequence = fields.Integer(string='Secuencia', compute='_compute_sequence')
    is_industrial = fields.Boolean(string='Es de Mantenimiento Industrial?')
    work_order_count = fields.Integer(string='Ord. de Trabajo', compute='_compute_work_order_count')
    history_work_order = fields.Many2many('turei_maintenance.work_order', string='Historial de OT', compute='_compute_history_work_order')
    history_work_order_count = fields.Integer(string='Historial de OT', compute='_compute_history_work_order_count')

    # @api.one
    # def _compute_equipment_parts_count(self):
    #     count = 0
    #     for parts in self.equipment_parts_ids:
    #         count += parts.quantity
    #     self.equipment_parts_count = count

    @api.depends('line_id')
    def _compute_sequence(self):
        for rec in self:
            if rec.line_id:
                self.sequence = rec.line_id.sequence
            else:
                self.sequence = 0

    @api.one
    @api.depends('maintenance_ids.stage_id.done')
    def _compute_maintenance_count(self):
        request_obj = self.env['maintenance.request']
        self.maintenance_count = request_obj.search_count(
            [('equipment_id', '=', self.id), ('year_char', '=', str(datetime.today().date().year))])
        # self.maintenance_count = len(self.maintenance_ids.filtered(lambda x: x.year_char == str(datetime.today().date().year)))
        # self.maintenance_count = self.maintenance_ids.search_count([('equipment_id', '=', self.id), ('year_char', '=', str(datetime.today().date().year))])
        self.maintenance_open_count = len(self.maintenance_ids.filtered(lambda x: not x.stage_id.done))

    def _compute_equipment_parts(self):
        equipment_parts_obj = self.env['turei_maintenance.equipment_parts']
        for record in self:
            equipment_parts = equipment_parts_obj.search([('equipment_ids', 'in', record.id)]).mapped('id')
            record.equipment_parts_ids = equipment_parts

    def _compute_equipment_electric_motor(self):
        equipment_electric_motor_obj = self.env['turei_maintenance.equipment_electric_motor']
        for record in self:
            equipment_electric_motor = equipment_electric_motor_obj.search([('equipment_ids', 'in', record.id)]).mapped(
                'id')
            record.equipment_electric_motor_ids = equipment_electric_motor

    # @api.one
    # def _compute_equipment_electric_motor_count(self):
    #     count = 0
    #     for motor in self.equipment_electric_motor_ids:
    #         count += motor.quantity
    #     self.equipment_electric_motor_count = count

    @api.one
    def _compute_history_work_order_count(self):
        work_order_obj = self.env['turei_maintenance.work_order']
        count = work_order_obj.search_count([('equipament_id', '=', self.id)])
        self.history_work_order_count = count

    @api.one
    def _compute_history_work_order(self):
        work_order_obj = self.env['turei_maintenance.work_order']
        self.history_work_order = work_order_obj.search([('equipament_id', '=', self.id)])

    @api.one
    def _compute_work_order_count(self):
        work_order_obj = self.env['turei_maintenance.work_order']
        count = work_order_obj.search_count(
            [('equipament_id', '=', self.id), ('opening_date', '>=', datetime.now().strftime('%Y-01-01')),
             ('opening_date', '<=', datetime.now().strftime('%Y-12-31'))])
        self.work_order_count = count

    # @api.one
    # @api.depends('maintenance_ids.stage_id.done')
    # def _compute_maintenance_count(self):
    #     self.maintenance_count = len(self.maintenance_ids)
    #     self.maintenance_open_count = len(self.maintenance_ids.filtered(lambda x: not x.stage_id.done))

    @api.one
    def _compute_cycle_maintenance(self):
        name = ''
        long = 0
        for cycle in self.cycle_maintenance_ids:
            if len(self.cycle_maintenance_ids) == 1 or long == 0:
                name = cycle.cycle
            else:
                name = name + "-" + cycle.cycle
            long += 1
            time = self.cycle_time / (len(self.cycle_maintenance_ids))
            cycle.write({'time': time})
        self.cycle_maintenance = name

    @api.onchange('cycle_maintenance_ids')
    def _onchange_cycle_maintenance_ids(self):
        name = ''
        long = 0
        for cycle in self.cycle_maintenance_ids:
            if len(self.cycle_maintenance_ids) == 1 or long == 0:
                name = cycle.cycle
            else:
                name = name + "-" + cycle.cycle
            long += 1
            cycle.write({'time': self.cycle_time / (len(self.cycle_maintenance_ids))})
        self.cycle_maintenance = name

    def next_date(self, startDate, days):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cont = 0
        while days != 0:
            nextDate = startDate + timedelta(cont)
            incident_plan = incident_plan_obj.search(
                [('year_char', '=', str(nextDate.year)), ('date_start', '<=', nextDate), ('date_end', '>=', nextDate)])
            if nextDate.weekday() not in (5, 6) and len(incident_plan) == 0:
                days -= 1
            cont += 1
        return nextDate

    def new_day_mant(self, date_mant, days):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        day_start_maint = int(self.category_id.day_start_maintenance)
        date_mant = date_mant + timedelta(days=days)
        while cond:
            incident_plan = incident_plan_obj.search(
                [('year_char', '=', str(date_mant.year)), ('date_start', '<=', date_mant),
                 ('date_end', '>=', date_mant)])
            if date_mant.weekday() not in (5, 6) and len(incident_plan) == 0 and day_start_maint <= date_mant.weekday():
                cond = False
            else:
                date_mant = date_mant + timedelta(days=1)
        return date_mant

    def get_cycle_maintenance_id(self, cycle):
        for i in xrange(0, len(self.cycle_maintenance_ids)):
            if self.cycle_maintenance_ids[i].cycle == cycle:
                if i == len(self.cycle_maintenance_ids) - 1:
                    return self.cycle_maintenance_ids[0].id
                else:
                    return self.cycle_maintenance_ids[i + 1].id

    # def delete_cycle_maint_plan(self, year):
    #     cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
    #     maint_request_obj = self.env['maintenance.request']
    #     one_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', self.id), ('year_char', '=', str(year))], order='date asc', limit=1)
    #     cycle_ids = self.cycle_maintenance_plan_ids.search([('equipment_id', '=', self.id), ('year_char', '=', str(year)), ('id', '!=', one_cycle.id)])
    #     for c in cycle_ids:
    #         maint_request_obj.search([('equipment_id', '=', self.id), ('request_date', '=', c.date), ('stage_id.done', '=', False)]).unlink()
    #     for cycle in cycle_ids:
    #         cycle.unlink()

    def delete_cycle_maint_plan(self, year):
        cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
        maint_request_obj = self.env['maintenance.request']
        first_incident_plan_id = self.env['turei_maintenance.incident_plan'].search([('year_char', '=', str(year))],
                                                                                    order='date_start asc', limit=1)
        one_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', self.id), ('year_char', '=', str(year)),
                                                 ('date', '>', first_incident_plan_id.date_end)], order='date asc',
                                                limit=1)
        # cycle_ids = self.cycle_maintenance_plan_ids.search([('equipment_id', '=', self.id), ('year_char', '=', str(year)), ('id', '!=', one_cycle.id)])
        cycle_ids = self.cycle_maintenance_plan_ids.search(
            [('equipment_id', '=', self.id), ('year_char', '=', str(year))])
        for c in cycle_ids:
            maint_request_obj.search(
                [('equipment_id', '=', self.id), ('request_date', '=', c.date), ('stage_id.done', '=', False)]).unlink()
        for cycle in cycle_ids:
            if cycle.stage_id.done == False:
                cycle.unlink()

    def plan_mtto(self, year, clean_request=False):
        today = datetime.today().date()
        date_end = today.replace(year=year, month=12, day=31)
        cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
        if self.config_maintenance:
            if len(cycle_maint_plan_obj.search([('equipment_id', '=', self.id), ('cycle', '=', self.config_cycle.id),
                                                ('date', '=', self.config_date), ('year_char', '=', str(year))])) == 0:
                cycle_maint_plan_obj.create({'equipment_id': self.id, 'cycle': self.config_cycle.id,
                                             'date': self.config_date, 'year_char': str(year)})
        else:
            if clean_request:
                self.delete_cycle_maint_plan(year)
            cond = True
            while cond:
                ultim_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', self.id)], order='date desc', limit=1)
                if ultim_cycle and ultim_cycle.date:
                    day = (self.cycle_time / len(self.cycle_maintenance_ids)) / self.work_time
                    date_mant = self.next_date(datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date(), day)
                    day_start_maint = int(self.category_id.day_start_maintenance)
                    if day_start_maint > date_mant.weekday():
                        days = day_start_maint - date_mant.weekday()
                        date_mant = self.new_day_mant(date_mant, days)
                    if date_mant <= date_end:
                        cycle_maint_plan_obj.create(
                            {'equipment_id': self.id, 'cycle': self.get_cycle_maintenance_id(ultim_cycle.cycle.cycle),
                             'date': date_mant})
                    else:
                        cond = False
                else:
                    cond = False
            self._cron_generate_requests()

    def date_time_to_utc(self, time, date_time):
        hour = float(str(time).split('.')[0])
        float_min = (time - hour) * 100
        date = date_time.replace(hour=int(str(time).split('.')[0]), minute=int((float_min * 60) / 100))
        tz = pytz.timezone(self._context.get('tz') or 'UTC')
        date = tz.localize(fields.Datetime.from_string(fields.Datetime.to_string(date)))
        date = date.astimezone(pytz.UTC)
        return fields.Datetime.to_string(date)

    def _create_new_request(self, date, cycle):
        self.ensure_one()
        schedule_date = datetime.strptime(date, '%Y-%m-%d')

        self.env['maintenance.request'].create({
            'name': _('%s - %s') % (self.code, cycle.cycle),
            'request_date': self.date_time_to_utc(self.start_time, schedule_date),
            'schedule_date': self.date_time_to_utc(self.start_time, schedule_date),
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'technician_user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'cycle_id': cycle.id
        })

    @api.model
    def _cron_generate_requests(self):
        year = str(datetime.today().date().year)
        for equip in self.search([]):
            for equipment in equip.cycle_maintenance_plan_ids.search(
                    [('year_char', '=', year), ('equipment_id', '=', equip.id)]):
                next_requests = self.env['maintenance.request'].search([
                    ('equipment_id', '=', equip.id),
                    ('maintenance_type', '=', 'preventive'),
                    ('request_date', '=', equipment.date)])
                if not next_requests:
                    equip._create_new_request(equipment.date, equipment.cycle)

    def delete_cycle_maintenance_plan_ids(self, date, cycle):
        for c in self.cycle_maintenance_plan_ids:
            if c.cycle.id == cycle and c.date == date and c.stage_id.done == False:
                c.unlink(False)


class CycleMaintenance(models.Model):
    _name = "turei_maintenance.cycle_maintenance"
    _rec_name = 'cycle'

    cycle = fields.Char(string='Código', required=True)
    time = fields.Integer('Tiempo entre ciclos(Horas)')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
                                   ondelete='cascade')
    duration = fields.Integer('Duración(Horas)')
    volume = fields.Html('Volumen de Trabajo')


class CycleMaintenancePlan(models.Model):
    _name = "turei_maintenance.cycle_maintenance_plan"
    _rec_name = 'cycle'
    _order = 'date asc'

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
                                   ondelete='cascade')
    cycle = fields.Many2one('turei_maintenance.cycle_maintenance', string='Ciclo',
                            domain="[('equipment_id', '=', equipment_id)]")

    date = fields.Date('Fecha Inicio')
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)

    request_maintenance_id = fields.Many2one('maintenance.request', string='Request Maintenance')

    @api.model
    def _default_stage(self):
        return self.env['maintenance.stage'].search([], limit=1)

    stage_id = fields.Many2one('maintenance.stage', string='Stage', default=_default_stage)

    @api.multi
    @api.depends('date')
    def _compute_year_char(self):
        for c_model in self:
            if c_model.date:
                date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
                c_model.year_char = str(date.year)

    @api.model
    def create(self, vals):
        res = super(CycleMaintenancePlan, self).create(vals)
        res.equipment_id._create_new_request(res.date, res.cycle)
        return res

    def write(self, vals, not_update_request=False):
        if not_update_request == False:
            request_id = self.env['maintenance.request'].search([('equipment_id', '=', self.equipment_id.id),
                                                                 ('cycle_id', '=', self.cycle.id),
                                                                 ('year_char', '=', self.year_char),
                                                                 ('request_date', '=', self.date)
                                                                 ])

            if request_id and vals.get('date') is not None:
                request_id.write({'schedule_date': vals['date'],
                                  'request_date': vals['date']}, no_update_plan=True)

        res = super(CycleMaintenancePlan, self).write(vals)
        return res

    @api.multi
    def unlink(self, delete_maintenance=True):
        for rec in self:
            if rec.stage_id.done:
                raise ValidationError(_('Error! No se pueden eliminar peticiones con Estado Reparada'))
            elif delete_maintenance:
                rec.env['maintenance.request'].search([('equipment_id', '=', rec.equipment_id.id),
                                                       ('cycle_id', '=', rec.cycle.id),
                                                       ('request_date', '=', rec.date),
                                                       ('stage_id.done', '=', False)
                                                       ]).unlink(delete_plan=False)
        return super(CycleMaintenancePlan, self).unlink()


class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    name = fields.Char('Nombre de Taller', required=True, translate=True)
    template_data = fields.Binary("Estudio de Lubricación", track_visibility='always')
    filename = fields.Char('File Name')
    day_start_maintenance = fields.Selection([('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'),
                                              ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'),
                                              ('6', 'Domingo')], 'Inicia el mantenimiento')
    is_secundary = fields.Boolean(string="Es Secundario?")


class MaintenanceTeam(models.Model):
    _inherit = "maintenance.team"

    member_ids = fields.One2many('turei_maintenance.members.team', inverse_name='member_team_id', string='Miembros...')


class MembersTeam(models.Model):
    _name = "turei_maintenance.members.team"

    member_id = fields.Many2one('hr.employee', string='Miembro')
    responsible = fields.Boolean('¿Es el Jefe de Brigada?')
    member_team_id = fields.Many2one(comodel_name="maintenance.team", string="Documento",
                                     required=False)


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    _order = "request_date asc"

    cycle_id = fields.Many2one('turei_maintenance.cycle_maintenance', string='Ciclo')
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)
    period_id = fields.Many2one('l10n_cu_period.period', string='Period Monthly', compute="_compute_period", store=True)
    line_id = fields.Many2one('turei_maintenance.line', related='equipment_id.line_id', store=True)
    sync = fields.Boolean(string='Sync', default=False)
    push_description = fields.Text(string='Push Description', readonly=True)
    request_date_first = fields.Date(string='Request Date First')
    count_pushes = fields.Integer(string='Count Pushes', default=0)
    work_order_ids = fields.One2many('turei_maintenance.work_order', inverse_name="maintenance_request_id",
                                     string="Órdenes de trabajo", readonly=True)
    work_order_id = fields.Many2one('turei_maintenance.work_order', string="Orden de trabajo", compute="_compute_work_order")

    # @api.multi
    # @api.depends('work_order_ids', 'work_order_id')
    # def _change_state_by_order(self):
    #     stage_id = self.env['maintenance.stage'].search([('name', '=', "En proceso")])
    #     print("_change_state_by_order")
    #     for rec in self:
    #         print(rec.stage_id.name)
    #         print(rec.work_order_ids.ids)
    #         print(rec.work_order_id)
    #         if rec.stage_id.name == "Nueva solicitud" and (len(rec.work_order_ids.ids) > 0 or rec.work_order_id):
    #             rec.stage_id = stage_id.id

    @api.multi
    @api.depends('work_order_ids')
    def _compute_work_order(self):
        for rec in self:
            if len(rec.work_order_ids.ids) > 1:
                raise ValidationError(_("No pueden existir varias ordenes de trabajo (%s) para una solicitud (%s)!") %(rec.work_order_ids.ids, rec.id))
            if rec.work_order_ids:
                rec.work_order_id = rec.work_order_ids[0]

    @api.multi
    @api.depends('request_date')
    def _compute_year_char(self):
        for c_model in self:
            if c_model.request_date:
                date = fields.datetime.strptime(c_model.request_date, DEFAULT_SERVER_DATE_FORMAT)
                c_model.year_char = str(date.year)

    @api.multi
    @api.depends('request_date')
    def _compute_period(self):
        for c_model in self:
            if c_model.request_date:
                date = fields.datetime.strptime(c_model.request_date, DEFAULT_SERVER_DATE_FORMAT)
                period_id = self.env['l10n_cu_period.period'].search([('date_start', '<=', date),
                                                                      ('date_stop', '>=', date),
                                                                      ('annual', '=', False)])
                c_model.period_id = period_id

    @api.multi
    def unlink(self, delete_plan=True):
        for rec in self:
            if delete_plan:
                self.env['turei_maintenance.cycle_maintenance_plan'].search([
                    ('equipment_id', '=', rec.equipment_id.id),
                    ('cycle', '=', rec.cycle_id.id),
                    ('date', '=', rec.request_date),
                    ('year_char', '=', rec.year_char)
                ]).unlink(delete_maintenance=False)
        return super(MaintenanceRequest, self).unlink()

    def write(self, vals, no_update_plan=False):
        if vals.get('stage_id') and no_update_plan == False:
            cycle_plan_id = self.env['turei_maintenance.cycle_maintenance_plan']. \
                search([('equipment_id', '=', self.equipment_id.id),
                        ('cycle', '=', self.cycle_id.id),
                        ('date', '=', self.request_date),
                        ('year_char', '=', self.year_char)], limit=1)

            cycle_plan_id.write({
                'stage_id': vals.get('stage_id')
            }, not_update_request=True)

        elif vals.get('request_date') and no_update_plan == False:
            cycle_plan_id = self.env['turei_maintenance.cycle_maintenance_plan']. \
                search([('equipment_id', '=', self.equipment_id.id),
                        ('cycle', '=', self.cycle_id.id),
                        ('date', '=', self.request_date),
                        ('year_char', '=', self.year_char)], limit=1)

            cycle_plan_id.write({
                'date': vals.get('request_date')
            }, not_update_request=True)

        return super(MaintenanceRequest, self).write(vals)

    _sql_constraints = [
        ('equipment_cycle_request_date_uniq',
         'UNIQUE (equipment_id,cycle_id,request_date)',
         'The request maintenance has unique!!')]


class MaintenancePushPlan(models.Model):
    _name = "turei_maintenance.push_plan"
    _rec_name = 'push_name'

    date_execute = fields.Date(string='Date executed Push')
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')
    push_name = fields.Char(string='Push Name', compute='_get_push_name')
    date_start = fields.Date(string='Date Start')
    date_stop = fields.Date(string='Date End')
    push_description = fields.Text(string='Push Description', readonly=True)
    name = fields.Char(string='Taller', readonly=True)

    def _get_push_name(self):
        for rec in self:
            rec.push_name = rec.name + '/' + rec.date_execute
