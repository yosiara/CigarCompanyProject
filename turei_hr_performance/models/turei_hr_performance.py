# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date

from datetime import date,datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class PerformancePeriod(models.Model):
    _name = 'turei_hr_performance.period'
    _description = "Performance Period"

    # COLUMNS--------------------------
    name = fields.Char('Period Name', size=32, required=True)
    annual = fields.Boolean('Annual', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True)
    date_stop = fields.Date('End of Period', required=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('closed', 'Closed')], 'Status', readonly=False,
                             copy=False, default='draft',
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    # END COLUMNS--------------------------
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'The name must be unique per Planification period!'),
    ]

    @api.onchange('date_start', 'annual')
    def _onchange_date_start(self):
        res = {'value': {}}
        if self.annual and self.date_start:
            d1 = date(int(self.date_start[0:4]), int(self.date_start[5:7]), int(self.date_start[-2:]))
            after_year_date = (d1 + relativedelta(years=+1, days=-1)).strftime('%Y-%m-%d')
            res['value'] = {'date_stop': after_year_date}
        else:
            res['value'] = {'date_stop': self.date_stop}
        return res

    @api.one
    def button_reset_draft(self):
        self.state = 'draft'

    @api.one
    def button_open(self):
        self.state = 'open'

    @api.one
    def button_close(self):
        self.state = 'closed'

    @api.one
    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        if self.date_start >= self.date_stop:
            raise ValidationError(_("The stop date of the period must be bigger than the start date!"))

        if self.annual:
            d1 = date(int(self.date_start[0:4]), int(self.date_start[5:7]), int(self.date_start[-2:]))
            after_year_date = (d1 + relativedelta(years=+1, days=-1)).strftime('%Y-%m-%d')
            if self.date_stop != after_year_date:
                raise ValidationError(_("The difference between the start date and stop date must be a year!"))

    def get_open_period(self):
        """ return open period """
        today = datetime.now()
        period_date = (today + relativedelta(days=-5)).strftime('%Y-%m-%d')
        period_id = self.search([('date_start', '<=', period_date),
                                 ('date_stop', '>=', period_date),
                                 ('annual', '=', False),
                                 ('state', '=', 'open')], limit=1)
        return period_id




class IndicatorPerformance(models.Model):
    _name = 'turei_hr_performance.indicator_performance'

    name = fields.Char(string='Name', required=True)
    min_value = fields.Integer(string='Min Value')
    max_value = fields.Integer(string='Max Value')
    period_type = fields.Selection([('monthly', 'Monthly'), ('annual', 'Annual')],
                                   string='Period Type', default='monthly')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Exist one Indicator with this name !'),
    ]


class EvaluationPerformanceLines(models.Model):
    _name = 'turei_hr_performance.evaluation_performance_lines'

    evaluation_performance_id = fields.Many2one('turei_hr_performance.evaluation_performance', string='Evaluation Trimester ID')
    indicator_performance_id = fields.Many2one('turei_hr_performance.indicator_performance', string='Indicator',required=True)
    value = fields.Integer(string='Value', required=True)

    @api.one
    @api.constrains('indicator_performance_id', 'value')
    def _check_value(self):
        if self.value > self.indicator_performance_id.max_value:
            raise ValidationError("At least one value in indicators is major than max. Please check!!")


class EvaluationPerformance(models.Model):
    _name = 'turei_hr_performance.evaluation_performance'
    _rec_name = 'description'


    evaluator_id = fields.Many2one('hr.employee', string='Evaluator', required=True)
    evaluated_id = fields.Many2one('hr.employee', string='Evaluated', required=True)
    job_id = fields.Many2one('hr.job', related='evaluated_id.job_id',string='Job Id', store=True, readonly=True )
    occupational_category_id = fields.Many2one(
        related='evaluated_id.job_id.position_id.salary_group_id.occupational_category_id', string='Occupational Category',
        store=True, readonly=True
    )
    department_id = fields.Many2one('hr.department',related='evaluated_id.department_id',string='Department',  store=True, readonly=True)
    period_id = fields.Many2one('turei_hr_performance.period', string='Period', required=True)
    year_char = fields.Char(string='Year', compute='_get_char', store=True)

    @api.depends('period_id')
    def _get_char(self):
        if self.period_id:
            year_temp = self.period_id.date_start
            year_temp = year_temp.split('-')
            self.year_char = year_temp[0]


    evaluation_performance_lines = fields.One2many('turei_hr_performance.evaluation_performance_lines','evaluation_performance_id',string='Evaluation Lines')

    description = fields.Char(string='Description',compute='_get_description')

    @api.depends('evaluated_id','period_id')
    def _get_description(self):
        if self.evaluated_id and self.period_id:
            self.description = self.evaluated_id.name + '/' + self.period_id.name



    @api.onchange('period_id')
    def load_indicators(self):
        indicators_list = []
        if self.period_id.annual == False:
            indicators_ids = self.env['turei_hr_performance.indicator_performance'].search([('period_type','=','monthly')])

            for ind in indicators_ids:
                indicators_list.append((0, 0,
                                      {'indicator_performance_id': ind.id,
                                       'value': 0
                                       }))
            self.evaluation_performance_lines = indicators_list
        else:
            indicators_ids = self.env['turei_hr_performance.indicator_performance'].search(
                [('period_type', '=', 'annual')])

            for ind in indicators_ids:
                indicators_list.append((0, 0,
                                        {'indicator_performance_id': ind.id,
                                         'value': 0
                                         }))
            self.evaluation_performance_lines = indicators_list