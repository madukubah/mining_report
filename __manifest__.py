# -*- coding: utf-8 -*-

{
    'name': 'Mining Report',
    'version': '1.0',
    'author': 'Technoindo.com',
    'category': 'Mining Management',
    'depends': [
        'mining_production',
    ],
    'data': [
        "wizard/mining_cost_performance_report.xml",

        "report/mining_cost_performance_report.xml",
        "report/mining_cost_performance_temp.xml",
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