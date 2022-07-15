# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    # get access to the configuration model
    ResConfig = env["res.config.settings"].create({})
    # get a copy of the default values
    default_values = ResConfig.default_get(list(ResConfig.fields_get()))
    default_values.update({"portal_allow_api_keys":True})
    default_values.update({"auth_signup_uninvited": "b2c"})
    ResConfig.create(default_values).execute()