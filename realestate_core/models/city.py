# realestate_core/models/location.py
from odoo import api, fields, models

class EstateCity(models.Model):
    _name = "estate.city"
    _description = "City"
    _order = "name"

    name = fields.Char(required=True, index=True)
    country_id = fields.Many2one("res.country", index=True)
    state_id = fields.Many2one("res.country.state", domain="[('country_id', '=', country_id)]", index=True)
    zip_prefix = fields.Char(help="Optional ZIP/Postal prefix")
    area_ids = fields.One2many("estate.area", "city_id", string="Areas/Localities")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_country_uniq", "unique(name, country_id, state_id)", "City must be unique per country/state."),
    ]


class EstateArea(models.Model):
    _name = "estate.area"
    _description = "Area / Locality"
    _order = "name"

    name = fields.Char(required=True, index=True)
    city_id = fields.Many2one("estate.city", required=True, index=True, ondelete="cascade")
    state_id = fields.Many2one(related="city_id.state_id", store=True)
    country_id = fields.Many2one(related="city_id.country_id", store=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_city_uniq", "unique(name, city_id)", "Area must be unique within a city."),
    ]