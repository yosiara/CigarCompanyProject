# -*- coding: utf-8 -*-


from odoo import models, fields, tools, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError, _logger


class WzdUpdateRequest(models.TransientModel):
    _name = 'wzd.update_request'

    options = work_type = fields.Selection([('clear-secundary', 'Borrar Peticiones'),
                                            ('update-secundary',
                                             'Actualizar Peticiones del Taller Secundario desde Configuración de Equipos'),
                                            ('update_cycle_plans',
                                             'Actualizar Estado de Peticiones en Configuracion de Equipos'),
                                            ('update_cycles_plan_for_maintenance',
                                             'Actualizar Configuracion de Equipos desde Peticiones'),
                                            ('sync-secundary','Sincronizar Peticiones'),
                                            ('update_maintenance_for_orders',
                                             'Actualizar Estado de Peticiones desde Ordenes de Trabajo Cerradas'),
                                            ('update_maintenance_under_current_year',
                                             'Actualizar Estado de Peticiones Anteriores al Año Actual'),
                                            ('update_maintenance_id_conf',
                                             'Actualizar ID de Peticiones en Configuracion'),
                                            ('push_secundary', 'Correr Plan Secundario a partir de Incidencia'),
                                            ('push_others', 'Correr Plan Otros Talleres a partir de Incidencia'),
                                            ('push_planta', 'Correr Plan Planta de Tabaco Reconstituido'),
                                            ('push_restore_secundary',
                                             'Restaurar Peticiones de Mantenimiento a Fechas Originales antes de correr Plan para Taller Secundario'),
                                            ('push_restore_others',
                                             'Restaurar Peticiones de Mantenimiento a Fechas Originales antes de correr Plan para Otros Talleres'),
                                            ('push_restore_planta',
                                             'Restaurar Peticiones de Mantenimiento a Fechas Originales antes de correr Plan para Planta de Tabaco Reconstituido'),
                                            ],
                                           string='Funcionalidad')

    # to push the plan secundary
    date_start_secundary = fields.Date(string='Date Start')
    date_stop_secundary = fields.Date(string='Date Stop')

    # to push the plan others
    date_start_others = fields.Date(string='Date Start')
    date_stop_others = fields.Date(string='Date Stop')

    # to push the plan planta
    date_start_planta = fields.Date(string='Date Start')
    date_stop_planta = fields.Date(string='Date Stop')

    # description motive
    description_secundary = fields.Text(string='Motive Description')
    description_others = fields.Text(string='Motive Description')
    description_planta = fields.Text(string='Motive Description')

    date = datetime.today().date()
    current_year = date.year
    new_year = date.replace(year=current_year + 1).year

    # year_pushed_secundary = fields.Selection(string="Año",
    #                         selection=[('current', tools.ustr(current_year)), ('new', tools.ustr(new_year))],
    #                         default='current')
    #
    # year_pushed_others = fields.Selection(string="Año",
    #                                          selection=[('current', tools.ustr(current_year)),
    #                                                     ('new', tools.ustr(new_year))],
    #                                          default='current')

    def validate_date(self, date, year, list_maintenance, line_id):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        ban = False
        for i in range(0, 4):
            date_new = date + timedelta(days=i)
            incident_plan_i = incident_plan_obj.search(
                [('year_char', '=', str(year)), ('date_start', '<=', date_new),
                 ('date_end', '>=', date_new)])

            if len(incident_plan_i) > 0:
                ban = True

        # search in list for this date if exist different or same line
        for m in list_maintenance:
            if m['new_date'] == date and m['line_id'] != line_id:
                ban = True
                break

        return ban

    def first_available_date(self, possible_date):
        today = datetime.today().date()
        current_year = today.year
        new_year = today.replace(year=current_year + 1).year

        if possible_date.date().year == current_year:
            year = current_year
        else:
            year = new_year

        first_available_date = possible_date.date()
        date_start = first_available_date
        date_end = today.replace(year=year + 1, month=12, day=31)

        while date_start <= date_end:
            if date_start.weekday() == 1:
                first_available_date = date_start
                break
            date_start += timedelta(days=1)

        return first_available_date

    def first_available_date_sunday(self, possible_date):
        today = datetime.today().date()
        current_year = today.year
        new_year = today.replace(year=current_year + 1).year

        if possible_date.date().year == current_year:
            year = current_year
        else:
            year = new_year

        first_available_date = possible_date.date()
        date_start = first_available_date
        date_end = today.replace(year=year + 1, month=12, day=31)

        while date_start <= date_end:
            if date_start.weekday() == 6:
                first_available_date = date_start
                break
            date_start += timedelta(days=1)

        return first_available_date

    def new_day_mant_dict(self, date_ult_mant, year, list_maintenance, line_id):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        # new_start_date = date_ult_mant + timedelta(days=7)
        new_start_date = date_ult_mant
        # new_end_date = new_start_date + timedelta(days=4)
        while cond:
            # incident_plan_i = incident_plan_obj.search(
            #     [('year_char', '=', str(year)), ('date_start', '<=', new_start_date),
            #      ('date_end', '>=', new_start_date)])
            #
            # if len(incident_plan_i) == 0:
            #     cond = False
            # else:
            #     new_start_date = new_start_date + timedelta(days=7)
            # new_end_date = new_start_date + timedelta(days=4)
            ban = self.validate_date(new_start_date, year, list_maintenance, line_id)

            if not ban:
                cond = False
            else:
                new_start_date = new_start_date + timedelta(days=7)

        return new_start_date

    def new_day_mant(self, date_ult_mant, year, line_id):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        # new_start_date = date_ult_mant + timedelta(days=7)
        new_start_date = date_ult_mant
        # new_end_date = new_start_date + timedelta(days=4)
        while cond:
            # incident_plan_i = incident_plan_obj.search(
            #     [('year_char', '=', str(year)), ('date_start', '<=', new_start_date),
            #      ('date_end', '>=', new_start_date)])
            #
            # if len(incident_plan_i) == 0:
            #     cond = False
            # else:
            #     new_start_date = new_start_date + timedelta(days=7)
            # new_end_date = new_start_date + timedelta(days=4)
            ban = self.validate_date(new_start_date, year)

            if not ban:
                cond = False
            else:
                new_start_date = new_start_date + timedelta(days=7)

            if cond == False:
                maint_line_id = self.env['maintenance.request'].search(
                    [('request_date', '=', new_start_date), ('line_id', '!=', line_id),
                     ('request_date_first', '!=', False)])

                print(maint_line_id)
                if len(maint_line_id) > 0:
                    cond = True

        return new_start_date

    # for others categorys
    def validate_date_others(self, date, year):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        ban = False
        for i in range(0, 4):
            date_new = date + timedelta(days=i)
            incident_plan_i = incident_plan_obj.search(
                [('year_char', '=', str(year)), ('date_start', '<=', date_new),
                 ('date_end', '>=', date_new)])
            if len(incident_plan_i) > 0:
                ban = True

        return ban

    def first_available_date_others(self, possible_date):
        today = datetime.today().date()
        current_year = today.year
        new_year = today.replace(year=current_year + 1).year

        if possible_date.date().year == current_year:
            year = current_year
        else:
            year = new_year

        first_available_date = possible_date.date()
        date_start = first_available_date
        date_end = today.replace(year=year + 1, month=12, day=31)

        while date_start <= date_end:
            if date_start.weekday() == 1:
                first_available_date = date_start
                break
            date_start += timedelta(days=1)

        return first_available_date

    def new_day_mant_others(self, date_mant, day_start_maint):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        while cond:
            incident_plan = incident_plan_obj.search(
                [('year_char', '=', str(date_mant.year)), ('date_start', '<=', date_mant),
                 ('date_end', '>=', date_mant)])
            if date_mant.weekday() not in (5, 6) and len(incident_plan) == 0 and day_start_maint <= date_mant.weekday():
                cond = False
            else:
                date_mant = date_mant + timedelta(days=1)
        return date_mant

    def update_request(self):
        if self.options == 'clear-secundary':
            cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            maint_request_obj = self.env['maintenance.request']
            equipment_obj = self.env['maintenance.equipment']
            equipment_ids = equipment_obj.search([])
            year = datetime.today().date().year
            for equip in equipment_ids:
                # cycle_ids = self.cycle_maintenance_plan_ids.search([('equipment_id', '=', self.id), ('year_char', '=', str(year)), ('id', '!=', one_cycle.id)])
                cycle_ids = equip.cycle_maintenance_plan_ids.search(
                    [('equipment_id', '=', equip.id), ('year_char', '=', str(year))])

                for c in cycle_ids:
                    maint_request_obj.search(
                        [('equipment_id', '=', self.id), ('request_date', '=', c.date),
                         ('stage_id.done', '=', False)]).unlink()
                for cycle in cycle_ids:
                    if cycle.stage_id.done == False:
                        cycle.unlink()

        elif self.options == 'update_maintenance_id_conf':
            cycle_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            maint_obj = self.env['maintenance.request']

            for maint in maint_obj.search([]):
                cycle_id = cycle_obj.search([
                    ('date', '=', maint.request_date),
                    ('year_char', '=', maint.year_char),
                    ('equipment_id', '=', maint.equipment_id.id),
                    ('cycle', '=', maint.cycle_id.id),
                ])
                if len(cycle_id) > 1:
                    cycle_id[0].write({
                        'request_maintenance_id': maint.id,
                    }, not_update_request=True)
                elif len(cycle_id) == 1:
                    cycle_id[0].write({
                        'request_maintenance_id': maint.id,
                    }, not_update_request=True)



        elif self.options == 'update-secundary':
            year = datetime.today().date().year
            maintenance_obj = self.env['maintenance.request']
            cycles_plans = self.env['turei_maintenance.cycle_maintenance_plan'].search(
                [('year_char', '=', str(year))], order='date asc')

            for maint in cycles_plans:
                mt = maintenance_obj.search([
                    ('request_date', '=', maint.date),
                    ('year_char', '=', maint.year_char),
                    ('equipment_id', '=', maint.equipment_id.id)])

                if maint.cycle:
                    mt.write({
                        'cycle_id': maint.cycle.id,
                        'name': maint.equipment_id.code + '-' + maint.cycle.cycle,
                    })

        # not only secundary, all categories
        elif self.options == 'sync-secundary':
            year = datetime.today().date().year
            maintenance_ids = self.env['maintenance.request'].search([('year_char', '=', year)])
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']

            for maint in maintenance_ids:
                cycle_count = cycles_plan_obj.search_count([
                                             ('date','=', maint.request_date),
                                             ('year_char', '=', maint.year_char),
                                             ('equipment_id', '=', maint.equipment_id.id),
                                             ('cycle','=',maint.cycle_id.id)
                                            ])

                if cycle_count == 0:
                    maint.unlink()
                else:
                    maint.write({
                        'sync': True
                    },no_update_plan=True)

            for cycle in cycles_plan_obj.search([('year_char', '=', year)]):
                maintenance_id = self.env['maintenance.request'].search([('year_char', '=', year),
                                                             ('request_date', '=', cycle.date),
                                                             ('equipment_id', '=', cycle.equipment_id.id),
                                                             ('cycle_id','=',cycle.cycle.id)
                                                             ])
                #if duplicate request then erase
                if len(maintenance_id) > 1:
                    for mtto in maintenance_id:
                        mtto.write({ 'sync': False },no_update_plan=True)


        elif self.options == 'update_cycle_plans':
            year = datetime.today().date().year
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']

            for cycle in cycles_plan_obj.search([('year_char', '=', year)]):
                maintenance_id = self.env['maintenance.request'].search([('year_char', '=', year),
                                                                         ('request_date', '=', cycle.date),
                                                                         ('equipment_id', '=', cycle.equipment_id.id),
                                                                         ('cycle_id', '=', cycle.cycle.id)
                                                                         ])

                if maintenance_id.id:
                    cycle.write({
                        'stage_id': maintenance_id.stage_id.id
                    }, no_update_request=True)

        elif self.options == 'update_maintenance_for_orders':
            year = datetime.today().date().year
            orders_obj = self.env['turei_maintenance.work_order']

            for order in orders_obj.search(
                    [('year_char', '=', year), ('state', '=', 'closed'), ('work_type', '=', 'plan_ciclo')]):
                maintenance_id = self.env['maintenance.request'].search([('id', '=', order.maintenance_request_id.id)
                                                                         ])

                if maintenance_id.id and maintenance_id.stage_id.done == False:
                    # set request in repair stage
                    maintenance_id.write({'stage_id': self.env.ref('maintenance.stage_1').id}, no_update_plan=True)

            # update cycle plans
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']

            for cycle in cycles_plan_obj.search([('year_char', '=', year)]):
                maint_id = self.env['maintenance.request'].search([('year_char', '=', year),
                                                                   ('request_date', '=', cycle.date),
                                                                   ('equipment_id', '=', cycle.equipment_id.id),
                                                                   ('cycle_id', '=', cycle.cycle.id)
                                                                   ])

                if maint_id.id:
                    cycle.write({
                        'stage_id': maint_id.stage_id.id
                    }, no_update_request=True)


        elif self.options == 'update_cycles_plan_for_maintenance':
            year = datetime.today().date().year
            year = datetime.today().date().year
            maintenance_ids = self.env['maintenance.request'].search([('year_char', '=', year)])
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']

            for maint in maintenance_ids:
                cycle_plan_id = cycles_plan_obj.search([('year_char', '=', year),
                                                        ('date', '=', maint.request_date),
                                                        ('equipment_id', '=', maint.equipment_id.id),
                                                        ('cycle', '=', maint.cycle_id.id)
                                                        ])

                if cycle_plan_id.id:
                    pass
                else:
                    cycles_plan_obj.create({
                        'date': maint.request_date,
                        'equipment_id': maint.equipment_id.id,
                        'cycle': maint.cycle_id.id,
                        'stage_id': maint.stage_id.id
                    })


        elif self.options == 'push_secundary':
            year = datetime.today().date().year
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            secundary_id = self.env['maintenance.equipment.category'].search([('is_secundary', '=', True)], limit=1)

            # check is exist push with this dates
            push_plan_obj = self.env['turei_maintenance.push_plan']
            push_plan_count = push_plan_obj.search_count([
                ('date_start', '<=', self.date_start_secundary),
                ('date_stop', '>=', self.date_stop_secundary),
                ('category_id.is_secundary', '=', True)])

            if push_plan_count > 0:
                raise ValidationError(
                    _("Exist at least one push with this dates for the category. Please check!! "))



            elif self.date_start_secundary and self.date_stop_secundary and self.date_start_secundary < self.date_stop_secundary:
                # update request_dates
                first_available_date_for_up = datetime.strptime(self.date_stop_secundary, '%Y-%m-%d') - timedelta(
                    days=6)
                next_prev_sunday = self.first_available_date_sunday(first_available_date_for_up)
                count_pushes = self.env['turei_maintenance.push_plan'].search_count(
                    [('category_id', '=', secundary_id.id)])

                maintenance_list = []
                # first put the requests in a dict list to process
                for maint in maintenance_obj.search([('year_char', '=', year),
                                                     ('category_id.is_secundary', '=', True),
                                                     ('request_date', '>=', self.date_start_secundary),
                                                     ], order='request_date asc'):
                    maintenance_list.append(
                        {
                            'id': maint.id,
                            'request_date': maint.request_date,
                            'request_date_first': maint.request_date if maint.request_date_first == False else maint.request_date_first,
                            'new_date': False,
                            'cycle_id': maint.cycle_id.id,
                            'equipment_id': maint.equipment_id.id,
                            'line_id': maint.line_id.id

                        })

                # second process the list request
                first_available_date = datetime.strptime(self.date_stop_secundary, '%Y-%m-%d') + timedelta(days=1)
                next_date = self.first_available_date(first_available_date)

                iter = 0
                for maintenance in maintenance_list:
                    new_day_maintenance = self.new_day_mant_dict(
                        datetime.strptime(maintenance['request_date'], '%Y-%m-%d'), next_date.year, maintenance_list,
                        maintenance['line_id'])
                    maintenance.update({
                        'new_date': new_day_maintenance
                    })
                    print(('%s- Maintenance Line: %s , old date: %s , new date: %s ') % (
                    iter, maintenance['line_id'], maintenance['request_date'], maintenance['new_date']))
                    iter += 1

                # third update request then
                for maintenance in maintenance_list:
                    maint = maintenance_obj.search([('id', '=', maintenance['id'])])

                    cycle_plan_id = cycles_plan_obj.search([('year_char', '=', year),
                                                            ('date', '=', maint.request_date),
                                                            ('equipment_id', '=', maint.equipment_id.id),
                                                            ('cycle', '=', maint.cycle_id.id)
                                                            ])

                    note_line = ''
                    count_pushes = self.env['turei_maintenance.push_plan'].search_count(
                        [('category_id', '=', secundary_id.id)])

                    if count_pushes == 0:
                        maint.write({
                            'request_date_first': maint.request_date
                        }, no_update_plan=True)

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': maintenance['new_date']
                        }, not_update_request=True)

                    if maint.push_description == False:
                        note_line = str(maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + \
                                    maintenance['request_date'] + ' a: ' + maintenance['new_date'].strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_secundary

                        maint.write({
                            'request_date': maintenance['new_date'],
                            'schedule_date': maintenance['new_date'],
                            'push_description': note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)
                    else:
                        note_line = '\n' + str(maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + \
                                    maintenance['request_date'] + ' a: ' + maintenance['new_date'].strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_secundary

                        maint.write({
                            'request_date': maintenance['new_date'],
                            'schedule_date': maintenance['new_date'],
                            'push_description': maint.push_description + note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)

                push_plan = self.env['turei_maintenance.push_plan'].create({
                    'date_execute': fields.datetime.today().date(),
                    'date_start': self.date_start_secundary,
                    'date_stop': self.date_stop_secundary,
                    'category_id': secundary_id.id,
                    'name': 'Secundario',
                    'push_description': self.description_secundary
                })
                return push_plan

            else:
                raise ValidationError(
                    _("Please check and fixed the dates"))


        elif self.options == 'push_others':
            year = datetime.today().date().year
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            categ_ids = self.env['maintenance.equipment.category'].search([('is_secundary', '=', False)])

            # check is exist push with this dates
            push_plan_obj = self.env['turei_maintenance.push_plan']
            push_plan_count = push_plan_obj.search_count([
                ('date_start', '<=', self.date_start_others),
                ('date_stop', '>=', self.date_stop_other),
                ('category_id.is_secundary', '=', False)])

            if push_plan_count > 0:
                raise ValidationError(
                    _("Exist at least one push with this dates for the category. Plesa check!! "))

            if self.date_start_others and self.date_stop_others and self.date_start_others < self.date_stop_others:

                diff_to_push = datetime.strptime(self.date_stop_others, '%Y-%m-%d') - datetime.strptime(
                    self.date_start_others, '%Y-%m-%d')

                count = 1
                for maint in maintenance_obj.search([('year_char', '=', year),
                                                     ('category_id.is_secundary', '=', False),
                                                     ('request_date', '>=', self.date_start_others),
                                                     ('request_date', '<=', self.date_stop_others)
                                                     ]):
                    next_possible_date = datetime.strptime(maint.request_date, '%Y-%m-%d') + timedelta(
                        days=(int(diff_to_push.days) + 1))

                    day_start_maint = maint.equipment_id.category_id.day_start_maintenance
                    new_day_maintenance = self.new_day_mant_others(next_possible_date.date(), int(day_start_maint))

                    # print("%s - Peticion: %s " % (count, maint.name))
                    # print("Fecha Planificada: %s " % (maint.request_date))
                    # print("Fecha al Empujar Plan: %s " % (new_day_maintenance))
                    # print('----------------------')
                    # count += 1
                    cycle_plan_id = cycles_plan_obj.search([('year_char', '=', year),
                                                            ('date', '=', maint.request_date),
                                                            ('equipment_id', '=', maint.equipment_id.id),
                                                            ('cycle', '=', maint.cycle_id.id)
                                                            ])

                    count_pushes = self.env['turei_maintenance.push_plan'].search_count(
                        [('category_id', '=', categ_ids[0].id)])

                    if count_pushes == 0:
                        maint.write({
                            'request_date_first': maint.request_date,
                        }, no_update_plan=True)

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': new_day_maintenance
                        }, not_update_request=True)

                    note_line = ''

                    if maint.push_description == False:
                        note_line = str(
                            maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + maint.request_date + ' a: ' + new_day_maintenance.strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_others

                        maint.write({
                            'request_date': new_day_maintenance,
                            'schedule_date': new_day_maintenance,
                            'push_description': note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)
                    else:
                        note_line = '\n' + str(
                            maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + maint.request_date + ' a: ' + new_day_maintenance.strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_others

                        maint.write({
                            'request_date': new_day_maintenance,
                            'schedule_date': new_day_maintenance,
                            'push_description': maint.push_description + note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)

                push_plan = self.env['turei_maintenance.push_plan'].create({
                    'date_execute': fields.datetime.today().date(),
                    'date_start': self.date_start_others,
                    'date_stop': self.date_stop_others,
                    'category_id': maint.category_id.id,
                    'name': 'Otros Talleres',
                    'push_description': self.description_others
                })
                return push_plan

        elif self.options == 'push_planta':
            year = datetime.today().date().year
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            categ_id_planta = self.env['maintenance.equipment.category'].search(
                [('name', '=', 'PLANTA DE TABACO RECONSTITUIDO')])

            # check is exist push with this dates
            push_plan_obj = self.env['turei_maintenance.push_plan']
            push_plan_count = push_plan_obj.search_count([
                ('date_start', '<=', self.date_start_secundary),
                ('date_stop', '>=', self.date_stop_secundary),
                ('category_id', '=', categ_id_planta.id)])

            if push_plan_count > 0:
                raise ValidationError(
                    _("Exist at least one push with this dates for the category. Plesa check!! "))

            if self.date_start_planta and self.date_stop_planta and self.date_start_planta < self.date_stop_planta:

                diff_to_push = datetime.strptime(self.date_stop_planta, '%Y-%m-%d') - datetime.strptime(
                    self.date_start_planta, '%Y-%m-%d')

                count = 1
                for maint in maintenance_obj.search([('year_char', '=', year),
                                                     ('category_id', '=', categ_id_planta.id),
                                                     ('request_date', '>=', self.date_start_planta),
                                                     ('request_date', '<=', self.date_stop_planta)
                                                     ]):
                    next_possible_date = datetime.strptime(maint.request_date, '%Y-%m-%d') + timedelta(
                        days=(int(diff_to_push.days) + 1))

                    day_start_maint = maint.equipment_id.category_id.day_start_maintenance
                    new_day_maintenance = self.new_day_mant_others(next_possible_date.date(), int(day_start_maint))

                    # print("%s - Peticion: %s " % (count, maint.name))
                    # print("Fecha Planificada: %s " % (maint.request_date))
                    # print("Fecha al Empujar Plan: %s " % (new_day_maintenance))
                    # print('----------------------')
                    # count += 1
                    cycle_plan_id = cycles_plan_obj.search([('year_char', '=', year),
                                                            ('date', '=', maint.request_date),
                                                            ('equipment_id', '=', maint.equipment_id.id),
                                                            ('cycle', '=', maint.cycle_id.id)
                                                            ])

                    count_pushes = self.env['turei_maintenance.push_plan'].search_count(
                        [('category_id', '=', categ_id_planta.id)])

                    if count_pushes == 0:
                        maint.write({
                            'request_date_first': maint.request_date
                        }, no_update_plan=True)

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': new_day_maintenance
                        }, not_update_request=True)

                    note_line = ''

                    if maint.push_description == False:
                        note_line = str(
                            maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + maint.request_date + ' a: ' + new_day_maintenance.strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_planta

                        maint.write({
                            'request_date': new_day_maintenance,
                            'schedule_date': new_day_maintenance,
                            'push_description': note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)
                    else:
                        note_line = '\n' + str(
                            maint.count_pushes + 1) + '- Se corre la fecha planificada desde ' + maint.request_date + ' a: ' + new_day_maintenance.strftime(
                            '%Y-%m-%d') + ' debido a: ' + self.description_planta

                        maint.write({
                            'request_date': new_day_maintenance,
                            'schedule_date': new_day_maintenance,
                            'push_description': maint.push_description + note_line,
                            'count_pushes': maint.count_pushes + 1
                        }, no_update_plan=True)

                push_plan = self.env['turei_maintenance.push_plan'].create({
                    'date_execute': fields.datetime.today().date(),
                    'date_start': self.date_start_planta,
                    'date_stop': self.date_stop_planta,
                    'category_id': categ_id_planta.id,
                    'name': 'Planta de Tabaco Reconstituido',
                    'push_description': self.description_planta
                })
                return push_plan

        elif self.options == 'push_restore_others':
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            push_plan_obj = self.env['turei_maintenance.push_plan'].search([('category_id.is_secundary', '=', False)])

            # first restore current year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                 ('category_id.is_secundary', '=', False),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):

                cycle_plan_id = cycles_plan_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                        ('date', '=', maint.request_date),
                                                        ('equipment_id', '=', maint.equipment_id.id),
                                                        ('cycle', '=', maint.cycle_id.id)
                                                        ])

                if maint.request_date_first != False:
                    original_date = maint.request_date_first

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            # second restore new year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.new_year)),
                                                 ('category_id.is_secundary', '=', False),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):
                cycle_plan_id = cycles_plan_obj.search(
                    [('year_char', '=', tools.ustr(self.new_year)),
                     ('date', '=', maint.request_date),
                     ('equipment_id', '=', maint.equipment_id.id),
                     ('cycle', '=', maint.cycle_id.id)
                     ])

                if maint.request_date_first != False:

                    original_date = maint.request_date_first

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            for push in push_plan_obj:
                push.unlink()


        elif self.options == 'push_restore_secundary':
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            push_plan_obj = self.env['turei_maintenance.push_plan'].search([('category_id.is_secundary', '=', True)])

            # first restore current year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                 ('category_id.is_secundary', '=', True),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):
                cycle_plan_id = cycles_plan_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                        ('date', '=', maint.request_date),
                                                        ('equipment_id', '=', maint.equipment_id.id),
                                                        ('cycle', '=', maint.cycle_id.id)
                                                        ])

                if maint.request_date_first != False:
                    original_date = maint.request_date_first
                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            # second restore next year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.new_year)),
                                                 ('category_id.is_secundary', '=', True),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):

                cycle_plan_id = cycles_plan_obj.search([('year_char', '=', tools.ustr(self.new_year)),
                                                        ('date', '=', maint.request_date),
                                                        ('equipment_id', '=', maint.equipment_id.id),
                                                        ('cycle', '=', maint.cycle_id.id)
                                                        ])
                if maint.request_date_first != False:
                    original_date = maint.request_date_first
                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            for push in push_plan_obj:
                push.unlink()

        elif self.options == 'push_restore_planta':
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            categ_id_planta = self.env['maintenance.equipment.category'].search(
                [('name', '=', 'PLANTA DE TABACO RECONSTITUIDO')])

            push_plan_obj = self.env['turei_maintenance.push_plan'].search([('category_id', '=', categ_id_planta.id)])

            # first restore current year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                 ('category_id', '=', categ_id_planta.id),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):

                cycle_plan_id = cycles_plan_obj.search([('year_char', '=', tools.ustr(self.current_year)),
                                                        ('date', '=', maint.request_date),
                                                        ('equipment_id', '=', maint.equipment_id.id),
                                                        ('cycle', '=', maint.cycle_id.id)
                                                        ])

                if maint.request_date_first != False:
                    original_date = maint.request_date_first

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            # second restore new year
            for maint in maintenance_obj.search([('year_char', '=', tools.ustr(self.new_year)),
                                                 ('category_id', '=', categ_id_planta.id),
                                                 ('stage_id.done', '=', False),
                                                 ('request_date_first', '!=', False)
                                                 ]):
                cycle_plan_id = cycles_plan_obj.search(
                    [('year_char', '=', tools.ustr(self.new_year)),
                     ('date', '=', maint.request_date),
                     ('equipment_id', '=', maint.equipment_id.id),
                     ('cycle', '=', maint.cycle_id.id)
                     ])

                if maint.request_date_first != False:

                    original_date = maint.request_date_first

                    if cycle_plan_id.id:
                        cycle_plan_id.write({
                            'date': original_date
                        }, not_update_request=True)

                    maint.write({
                        'request_date': original_date,
                        'schedule_date': original_date,
                        'push_description': False,
                        'count_pushes': 0
                    }, no_update_plan=True)

            for push in push_plan_obj:
                push.unlink()

        # todo wizard to close request under current year
        elif self.options == 'update_maintenance_under_current_year':
            maintenance_obj = self.env['maintenance.request']
            cycles_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            # first_date current year
            today = datetime.today().date()
            first_date = today.replace(year=self.current_year, month=1, day=1)

            for maint in maintenance_obj.search([('request_date', '<', first_date),
                                                 ('stage_id.done', '=', False)
                                                 ]):
                maint.write({'stage_id': self.env.ref('maintenance.stage_3').id}, no_update_plan=True)

            for cycle_plan_id in cycles_plan_obj.search([('date', '<', first_date),
                                                         ('stage_id.done', '=', False)
                                                         ]):
                cycle_plan_id.write({'stage_id': self.env.ref('maintenance.stage_3').id}, not_update_request=True)
