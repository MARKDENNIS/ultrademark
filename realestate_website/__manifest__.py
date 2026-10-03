# -*- coding: utf-8 -*-
{
    "name": "Real Estate Website",
    "version": "1.0.0",
    "summary": "Public listings, SEO, filters, and lead capture",
    "category": "Website",
    "license": "LGPL-3",
    "author":"Taqnix",
    "depends": [
        "website",
        "website_crm",
        "realestate_core",
        "http_routing",
    ],
    "data": [
        "data/ir_asset.xml",
        "views/website_menus.xml",
        "views/property_backend_views.xml",
        "templates/properties_template.xml",
        "templates/property_card.xml",
        'templates/property_description.xml',
        'templates/similar_properties_template.xml',
        "templates/property_template.xml",
        "templates/assets_property_lightbox.xml",
    ],

    "images": [
    "static/description/banner.png",
    "static/description/icon.png",
    ],
    
    "assets": {
        "web.assets_frontend": [
            "realestate_website/static/src/js/filter.js",
            "realestate_website/static/src/js/property_lightbox.js",
            "realestate_website/static/src/js/seo_property_search.js",
            "realestate_website/static/src/scss/styles.scss",
            "realestate_website/static/src/scss/property_cards.scss",
            "realestate_website/static/src/scss/primary_variables.scss",
            "realestate_website/static/src/scss/property_detail.scss",
            'realestate_website/static/src/scss/realestate_badges.scss',
            "realestate_website/static/src/scss/property_lightbox.scss",
        ],
    },
    "installable": True,
    "application": True,
}
