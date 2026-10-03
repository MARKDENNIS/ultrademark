# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class RealEstateBannersController(http.Controller):

    @http.route('/api/realestate_core/banners', type='json', auth='public', methods=['POST'], csrf=False)
    def get_banners(self, **kw):

        # ✅ Accept param OR cookie OR context
        lang_code = (
            kw.get('lang')
            or kw.get('frontend_lang')
            or request.httprequest.cookies.get('frontend_lang')
            or request.env.context.get('lang')
            or 'en_US'
        )

        # ✅ Normalize
        if lang_code in ('ar', 'ar_SA'):
            odoo_lang = 'ar_001'
        elif lang_code == 'en':
            odoo_lang = 'en_US'
        else:
            odoo_lang = lang_code  # already ar_001 / en_US

        # Ensure this model name matches your actual banner model in realestate_core
        Banner = request.env['realestate.core.banner'].sudo().with_context(lang=odoo_lang)
        banners = Banner.search([('active', '=', True)])

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        data = []

        for b in banners:
            image_field = 'image_1920'
            if odoo_lang.startswith('ar') and b.image_ar_1920:
                image_field = 'image_ar_1920'

            has_image = getattr(b, image_field)
            # Update the model string in the URL to match your real estate banner model
            image_url = f"{base_url}/web/image/realestate.core.banner/{b.id}/{image_field}" if has_image else None

            data.append({
                'id': b.id,
                'title': b.name,                 # translated
                'subtitle': b.subtitle or '',    # translated if field translatable
                'image_url': image_url,
                'color': b.hex_color or '#1A237E',
                'action_type': b.click_action,
                'target_screen': b.target_screen,
                'target_id': b.target_id or 0,
                'target_url': b.target_url or '',
            })

        return {'status': 'success', 'data': data}