# PYTHON script

'''
PAMCRASH check materials for Skoda
==================================

Check materials based matching list and name in properties name.

Usage
-----

**Primary solver** - ABAQUS/PAMCRASH/NASTRAN.

**User defined parameters**:

- delimiter for part name of segment e.g. __
- number of segments of names of properties e.g. 5
- type of loadcase e.g. COMMON
  in case of empty parametr, the list of loadcases is popup
  in case of only one loadcase in matching list is appied just this
- segment of material name e.g. 5
- matching list - /data/fem/+software/SKODA_INCLUDE/white_list

**Fix function** is available for some warnings.

'''

import os, ansa
from ansa import base, constants

# ==============================================================================

DEBUG = 0

if DEBUG:
	PATH_SELF = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'
#	PATH_SELF = os.path.dirname(os.path.realpath(__file__))
else:
	PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

ansa.ImportCode(os.path.join(PATH_SELF, 'check_PAM_materials_ex_fix.py'))
exe = check_PAM_materials_ex_fix.exe
fix = check_PAM_materials_ex_fix.fix

# ==============================================================================

class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']

# ==============================================================================

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check materials with a checking list (ABA/PAM/NAS) - SKODA: -10',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks materials'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('Number of segments', '5')
checkDescription.add_str_param('Segment of material name', '5')
checkDescription.add_str_param('Type of loadcase', 'SK3165_-10')
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Matching list', '/data/fem/+software/SKODA_INCLUDE/white_list_bumpers_SK316')
checkDescription.add_str_param('Delimiter for part name', '__')

# ==============================================================================

if __name__ == '__main__' and DEBUG:
	
	testParams = {
		'Number of segments': '5',
		'Segment of material name': '5',
		'Type of loadcase': 'SK3165_-10',
		'Solver': 'PAMCRASH',
		'Matching list': '/data/fem/+software/SKODA_INCLUDE/white_list_bumpers_SK316',
		'Delimiter for part name': '__'}

	check_base_items.debugModeTestFunction(CheckItem, testParams)

# ==============================================================================
