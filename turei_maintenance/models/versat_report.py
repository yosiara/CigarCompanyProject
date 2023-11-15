# -*- coding: utf-8 -*-
from odoo import fields, models


class VersatReport(models.Model):
    _name = 'turei_maintenance.versat_report'

    number = fields.Char(string='No.')
    date = fields.Char(string='Fecha')
    code = fields.Char(string='Código')
    description = fields.Char(string='Descripción')
    mu = fields.Char(string='UM')
    existence = fields.Char(string='Existencia')
    amount = fields.Char(string='Cantidad')
    cup = fields.Char(string='CUP')
    cuc = fields.Char(string='CUC')
    ca = fields.Char(string='C.A')
    warehouse = fields.Char(string='Nombre Almacén')
    name = fields.Char(string='Nombre')
    ccosto = fields.Char(string='C.Costo')
    centro_costo = fields.Char(string='Centro Costo')
    doc_status = fields.Char(string='Estado Doc')
    norder = fields.Char(string='N. Orden')

