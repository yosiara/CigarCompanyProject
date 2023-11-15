from odoo import models, api, fields, _


class DashBoard(models.Model):
    _name = 'maintenance.dashboard'
    _description = "maintenance dashboard primary view"

    name = fields.Char()

