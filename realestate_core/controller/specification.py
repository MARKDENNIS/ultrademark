import json
from odoo import http
from odoo.http import request


class SpecificationAPI(http.Controller):

    @http.route('/api/realestate/property/<int:property_id>/specifications', type='http', auth='public',
                methods=['GET'], csrf=False)
    def get_property_specifications(self, property_id, **kwargs):
        try:
            # 1. Fetch the specification groups for this specific property
            spec_groups = request.env['estate.property.spec.group'].sudo().search([
                ('property_id', '=', property_id)
            ], order='sequence, id')

            formatted_specs = []

            # 2. Loop through the groups to build the nested payload
            for group in spec_groups:

                # 3. Process the nested One2many items for this specific group
                group_items = []
                for item in group.item_ids:
                    group_items.append({
                        'id': item.id,
                        'name': item.name,
                        'note': item.note or "",
                        'sequence': item.sequence
                    })

                # Only add the group to the payload if it actually contains items
                if group_items:
                    formatted_specs.append({
                        'id': group.id,
                        'group_name': group.name,
                        'sequence': group.sequence,
                        'items': group_items  # The nested array of specification details
                    })

            # 4. Return the JSON payload
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': f'Specifications fetched successfully for property {property_id}',
                    'data': formatted_specs
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )