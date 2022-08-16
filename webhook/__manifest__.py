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
    'depends': ['website','base','base_automation','rest'],
    'data': [
        "security/ir.model.access.csv",
        "security/webhook_log_security.xml",
        "security/webhook_subscription_security.xml",
        "views/webhook_menus.xml",
        "views/portal_template.xml",
        "views/base_automation_view.xml",
        "views/webhook_log_view.xml"
    ],
    'assets' : {
        'web.assets_frontend' : [
            'webhook/static/src/js/webhook.js',
        ],
        'web.assets_qweb': [
            'webhook/static/src/xml/webhook.xml',
            "static/src/xml/*.xml",
        ]
    }
}
