# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class RealEstateWishlistController(http.Controller):

    @http.route('/api/realestate_core/wishlist/toggle', type='json', auth='user', methods=['POST'], csrf=False)
    def toggle_wishlist(self, **kwargs):
        property_id = kwargs.get('property_id') or kwargs.get('product_id')

        if not property_id:
            return {'status': 'error', 'message': 'Property ID required'}

        user = request.env.user
        prop_id = int(property_id)

        # Ensure property exists
        property_record = request.env['estate.property'].sudo().browse(prop_id)
        if not property_record.exists():
            return {'status': 'error', 'message': 'Property not found'}

        # Toggle logic
        if prop_id in user.property_wishlist_ids.ids:
            user.sudo().write({'property_wishlist_ids': [(3, prop_id)]})
            is_wishlisted = False
        else:
            user.sudo().write({'property_wishlist_ids': [(4, prop_id)]})
            is_wishlisted = True

        # 🔥 CRITICAL FIX: Force Postgres to save the data immediately!
        request.env.cr.commit()

        return {
            'status': 'success',
            'is_wishlisted': is_wishlisted,
            'message': 'Added to wishlist' if is_wishlisted else 'Removed from wishlist'
        }

    @http.route('/api/realestate_core/wishlist/ids', type='json', auth='user', methods=['POST', 'GET'], csrf=False)
    def get_wishlist_ids(self, **kwargs):
        user = request.env.user
        return {
            'status': 'success',
            'data': user.property_wishlist_ids.ids
        }