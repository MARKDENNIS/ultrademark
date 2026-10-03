from odoo import http
from odoo.http import request


class LocationAPI(http.Controller):

    # --- LOCATION API ---
    @http.route('/api/realestate/locations', type='json', auth='public', methods=['POST'], csrf=False)
    def get_locations(self, **kwargs):
        try:
            cities = request.env['estate.city'].sudo().search([('active', '=', True)], order='name')
            formatted_locations = []
            for city in cities:
                country_data = {'id': city.country_id.id, 'name': city.country_id.name} if city.country_id else None
                #state_data = {'id': city.state_id.id, 'name': city.state_id.name} if city.state_id else None

                formatted_areas = [{'id': area.id, 'name': area.name} for area in
                                   city.area_ids.filtered(lambda a: a.active)]

                formatted_locations.append({
                    'id': city.id,
                    'name': city.name,
                    'country': country_data,
                    #'state': state_data,
                    'zip_prefix': city.zip_prefix or "",
                    'areas': formatted_areas
                })

            return {'success': True, 'message': 'Locations fetched', 'data': formatted_locations}
        except Exception as e:
            return {'success': False, 'message': str(e), 'data': []}


