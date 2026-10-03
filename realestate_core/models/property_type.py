from odoo import api, fields, models

class RealEstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "name"

    name = fields.Char(required=True, index=True)
    code = fields.Char(index=True, help="Short code, optional")
    active = fields.Boolean(default=True)
    color = fields.Integer(default=0)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Property type must be unique."),
    ]
