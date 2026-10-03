import json
from odoo import http
from odoo.http import request


class PartnerAPI(http.Controller):

    @http.route('/api/realestate/professionals', type='http', auth='public', methods=['GET'], csrf=False)
    def get_real_estate_professionals(self, **kwargs):
        try:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

            domain = [
                ('active', '=', True),
                '|',
                ('is_property_agent', '=', True),
                ('is_property_builder', '=', True)
            ]

            # FIX: Removed 'mobile' from fields_to_fetch to prevent 500 error
            fields_to_fetch = [
                'id', 'name', 'phone', 'email',
                'is_property_agent', 'is_property_builder',
                'rera_number', 'agency_name'
            ]

            partners = request.env['res.partner'].sudo().search_read(
                domain=domain,
                fields=fields_to_fetch
            )

            formatted_partners = []
            for partner in partners:
                image_url = f"{base_url}/web/image/res.partner/{partner['id']}/avatar_128"

                # Logic for role label
                is_agent = partner.get('is_property_agent') or False
                is_builder = partner.get('is_property_builder') or False

                if is_agent and is_builder:
                    role_label = "Agent & Builder"
                elif is_builder:
                    role_label = "Builder/Developer"
                else:
                    role_label = "Real Estate Agent"

                # FIX: Use 'phone' as the primary contact number since 'mobile' is missing
                contact_number = partner.get('phone') or ""

                # WhatsApp link construction
                whatsapp_link = f"https://wa.me/{contact_number.replace('+', '').replace(' ', '')}" if contact_number else ""

                formatted_partners.append({
                    'id': partner['id'],
                    'name': partner['name'],
                    'role_label': role_label,
                    'is_agent': is_agent,
                    'is_builder': is_builder,
                    'agency_name': partner.get('agency_name') or "",
                    'rera_number': partner.get('rera_number') or "",
                    'phone': contact_number,
                    'email': partner.get('email') or "",
                    'whatsapp_link': whatsapp_link,
                    'image_url': image_url
                })

            return request.make_response(
                json.dumps({'success': True, 'message': 'Professionals fetched', 'data': formatted_partners}),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            # Added a log print here to help you debug errors in the Odoo terminal
            print(f"ERROR: {str(e)}")
            return request.make_response(
                json.dumps({'success': False, 'message': str(e), 'data': []}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )