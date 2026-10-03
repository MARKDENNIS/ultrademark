from odoo import api, fields, models

class RealEstateAttribute(models.Model):
    _name = "estate.property.attribute"
    _description = "Property Attribute"
    _order = "name"

    name = fields.Char(required=True, index=True)
    display_name = fields.Char(compute="_compute_display_name", store=False)
    attr_type = fields.Selection([
        ("select", "Single Select"),
        ("multi", "Multi Select"),
    ], default="select", required=True)
    value_ids = fields.One2many("estate.property.attribute.value", "attribute_id", string="Values")
    show_in_website_filter = fields.Boolean(
        string="Show in Website Filter",
        default=True,
        help="If checked, this attribute will be shown in the website filter sidebar."
    )

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.name

    _sql_constraints = [
        ("name_uniq", "unique(name)", "Attribute name must be unique."),
    ]


class RealEstateAttributeValue(models.Model):
    _name = "estate.property.attribute.value"
    _description = "Property Attribute Value"
    _order = "attribute_id, name"

    name = fields.Char(required=True, index=True)
    attribute_id = fields.Many2one("estate.property.attribute", required=True, ondelete="cascade")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("attr_value_uniq", "unique(attribute_id,name)", "Value must be unique per attribute."),
    ]


class RealEstateAttributeLine(models.Model):
    _name = "estate.property.attribute.line"
    _description = "Property Attribute Line"
    _rec_name = "attribute_id"
    _order = "attribute_id"

    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade", index=True)
    attribute_id = fields.Many2one("estate.property.attribute", required=True, ondelete="cascade")
    value_id = fields.Many2one("estate.property.attribute.value", domain="[('attribute_id','=',attribute_id)]")
    value_ids = fields.Many2many(
        "estate.property.attribute.value",
        "estate_attr_line_value_rel",  # shorter M2M table name
        "line_id",
        "value_id",
        string="Values (Multi)",
        domain="[('attribute_id','=',attribute_id)]",
    )
    attr_type = fields.Selection(related="attribute_id.attr_type", store=False)
