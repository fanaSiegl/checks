# PYTHON script

import os
from ansa import base
from ansa import constants
import re
from ansa import calc
from datetime import date
import getpass

# ==============================================================================

class entity_cls (base.Entity):
	def __init__(self, id, type_check):
		super().__init__( constants.ABAQUS, id, type_check)

		
	def check(self,params):
		fieldConnector = ['G1','G2']
		dict_node = self.get_entity_values(constants.ABAQUS, fieldConnector)
		pos_A = dict_node['G1'].position
		pos_B = dict_node['G2'].position		

		
		fieldConnectorSection = ['ORIENT_1']		
		connectorSections = base.CollectEntities(constants.ABAQUS, self, "CONNECTOR_SECTION",prop_from_entities = True)		
		#print('connectorSections',connectorSections)		
		dict_cs = connectorSections[0].get_entity_values(constants.ABAQUS, fieldConnectorSection)		
		#print('dict_cs',dict_cs)
		ret4x3 = calc.GetCoordTransformMatrix4x3(constants.ABAQUS, dict_cs['ORIENT_1'], 0, 0, 0)

		pos_A = calc.GlobalToLocal(dict_cs['ORIENT_1']._id, pos_A, "point")
		pos_B = calc.GlobalToLocal(dict_cs['ORIENT_1']._id, pos_B, "point")
		
		dist_x , dist_y, dist_z =pos_B[0] - pos_A[0],pos_B[1] - pos_A[1],pos_B[2] - pos_A[2]
		#print(dist_x , dist_y, dist_z)
		
		connectorBehavior = base.CollectEntities(constants.ABAQUS, self, "CONNECTOR BEHAVIOR",mat_from_entities = True)
		field_stop = ['*STOP', 'STP>data']
		dict_stop = connectorBehavior[0].get_entity_values(constants.ABAQUS, field_stop)
		field_stop_lim = ['Low.Lim.(1)','Up.Lim.(1)','Low.Lim.(2)','Up.Lim.(2)','Low.Lim.(3)','Up.Lim.(3)']
		#print(dict_stop)
		dict_stop_lim = dict_stop['STP>data'].get_entity_values(constants.ABAQUS, field_stop_lim)
		#print('test')
		print(dict_stop_lim)
		
		status = ''
		if 'Low.Lim.(1)' in dict_stop_lim:
			if not (dist_x > dict_stop_lim ['Low.Lim.(1)'] and dist_x < dict_stop_lim ['Up.Lim.(1)']):
				status = 'Penetration for x - connector x lenght: '+ str(dist_x) + ' , connector x limit:<' + str(dict_stop_lim ['Low.Lim.(1)']) + ',' + str(dict_stop_lim ['Up.Lim.(1)']) + '>'
		if 'Low.Lim.(2)' in dict_stop_lim:
			if not (dist_y > dict_stop_lim ['Low.Lim.(2)'] and dist_y < dict_stop_lim ['Up.Lim.(2)']):
				status = status + 'Penetration for y - connector y lenght: '+ str(dist_x) + ' , connector y limit:<' + str(dict_stop_lim ['Low.Lim.(2)']) + ',' + str(dict_stop_lim ['Up.Lim.(2)']) + '>'
		if 'Low.Lim.(3)' in dict_stop_lim:                            
			if not (dist_z > dict_stop_lim ['Low.Lim.(3)'] and dist_z < dict_stop_lim ['Up.Lim.(3)']):
				status = status + 'Penetration for z - connector z lenght: '+ str(dist_z) + ' , connector z limit:<' + str(dict_stop_lim ['Low.Lim.(3)']) + ',' + str(dict_stop_lim ['Up.Lim.(3)']) + '>'
		print(status)
		return status

# ==============================================================================
	
def ExecCheckQualityElements(entities, params):
	to_report = []
	t = base.CheckReport('Element check' + params['type_check'])			
	t.has_fix = True	
	if entities:
		if not(type(entities) == list):
			entities = [entities]
		if type(entities) == list:
			for entity in entities:
				entity_full = entity_cls(entity._id, params['type_check'])
				entity_full.check(params)
				ent = [base.GetEntity(constants.ABAQUS, params['type_check'], entity._id)]
				status = entity_full.check(params)
				descriptions = ''
				if status != '':
					descriptions = status
					t.add_issue(entities=ent, status="Warning" , description=descriptions)
	to_report.append(t)				
	return to_report

# ==============================================================================

checkOptions = { 'name': 'Check CONNECTOR section Elements ', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements', os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['CONNECTOR'], 
        'info': 'Check CONNECTOR Elements - penetration'}
 
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('type_check', 'CONNECTOR')

# ==============================================================================
