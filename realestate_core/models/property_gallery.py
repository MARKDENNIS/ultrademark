# realestate_core/models/property_gallery.py
from odoo import models, fields

class EstatePropertyImage(models.Model):
    _name = "estate.property.image"
    _description = "Property Gallery Image"
    _order = "sequence, id"

    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade", index=True)
    image_1920 = fields.Image(required=True)
    caption = fields.Char()
    is_cover = fields.Boolean(help="If checked, used as primary image on website/cards.")
    sequence = fields.Integer(default=10)