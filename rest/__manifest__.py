# -*- coding: utf-8 -*-
{
    'name': "REST API",
    'summary': """
        summ
    """,
    'description': """
        desc
    """,
    'author': "Odoo",
    'website': "https://www.odoo.com",
    'license': 'OPL-1',
    'application': True,
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base','website'],
    'data': [
        "security/ir.model.access.csv",
        "views/rest_views.xml",
        "views/rest_field_views.xml",
        "views/rest_menus.xml",
        "views/portal_template.xml",
    ],
    'post_init_hook' : 'post_init_hook',
}
