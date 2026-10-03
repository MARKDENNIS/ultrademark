import json
from odoo import http
from odoo.http import request

class PropertyTypeAPI(http.Controller):

    @http.route('/api/realestate/types', type='http', auth='public', methods=['GET'], csrf=False)
    def get_property_types(self, **kwargs):
        try:
            # We use search_read because there are no heavy relational fields or images to process here.
            # This makes the database query extremely fast.
            property_types = request.env['estate.property.type'].sudo().search_read(
                domain=[('active', '=', True)],
                fields=['id', 'name', 'code', 'color'],
                order='name'
            )

            # Format the response
            formatted_types = []
            for p_type in property_types:
                formatted_types.append({
                    'id': p_type['id'],
                    'name': p_type['name'],
                    # Ensure code is a string even if empty, useful for Flutter asset mapping
                    'code': p_type['code'] or "",
                    # Odoo uses integers (0-11) for colors. We pass it so Flutter can apply UI themes if needed.
                    'color_index': p_type['color']
                })

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Property types fetched successfully',
                    'data': formatted_types
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )