import json
from odoo import http
from odoo.http import request

class AttributeAPI(http.Controller):

    @http.route('/api/realestate/attributes', type='http', auth='public', methods=['GET'], csrf=False)
    def get_filter_attributes(self, **kwargs):
        try:
            # Only fetch attributes meant for filtering
            attributes = request.env['estate.property.attribute'].sudo().search(
                [('show_in_website_filter', '=', True)],
                order='name'
            )

            formatted_attributes = []
            for attr in attributes:
                # Fetch nested active values for this attribute
                active_values = []
                for val in attr.value_ids.filtered(lambda v: v.active):
                    active_values.append({
                        'id': val.id,
                        'name': val.name
                    })

                # Only include attributes that actually have active values
                if active_values:
                    formatted_attributes.append({
                        'id': attr.id,
                        'name': attr.name,
                        'type': attr.attr_type, # Let's Flutter know if it should render Radio buttons (select) or Checkboxes (multi)
                        'values': active_values
                    })

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Attributes fetched successfully',
                    'data': formatted_attributes
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )