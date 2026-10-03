import json
from odoo import http
from odoo.http import request


class AmenityAPI(http.Controller):

    @http.route('/api/realestate/amenities', type='http', auth='public', methods=['GET'], csrf=False)
    def get_amenities(self, **kwargs):
        try:
            # 1. Get the base URL of your Odoo server to construct image links
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # 2. Define the search domain (Only active ones flagged for the website)
            domain = [('active', '=', True), ('show_on_website', '=', True)]

            # 3. Specify fields to fetch.
            # Notice we DO NOT fetch 'image_1920' here to avoid massive base64 payloads
            fields_to_fetch = ['id', 'name', 'category_id', 'sequence', 'description']

            # 4. Fetch the records
            amenities = request.env['estate.property.amenity'].sudo().search_read(
                domain=domain,
                fields=fields_to_fetch,
                order='sequence, name'
            )

            # 5. Format the data perfectly for mobile parsing
            formatted_amenities = []
            for amenity in amenities:
                # Odoo's standard image route: /web/image/<model>/<id>/<field>
                image_url = f"{base_url}/web/image/estate.property.amenity/{amenity['id']}/image_1920"

                # Extract category tuple (id, "Name") safely
                category_data = None
                if amenity.get('category_id'):
                    category_data = {
                        'id': amenity['category_id'][0],
                        'name': amenity['category_id'][1]
                    }

                formatted_amenities.append({
                    'id': amenity['id'],
                    'name': amenity['name'],
                    'sequence': amenity['sequence'],
                    'description': amenity['description'] or "",
                    'category': category_data,
                    'image_url': image_url
                })

            # 6. Return the JSON payload
            response_data = {
                'success': True,
                'message': 'Amenities fetched successfully',
                'data': formatted_amenities
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            error_response = {
                'success': False,
                'message': str(e),
                'data': []
            }
            return request.make_response(
                json.dumps(error_response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )