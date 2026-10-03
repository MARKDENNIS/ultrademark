# realestate_website/models/badge.py
from odoo import fields, models

class EstatePropertyBadge(models.Model):
    _name = "estate.property.badge"
    _description = "Property Badge / Ribbon"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    # Bootstrap-ish color classes you can reuse on website
    color = fields.Selection([
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("success", "Success"),
        ("danger", "Danger"),
        ("warning", "Warning"),
        ("info", "Info"),
        ("dark", "Dark"),
        ("light", "Light"),
    ], default="primary", required=True)
    active = fields.Boolean(default=True)