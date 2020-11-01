# -*- coding: utf-8 -*-

{
    'name': 'Fleet Report',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Fleet Management',
    'depends': [
        'fleet',
    ],
    'data': [
        "wizard/fleet_vehicle_report.xml",

        "report/fleet_vehicle_report.xml",
        "report/fleet_vehicle_temp.xml",
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
