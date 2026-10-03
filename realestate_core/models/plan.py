# realestate_core/models/plan.py
from odoo import models, fields

class EstatePlanCategory(models.Model):
    _name = "estate.property.plan.category"
    _description = "Plan Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(help="e.g., location_map, masterplan, floor_2bhk")
    sequence = fields.Integer(default=10)
    show_on_website = fields.Boolean(default=True)

class EstatePropertyPlan(models.Model):
    _name = "estate.property.plan"
    _description = "Property Plan"
    _order = "sequence, id"

    name = fields.Char(required=True)
    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade", index=True)
    category_id = fields.Many2one("estate.property.plan.category", required=True, index=True)
    sequence = fields.Integer(default=10)
    # a cover image for the plan card
    cover_image_1920 = fields.Image()
    # per-plan gallery
    image_ids = fields.One2many("estate.property.plan.image", "plan_id", string="Images")

class EstatePropertyPlanImage(models.Model):
    _name = "estate.property.plan.image"
    _description = "Plan Image"
    _order = "sequence, id"

    plan_id = fields.Many2one("estate.property.plan", required=True, ondelete="cascade", index=True)
    image_1920 = fields.Image(required=True)
    caption = fields.Char()
    sequence = fields.Integer(default=10)
