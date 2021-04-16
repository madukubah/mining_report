# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class ReportMining_cost_performance_temp(models.AbstractModel):
    _name = 'report.mining_report.mining_cost_performance_temp'

    @api.model
    def render_html(self, docids, data=None):
        docargs =  {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': data['form'],

            'location_names': data['location_names'],
            'locations': data['locations'],
            'c_code_names': data['c_code_names'],
            'c_codes': data['c_codes'],

            'prod_product_names': data['prod_product_names'],
            '_sr': data['_sr'],
            'loc_sr': data['loc_sr'],
            '_cost_p_ton': data['_cost_p_ton'],
            
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
        # print "===================docargs",docargs
        # _logger.warning( docargs )
        return self.env['report'].render('mining_report.mining_cost_performance_temp', docargs)
