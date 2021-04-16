# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar 
import logging
_logger = logging.getLogger(__name__)

class MiningCostPerformanceReport(models.TransientModel):
    _name = 'mining.cost.performance.report'

    @api.model
    def _default_config(self):
        ProductionConfig = self.env['production.config'].sudo()
        production_config = ProductionConfig.search([ ( "active", "=", True ) ]) 
        if not production_config :
            raise UserError(_('Please Set Configuration file') )
        return production_config[0]

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    pit_ids = fields.Many2many('production.pit', 'cost_performance_report_pit_rel', 'report_id', 'pit_id', string='Pits' )
    
    @api.multi
    def action_print(self):
        # separate vehicle cost and tag log
        tag_ids = self.env['production.cop.tag'].search( [] )
        tag_ids = tag_ids.ids
        service_types = self.env['fleet.service.type'].search([ ( 'tag_id', 'in', tag_ids ) ])
        stag_ids = [ service_type.tag_id.id for service_type in service_types ]

        production_config = self._default_config()
        config_tag_ids = [ 
            production_config.rit_tag_id.id, 
            production_config.hm_tag_id.id, 
            production_config.wt_tag_id.id,
            ]

        _logger.warning( config_tag_ids )
        stag_ids += config_tag_ids
        _logger.warning( stag_ids )
        tag_ids = [ x for x in tag_ids if x not in stag_ids ]
        # End separate vehicle cost and tag log
        request = ("select COALESCE(data.cost_code, 'OTHER') as cost_code , COALESCE(data.location, 'OTHER') as location, SUM( base.cost_per_value * data.value ) as amount, SUM(base.amount) as total_amount" +\
                    " from (( select fl.name as vehicle, cc.name as cost_code, loc.name as location, SUM(hm.value) as value" +\
                    "		from ( " +\
                    "			select * from production_vehicle_hourmeter_log " +\
                    "			where state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"') hm " +\
                    "		inner join fleet_vehicle fl on fl.id = hm.vehicle_id " +\
                    "		inner join production_cost_code cc on cc.id = hm.cost_code_id " +\
                    "		inner join stock_location loc on loc.id = hm.location_id " +\
                    "		group by fl.name, cc.name, loc.name) UNION " +\
                    "	( select fl.name as vehicle, cc.name as cost_code, loc.name as location, SUM(rit.minutes) as value " +\
                    "		from ( " +\
                    "			select * from production_ritase_counter " +\
                    "			where state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"') rit " +\
                    "		inner join fleet_vehicle fl on fl.id = rit.vehicle_id " +\
                    "		inner join production_cost_code cc on cc.id = rit.cost_code_id " +\
                    "		inner join stock_location loc on loc.id = rit.location_id " +\
                    "		group by fl.name, cc.name, loc.name)) as data \n" +\
                    " FULL OUTER JOIN " +\
                    " ( " +\
                    "	select v_cost.vehicle, SUM(v_cost.value) as value, SUM(v_cost.amount) as amount, ( SUM(v_cost.amount)/ NULLIF(SUM(v_cost.value),0) ) as cost_per_value " +\
                    "	from ((select fl.name as vehicle, SUM(hm.value) as value, SUM(hm.amount) as amount " +\
                    "			from (" +\
                    "				select * from production_vehicle_hourmeter_log " +\
                    "				where state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"' ) hm " +\
                    "			inner join fleet_vehicle fl on fl.id = hm.vehicle_id " +\
                    "			group by fl.name ) UNION " +\
                    "		(select fl.name as vehicle, SUM(rit.minutes) as value, SUM(rit.amount) as amount " +\
                    "			from ( " +\
                    "				select * from production_ritase_counter " +\
                    "				where state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"' ) rit " +\
                    "			inner join fleet_vehicle fl on fl.id = rit.vehicle_id " +\
                    "			group by fl.name ) UNION " +\
                    "		( select fl.name as vehicle, SUM( 0 ) as value, SUM(vc.amount) as amount " +\
                    "			from (" +\
                    "				select * from fleet_vehicle_cost " +\
                    "				where state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"' ) vc " +\
                    "			inner join fleet_vehicle fl on fl.id = vc.vehicle_id " +\
                    "			group by fl.name )) v_cost " +\
                    "	group by v_cost.vehicle " +\
                    "	order by v_cost.vehicle " +\
                    ") as base " +\
                    "on base.vehicle = data.vehicle " +\
                    "group by data.cost_code, data.location " +\
                    "order by data.cost_code, data.location "
                    )
        self.env.cr.execute(request)
        
        cost_per_locations = self.env.cr.dictfetchall()

        pit_ids = self.env['production.pit'].search( [ ] )
        pit_names = [ pit_id.location_id.name for pit_id in pit_ids ]
        cost_code_ids = self.env['production.cost.code'].search( [ ] )

        c_codes =  [ cost_code_id.name for cost_code_id in cost_code_ids ]
        c_codes += [ "OTHER" ]

        c_code_names =  {}
        for cost_code_id in cost_code_ids :
            c_code_names[ cost_code_id.name ] = 0
        c_code_names[ "OTHER" ] = 0
        location_names =  {}
        location_names[ "OTHER" ] = 0

        locations = []
        
        location_c_code_dict = {}
        location_c_code_dict['OTHER'] = {}
        for cost_code_id in cost_code_ids :
            location_c_code_dict[ 'OTHER' ][ cost_code_id.name ] = 0
        location_c_code_dict['OTHER']['OTHER'] = 0

        for cost_per_location in cost_per_locations :
            c_code = cost_per_location["cost_code"]
            location = cost_per_location["location"]
            if location =='OTHER' and location =='OTHER' : 
                location_c_code_dict['OTHER']['OTHER'] += cost_per_location["total_amount"]
                c_code_names[ "OTHER" ] += cost_per_location["total_amount"]
                location_names[ "OTHER" ] += cost_per_location["total_amount"]
                continue

            if location not in pit_names : 
                location = 'OTHER'
            if location_c_code_dict.get( location, False ):
                location_c_code_dict[ location ][ c_code ] += cost_per_location["amount"]
                c_code_names[ c_code ] += cost_per_location["amount"]
                location_names[ location ] += cost_per_location["amount"]
            else :
                locations += [ location ]
                location_c_code_dict[ location ] = {}
                for cost_code_id in cost_code_ids :
                    location_c_code_dict[ location ][ cost_code_id.name ] = 0
                location_c_code_dict[ location ][ 'OTHER' ] = 0

                location_c_code_dict[ location ][ c_code ] += cost_per_location["amount"]
                c_code_names[ c_code ] += cost_per_location["amount"]
                location_names[ location ] = cost_per_location["amount"]
        locations += [ 'OTHER' ]

        _logger.warning( "("+','.join( [ str(x) for x in tag_ids ] ) + ")" )
        # COP TAG LOG
        request = "select SUM(amount) as total_amount from production_cop_tag_log where "
        if tag_ids :
            request += "tag_id in " + "("+','.join( [ str(x) for x in tag_ids ] ) + ") AND "
        request += "state='posted' AND date BETWEEN '"+self.start_date+"' AND '"+self.end_date+"' "

        self.env.cr.execute(request)
        
        tag_logs = self.env.cr.dictfetchall()
        for tag_log in tag_logs :
            location_c_code_dict['OTHER']['OTHER'] += tag_log["total_amount"]
            c_code_names[ "OTHER" ] += tag_log["total_amount"]
            location_names[ "OTHER" ] += tag_log["total_amount"]

        final_dict = location_c_code_dict
        datas = {
            'ids': self.ids,
            'model': 'fuel.diesel.report',
            'form': final_dict,
            'location_names': location_names,
            'locations': locations,
            'c_code_names': c_code_names,
            'c_codes': c_codes,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].with_context( landscape=True ).get_action(self,'mining_report.mining_cost_performance_temp', data=datas)        


    @api.multi
    def action_print2(self):
        # separate vehicle cost and tag log
        tag_ids = self.env['production.cop.tag'].search( [] )
        tag_ids = tag_ids.ids
        service_types = self.env['fleet.service.type'].search([ ( 'tag_id', 'in', tag_ids ) ])
        stag_ids = [ service_type.tag_id.id for service_type in service_types ]

        production_config = _default_config()
        config_tag_ids = [ 
            production_config.rit_tag_id.id, 
            production_config.hm_tag_id.id, 
            production_config.wt_tag_id.id,
            ]
        stag_ids += config_tag_ids
        tag_ids = [ x for x in tag_ids if x not in stag_ids ]
        # End separate vehicle cost and tag log
        vehicle_costs = self.env['fleet.vehicle.cost'].search( [ ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ), ( "state", "=", "posted" )  ], order="name asc" )
        tag_logs = self.env['production.cop.tag.log'].search( [ ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ), ( "tag_id", "in", tag_ids ), ( "state", "=", "posted" )  ], order="date asc" )

        ritase_counter = self.env['production.ritase.counter'].search( [ ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ), ( "state", "=", "posted" ) ] )
        hourmeter_log = self.env['production.vehicle.hourmeter.log'].search( [ ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ), ( "state", "=", "posted" ) ] )
        watertrucks = self.env['production.watertruck.counter'].search( [ ( "date", ">=", self.start_date ), ( "date", "<=", self.end_date ), ( "state", "=", "posted" )  ] )

        cost_code_ids = self.env['production.cost.code'].search( [ ] )
        c_code_location_dict = {}
        for cost_code_id in cost_code_ids:
            c_code_location_dict[ cost_code_id.name ] = {}
            for pit_id in pit_ids:
                location_name = pit_id.location_id.name if pit_id.location_id else "Other"
                c_code_location_dict[ cost_code_id.name ][ location_name ] = { "value":0,"amount":0,}
            c_code_location_dict[ cost_code_id.name ][ "Other" ] = {"value":0,"amount":0,}
        c_code_location_dict[ "Other" ] = {}
        for pit_id in pit_ids:
            location_name = pit_id.location_id.name if pit_id.location_id else "Other"
            c_code_location_dict[ "Other" ][ location_name ] = {"value":0,"amount":0,}
        c_code_location_dict[ "Other" ][ "Other" ] = {"value":0,"amount":0,}
        
        
        vehicle_ids = self.env['fleet.vehicle'].search( [ ] )
        vehicle_cost_dict = {}
        for vehicle_id in vehicle_ids:
            temp = {}
            temp[ "name" ] = vehicle_id.name
            for cost_code_id in cost_code_ids:
                temp[ cost_code_id.name ] = {}
                for pit_id in pit_ids:
                    location_name = pit_id.location_id.name if pit_id.location_id else "Other"
                    temp[ cost_code_id.name ][ location_name ] = { "value":0,"amount":0,}
                temp[ cost_code_id.name ][ "Other" ] = { "value":0,"amount":0,}
            temp[ "Other" ] = {}
            for pit_id in pit_ids:
                location_name = pit_id.location_id.name if pit_id.location_id else "Other"
                temp[ "Other" ][ location_name ] = {"value":0,"amount":0,}
            temp[ "Other" ][ "Other" ] = {"value":0,"amount":0,}
            
            temp[ "total_working_value" ] = 0
            temp[ "total_working_cost" ] = 0
            vehicle_cost_dict[ vehicle_id.name ] = temp

        final_dict = {}
        datas = {
            'ids': self.ids,
            'model': 'fuel.diesel.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].with_context( landscape=True ).get_action(self,'mining_report.mining_cost_performance_temp', data=datas)
        