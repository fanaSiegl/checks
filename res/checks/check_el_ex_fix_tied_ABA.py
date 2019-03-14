# PYTHON script

'''
ABAQUS check TIEDs
===================
Description:
* check the reduced shell elements
POS_TOLER,  DISTANCE= 5, TYPE_tie_coefficients = SURFACE TO SURFACE, ADJUST = NO
 
Fix function
------------
* fixed to suggested setting
'''

import os
from ansa import base
from ansa import constants
import re
from datetime import date
import getpass

# ==============================================================================

class entity_cls (base.Entity):
	def __init__(self, id, type_check):
		super().__init__( constants.ABAQUS, id, type_check)

		
	def check(self,params):
		vals_ent = []
		if_cond = []
		params_out = {}
		for par in params:
			if "IF-CHECK" in par:
				if_cond.append(par)
				par = par.replace("IF-CHECK " , "")
			if "IF-NOT-CHECK" in par:
				if_cond.append(par)
				par = par.replace("IF-NOT-CHECK " , "")				
			if par != 'type_check':
				vals_ent.append(par)
				
		ents = base.GetEntityCardValues(constants.ABAQUS, self, vals_ent)
		result = {}
		for val in params:
			if val not in ents:
				ents [val] = None
			if val != 'type_check':
				status,number = self.evaluate(ents[val],params [val])
				result [val] = [ents[val], status, params [val]]

				if "IF-CHECK" in val:
					val_cond = val.replace("IF-CHECK " , "")
					if val_cond not in ents:
						ents[val_cond] = " "			
					status,number = self.evaluate(ents[val_cond],params [val])
					del result [val]
					if status != 'OK':
						result = {}
						break
					
				if "IF-NOT-CHECK" in val:
					val_cond = val.replace("IF-NOT-CHECK " , "")
					if val_cond not in ents:
						ents[val_cond] = " "	
					status,number = self.evaluate(ents[val_cond],params [val])
					del result [val]
					if status == 'OK':
						result = {}
						break
						
			if (val != 'type_check') and ("IF-CHECK" not in val) and ("IF-NOT-CHECK" not in val):
				params_out [val] = number
				
		return result, if_cond, params_out
	
	def evaluate(self, condition ,text ):
		st_list = ['OK', 'Warning','Error' ]
		
		if text == None:
			text = ''					
		if type(text) == str:
			text = text.replace(" " , "")
		
		
		if "=" in str(text) or "<" in str(text) or ">" in str(text):
			if type(condition) == str:
				condition = condition.replace(" " , "")
			if (condition == '') or (condition == None):
				condition = -1.0
			condition = float(condition)
				
		else:
			if type(condition) == str:
				condition = condition.replace(" " , "")
				if  condition == "" or condition == None:
					condition = -1.0		
		
		if "==" in str(text) :
			text_new = text.replace("==" , "")
			number = float(text_new)
			
			if condition == number:
				status = st_list[0]
			else:
				status = st_list[1]
				
		elif "<=" in str(text):
			text_new = text.replace("<=" , "")
			number = float(text_new)
			if number <= number:
				status = st_list[0]
			else:
				status = st_list[1]
				
		elif ">=" in str(text):
			text_new = text.replace(">=" , "")
			number = float(text_new)
			if condition >= number:
				status = st_list[0]
			else:
				status = st_list[1]
			
		elif ">" in str(text) and not("=" in str(text)):
			text_new = text.replace(">" , "")
			number = float(text_new)
			if condition > number:
				status = st_list[0]
			else:
				status = st_list[1]		
		elif "<" in str(text) and not("=" in str(text)):
			text_new = text.replace("<" , "")
			number = float(text_new)
			if condition < number:
				status = st_list[0]
			else:
				status = st_list[1]
		else:
			number = text
			if str(number) == str(condition):
				status = st_list[0]
			else:
				status = st_list[1]
				
		return status, number

# ==============================================================================
	
def ExecCheckQualityElements(entities, params):
	#print('test')
	to_report = []
	t = base.CheckReport('Element check' + params['type_check'])			
	t.has_fix = True	
	#print(params)	
	#print(entities)
	if entities:
		if not(type(entities) == list):
			entities = [entities]
			
		if type(entities) == list:
			for entity in entities:
				entity_full = entity_cls(entity._id, params['type_check'])
				entity_full.check(params)
				ent = [base.GetEntity(constants.ABAQUS, params['type_check'], entity._id)]
				result,if_cond,params_out = entity_full.check(params)
				descriptions = ''
				for val, res  in result.items():
					if res[1] == 'Warning':
						descriptions = descriptions + ' '+ str(val) + '=' +str(res[0])+' '
					if res[1] == 'OK':
						del params_out[val]
				if descriptions != '':
					t.add_issue(entities=ent, status="Warning" , description=descriptions, param_to_fix = str(params_out))
#
	to_report.append(t)				
	return to_report

# ==============================================================================

def FixCheckQualityElements(issues):
	print('Fixed')
	for issue in issues:
		dict_param = {}
		problem_description = issue.description
		param_to_fix = issue.param_to_fix
		param_to_fix = re.sub('[{}\'\ ]', '', param_to_fix)
		param = param_to_fix.split(',')
		for par in param:
			print(par)
			values = par.split(':')
			if values[0] != 'type_check':
				dict_param [values[0]] = values[1]
		entities = issue.entities
		for ent in entities:
			success = ent.set_entity_values(constants.ABAQUS, dict_param)
			if success == 0:
				issue.is_fixed = True

# ==============================================================================

checkOptions = { 'name': 'Check ABAQUS : TIEDs ', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements',  os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['TIE'], 
        'info': 'Checks ABAQUS TIEDs'}
    
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('type_check', 'TIE')  
checkDescription.add_str_param('PARAM', 'POS_TOLER')
checkDescription.add_str_param('DISTANCE', '==5')
checkDescription.add_str_param('TYPE_tie_coefficients', 'SURFACE TO SURFACE')
checkDescription.add_str_param('ADJUST', 'NO')  
  
# ==============================================================================