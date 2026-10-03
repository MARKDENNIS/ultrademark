from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class RealEstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"
    _inherit = ["mail.thread", "mail.activity.mixin", 'website.seo.metadata', 'website.published.mixin']
    _order = "priority desc, write_date desc"

    name = fields.Char(required=True, tracking=True)
    ref = fields.Char(string="Reference", copy=False, index=True, default=lambda self: _("New"))

    type_id = fields.Many2one("estate.property.type", required=True, index=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("published", "Published"),
        ("under_offer", "Under Offer"),
        ("sold", "Sold"),
        ("archived", "Archived"),
    ], default="draft", tracking=True, index=True)

    active = fields.Boolean(default=True)
    priority = fields.Selection([(str(i), str(i)) for i in range(1, 6)], default="3", index=True)

    description = fields.Html(
        string="Description",
        placeholder="Provide a detailed description of the property...",
        help="Add a detailed property description. You can include images, formatted text, and lists."
    )

    short_description = fields.Text(
        string="Short Description",
        placeholder="A brief summary, e.g. 'Spacious 3BR Apartment near Central Park'",
        help="Enter a short summary of the property. This is often used in listings and previews."
    )

    # Pricing
    currency_id = fields.Many2one("res.currency", required=True, default=lambda self: self.env.company.currency_id.id)
    price = fields.Monetary(index=True)
    rent_price = fields.Monetary(string="Rent (per month)", currency_field="currency_id")
    tenure = fields.Selection([
        ("sale", "For Sale"),
        ("rent", "For Rent"),
    ], default="sale", index=True)

    # Specs
    bedrooms = fields.Integer(index=True)
    bathrooms = fields.Integer(string="Bathrooms", index=True)
    parking_spaces = fields.Integer()
    area_built = fields.Float(help="Built-up area in sq.ft or sq.m")
    area_total = fields.Float(help="Total/Plot area")
    furnishing = fields.Selection([
        ("unfurnished", "Unfurnished"),
        ("semi_furnished", "Semi-furnished"),
        ("furnished", "Furnished"),
    ], index=True)
    year_built = fields.Integer()
    floor_no = fields.Integer()
    total_floors = fields.Integer()

    # Location
    street = fields.Char(
        string="Street Address",
        placeholder="e.g. 123 Palm Avenue",
        help="Enter the full street address of the property."
    )

    city = fields.Char(
        string="City",
        index=True,
        placeholder="e.g. New York",
        help="Enter the city where the property is located."
    )

    # --- Location (new relational) ---
    city_id = fields.Many2one("estate.city", string="City", index=True)
    area_id = fields.Many2one(
        "estate.area", string="Area / Locality",
        domain="[('city_id', '=', city_id)]", index=True)

    zip = fields.Char(
        string="ZIP / Postal Code",
        index=True,
        placeholder="e.g. 10001",
        help="Enter the postal code for the property's location."
    )
    state_id = fields.Many2one("res.country.state", index=True)
    country_id = fields.Many2one("res.country", index=True)
    latitude = fields.Float(digits=(16, 8))
    longitude = fields.Float(digits=(16, 8))

    # Media
    image_1920 = fields.Image(max_width=1920, max_height=1920, string="Image")

    # Attributes
    attribute_line_ids = fields.One2many("estate.property.attribute.line", "property_id", string="Attributes")

    spec_group_ids = fields.One2many("estate.property.spec.group", "property_id", string="Specifications")
    plan_ids = fields.One2many("estate.property.plan", "property_id", string="Plans")
    gallery_ids = fields.One2many("estate.property.image", "property_id", string="Gallery")

    amenity_ids = fields.Many2many(
        "estate.property.amenity",
        "estate_property_amenity_rel",
        "property_id",
        "amenity_id",
        string="Amenities",
        help="Select amenities available for this property.",
    )

    badge_ids = fields.Many2many(
        "estate.property.badge", "estate_property_badge_rel",
        "property_id", "badge_id", string="Badges")

    # Availability
    availability_date = fields.Date()

    # CRM link
    lead_ids = fields.One2many("crm.lead", "property_id", string="Leads")
    lead_count = fields.Integer(compute="_compute_lead_count")

    listed_by = fields.Selection([
        ("owner", "Owner"),
        ("agent", "Agent"),
        ("builder", "Builder/Developer"),
        ("salesperson", "Internal Salesperson"),
    ], default="agent", index=True, tracking=True)

    agent_id = fields.Many2one(
        "res.partner", string="Agent",
        domain="[('is_property_agent','=',True)]", tracking=True)

    co_agent_ids = fields.Many2many(
        "res.partner", "estate_property_agent_rel", "property_id", "partner_id",
        string="Co-Agents", domain="[('is_property_agent','=',True)]")

    builder_id = fields.Many2one(
        "res.partner", string="Builder/Developer",
        domain="[('is_property_builder','=',True)]", tracking=True)

    sales_user_id = fields.Many2one(
        "res.users", string="Internal Salesperson", tracking=True)

    brokerage_type = fields.Selection([
        ("percent", "Percent of Price"),
        ("fixed", "Fixed Amount"),
    ], default="percent")

    brokerage_value = fields.Float(string="Brokerage Value")
    brokerage_currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id.id)

    # helper: computed display for website / reports
    agent_display = fields.Char(compute="_compute_agent_display", store=False)

    canonical_url = fields.Char(help="Optional canonical URL")

    # ==========================================
    # SEO URL GENERATION
    # ==========================================
    def _slugify_text(self, text):
        # Helper to clean text for URLs
        return re.sub(r"[^a-z0-9]+", "-", (text or "").strip().lower()).strip("-") or "any"

    def _get_website_url(self):
        self.ensure_one()
        # Grab all the specific property details for the deep URL
        tenure_slug = self.tenure.lower() if self.tenure else 'any'
        ptype_slug = self._slugify_text(self.type_id.name) if self.type_id else 'any'
        city_slug = self._slugify_text(self.city_id.name) if self.city_id else 'any'
        prop_slug = f"{self._slugify_text(self.name)}-{self.id}"

        # Build the new deep SEO URL
        return f"/property/{tenure_slug}/{ptype_slug}/{city_slug}/{prop_slug}"

    @api.depends('name', 'tenure', 'type_id', 'city_id')
    def _compute_website_url(self):
        super()._compute_website_url()
        for prop in self:
            prop.website_url = prop._get_website_url()

    # Optional helpers to keep legacy Char in sync on edit
    @api.onchange("city_id")
    def _onchange_city_id_sync_legacy(self):
        for rec in self:
            if rec.city_id and (not rec.city or rec.city != rec.city_id.name):
                rec.city = rec.city_id.name
            # auto-set state/country from city if empty
            if rec.city_id:
                if not rec.state_id:
                    rec.state_id = rec.city_id.state_id
                if not rec.country_id:
                    rec.country_id = rec.city_id.country_id

    @api.onchange("area_id")
    def _onchange_area_id_fill_city(self):
        for rec in self:
            if rec.area_id and rec.area_id.city_id:
                rec.city_id = rec.area_id.city_id

    @api.depends("listed_by", "agent_id", "builder_id", "sales_user_id")
    def _compute_agent_display(self):
        for rec in self:
            if rec.listed_by == "agent" and rec.agent_id:
                rec.agent_display = rec.agent_id.display_name
            elif rec.listed_by == "builder" and rec.builder_id:
                rec.agent_display = rec.builder_id.display_name
            elif rec.listed_by == "salesperson" and rec.sales_user_id:
                rec.agent_display = rec.sales_user_id.name
            else:
                rec.agent_display = "Owner"

    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for rec in self:
            rec.lead_count = len(rec.lead_ids)

    @api.constrains("price", "rent_price")
    def _check_price(self):
        for rec in self:
            if rec.tenure == "sale" and rec.price < 0:
                raise ValidationError(_("Sale price cannot be negative."))
            if rec.tenure == "rent" and rec.rent_price < 0:
                raise ValidationError(_("Rent price cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # 1. Existing Logic: Generate Reference Sequence
            if vals.get("ref") in (False, _("New")):
                vals["ref"] = self.env["ir.sequence"].next_by_code("estate.property") or _("New")

            # 🚀 AGGRESSIVE FIX: Force published and active! Do not even check.
            vals["state"] = "published"
            vals["active"] = True

            # 2. Safety Shield: Validate City ID
            if 'city_id' in vals and vals['city_id']:
                try:
                    city_id = int(vals['city_id'])
                    # Check if the city actually exists
                    city_exists = self.env['estate.city'].sudo().browse(city_id).exists()

                    if not city_exists:
                        vals.pop('city_id', None)
                except (ValueError, TypeError):
                    # If ID isn't an integer, pop it to prevent crash
                    vals.pop('city_id', None)

        # 3. Save the record.
        return super().create(vals_list)

    def action_publish(self):
        self.write({"state": "published"})

    def action_mark_sold(self):
        self.write({"state": "sold"})

    def action_archive(self):
        self.write({"state": "archived"})

    def action_new_lead(self):
        Lead = self.env["crm.lead"]
        for prop in self:
            Lead.create({
                "name": f"Inquiry: {prop.name}",
                "type": "opportunity",
                "property_id": prop.id,
                "team_id": self.env.ref("crm.crm_team_1").id if self.env.ref("crm.crm_team_1",
                                                                             raise_if_not_found=False) else False,
                "description": _("Lead created from property form."),
            })


# Extend CRM to link back to property
class CrmLead(models.Model):
    _inherit = "crm.lead"

    property_id = fields.Many2one("estate.property", index=True, ondelete="set null")