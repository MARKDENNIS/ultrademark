# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class RealEstatePropertyController(http.Controller):

    # ==========================================
    # 1. SEARCH PROPERTIES ENDPOINT
    # ==========================================
    @http.route('/api/realestate_core/search', type='json', auth='public', methods=['POST'], csrf=False)
    def search_properties(self, category_id=None, location_keyword=None, property_id=None, keyword=None, sort_by='newest',
                          limit=20, offset=0):
        """
        Fetches real estate properties with filters.
        Returns data translated based on the 'frontend_lang' cookie.
        """

        # --- 1. LANGUAGE DETECTION ---
        cookie_lang = request.httprequest.cookies.get('frontend_lang')
        context_lang = request.env.context.get('lang')
        lang_to_use = cookie_lang or context_lang or 'en_US'

        valid_lang = request.env['res.lang'].sudo().search_count([('code', '=', lang_to_use)]) > 0
        if not valid_lang:
            lang_to_use = 'en_US'

        # --- 2. BUILD SEARCH DOMAIN ---
        # Base domain: only published, and marked as a real estate property
        # Ensure 'is_property' exists on your product.template/property model!
        domain = [
            ('is_published', '=', True),
            ('is_property', '=', True)
        ]

        if property_id:
            domain.append(('id', '=', int(property_id)))

        if category_id:
            domain.append(('public_categ_ids', 'child_of', int(category_id)))

        if location_keyword:
            domain.append(('property_location', 'ilike', location_keyword))

        if keyword:
            domain.append(('name', 'ilike', keyword))

        # --- 3. SORTING ---
        order = 'create_date desc'
        if sort_by == 'price_asc':
            order = 'list_price asc'
        elif sort_by == 'price_desc':
            order = 'list_price desc'
        elif sort_by == 'name':
            order = 'name asc'

        # --- 4. FETCH DATA WITH CONTEXT ---
        # Update this model if you use something like 'realestate.property'
        PropertyModel = request.env['product.template'].with_context(lang=lang_to_use).sudo()

        properties = PropertyModel.search(domain, order=order, limit=limit, offset=offset)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # --- 5. FORMAT RESPONSE ---
        data = []
        for p in properties:
            # 1. Main Image & Gallery
            main_image_url = f"{base_url}/web/image/product.template/{p.id}/image_1920" if p.image_1920 else ''
            gallery_urls = [f"{base_url}/web/image/product.image/{img.id}/image_1920" for img in
                            p.product_template_image_ids]
            all_images = [main_image_url] + gallery_urls if main_image_url else gallery_urls

            # 2. Agent / Landlord Data
            agent_data = {
                'id': p.vendor_id.id if p.vendor_id else 0,
                'name': p.vendor_id.name if p.vendor_id else 'Internal Agency',
                'phone': p.vendor_id.phone or '',
                'image_url': f"{base_url}/web/image/res.partner/{p.vendor_id.id}/image_128" if p.vendor_id else None
            }

            # 3. Dynamic Attributes Extraction (e.g., Amenities, Views)
            attributes_list = []
            for line in p.attribute_line_ids:
                attributes_list.append({
                    'attribute_name': line.attribute_id.name,
                    'values': [val.name for val in line.value_ids]
                })

            # 4. Build the Mobile-Friendly Object
            data.append({
                'id': p.id,
                'name': p.name,
                'currency': request.env.company.currency_id.symbol or 'OMR',
                'images': all_images,
                'image_url': main_image_url,
                'agent': agent_data,
                'attributes': attributes_list,

                # --- PRICING ---
                'sale_price': p.list_price or 0.0,
                'rent_monthly': getattr(p, 'rent_monthly', 0.0),
                'rent_yearly': getattr(p, 'rent_yearly', 0.0),
                'security_deposit': getattr(p, 'security_deposit', 0.0),

                # --- PROPERTY FEATURES (Customize based on your actual fields) ---
                'property_type': getattr(p, 'property_type', 'apartment'),
                'furnishing_status': getattr(p, 'furnishing_status', 'unfurnished'),
                'bedrooms': getattr(p, 'bedrooms', 0),
                'bathrooms': getattr(p, 'bathrooms', 0),
                'area_sqft': getattr(p, 'area_sqft', 0.0),

                # --- SPECIFICS & LOCATION ---
                'plot_number': getattr(p, 'plot_number', ''),
                'registration_number': getattr(p, 'registration_number', ''),
                'location_name': getattr(p, 'property_location', ''),
                'latitude': p.latitude or 0.0,
                'longitude': p.longitude or 0.0,
                'status': getattr(p, 'property_status', 'available'),

                'description': getattr(p, 'description_ecommerce', ''),
                'website_description': getattr(p, 'website_description', ''),
            })

        return {'status': 'success', 'data': data}

    # ==========================================
    # 2. CREATE PROPERTY ENDPOINT
    # ==========================================
    @http.route('/api/realestate_core/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        """
        Creates a new real estate property from the mobile app/frontend.
        Expected JSON payload:
        {
            "name": "Luxury Marina Villa",
            "category_id": 14,
            "sale_price": 250000.0,
            "rent_monthly": 1500.0,
            "bedrooms": 4,
            "bathrooms": 3,
            "area_sqft": 3200,
            "furnishing_status": "furnished",
            "property_location": "Dubai Marina",
            "registration_number": "DLD-91504",
            ...
        }
        """
        vals = {
            'name': kwargs.get('name'),
            'is_property': True,  # Replaces 'car_rental'
            'sale_ok': True,
            'website_published': True,

            # Categories & Ownership
            'public_categ_ids': [(6, 0, [int(kwargs.get('category_id'))])] if kwargs.get('category_id') else False,
            'vendor_id': request.env.user.partner_id.id,

            # --- PRICING ---
            'list_price': float(kwargs.get('sale_price', 0.0)),
            'rent_monthly': float(kwargs.get('rent_monthly', 0.0)),
            'rent_yearly': float(kwargs.get('rent_yearly', 0.0)),
            'security_deposit': float(kwargs.get('security_deposit', 0.0)),

            # --- PROPERTY FEATURES ---
            'bedrooms': int(kwargs.get('bedrooms', 0)),
            'bathrooms': int(kwargs.get('bathrooms', 0)),
            'area_sqft': float(kwargs.get('area_sqft', 0.0)),
            'property_type': kwargs.get('property_type', 'apartment'),
            'furnishing_status': kwargs.get('furnishing_status', 'unfurnished'),

            # --- LOCATION & SPECIFICS ---
            'property_location': kwargs.get('property_location'),
            'latitude': float(kwargs.get('latitude', 0.0)),
            'longitude': float(kwargs.get('longitude', 0.0)),
            'registration_number': kwargs.get('registration_number'),
            'plot_number': kwargs.get('plot_number'),
            'property_status': 'available',

            'description_sale': kwargs.get('description'),
        }

        # Create the Property Object (Update model if needed)
        PropertyModel = request.env['product.template']
        new_property = PropertyModel.create(vals)

        # --- Handle Base64 Images ---
        images = kwargs.get('images', [])
        if images:
            new_property.write({'image_1920': images[0]})
            for img_data in images[1:]:
                request.env['product.image'].create({
                    'product_tmpl_id': new_property.id,
                    'name': new_property.name,
                    'image_1920': img_data
                })

        return {
            'status': 'success',
            'message': 'Property successfully added to portfolio',
            'property_id': new_property.id
        }