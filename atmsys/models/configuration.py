# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportConfiguration(models.Model):
    _name = 'atmsys.report_configuration'
    _description = 'atmsys.report_configuration'

    working_days = fields.Float(string='Días laborables')

    # Report one configuration...
    report_one_product_ids = fields.Many2many(
        'atmsys.report_one_record', relation='report_one_product_rel', column1='config_id', column2='product_id',
        string='Products'
    )

    report_one_other_product_ids = fields.Many2many(
        'atmsys.report_one_record', relation='report_one_other_product_rel', column1='config_id',
        column2='product_id', string='Otros'
    )

    # Report two configuration...
    report_two_product_ids = fields.Many2many(
        'atmsys.report_two_record', relation='report_two_product_rel', column1='config_id', column2='product_id',
        string='Products'
    )

    report_two_other_product_ids = fields.Many2many(
        'atmsys.report_two_record', relation='report_two_other_product_rel', column1='config_id',
        column2='product_id', string='Otros'
    )

    # Report three configuration...
    report_three_product_ids = fields.Many2many(
        'atmsys.report_three_record', relation='report_three_product_rel', column1='config_id', column2='product_id',
        string='Products'
    )

    # Report four configuration...
    report_four_product_ids = fields.Many2many(
        'atmsys.report_four_record', relation='report_four_product_rel', column1='config_id', column2='product_id',
        string='Products'
    )

    # Report six configuration...
    report_six_product_ids = fields.Many2many(
        'atmsys.report_six_record', relation='report_six_product_rel', column1='config_id', column2='product_id',
        string='Products'
    )

    @api.one
    def action_save(self):
        return True


class ReportOneProducts(models.Model):
    _name = 'atmsys.report_one_record'
    _description = 'atmsys.report_one_record'
    _order = 'product_id asc'

    config_id = fields.Many2one('atmsys.report_configuration', string='Configuration')
    product_id = fields.Many2one('simple_product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    conversion_factor = fields.Float(string='Factor de conversión')

class ReportTwoProducts(models.Model):
    _name = 'atmsys.report_two_record'
    _description = 'atmsys.report_two_record'
    _order = 'product_id asc'

    config_id = fields.Many2one('atmsys.report_configuration', string='Configuration')
    product_id = fields.Many2one('simple_product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)


class ReportThreeProducts(models.Model):
    _name = 'atmsys.report_three_record'
    _description = 'atmsys.report_three_record'
    _order = 'product_id asc'

    config_id = fields.Many2one('atmsys.report_configuration', string='Configuration')
    product_id = fields.Many2one('simple_product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    conversion_factor = fields.Float(string='Factor de conversión')


class ReportFourProducts(models.Model):
    _name = 'atmsys.report_four_record'
    _description = 'atmsys.report_four_record'
    _order = 'product_id asc'

    config_id = fields.Many2one('atmsys.report_configuration', string='Configuration')
    product_id = fields.Many2one('simple_product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    conversion_factor = fields.Float(string='Factor de conversión')

class ReportSixProducts(models.Model):
    _name = 'atmsys.report_six_record'
    _description = 'atmsys.report_six_record'

    config_id = fields.Many2one('atmsys.report_configuration', string='Configuration')
    product_id = fields.Many2one('simple_product.product', string='Product', required=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
