# realestate_core/models/specification.py
from odoo import models, fields

class EstateSpecGroup(models.Model):
    _name = "estate.property.spec.group"
    _description = "Specification Group"
    _order = "sequence, id"

    name = fields.Char(required=True)
    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    item_ids = fields.One2many("estate.property.spec.item", "group_id", string="Items")

class EstateSpecItem(models.Model):
    _name = "estate.property.spec.item"
    _description = "Specification Item"
    _order = "sequence, id"

    group_id = fields.Many2one("estate.property.spec.group", required=True, ondelete="cascade", index=True)
    name = fields.Char(required=True)
    note = fields.Text()
    sequence = fields.Integer(default=10)