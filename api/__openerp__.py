# -*- coding: utf-8 -*-
{
    'name': "api",

    'summary': """
        My routing API's for interaction between 3 party app and odoo server""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ashish Mishra",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}