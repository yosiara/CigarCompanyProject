# -*- coding: utf-8 -*-


from odoo import models, fields, tools, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError, _logger


class WzdPrintEval(models.TransientModel):
    _name = 'wzd.print_eval'

    choice_eval = fields.Selection([('trimester', 'Evaluación Trimestral'),
                                    ('annual', 'Evaluación Anual')],default='trimester',
                                           string='Evaluación')
    evaluated_id = fields.Many2one('hr.employee', string='Evaluated ID')



    def print_eval(self):
        pass