# realestate_core/models/amenity.py
from odoo import models, fields, api, _

class EstateAmenityCategory(models.Model):
    _name = "estate.property.amenity.category"
    _description = "Amenity Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    icon = fields.Char(help="Optional CSS/FA icon class, e.g., 'fa fa-swimming-pool'.")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Amenity category name must be unique."),
    ]


class EstateAmenity(models.Model):
    _name = "estate.property.amenity"
    _description = "Property Amenity"
    _order = "sequence, name"

    name = fields.Char(required=True, index=True)
    category_id = fields.Many2one(
        "estate.property.amenity.category", string="Category", index=True
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    show_on_website = fields.Boolean(default=True)
    description = fields.Text()
    image_1920 = fields.Image(help="Large image for website or cards.")

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Amenity name must be unique."),
    ]