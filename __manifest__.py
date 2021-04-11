# -*- coding: utf-8 -*-

{
    'name': 'Mining Fuel Report',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Mining Management',
    'depends': [
        'mining_production',
    ],
    'data': [
        "wizard/fuel_diesel_report.xml",
        # "wizard/fleet_vehicle_fuel_report.xml",

        "report/fuel_diesel_report.xml",
        "report/fuel_diesel_temp.xml",

        # "report/fleet_vehicle_fuel_report.xml",
        # "report/fleet_vehicle_fuel_temp.xml",
    ],
    'qweb': [
        # 'static/src/xml/cashback_templates.xml',
    ],
    'demo': [
        # 'demo/sale_agent_demo.xml',
    ],
    "installable": True,
	"auto_instal": False,
	"application": False,
}