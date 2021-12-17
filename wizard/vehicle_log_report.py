# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta
import dateutil
import calendar 
import logging
_logger = logging.getLogger(__name__)

class MiningVehicleLogReport(models.TransientModel):
    _name = 'vehicle.log.report'

    @api.model
    def _default_config(self):
        ProductionConfig = self.env['production.config'].sudo()
        production_config = ProductionConfig.search([ ( "active", "=", True ) ]) 
        if not production_config :
            raise UserError(_('Please Set Configuration file') )
        return production_config[0]

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    service_type_ids = fields.Many2many('fleet.service.type', 'vehicle_log_report_fleet_service_type_rel', 'report_id', 'service_type_id', string='Service Types' )
    
    def get_logs_by_type(self):
        start = datetime.datetime.strptime( self.start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime( self.end_date, '%Y-%m-%d')
        days = abs( relativedelta(end, start).days )

        vehicle_logs = self.env['fleet.vehicle.log.services'].search([ ( 'cost_subtype_id', 'in', self.service_type_ids.ids ), ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ) ], order="vehicle_id asc")
        service_type_vehicle_logs_dict = {}
        for vehicle_log in vehicle_logs :
            service_type_name = vehicle_log.cost_subtype_id.name
            if service_type_vehicle_logs_dict.get( service_type_name, False ):
                service_type_vehicle_logs_dict[service_type_name]["items"] += [
                        {
                            "name" : vehicle_log.name ,
                            "date" : vehicle_log.date ,
                            "vehicle" : vehicle_log.vehicle_id.name ,
                            "product" : vehicle_log.product_id.name ,
                            "product_uom_qty" : vehicle_log.product_uom_qty,
                            "price_unit" : vehicle_log.price_unit,
                            "state" : vehicle_log.state,
                        }
                    ]
            else:
                service_type_vehicle_logs_dict[service_type_name]= {
                    "items" : [
                        {
                            "name" : vehicle_log.name ,
                            "date" : vehicle_log.date ,
                            "vehicle" : vehicle_log.vehicle_id.name ,
                            "product" : vehicle_log.product_id.name ,
                            "product_uom_qty" : vehicle_log.product_uom_qty,
                            "price_unit" : vehicle_log.price_unit,
                            "state" : vehicle_log.state,
                        }
                    ],
                    "name": service_type_name
                }

        # vehicle_log_date_dict
        # for i in range( days+1 ) :
        #     dates += [ date ]
        #     vehicle_log_date_dict[ date ] = {
        #         "date" : date,
        #         "begining_balance" : 0,
        #         "in" : 0,
        #         "out" : 0,
        #         "balance" : 0
        #     }
        #     start += datetime.timedelta(days=1)
        #     date = start.strftime( '%Y-%m-%d')
        
        # vehicle_log_date_dict["dates"] = dates

        return service_type_vehicle_logs_dict
    @api.multi
    def action_print(self):

        final_dict = {}
        final_dict["logs_by_type"] = self.get_logs_by_type()
        
        datas = {
            'ids': self.ids,
            'model': 'fuel.diesel.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].with_context( landscape=True ).get_action(self,'mining_report.vehicle_log_report_temp', data=datas)        


    