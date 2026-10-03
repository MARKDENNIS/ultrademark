import json
from odoo import http
from odoo.http import request

class PlanAPI(http.Controller):

    # Notice the route includes <int:property_id> so the app can ask for a specific property's plans
    @http.route('/api/realestate/property/<int:property_id>/plans', type='http', auth='public', methods=['GET'], csrf=False)
    def get_property_plans(self, property_id, **kwargs):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # 1. Fetch the plans for this specific property
            plans = request.env['estate.property.plan'].sudo().search([
                ('property_id', '=', property_id)
            ], order='sequence, id')

            formatted_plans = []

            # 2. Loop through the plans to build the nested payload
            for plan in plans:
                # Format category data
                category_data = None
                if plan.category_id and plan.category_id.show_on_website:
                    category_data = {
                        'id': plan.category_id.id,
                        'name': plan.category_id.name,
                        'code': plan.category_id.code or ""
                    }

                # Construct the cover image URL
                cover_image_url = ""
                if plan.cover_image_1920:
                    cover_image_url = f"{base_url}/web/image/estate.property.plan/{plan.id}/cover_image_1920"

                # 3. Process the nested One2many gallery images for this specific plan
                gallery_images = []
                for img in plan.image_ids:
                    gallery_images.append({
                        'id': img.id,
                        'caption': img.caption or "",
                        'sequence': img.sequence,
                        'image_url': f"{base_url}/web/image/estate.property.plan.image/{img.id}/image_1920"
                    })

                formatted_plans.append({
                    'id': plan.id,
                    'name': plan.name,
                    'sequence': plan.sequence,
                    'category': category_data,
                    'cover_image_url': cover_image_url,
                    'gallery': gallery_images  # The nested array of images
                })

            # 4. Return the JSON payload
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': f'Plans fetched successfully for property {property_id}',
                    'data': formatted_plans
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )