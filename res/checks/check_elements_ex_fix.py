# PYTHON script

'''
PAMCRASH check SHELL elements
=============================

* Check the shell elements based the Nissan lenght ranges (x-y) separated by comma.
* After : are limit percents - limit amount of shell elements which are in range, e.g. 3.5-4.5,5.5-6:<=30.

'''

import os
from ansa import base
from ansa import constants
from ansa import  mesh
import re
import operator
import copy

# ==============================================================================

def evaluate_percents(text, total_len, current_len):
	st_list = ['OK', 'Warning','Error' ]
	percent = 100.0*current_len/total_len	
	
	if "==" in text :
		text_new = text.replace("==" , "")
		number = float(text_new)
		if percent == number:
			status = st_list[0]
		else:
			status = st_list[1]
			
	elif "<=" in text:
		text_new = text.replace("<=" , "")
		number = float(text_new)
		if percent <= number:
			status = st_list[0]
		else:
			status = st_list[1]
			
	elif ">=" in text:
		text_new = text.replace(">=" , "")
		number = float(text_new)
		if percent >= number:
			status = st_list[0]
		else:
			status = st_list[1]
		
	elif ">" in text:
		text_new = text.replace(">" , "")
		number = float(text_new)
		if percent > number:
			status = st_list[0]
		else:
			status = st_list[1]		
	elif "<" in text:
		text_new = text.replace("<" , "")
		number = float(text_new)
		if percent < number:
			status = st_list[0]
		else:
			status = st_list[1]		
	ret = [percent, number, status]
	return ret

# ==============================================================================
		
def ExecCheckQualityElements(entities, params):

	i = 0 
	criteria_matrix_1 = list()
	criteria_matrix_2 = list()
	criteria_matrix = list()
	criteria_percent = list()
	global qualit
	qualit = {}
	qual_n = ('MIN-LEN','MAX-LEN')
	for parameter_name, parameter_value in params.items():
		criteria = parameter_value
		criteria_value =  criteria.split(":")
		criteria_limits = criteria_value[0]

		criteria_matrix = list()
		criteria_percent= list()
		if "LEN" in parameter_name:
			i = i +1 
			criteria_limit = criteria_limits.split(",")
			criteria_matrix_2 = list()			
			for limit in criteria_limit:
				lim = limit.split("-")
				criteria_matrix_1 = list()
				for l in lim:
					criteria_matrix_1.append(l)
				criteria_matrix_2.append(criteria_matrix_1)	
				
			criteria_matrix.extend(criteria_matrix_2)
			criteria_percent.append(criteria_value[1])
			qualit[parameter_name] = criteria_matrix,criteria_percent
	
	total_len = len(entities)
	lenght = list()		
	
	for ent in entities:
		qual = base.ElementQuality(ent, qual_n)	
		lenght.append([ent._id,qual[0],qual[1]])
		
	h={}
	i={}
	j={}
	for it, criteria in qualit.items():
		i[it] = 0
		j[it] = 0
		h[it] = []	
	for min in lenght:
		for it, criteria in qualit.items():
			crit_1 = criteria[0]
			number_criteria	= len(crit_1)
			
			if number_criteria == 2:

				if crit_1 [0][0] and crit_1 [0][1] and crit_1 [1][0] and crit_1 [1][1]:

					if float(min[1])> float(crit_1 [0][0]) and float(min[1])< float(crit_1 [0][1]) :
				
						i[it] = i[it] +1
						h[it].append (base.Entity(constants.PAMCRASH, min[0], "SHELL"))
					elif float(min[2])> float(crit_1 [1][0]) and float(min[2])< float(crit_1 [1][1]) :
				
						i[it] = i[it] +1
						h[it].append (base.Entity(constants.PAMCRASH, min[0], "SHELL"))

			if number_criteria == 1:

				if crit_1 [0][0] and crit_1 [0][1]:				
					if min[1]> float(crit_1 [0][0]) and min[2]< float(crit_1 [0][1]) :
						i[it] = i[it] +1
						h[it].append (base.Entity(constants.PAMCRASH, min[0], "SHELL"))

	to_report = []
	t1 = base.CheckReport('Origin criteria')
	t2 = base.CheckReport('Weak glue creteria')
	t3 = base.CheckReport('Weak creteria')
	t1.has_fix = True
	t2.has_fix = True
	t3.has_fix = True
						
	for it, criteria in qualit.items():
		status = 'OK'
		number = 0
		cr_1 = criteria[1]
		cr = cr_1[0]
		return_val = 0
		u = evaluate_percents(cr,total_len,len(h[it]))
		name_info = 'Status of Criteria '+it+ " - number of shells in range:"+str(len(h[it]))+' percent:'+str(u[0])+ '  percent target:' + str(cr)
#
		if "old" in it:
			t1.add_issue(entities = h[it], status = u[2], description = name_info)
			t = 1
		elif "new - glue" in it:
			t2.add_issue(entities = h[it], status = u[2], description = name_info)	
		elif "new" in it:
			t3.add_issue(entities = h[it], status = u[2], description = name_info)
	to_report.append(t1)
	to_report.append(t2)
	to_report.append(t3)

	return to_report

# ==============================================================================
	
def FixCheckQualityElements(issues):
	base.All()   
	base.Invert()

	for issue in issues:
		print(issue.has_fix)
		problem_description = issue.description
		ents = issue.entities
# ==============================================================================

checkOptions = { 'name': 'Check Quality of Shell Elements for NISSAN (PAM', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements',  os.path.realpath(__file__)), 
        'deck': constants.PAMCRASH, 
        'requested_types': ['SHELL',"MEMBRANE"], 
        'info': 'Checks Quality of Shell Elements'}

checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('LEN 1 - old ', '4.0-4.5,5.5-6:<=5') 
checkDescription.add_str_param('LEN 2 - old ', '4.5-4.8,5.2-5.5:<=20') 
checkDescription.add_str_param('LEN 3 - old ', '4.8-5.2:>=75')
checkDescription.add_str_param('LEN 4 - old ', '0-0.1,5.5-100:==0')
checkDescription.add_str_param('LEN 5 - old ', '0-4.5,100-101:==0')  
checkDescription.add_str_param('LEN 10 - new ', '4.8-5.2:>=60') 
checkDescription.add_str_param('LEN 11 - new ', '4.5-4.8,5.2-5.5:<=30') 
checkDescription.add_str_param('LEN 12 - new ', '4.0-4.5,5.5-6:<=10')
checkDescription.add_str_param('LEN 13 - new - glue', '4.5-5.5:>=70')
checkDescription.add_str_param('LEN 14 - new - glue', '3.5-4.5,5.5-6:<=30')
  
# ==============================================================================
        
