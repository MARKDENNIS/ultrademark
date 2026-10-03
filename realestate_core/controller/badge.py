import json
from odoo import http
from odoo.http import request

class PropertyBadgeAPI(http.Controller):

    @http.route('/api/realestate/badges', type='http', auth='public', methods=['GET'], csrf=False)
    def get_property_badges(self, **kwargs):
        try:
            # sudo() is used so public users/mobile apps can read the data without needing to log in first
            # search_read automatically fetches records and formats them as a list of dictionaries
            badges = request.env['estate.property.badge'].sudo().search_read(
                domain=[('active', '=', True)],
                fields=['id', 'name', 'color', 'sequence']
            )

            # Construct the API response payload
            response_data = {
                'success': True,
                'message': 'Badges fetched successfully',
                'data': badges
            }

            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            # Handle any server errors gracefully
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