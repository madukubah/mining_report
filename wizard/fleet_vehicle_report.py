# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar 
import logging
_logger = logging.getLogger(__name__)

class FleetVehicleReport(models.TransientModel):
    _name = 'fleet.vehicle.report'

    @api.model
    def _default_tags(self):
        vehicle_tags = self.env['fleet.vehicle.tag'].sudo().search([ ] )
        return vehicle_tags.ids 

    @api.model
    def _default_states(self):
        vehicle_states = self.env['fleet.vehicle.state'].sudo().search([ ] )
        return vehicle_states.ids 

    # start_date = fields.Date('Start Date', required=True)
    # end_date = fields.Date(string="End Date", required=True)
    tag_ids = fields.Many2many('fleet.vehicle.tag', 'vehicle_report_vehicle_tag_rel', 'vehicle_report_id', 'tag_id', 'Tags', store=True, default=_default_tags )
    state_ids = fields.Many2many('fleet.vehicle.state', 'vehicle_report_vehicle_state_rel', 'vehicle_report_id', 'state_id', 'States', store=True, default=_default_states )
    
    @api.multi
    def action_print(self):
        # vehicles = self.env['fleet.vehicle'].search([ ( 'tag_ids', 'in', self.tag_ids.ids ) ])
        # tag_names = [ tag_id.name for tag_id in self.tag_ids ]
        # # tag_names += [ "-" ]
        # final_dict = {}
        # tag_state_dict = {}
        # for tag_name in tag_names:
        #     tag_state_dict[ tag_name ] = {}
        #     for state_id in self.state_ids :
        #         tag_state_dict[ tag_name ][ state_id.name ] = 0
        # for vehicle in vehicles:
        #     if vehicle.tag_ids and vehicle.state_id :
        #         tag_state_dict[ vehicle.tag_ids[0].name ][ vehicle.state_id.name ] += 1

        vehicles = self.env['fleet.vehicle'].search([ ( 'tag_ids', 'in', self.tag_ids.ids ) ])
        state_names = [ state_id.name for state_id in self.state_ids ]
        tag_names = [ tag_id.name for tag_id in self.tag_ids ]
        final_dict = {}
        tag_state_dict = {}
        tag_total_dict = {}
        for tag_name in tag_names:
            tag_state_dict[ tag_name ] = []
            tag_total_dict[ tag_name ] = {
                "name" : "Total"
            }
            for state_id in self.state_ids :
                tag_total_dict[ tag_name ][ state_id.name ] = 0

        for vehicle in vehicles:
            if vehicle.tag_ids and vehicle.state_id :
                row = {}
                row[ "name" ] = vehicle.name
                for state_id in self.state_ids :
                    row[ state_id.name ] = 1 if vehicle.state_id.name == state_id.name else 0
                tag_state_dict[ vehicle.tag_ids[0].name ] += [ row ]
                tag_total_dict[ vehicle.tag_ids[0].name ][ vehicle.state_id.name ] += 1
        
        final_dict = tag_state_dict
        datas = {
            'ids': self.ids,
            'model': 'fleet.vehicle.report',
            'form': final_dict,
            'tag_total_dict': tag_total_dict,
            'state_names': state_names,
            'date': datetime.datetime.now().strftime("%d/%m/%Y"),
        }
        return self.env['report'].get_action(self,'fleet_report.fleet_vehicle_temp', data=datas)