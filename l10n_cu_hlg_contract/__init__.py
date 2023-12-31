# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import models
import wizard
import report
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    data = env['l10n_cu_base.reg'].search(
        [('name', '=', 'l10n_cu_contract')])
    if len(data) == 0:
        env['l10n_cu_base.reg'].create({
            'name': 'l10n_cu_contract'
        })