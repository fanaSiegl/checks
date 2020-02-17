# PYTHON script

'''
PAMCRASH/ABAQUS check parts for Skoda
=====================================

Usage
-----

Check parts for the following rules:

* Number of segments = 5
* Delimiter for part name = __
* Number of digits for thickness = 1
* Max. number of chars = 80
* Contact thickness check = YES

  - the contact thickness should be same as thckness
  - some exceptions: contact thickness should be bigger than 0.5 and smaller then 3 mm

* Thickness by part name check = YES (not for Skoda)

**Primary solver** - ABAQUS/PAMCRASH.

**Fix function** is available for some warnings.

'''

import os, ansa
from ansa import base, constants, session

# ==============================================================================

DEBUG = 0

if DEBUG:
	PATH_SELF = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'
#	PATH_SELF = os.path.dirname(os.path.realpath(__file__))
else:
	PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

# ==============================================================================

class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']

# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):

	solver = params['Solver']
	solver_name = solver.upper()
	if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH':
		if solver_name == 'ABAQUS':
			solver = constants.ABAQUS
			ent = ["SHELL_SECTION","SOLID_SECTION", "MEMBRANE_SECTION"]
			id_mat = 'MID'
			thickness = 'T'
			remove_text = "_SECTION"
		if solver_name == 'PAMCRASH':
			solver = constants.PAMCRASH
			ent = ["PART_SHELL","PART_SOLID", "PART_MEMBRANE"]
			id_mat = 'IMAT'
			remove_text = "PART_"
			thickness = 'h'
			c_thickness = 'TCONT'
	else:
		session.Quit()

	t4 = base.CheckReport('Number of segments')
	t5 = base.CheckReport('Thickness same as in part name')
	t6 = base.CheckReport('Rounding of thickness')
	t7 = base.CheckReport('Filling the TCONT based on SKODA')
	t8 = base.CheckReport('Lenght of part name')

	t4.has_fix = False
	t5.has_fix = True
	t6.has_fix = True
	t7.has_fix = True
	t8.has_fix = False

	parts = base.CollectEntities(solver, entities, ent, prop_from_entities=True)
	deck = base.CurrentDeck()

	for part in parts:
		name = part._name
		name_list = name.split(params['Delimiter for part name'])
		thickness_number = part.get_entity_values(solver, [thickness])
		if thickness_number:
			thickness_number = float(thickness_number[thickness])
		else:
			thickness_number = 0.0

		# Check of number of segments
		if len(name_list) != int(params['Number of segments']):
			t4.add_issue(entities = [part], status = 'Error', description = 'Wrong numer of segment')

		else:
			# Check of number of chars
			if len(name) > int(params['Max. number of chars']):
				t8.add_issue(entities = [part], status = 'Error',
					description = 'The lenght is bigger then ' + str(params['Max. number of chars']))

			# Check of rouding
			thickness_number_round = round(thickness_number, int(params['Number of digits for thickness']))
			if float(thickness_number) != thickness_number_round:
				t6.add_issue(entities = [part], status = 'Error',
					description = 'Thickness -  digits are bigger then '+str(params['Number of digits for thickness']),
					thickness = str(thickness_number),
					thickness_suggest = str(thickness_number_round),
					__key  = thickness,
					__solver = str(solver))

			# Check of thickness by info from part name
			if str(params['Thickness by part name check']) == 'YES':
				if (str(params['Segment of thickness name']) != "0" and str(params['Segment of thickness name']) != "var") and str(params['Segment of thickness name']) != "" :
					thickness_from_part_name = name_list[int(params['Segment of thickness name'])-1]
					thickness_from_part_name = thickness_from_part_name.replace("mm","")
					thickness_from_part_name = thickness_from_part_name.replace("t", "")
					thickness_from_part_name = thickness_from_part_name.replace("_", "")

					# TODO ValueError: could not convert string to float: 'TM2'
					if float(thickness_number) != float(thickness_from_part_name):
						t5.add_issue(entities=[part], status='Error',
							description='Thickness is different than ' + thickness_from_part_name,
							thickness=str(thickness_number),
							thickness_suggest=str(thickness_from_part_name),
							__key=thickness, __solver=str(solver))

			# Check of contact thickness
			if deck == constants.PAMCRASH and str(params['Contact thickness check']) == 'YES':
				c_thickness_number = part.get_entity_values(solver, [c_thickness])

				if c_thickness_number:
					c_thickness_number = float(c_thickness_number[c_thickness])
				else:
					c_thickness_number = 0.0

				if 'CONNECTION' in name:
					if float(c_thickness_number) != 0.5:
						t7.add_issue(entities = [part], status = 'Error',
							description = 'Contact thickness for CONNECTION parts should be 0.5 mm',
							c_thickness = str(c_thickness_number),
							c_thickness_suggest = str(0.5),
							__key = c_thickness,
							__solver = str(solver))
						continue

				if c_thickness_number == 0.0:
					c_thickness_suggest = thickness
					if c_thickness_number < 0.5:
						c_thickness_number = 0.5
					if c_thickness_number > 3:
						c_thickness_number = 3

					t7.add_issue(entities = [part], status = 'Error',
						description='Contact thickness is different then thickness '+thickness_number,
						c_thickness=str(c_thickness_number),
						thickness=str(thickness_number),
						c_thickness_suggest=c_thickness_number,
						__key=c_thickness,
						__solver=str(solver))

				else:
					if  c_thickness_number != thickness_number and thickness_number <= 3 and thickness_number >= 0.5:
						t7.add_issue(entities=[part], status='Warning',
							description='Contact thickness should be same as thickness',
							c_thickness=str(c_thickness_number),
							thickness=str(thickness_number),
							c_thickness_suggest=str(thickness_number),
							__key=c_thickness,
							__solver=str(solver))

					if c_thickness_number < 0.5 and thickness_number < 0.5:
						t7.add_issue(entities=[part], status='Error',
							description='Contact thickness should be >= 0.5',
							c_thickness=str(c_thickness_number),
							thickness=str(thickness_number),
							c_thickness_suggest='0.5' ,
							__key=c_thickness,
							__solver=str(solver))

					if c_thickness_number > 3 and thickness_number >= 3.0:
						t7.add_issue(entities = [part], status = 'Error',
							description='Contact thickness should be <= 3',
							c_thickness=str(c_thickness_number),
							thickness=str(thickness_number),
							c_thickness_suggest='3',
							__key=c_thickness,
							__solver=str(solver))

	# TODO OSError: [Errno5] Input/output error - can't fix
	print('Properties check for PAMCRASH - SKODA. Number of errors:',
		len(t4.issues) + len(t5.issues) + len(t7.issues))
	return [t4, t5, t6, t7, t8]

# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):

	for issue in issues:
		ents = issue.entities
		if issue.description.startswith( 'Contact thickness' ):
			field = {issue.__key:issue.c_thickness_suggest}

		if issue.description.startswith( 'Thickness' ):
			field = {issue.__key:issue.thickness_suggest}
		for ent in ents:
			success = ent.set_entity_values(int(issue.__solver), field)
			if success == 0:
				issue.is_fixed = True

# ==============================================================================

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check parts for SKODA/NISSAN (ABA/PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks parts'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('Number of segments', '5')
checkDescription.add_str_param('Segment of thickness name', '2')
checkDescription.add_str_param('Number of digits for thickness', '1')
checkDescription.add_str_param('Max. number of chars', '80')
checkDescription.add_str_param('Contact thickness check', 'YES')
checkDescription.add_str_param('Thickness by part name check', 'YES')
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Delimiter for part name', '__')

# ==============================================================================

if __name__ == '__main__' and DEBUG:
	
	testParams = {
		'Number of segments': '5',
		'Segment of thickness name': '2',
		'Number of digits for thickness': '1',
		'Max. number of chars': '80',
		'Contact thickness check': 'YES',
		'Thickness by part name check': 'YES',
		'Solver': 'PAMCRASH',
		'Delimiter for part name': '__'}
	check_base_items.debugModeTestFunction(CheckItem, testParams)

# ==============================================================================
