# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_evaluator = fields.Boolean(string='Is Evaluator')
    evaluator_id = fields.Many2one('hr.employee',string='Evaluator')




