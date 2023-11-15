# -*- coding: utf-8 -*-
{
    'name': 'Sistema de Evaluacion del Desempeño',
    'summary': 'Sistema de Evaluacion del Desempeño',
    'description': """Sistema de Evaluacion del Desempeño""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': [
        'base',
        'l10n_cu_base',
        'l10n_cu_hlg_hr',
        'l10n_cu_report_docxtpl',
        'app_seleccion',
    ],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/turei_hr_performance_security.xml',
        'security/ir.model.access.csv',

        # Data files to load...
        'data/performance_data.xml',

        # Views definitions...
        'views/turei_hr_performance_view.xml',
        'views/hr_employee_view.xml',

        # Reports definitions...
        'reports/print_evaluation_trimestral.xml',



        # Wizards...
        'wizard/wzd_print_eval.xml',

    ],

    # Only loaded in demonstration mode.
    'demo': [],
    'test': [],

    'installable': True,
    'application': True,
    'auto_install': False,

}
