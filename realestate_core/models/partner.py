# realestate_core/models/partner.py
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_property_agent = fields.Boolean(string="Real Estate Agent")
    is_property_builder = fields.Boolean(string="Real Estate Builder/Developer")
    rera_number = fields.Char(string="RERA Registration No.")
    agency_name = fields.Char(string="Agency/Builder Name")