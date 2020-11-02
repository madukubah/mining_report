# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar 
import logging
_logger = logging.getLogger(__name__)

class FleetVehicleFuelReport(models.TransientModel):
    _name = 'fleet.vehicle.fuel.report'

    @api.model
    def _default_tags(self):
        vehicle_tags = self.env['fleet.vehicle.tag'].sudo().search([ ] )
        return vehicle_tags.ids 

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    tag_ids = fields.Many2many('fleet.vehicle.tag', 'vehicle_fuel_report_vehicle_tag_rel', 'vehicle_fuel_report_id', 'tag_id', 'Tags', default=_default_tags )
    
    @api.multi
    def action_print(self):
        log_fuels = self.env['fleet.vehicle.log.fuel'].search([ ( 'date', '>=', self.start_date ), ( 'date', '<=', self.end_date ) ])
        tag_names = [ tag_id.name for tag_id in self.tag_ids ]
        # tag_names += [ "-" ]
        final_dict = {}
        tag_fuel_dict = {}
        for tag_name in tag_names:
            tag_fuel_dict[ tag_name ] = []
        tag_fuel_dict[ "-" ] = []
        for log_fuel in log_fuels:
            row = {}
            row["date"] = log_fuel.date
            row["vehicle_name"] = log_fuel.vehicle_id.name
            if log_fuel.vehicle_id.tag_ids:
                row["vehicle_tag_name"] = log_fuel.vehicle_id.tag_ids[0].name
            else:
                row["vehicle_tag_name"] = "-"
            row["driver_name"] = log_fuel.vehicle_id.driver_id.name
            row["liter"] = log_fuel.liter
            row["price_per_liter"] = log_fuel.price_per_liter
            row["amount"] = log_fuel.amount

            if row["vehicle_tag_name"] in tag_names :
                tag_fuel_dict[ row["vehicle_tag_name"] ] += [ row ]
            # else :
            #     tag_fuel_dict[ row["vehicle_tag_name"] ] = [row]

        final_dict = tag_fuel_dict
        datas = {
            'ids': self.ids,
            'model': 'fleet.vehicle.fuel.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'fleet_report.fleet_vehicle_fuel_temp', data=datas)