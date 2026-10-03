import json
from odoo import http
from odoo.http import request

class GalleryAPI(http.Controller):

    @http.route('/api/realestate/property/<int:property_id>/gallery', type='http', auth='public', methods=['GET'], csrf=False)
    def get_property_gallery(self, property_id, **kwargs):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # Fetch all images for the property, ordered by sequence
            images = request.env['estate.property.image'].sudo().search([
                ('property_id', '=', property_id)
            ], order='is_cover desc, sequence, id')

            formatted_gallery = []

            for img in images:
                formatted_gallery.append({
                    'id': img.id,
                    'caption': img.caption or "",
                    'is_cover': img.is_cover,
                    'image_url': f"{base_url}/web/image/estate.property.image/{img.id}/image_1920"
                })

            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': 'Gallery fetched successfully',
                    'data': formatted_gallery
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )