# -*- coding: utf-8 -*-
from datetime import datetime

import pkg_resources

from odoo import models, fields, api, tools
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class ReportWzd(models.TransientModel):
    _name = 'l10n_cu_hlg_uforce.report_wzd'

    def get_parent_degree_domain(self):
        parents = []
        for d in self.env['l10n_cu_hlg_uforce.degree'].search([]):
            if d.parent_id.id and d.parent_id.id not in parents:
                parents.append(d.parent_id.id)
        return "[('id', 'in', " + str(parents) + ")]"

    def get_period_domain(self):
        periods = []
        for d in self.env['l10n_cu_hlg_uforce.graduates_demand'].search([]):
            if d.period_id.id and d.period_id.id not in periods:
                periods.append(d.period_id.id)
        return "[('id', 'in', " + str(periods) + ")]"

    def get_degree_domain(self):
        degrees = []
        for d in self.env['l10n_cu_hlg_uforce.graduates_demand'].search([]):
            if d.degree_id.id and d.degree_id.id not in degrees:
                degrees.append(d.degree_id.id)
        return "[('id', 'in', " + str(degrees) + ")]"

    reports = fields.Selection([('degree', 'Degree'), ('employee', 'Employees'), ('hire_drop', 'Hired Drop'),
                                ('demand', 'Graduates demand'), ('existences','Existences')], string='Reports', default='degree')

    degree_filter = fields.Selection([('all', 'All'), ('branch', 'Branch Science'), ('specialty', 'Specialty Family'),
                                      ('parent', 'Degree Parent')], string='Filter by', default='all')
    demand_filter = fields.Selection([('year', 'Year'), ('degree', 'Degree')], string='Filter by', default='year')
    employee_filter = fields.Selection([('occupational', 'Occupational Category'), ('age_range', 'Age Range')],
                                       string='Filter by', default='occupational')
    hire_drop_filter = fields.Selection([('age_range', 'Age Range'), ('gender', 'Gender'), ('motive', 'Motive'), ('cause_degree', 'Cause and Degree')],
                                        string='Filter by', default='age_range')
    existences_filter = fields.Selection([('age_range_degree', 'Existences by degree and age range')], string='Filter by', default='age_range_degree')

    branch_science_id = fields.Many2one('l10n_cu_hlg_uforce.branch_science', string='Branch Science')
    specialty_family_id = fields.Many2one('l10n_cu_hlg_uforce.specialty_family', string='Specialty Family')
    parent_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Parent', domain=get_parent_degree_domain)
    degree_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Degree', domain=get_degree_domain)
    period_id = fields.Many2one('l10n_cu_period.period', string='Year', domain=get_period_domain)
    occupational_id = fields.Many2one('l10n_cu_hlg_hr.occupational_category', string='Occupational Category')
    age_range_employee_id = fields.Many2one('l10n_cu_hlg_uforce.age_range', string='Age Range')
    age_range_hire_drop_id = fields.Many2one('l10n_cu_hlg_uforce.age_range', string='Age Range')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    motive_id = fields.Many2one('hr_contract.supplement_motive', string='Motive')
    hire_drop_year = fields.Date(string='Date')

    @api.multi
    def report_print(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        degree_obj = self.env['l10n_cu_hlg_uforce.degree']
        employee_obj = self.env['hr.employee']
        datas = {}

        # path = pkg_resources.resource_filename(
        #     "odoo.addons.l10n_cu_hlg_uforce",
        #     "static/src/img/dummy_logo.png",
        # )
        # datas['replace_logo'] = {'src': 'path', 'data': path}

        if self.reports == 'degree':
            list_degree = []
            if self.degree_filter == 'all':
                datas['report_type'] = _('Degree List')
                degrees = degree_obj.search([])
            elif self.degree_filter == 'branch' and self.branch_science_id:
                datas['report_type'] = _('Degree list by Science branch: ') + self.branch_science_id.name
                degrees = degree_obj.search([('branch_science_id', '=', self.branch_science_id.id)])
            elif self.degree_filter == 'specialty' and self.specialty_family_id:
                datas['report_type'] = _('Degree list by family of specialities : ') + self.specialty_family_id.name
                degrees = degree_obj.search([('specialty_family_id', '=', self.specialty_family_id.id)])
            else:
                datas['report_type'] = _('Degree list by parent degree: ') + self.parent_id.name
                degrees = degree_obj.search([('parent_id', '=', int(self.parent_id.id))])

            for degree in degrees:
                data_degree = {'code': degree.code, 'name': degree.name,
                               'level': degree.degree_level_id.name if degree.degree_level_id.id else '-'}
                list_degree.append(data_degree)

            datas['list_degree'] = list_degree
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_uforce.print_by_wzd_degree_report',
                'datas': datas,
            }

        if self.reports == 'demand':
            if self.demand_filter == 'year':
                datas['report_type'] = _('Graduates demand of year: ') + self.period_id.name
                demands = self.env['l10n_cu_hlg_uforce.graduates_demand'].search(
                    [('period_id', '=', self.period_id.id)]
                )
                if len(demands) == 0:
                    raise ValidationError(_('There is not graduates demand for this year!'))

                periods = []
                for dl in demands[0].line_ids:
                    periods.append({'name': dl.period_id.name})
                datas['periods'] = periods

                dict_demands = {}
                list_entities = []
                for d in demands:
                    if d.entity_id.name not in dict_demands:
                        list_entities.append(d.entity_id.name)
                        years = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name] = {
                            d.degree_id.degree_level_id.name: {
                                'degrees': {
                                    d.degree_id.name: {
                                        'years': years,
                                        'total': total
                                    }
                                },
                                'years': years,
                                'total': total,
                                'list_degrees': [d.degree_id.name]
                            },
                            'years': years,
                            'total': total,
                            'list_levels': [d.degree_id.degree_level_id.name]
                        }
                    elif d.degree_id.degree_level_id.name not in dict_demands[d.entity_id.name]:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name] = {
                            'degrees': {
                                d.degree_id.name: {
                                    'years': years_level,
                                    'total': total
                                }
                            },
                            'years': years_level,
                            'total': total,
                            'list_degrees': [d.degree_id.name]
                        }
                        dict_demands[d.entity_id.name]['list_levels'].append(d.degree_id.degree_level_id.name)
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total
                    elif d.degree_id.name not in dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['degrees']:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years']
                        years_degree = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] += dl.quantity
                            years_degree[dl.period_id.name] = dl.quantity
                            total += dl.quantity

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['degrees'][d.degree_id.name] = {
                            'years': years_degree,
                            'total': total
                        }
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['list_degrees'].append(d.degree_id.name)
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years'] = years_level
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['total'] += total
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total

                datas['list_entities'] = list_entities
                datas['dict_demands'] = dict_demands

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.print_demand_year_report',
                    'datas': datas,
                }
            if self.demand_filter == 'degree':
                datas['report_type'] = _('Graduates demand of degree: ') + self.degree_id.name
                demands = self.env['l10n_cu_hlg_uforce.graduates_demand'].search(
                    [('degree_id', '=', self.degree_id.id)]
                )
                if len(demands) == 0:
                    raise ValidationError(_('There is not graduates demand for this degree!'))

                periods = []
                list_periods = []
                for d in demands:
                    for dl in d.line_ids:
                        if dl.period_id.id not in list_periods:
                            list_periods.append(dl.period_id.id)
                            periods.append({'name': dl.period_id.name})
                datas['periods'] = periods

                dict_demands = {}
                list_entities = []
                for d in demands:
                    if d.entity_id.name not in dict_demands:
                        list_entities.append(d.entity_id.name)
                        years = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years:
                                years[p['name']] = 0

                        dict_demands[d.entity_id.name] = {
                            d.degree_id.degree_level_id.name: {
                                'periods': {
                                    d.period_id.name: {
                                        'years': years,
                                        'total': total
                                    }
                                },
                                'years': years,
                                'total': total,
                                'list_periods': [d.period_id.name]
                            },
                            'years': years,
                            'total': total,
                            'list_levels': [d.degree_id.degree_level_id.name]
                        }
                    elif d.degree_id.degree_level_id.name not in dict_demands[d.entity_id.name]:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years_level:
                                years_level[p['name']] = 0

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name] = {
                            'periods': {
                                d.period_id.name: {
                                    'years': years_level,
                                    'total': total
                                }
                            },
                            'years': years_level,
                            'total': total,
                            'list_degrees': [d.period_id.name]
                        }
                        dict_demands[d.entity_id.name]['list_levels'].append(d.degree_id.degree_level_id.name)
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total
                    elif d.period_id.name not in dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['periods']:
                        years = dict_demands[d.entity_id.name]['years']
                        years_level = dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years']
                        years_degree = {}
                        total = 0
                        for dl in d.line_ids:
                            years[dl.period_id.name] += dl.quantity
                            years_level[dl.period_id.name] += dl.quantity
                            years_degree[dl.period_id.name] = dl.quantity
                            total += dl.quantity
                        for p in periods:
                            if p['name'] not in years_degree:
                                years_degree[p['name']] = 0

                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['periods'][d.period_id.name] = {
                            'years': years_degree,
                            'total': total
                        }
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['list_periods'].append(d.period_id.name)
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['years'] = years_level
                        dict_demands[d.entity_id.name][d.degree_id.degree_level_id.name]['total'] += total
                        dict_demands[d.entity_id.name]['years'] = years
                        dict_demands[d.entity_id.name]['total'] += total

                datas['list_entities'] = list_entities
                datas['dict_demands'] = dict_demands

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.print_demand_degree_report',
                    'datas': datas,
                }

        if self.reports == 'employee':
            list_employee = []
            if self.employee_filter == 'occupational':
                employees = employee_obj.search([('occupational_category_id', '=', int(self.occupational_id.id))])
                dict_categories = {
                    'C': _('Directive'),
                    'A': _('Administrative'),
                    'T': _('Technician'),
                    'S': _('Service'),
                    'O': _('Workman'),
                    'E': _('Student')
                }
                if self.occupational_id.name in dict_categories:
                    category = dict_categories[self.occupational_id.name]
                else:
                    category = self.occupational_id.name
                datas['report'] = _('List of employees that has the %s category') % category

                for employee in employees:
                    data_employee = {'identification_id': employee.identification_id, 'name': employee.name,
                                     'degree': employee.degree_id.name if employee.degree_id.id else '-'}
                    list_employee.append(data_employee)

                datas['list_employee'] = list_employee

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.employee_report',
                    'datas': datas,
                }
            elif self.employee_filter == 'age_range':
                employees = employee_obj.search([('age_range_id', '=', self.age_range_employee_id.id)])
                datas['report'] = _('List of employees in the %s age range') % self.age_range_employee_id.name

                for employee in employees:
                    data_employee = {'identification_id': employee.identification_id, 'name': employee.name,
                                     'degree': employee.degree_id.name if employee.degree_id.id else '-'}
                    list_employee.append(data_employee)

                datas['list_employee'] = list_employee

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.employee_report',
                    'datas': datas,
                }

        if self.reports == 'hire_drop':
            hire_drop_obj = self.env['l10n_cu_hlg_uforce.hire_drop_record']
            list_hire_drop = []

            if self.hire_drop_filter == 'cause_degree':
                year = str(self.hire_drop_year).split("-")[0]
                start_date = "{}-01-01".format(year)
                end_date= "{}-12-31".format(year)
                sql_query = """SELECT motive_id, hr_contract_supplement_motive.name, l10n_cu_hlg_uforce_degree.name, count(hr_employee.id)
                    FROM hr_employee inner join l10n_cu_hlg_uforce_hire_drop_record on hr_employee.id = employee_id 
                    inner join hr_contract_supplement_motive on hr_contract_supplement_motive.id=motive_id inner join l10n_cu_hlg_uforce_degree 
                    on degree_id=l10n_cu_hlg_uforce_degree.id where record_type='drop' and record_date >= '{}' and record_date <= '{}' GROUP BY motive_id, hr_contract_supplement_motive.name, l10n_cu_hlg_uforce_degree.name 
                    ORDER BY motive_id;""".format(start_date, end_date)
                datas['report'] = _("Reporte Fluctuación por Causales y Carreras {}").format(year)

                self.env.cr.execute(sql_query)
                drop_cause_degree = self.env.cr.fetchall()

                list_degree = []
                cause_list = []
                query_len = len(drop_cause_degree)
                aux_id_cause,aux_cause, subtotal = drop_cause_degree[0][0],drop_cause_degree[0][1], drop_cause_degree[0][3]
                list_degree.append({
                    'degree': drop_cause_degree[0][2],
                    'total_degree': drop_cause_degree[0][3],
                })
                total = int(subtotal)
                for i in range(1, query_len):
                    if not drop_cause_degree[i][0] == aux_id_cause:
                        cause_list.append({
                            'cause':aux_cause,
                            'total':total,
                            'list_degree': list_degree,
                        })
                        aux_id_cause, aux_cause, subtotal = drop_cause_degree[i][0], drop_cause_degree[i][1], \
                                                            drop_cause_degree[i][3]
                        total = int(subtotal)
                        list_degree = []
                        list_degree.append({
                            'degree': drop_cause_degree[i][2],
                            'total_degree': drop_cause_degree[i][3],
                        })
                    else:
                        total += int(drop_cause_degree[i][3])
                        list_degree.append({
                            'degree': drop_cause_degree[i][2],
                            'total_degree': drop_cause_degree[i][3],
                        })

                cause_list.append({
                    'cause': aux_cause,
                    'total': total,
                    'list_degree': list_degree,
                })

                sum_total = 0
                for cause in cause_list:
                    sum_total += cause['total']

                cause_list.append({
                    'cause' : "Total",
                    'total' : sum_total,
                    'list_degree' : [],
                })

                datas['cause_list'] = cause_list

                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.hire_drop_degree_cause_report',
                    'datas': datas,
                }

            if self.hire_drop_filter == 'age_range':
                datas['report'] = _('Employee hire and drop by %s age range') % self.age_range_hire_drop_id.name

                for hd in hire_drop_obj.search([]):
                    if hd.employee_id.age_range_id.id == self.age_range_hire_drop_id.id:
                        hire_drop_data = {
                            'employee': hd.employee_id.name,
                            'ci': hd.employee_id.identification_id,
                            'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                            'type': dict(self.env['l10n_cu_hlg_uforce.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                            'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                            'motive': hd.motive_id.name
                        }
                        list_hire_drop.append(hire_drop_data)

            if self.hire_drop_filter == 'gender':
                datas['report'] = _('Employee hire and drop by %s gender') % self.gender

                for hd in hire_drop_obj.search([]):
                    if hd.employee_id.gender == self.gender:
                        hire_drop_data = {
                            'employee': hd.employee_id.name,
                            'ci': hd.employee_id.identification_id,
                            'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                            'type': dict(self.env['l10n_cu_hlg_uforce.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                            'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                            'motive': hd.motive_id.name
                        }
                        list_hire_drop.append(hire_drop_data)

            if self.hire_drop_filter == 'motive':
                datas['report'] = _('Employee hire and drop by %s motive') % self.motive_id.name

                for hd in hire_drop_obj.search([('motive_id', '=', self.motive_id.id)]):
                    hire_drop_data = {
                        'employee': hd.employee_id.name,
                        'ci': hd.employee_id.identification_id,
                        'date': datetime.strptime(hd.record_date, "%Y-%m-%d").strftime("%d-%m-%Y"),
                        'type': dict(self.env['l10n_cu_hlg_uforce.hire_drop_record'].fields_get(allfields=['record_type'])['record_type']['selection'])[hd.record_type],
                        'department': hd.employee_id.department_id.name if hd.employee_id.department_id.id else '-',
                        'motive': hd.motive_id.name
                    }
                    list_hire_drop.append(hire_drop_data)

            datas['list_hire_drop'] = list_hire_drop
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'l10n_cu_hlg_uforce.hire_drop_report',
                'datas': datas,
            }

        if self.reports == 'existences':

            if self.existences_filter == 'age_range_degree':
                age_ranges = self.env['l10n_cu_hlg_uforce.age_range']
                datas['report'] = _("Existence age range degree report")
                ages_ranges_srt_sql = ''
                age_ranges_name=[]
                for age in age_ranges.search([]):
                    age_ranges_name.append(age.name)
                    aux = """, COUNT(CASE WHEN hr_employee.age_range_id = {} THEN hr_employee.id ELSE NULL END) as "{}" """.format(
                        age.id, age.name)
                    ages_ranges_srt_sql += aux
                # TODO
                exist_degree = """SELECT l10n_cu_hlg_uforce_degree.name,
                count(hr_employee.id) as total {}
                    FROM public.hr_employee inner join l10n_cu_hlg_uforce_degree on hr_employee.degree_id = l10n_cu_hlg_uforce_degree.id
                    where degree_id is not null GROUP BY degree_id, l10n_cu_hlg_uforce_degree.name;""".format(
                    ages_ranges_srt_sql)
                self.env.cr.execute(exist_degree)
                record_existence_degree = self.env.cr.fetchall()
                dict_degree_total= []
                values_list = {}
                sum_total = 0
                total_by_age = {}
                for age in age_ranges_name:
                    total_by_age[age] = 0
                for ii in record_existence_degree:
                    dict_degree_total.append({
                        'degree_name' : ii[0],
                        'total': ii[1],
                    })
                    sum_total += ii[1]
                    k = 2
                    dict_aux = {}
                    for age in age_ranges_name:
                        dict_aux[age] = ii[k]
                        total_by_age[age] += ii[k]
                        k += 1
                    values_list[ii[0]] = dict_aux
                print values_list
                dict_degree_total.append({
                    'degree_name' : "Total",
                    'total': sum_total
                })

                values_list["Total"] = total_by_age

                datas['age_ranges'] = age_ranges_name
                datas['values_list'] = values_list
                datas['dict_degree_total'] = dict_degree_total
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'l10n_cu_hlg_uforce.existences_report',
                    'datas':datas,
                }