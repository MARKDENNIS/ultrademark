from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    property_wishlist_ids = fields.Many2many(
        'estate.property', # Or your custom property model
        'property_user_wishlist_rel',
        'user_id',
        'property_id',
        string='Property Wishlist'
    )