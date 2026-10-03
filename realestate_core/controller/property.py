import json
import logging
import base64
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PropertyAPI(http.Controller):

    # =======================================================
    # ROUTE 0: NEW PUBLIC IMAGE SERVER (Bypasses Access Denied)
    # =======================================================
    @http.route('/api/realestate/image/<string:model>/<int:record_id>', type='http', auth='public', methods=['GET'],
                csrf=False)
    def get_public_image(self, model, record_id, **kwargs):
        try:
            # sudo() forces Odoo to give us the image regardless of guest permissions
            record = request.env[model].sudo().browse(record_id)
            if record.exists():
                # Try image_1920 first, then fallback to image
                image_data = getattr(record, 'image_1920', False)
                if not image_data:
                    image_data = getattr(record, 'image', False)

                if image_data:
                    image_decoded = base64.b64decode(image_data)
                    return request.make_response(image_decoded, headers=[('Content-Type', 'image/jpeg')])

            # If no image is found, return the standard placeholder
            return request.redirect('/web/static/img/placeholder.png')
        except Exception:
            return request.redirect('/web/static/img/placeholder.png')

    # =======================================================
    # ROUTE 1: GET ALL PROPERTIES (LIST VIEW / SEARCH RESULTS)
    # =======================================================
    @http.route('/api/realestate/properties', type='json', auth='public', methods=['POST'], csrf=False)
    def get_properties_list(self, **kwargs):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            domain = [('active', '=', True), ('state', 'in', ['published', 'Published'])]

            if kwargs.get('city_id'):
                domain.append(('city_id', '=', int(kwargs.get('city_id'))))
            if kwargs.get('type_id'):
                domain.append(('type_id', '=', int(kwargs.get('type_id'))))
            if kwargs.get('tenure'):
                domain.append(('tenure', '=', kwargs.get('tenure')))
            if kwargs.get('keyword'):
                domain.append(('name', 'ilike', kwargs.get('keyword')))

            # ✅ ADD THIS: Allow Flutter to send an array of IDs
            if kwargs.get('property_ids'):
                domain.append(('id', 'in', kwargs.get('property_ids')))

            # ✅ ADD THIS BLOCK: Support for fetching ONLY wishlisted properties
            if kwargs.get('wishlist_only'):
                user = request.env.user
                if user and user.id:  # Ensure user is logged in
                    wishlist_ids = user.property_wishlist_ids.ids
                    if not wishlist_ids:
                        # If wishlist is empty, immediately return empty list
                        return {'success': True, 'message': 'Empty', 'data': []}
                    domain.append(('id', 'in', wishlist_ids))
                else:
                    # If guest tries to fetch wishlist, return empty
                    return {'success': True, 'message': 'Not logged in', 'data': []}

            # ✅ FIX: Price Logic correctly aligned and independent
            min_price = kwargs.get('min_price')
            max_price = kwargs.get('max_price')

            if min_price is not None and max_price is not None:
                min_val = float(min_price)
                max_val = float(max_price)

                # Check rent vs sale explicitly to filter the right field
                if kwargs.get('tenure') == 'rent':
                    domain.append(('rent_price', '>=', min_val))
                    domain.append(('rent_price', '<=', max_val))
                elif kwargs.get('tenure') == 'sale':
                    domain.append(('price', '>=', min_val))
                    domain.append(('price', '<=', max_val))
                else:
                    # If "Any" is selected, safely check both rent and sale fields
                    domain += [
                        '|',
                        '&', ('tenure', '=', 'sale'), '&', ('price', '>=', min_val), ('price', '<=', max_val),
                        '&', ('tenure', '=', 'rent'), '&', ('rent_price', '>=', min_val), ('rent_price', '<=', max_val)
                    ]

            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))

            # ✅ FIX: Sorting Logic correctly aligned and checks rent vs sale
            sort_by = kwargs.get('sort_by', 'newest')
            tenure_type = kwargs.get('tenure')

            if sort_by == 'price_asc':
                order_string = 'rent_price asc' if tenure_type == 'rent' else 'price asc'
            elif sort_by == 'price_desc':
                order_string = 'rent_price desc' if tenure_type == 'rent' else 'price desc'
            else:
                order_string = 'priority desc, write_date desc'

            # Execute the search
            properties = request.env['estate.property'].sudo().search(
                domain, limit=limit, offset=offset, order=order_string
            )

            formatted_properties = []
            for prop in properties:
                unique_token = prop.write_date.strftime("%Y%m%d%H%M%S") if prop.write_date else "1"
                gallery_images = []

                # USE THE NEW PUBLIC IMAGE SERVER
                if getattr(prop, 'image_1920', False) or getattr(prop, 'image', False):
                    gallery_images.append(
                        f"{base_url}/api/realestate/image/estate.property/{prop.id}?unique={unique_token}")

                for img in prop.gallery_ids:
                    img_token = img.write_date.strftime("%Y%m%d%H%M%S") if img.write_date else "1"
                    if getattr(img, 'image_1920', False) or getattr(img, 'image', False):
                        gallery_images.append(
                            f"{base_url}/api/realestate/image/estate.property.image/{img.id}?unique={img_token}")

                main_image_url = gallery_images[0] if len(gallery_images) > 0 else ""

                contact_info = None
                if prop.listed_by == 'agent' and prop.agent_id:
                    contact_info = {
                        'id': prop.agent_id.id,
                        'name': prop.agent_id.name,
                        'phone': prop.agent_id.phone or prop.agent_id.mobile or "",
                        'email': prop.agent_id.email or ""
                    }
                elif prop.listed_by == 'builder' and prop.builder_id:
                    contact_info = {
                        'id': prop.builder_id.id,
                        'name': prop.builder_id.name,
                        'phone': prop.builder_id.phone or prop.builder_id.mobile or "",
                        'email': prop.builder_id.email or ""
                    }
                else:
                    contact_info = {
                        'id': 0,
                        'name': "Property Owner",
                        'phone': prop.phone if hasattr(prop, 'phone') else "",
                        'email': ""
                    }

                formatted_properties.append({
                    'id': prop.id,
                    'name': prop.name,
                    'ref': prop.ref,
                    'tenure': prop.tenure or 'sale',
                    'price': float(prop.price) if prop.tenure == 'sale' else float(prop.rent_price or 0.0),
                    'currency': prop.currency_id.name if prop.currency_id else "",
                    'short_description': prop.short_description or "",
                    'description_html': prop.description or "",
                    'furnishing': prop.furnishing or "",
                    'updated_date': prop.write_date.strftime("%d %b, %Y") if prop.write_date else "",
                    'bedrooms': prop.bedrooms or 0,
                    'bathrooms': prop.bathrooms or 0,
                    'area_built': prop.area_built or 0.0,
                    'city': prop.city_id.name if prop.city_id else "",
                    'area': prop.area_id.name if prop.area_id else "",
                    'main_image_url': main_image_url,
                    'gallery': gallery_images,
                    'badges': [{'id': b.id, 'name': b.name, 'color': b.color} for b in prop.badge_ids if b.active],
                    'contact_person': contact_info,
                    'location': {
                        'latitude': prop.latitude or 0.0,
                        'longitude': prop.longitude or 0.0
                    }
                })

            return {
                'success': True,
                'message': 'Properties fetched successfully',
                'data': formatted_properties
            }

        except Exception as e:
            _logger.error(f"CRITICAL ERROR IN PROPERTY API: {str(e)}")
            return {'success': False, 'message': str(e), 'data': []}

    # =======================================================
    # ROUTE 2: GET PROPERTY DETAILS (DEEP VIEW)
    # =======================================================
    @http.route('/api/realestate/property/<int:property_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_property_details(self, property_id, **kwargs):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            prop = request.env['estate.property'].sudo().browse(property_id)

            if not prop.exists() or not prop.active or prop.state != 'published':
                return request.make_response(
                    json.dumps({'success': False, 'message': 'Property not found or not published', 'data': {}}),
                    headers=[('Content-Type', 'application/json')], status=404)

            unique_token = prop.write_date.strftime("%Y%m%d%H%M%S") if prop.write_date else "1"
            gallery_images = []

            if getattr(prop, 'image_1920', False) or getattr(prop, 'image', False):
                gallery_images.append(
                    f"{base_url}/api/realestate/image/estate.property/{prop.id}?unique={unique_token}")

            for img in prop.gallery_ids:
                img_token = img.write_date.strftime("%Y%m%d%H%M%S") if img.write_date else "1"
                if getattr(img, 'image_1920', False) or getattr(img, 'image', False):
                    gallery_images.append(
                        f"{base_url}/api/realestate/image/estate.property.image/{img.id}?unique={img_token}")

            contact_info = {}
            if prop.listed_by == 'agent' and prop.agent_id:
                contact_info = {
                    'id': prop.agent_id.id,
                    'name': prop.agent_id.name,
                    'phone': prop.agent_id.phone or prop.agent_id.mobile or "",
                    'image_url': f"{base_url}/web/image/res.partner/{prop.agent_id.id}/avatar_128"
                }
            elif prop.listed_by == 'builder' and prop.builder_id:
                contact_info = {'id': prop.builder_id.id, 'name': prop.builder_id.name,
                                'phone': prop.builder_id.phone or prop.builder_id.mobile or ""}

            detail_data = {
                'id': prop.id,
                'name': prop.name,
                'ref': prop.ref,
                'state': prop.state,
                'tenure': prop.tenure,
                'price': prop.price if prop.tenure == 'sale' else prop.rent_price,
                'currency': prop.currency_id.name if prop.currency_id else "",
                'description_html': prop.description or "",
                'short_description': prop.short_description or "",
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'parking_spaces': prop.parking_spaces,
                'area_built': prop.area_built,
                'area_total': prop.area_total,
                'furnishing': prop.furnishing or "",
                'updated_date': prop.write_date.strftime("%d %b, %Y") if prop.write_date else "",
                'year_built': prop.year_built,
                'floor_no': prop.floor_no,
                'total_floors': prop.total_floors,
                'availability_date': str(prop.availability_date) if prop.availability_date else "",
                'location': {
                    'street': prop.street or "",
                    'city': prop.city_id.name if prop.city_id else prop.city or "",
                    'area': prop.area_id.name if prop.area_id else "",
                    'zip': prop.zip or "",
                    'latitude': prop.latitude,
                    'longitude': prop.longitude
                },
                'gallery': gallery_images,
                'amenities': [{'id': a.id, 'name': a.name, 'icon': a.icon or ""} for a in prop.amenity_ids if
                              a.active and a.show_on_website],
                'listed_by_type': prop.listed_by,
                'contact_person': contact_info,
                'agent_display_name': prop.agent_display
            }

            return request.make_response(
                json.dumps({'success': True, 'message': 'Property details fetched', 'data': detail_data}),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(json.dumps({'success': False, 'message': str(e), 'data': {}}),
                                         headers=[('Content-Type', 'application/json')], status=500)

    # =======================================================
    # ROUTE 3: CREATE NEW PROPERTY
    # =======================================================
    @http.route('/api/realestate/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        try:
            # Safely support payloads regardless of whether they arrive via standard kwargs or raw JSON
            data = kwargs if kwargs else (request.get_json_data() if request.get_json_data() else {})

            # Map values dynamically to matching database configurations
            vals = {
                'name': data.get('name'),
                'tenure': data.get('tenure', 'sale'),
                'bedrooms': int(data.get('bedrooms', 0)),
                'bathrooms': int(data.get('bathrooms', 0)),
                'area_built': float(data.get('area_built', 0.0)),
                'description': data.get('description', ''),
                'city_id': int(data.get('city_id')) if data.get('city_id') else False,
                'type_id': int(data.get('type_id')) if data.get('type_id') else False,
                # ✅ ADDED: Capture and persist furnishing values
                'furnishing': data.get('furnishing', 'unfurnished'),
            }

            # Handle coordinate metrics gracefully if present
            if data.get('latitude'):
                vals['latitude'] = float(data.get('latitude'))
            if data.get('longitude'):
                vals['longitude'] = float(data.get('longitude'))

            # Route financial metrics securely down the correct target path
            price_val = float(data.get('price', 0.0)) or float(data.get('rent_price', 0.0))
            if vals['tenure'] == 'sale':
                vals['price'] = price_val
            else:
                vals['rent_price'] = price_val

            # Execute context-safe creation sequence
            new_property = request.env['estate.property'].sudo().create(vals)

            return {
                'success': True,
                'message': 'Property created successfully',
                'property_id': new_property.id
            }

        except Exception as e:
            _logger.error(f"CRITICAL ERROR IN PROPERTY CREATION API: {str(e)}")
            return {'success': False, 'message': str(e), 'property_id': 0}