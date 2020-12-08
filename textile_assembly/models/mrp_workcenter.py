# -*- coding: utf-8 -*-
from odoo import fields, models


class MrpWorkCenter(models.Model):
    _inherit = 'mrp.workcenter'

    is_cutting = fields.Boolean(string="Cutting", copy=False)
