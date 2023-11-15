# -*- coding: utf-8 -*-


from odoo import models, fields, tools, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class WzdGeneratePlanMtto(models.TransientModel):
    _name = 'wzd.generate.plan.mtto'

    date = datetime.today().date()
    current_year = date.year
    new_year = date.replace(year=current_year + 1).year
    year = fields.Selection(string="Año",
                            selection=[('current', tools.ustr(current_year)), ('new', tools.ustr(new_year))],
                            required=True, default='current')
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')
    clean_request = fields.Boolean(string="Plan definitivo")

    def exist_maintenance_in_current_year(self, equipment_id):
        date = datetime.today().date()
        current_year = date.year
        exist = False
        cycle_maint_plan_count = self.env['turei_maintenance.cycle_maintenance_plan'].search_count(
            [('year_char', '=', str(current_year)), ('id', '=', equipment_id)])

        if cycle_maint_plan_count > 0:
            exist = True

        return exist

    def generate_plan_mtto(self):
        equipment_obj = self.env['maintenance.equipment']
        date = datetime.today().date()
        current_year = date.year
        new_year = date.replace(year=current_year + 1).year

        if self.year == 'current':
            year = current_year
        else:
            year = new_year

        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        if len(incident_plan_obj.search([('year_char', '=', str(year))])) == 0:
            raise ValidationError(_('Error! No hay incidencias registradas para el: %s') % (year))

        # Genera el plan para todos los talleres menos el secundario
        if not self.category_id.is_secundary:
            for equip in equipment_obj.search([('category_id', '=', self.category_id.id), ('is_industrial', '=', True),
                                               ('state', 'not in', ['fuera_servicio', 'baja'])]):
                equip.plan_mtto(year, self.clean_request)
        else:
            if self.clean_request:
                self.clear_request_secundary()
            # A partir de aquí es se genera el plan para el taller secundario
            cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            maint_request_obj = self.env['maintenance.request']

            # fijar el primer mantenimiento para la primera linea para empezar
            last_request = self.env['maintenance.request'].search(
                [('category_id', '=', self.category_id.id), ('year_char', '=', year - 1), ('request_date', '!=', False)],
                order="request_date desc", limit=1)
            # print("last request")
            # first_line = self.env['turei_maintenance.line'].search([('is_start', '=', True), ('is_module', '=', False),
            #                                                         ('is_secundary', '=', True)])
            first_line = self.env['turei_maintenance.line'].search([('sequence', '=', last_request.line_id.sequence+1),
                                                                    ('taller', '=', last_request.line_id.taller.id),
                                                                    ('is_module', '=', last_request.line_id.is_module)])
            first_line_module = self.env['turei_maintenance.line'].search(
                [('is_start', '=', True), ('is_module', '=', True),
                 ('is_secundary', '=', True)])
            # buscar la primera fecha disponible y crear la primera peticion a partir de ahi generar el resto
            first_available_date = self.first_available_date()

            # buscar los equipos de la primera linea para crearle el primer mantenimiento
            first_equipment_ids = equipment_obj.search(
                [('category_id.is_secundary', '=', True), ('is_industrial', '=', True),
                 ('line_id', '=', first_line.id)], order='line_id asc')

            for first_equipment in first_equipment_ids:
                cycle_maint_plan_obj.create(
                    {'equipment_id': first_equipment.id, 'cycle': self.get_next_cycle(first_equipment),
                     'date': self.new_day_mant(first_available_date, year)})

            # fijar el primer modulo
            # first_equipment_modules_ids = equipment_obj.search(
            #     [('category_id.is_secundary', '=', True), ('is_industrial', '=', True),
            #      ('line_id', '=', first_line_module.id)], order='line_id asc')
            #
            # for first_equipment_module in first_equipment_modules_ids:
            #     #todo buscar el ciclo, en este caso el inicial en el one2many cycle_maintenance_ids
            #     cyclem_regs = []
            #     for fm in first_equipment_module.cycle_maintenance_ids:
            #         cyclem_regs.append(fm.cycle)
            #
            #     cyclem_first_id = self.env['turei_maintenance.cycle_maintenance'].search([('cycle','=',cyclem_regs[0])],limit=1)
            #
            #     cycle_maint_plan_obj.create({'equipment_id': first_equipment_module.id, 'cycle': self.get_next_cycle(first_equipment_module),
            #                                  'date': self.new_day_mant(first_available_date + timedelta(days=7), year)})

            for line in equipment_obj.search([('category_id.is_secundary', '=', True), ('is_industrial', '=', True)],
                                             order='line_id asc'):
                if line.config_maintenance:
                    if len(cycle_maint_plan_obj.search(
                            [('equipment_id', '=', line.id), ('cycle', '=', line.config_cycle.id),
                             ('date', '=', line.config_date)])) == 0:
                        cycle_maint_plan_obj.create({'equipment_id': line.id, 'cycle': line.config_cycle.id,
                                                     'date': line.config_date})
                # else:
                #     min_date_line = self.min_date_line(cycle_maint_plan_obj, year)
                #     cycle_id = min_date_line[0]
                #     equip_id = min_date_line[1]
                #     date = min_date_line[2]
                #
                #
                #     if line.id == equip_id:
                #         cycle_ids = line.cycle_maintenance_plan_ids.search([('equipment_id', '=', line.id), ('year_char', '=', str(year)), ('id', '!=', cycle_id)])
                #     else:
                #         cycle_ids = line.cycle_maintenance_plan_ids.search([('equipment_id', '=', line.id), ('year_char', '=', str(year)), ('date', '!=', date)])
                #     for c in cycle_ids:
                #         maint_request_obj.search([('equipment_id', '=', self.id), ('request_date', '=', c.date), ('stage_id.done', '=', False)]).unlink()
                #     for cycle in cycle_ids:
                #         cycle.unlink()

            cond = True
            today = datetime.today().date()
            date_end = today.replace(year=year, month=12, day=31)
            line_obj = self.env['turei_maintenance.line']
            while cond:
                ult_date_line = self.ult_date_line(cycle_maint_plan_obj, year)
                date_ult_mant = ult_date_line[0]
                line_ult_mant = ult_date_line[1]
                cycle_ult_mant = ult_date_line[2]
                new_start_date = self.new_day_mant(date_ult_mant, year)
                if new_start_date <= date_end:
                    domain = []
                    if line_ult_mant.is_module:
                        print('Here')
                        if line_ult_mant.is_end:
                            sequence = line_obj.search([('is_module', '=', False), ('is_start', '=', True)]).sequence
                            is_module = False
                            cycle_change = True
                        else:
                            sequence = line_ult_mant.sequence + 1
                            is_module = True
                            cycle_change = False
                    else:
                        if line_ult_mant.is_end:
                            if cycle_ult_mant == 'M2':
                                sequence = line_obj.search([('is_module', '=', True), ('is_start', '=', True)]).sequence
                                is_module = True
                                cycle_change = True
                            else:
                                sequence = line_obj.search(
                                    [('is_module', '=', False), ('is_start', '=', True)]).sequence
                                is_module = False
                                cycle_change = True

                        else:
                            sequence = line_ult_mant.sequence + 1
                            is_module = False
                            cycle_change = False
                    domain.append(('sequence', '=', sequence))
                    domain.append(('is_module', '=', is_module))
                    next_line = line_obj.search(domain)
                    for equip in equipment_obj.search(
                            [('category_id.is_secundary', '=', True), ('line_id', '=', next_line.id)]):
                        if cycle_change:
                            if cycle_ult_mant == 'M3':
                                cycle_id = equip.get_cycle_maintenance_id('M2')
                            else:
                                cycle_id = equip.get_cycle_maintenance_id(cycle_ult_mant)
                        else:
                            cycle_id = equip.cycle_maintenance_ids.search(
                                [('cycle', '=', cycle_ult_mant), ('equipment_id', '=', equip.id)]).id

                        if not cycle_id:
                            cycle_id = self.get_next_cycle(equip)
                        cycle_maint_plan_obj.create(
                            {'equipment_id': equip.id, 'cycle': cycle_id, 'date': new_start_date,
                             'year_char': str(year)})
                else:
                    cond = False

    def ult_date_line(self, cycle_maint_plan_obj, year):
        today = datetime.today().date()
        date_start = today.replace(year=year, month=1, day=1)

        for line in self.env['maintenance.equipment'].search([('category_id.is_secundary', '=', True)],
                                                             order='line_id asc'):
            ultim_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', line.id)], order='date desc', limit=1)

            # el ultimo ciclo debe ser el de una peticion que tenga el estado reparada
            # ultim_cycle_ids = cycle_maint_plan_obj.search([('equipment_id', '=', line.id)],order = 'date desc')
            # for ultim in ultim_cycle_ids:
            #     maint_request_count = self.env['maintenance.request'].search_count([('equipment_id','=',line.id),
            #                                                                         ('cycle_id','=',ultim.cycle.id),
            #                                                             ('stage_id.done', '=', True),
            #                                                             ('request_date','=',ultim.date)
            #                                                             ])
            #     if maint_request_count > 0:
            #         ultim_cycle = ultim
            #         break

            if ultim_cycle and ultim_cycle.date:
                if datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date() > date_start:
                    date_start = datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date()
                    li = line.line_id
                    cycle = ultim_cycle.cycle.cycle

        # if li == False:
        #     date_start = today.replace(year=year - 1, month=1, day=1)
        #     for line in self.env['maintenance.equipment'].search([('category_id.is_secundary', '=', True)],
        #                                                          order='line_id asc'):
        #         ultim_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', line.id)],order='date desc', limit=1)
        #
        #         # el ultimo ciclo debe ser el de una peticion que tenga el estado reparada
        #         # ultim_cycle_ids = cycle_maint_plan_obj.search([('equipment_id', '=', line.id)], order='date desc')
        #         # for ultim in ultim_cycle_ids:
        #         #     maint_request_count = self.env['maintenance.request'].search_count([('equipment_id', '=', line.id),
        #         #                                                                         (
        #         #                                                                         'cycle_id', '=', ultim.cycle.id),
        #         #                                                                         ('stage_id.done', '=', True),
        #         #                                                                         (
        #         #                                                                         'request_date', '=', ultim.date)
        #         #                                                                         ])
        #         #     if maint_request_count > 0:
        #         #         ultim_cycle = ultim
        #         #         break
        #
        #         if ultim_cycle and ultim_cycle.date:
        #             if datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date() > date_start:
        #                 date_start = datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date()
        #                 li = line.line_id
        #                 cycle = ultim_cycle.cycle.cycle

        return date_start, li, cycle

    def min_date_line(self, cycle_maint_plan_obj, year):
        today = datetime.today().date()
        date_start = today.replace(year=year, month=12, day=31)
        for line in self.env['maintenance.equipment'].search([('category_id.is_secundary', '=', True)],
                                                             order='line_id asc'):
            primer_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', line.id)],
                                                       order='date desc', limit=1)

            if primer_cycle and primer_cycle.date:
                if datetime.strptime(primer_cycle.date, '%Y-%m-%d').date() < date_start:
                    date_start = datetime.strptime(primer_cycle.date, '%Y-%m-%d').date()
                    equip_id = line.id
                    cycle_plan_id = primer_cycle.id

        return cycle_plan_id, equip_id, date_start

    def new_day_mant(self, date_ult_mant, year):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        new_start_date = date_ult_mant + timedelta(days=7)
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
        return new_start_date

    def validate_date(self, date, year):
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

    def first_available_date(self):
        today = datetime.today().date()
        current_year = today.year
        new_year = today.replace(year=current_year + 1).year

        if self.year == 'current':
            year = current_year
        else:
            year = new_year
        first_available_date = today.replace(year=year, month=1, day=31)
        date_start = today.replace(year=year, month=1, day=1)
        date_end = today.replace(year=year, month=12, day=31)

        while date_start <= date_end:
            if self.validate_date(date_start, year) and date_start.weekday() == 1:
                first_available_date = date_start
                break
            date_start += timedelta(days=1)

        return first_available_date

    def clear_request_secundary(self):
        cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
        maint_request_obj = self.env['maintenance.request']
        equipment_obj = self.env['maintenance.equipment']

        equipment_ids = equipment_obj.search([('category_id.is_secundary', '=', True)])
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

    def last_execute_cycle_id(self, equipment_id):
        cycles_ids = [e for e in equipment_id.cycle_maintenance_plan_ids]
        cycles_ids.reverse()
        cycle_last = False
        for cycle in cycles_ids:
            maintenance_execute_count = self.env['maintenance.request'].search_count(
                [('equipment_id', '=', equipment_id.id), ('request_date', '=', cycle.date),
                 ('stage_id.done', '=', True)])
            if maintenance_execute_count > 0:
                cycle_last = cycle.cycle.id

        return cycle_last

    def get_next_cycle(self, equipment_id):
        # buscar configuracion de ciclos
        cycle_id = False
        today = datetime.today().date()
        year_char = str(today.year)

        maintenance_in_year_count = self.env['maintenance.request'].search_count(
            [('equipment_id', '=', equipment_id.id), ('year_char', '=', year_char)])

        if maintenance_in_year_count == 0:
            cycle_maintenance_arr = [c.cycle for c in equipment_id.cycle_maintenance_ids]
            cycle_last = self.last_execute_cycle_id(equipment_id)

            if len(cycle_maintenance_arr) == 1:
                cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                    [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id


            elif len(cycle_maintenance_arr) > 0:
                if cycle_last == False:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id
                # esta en el ultimo debe iniciar por el primero
                elif cycle_last == cycle_maintenance_arr[len(cycle_maintenance_arr) - 1]:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id
                # esta en el primero debe ir al segundo
                elif cycle_last == cycle_maintenance_arr[0]:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[1])], limit=1).id
                # buscar cual le corresponde
                else:
                    for i in range(0, len(cycle_maintenance_arr)):
                        if cycle_maintenance_arr[i] == cycle_last:
                            cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                                [('cycle', '=', cycle_maintenance_arr[i + 1])], limit=1).id

                # si no se encuentra el ciclo poner el primero

            if cycle_id == False and len(cycle_maintenance_arr) > 0:
                cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                    [('cycle', '=', cycle_maintenance_arr[0])],
                    limit=1).id
            elif cycle_id == False and len(cycle_maintenance_arr) == 0:
                cycle_id = False

        else:
            cycle_maintenance_arr = [c.cycle for c in equipment_id.cycle_maintenance_ids]
            cycles_ids = [e.cycle.cycle for e in equipment_id.cycle_maintenance_plan_ids]

            if len(cycle_maintenance_arr) == 1:
                cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                    [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id


            elif len(cycles_ids) > 0 and len(cycle_maintenance_arr) > 0:
                if cycles_ids[len(cycles_ids) - 1] == False:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id
                # esta en el ultimo debe iniciar por el primero
                elif cycles_ids[len(cycles_ids) - 1] == cycle_maintenance_arr[len(cycle_maintenance_arr) - 1]:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[0])], limit=1).id
                # esta en el primero debe ir al segundo
                elif cycles_ids[len(cycles_ids) - 1] == cycle_maintenance_arr[0]:
                    cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                        [('cycle', '=', cycle_maintenance_arr[1])], limit=1).id
                # buscar cual le corresponde
                else:
                    for i in range(0, len(cycle_maintenance_arr)):
                        if cycle_maintenance_arr[i] == cycles_ids[len(cycles_ids) - 1]:
                            cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                                [('cycle', '=', cycle_maintenance_arr[i + 1])], limit=1).id

                # si no se encuentra el ciclo poner el primero

            if cycle_id == False and len(cycle_maintenance_arr) > 0:
                cycle_id = self.env['turei_maintenance.cycle_maintenance'].search(
                    [('cycle', '=', cycle_maintenance_arr[0])],
                    limit=1).id
            elif cycle_id == False and len(cycle_maintenance_arr) == 0:
                cycle_id = False

        return cycle_id
