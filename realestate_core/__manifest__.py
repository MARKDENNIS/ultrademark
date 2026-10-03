# -*- coding: utf-8 -*-
{
    "name": "Real Estate Core",
    "version": "1.0.0",
    "summary": "Core models for properties, types, attributes; CRM-ready",
    "category": "Sales/Real Estate",
    "author": "Taqnix",
    "license": "LGPL-3",
    "depends": ["base", "mail", "crm", "utm", "sales_team", "website","taqnix_app_builder"],
    "data": [
        # 1. Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # 2. Sequences
        "data/sequence.xml",

        # 3. Foundational Data
        'data/property_type.xml',
        'data/amenity_data.xml',
        'data/property_attribute_area.xml',
        'data/estate_city_data.xml',

        # 4. Main Data
        'data/property_data.xml',

        # 5. Root Menus (Must load before view files can use them as parents)
        "views/menu.xml",

        # 6. Views & Child Menus
        "views/attribute_views.xml",
        "views/type_views.xml",
        "views/property_views.xml",
        "views/plan_view.xml",           # Will now successfully find the parent menu
        "views/specification_view.xml",  # Will now successfully find the parent menu
        "views/amenity_views.xml",
        "views/location_views.xml",
        "views/badge_views.xml",
    ],

    "images": [
    "static/description/banner.png",
    "static/description/icon.png",
    ],
    
    "demo": [
        # Demo data is automatically loaded last, which is correct
        "demo/property_demo.xml",
    ],
    "installable": True,
    "application": True,
}