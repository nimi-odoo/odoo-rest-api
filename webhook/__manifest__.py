# -*- coding: utf-8 -*-
{
    'name': "Webhook",
    'summary': """
        Webhook
    """,
    'description': """
        Webhook
    """,
    'author': "Odoo",
    'website': "https://www.odoo.com",
    'license': 'OPL-1',
    'application': True,
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['base','website'],
    'data': [
        "security/ir.model.access.csv",
        "views/webhook_menus.xml",
        "views/portal_template.xml"
    ]
}
