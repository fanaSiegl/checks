# PYTHON script

'''
PAMCRASH check parts for Nissan
======================================

Usage
-----

Check parts for the following rules:

* Number of segments = 4
* Delimiter for part name = __
* Number of digits for thickness = 1
* Max. number of chars = 80
* Contact thickness check = NO (YES for Skoda)
* Thickness by part name check = YES
* Segment of thickness name = 2

**Primary solver** - ABAQUS/PAMCRASH.

**Fix function** is available for some warnings.

'''

import os, ansa
from ansa import base, constants



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']



ansa.ImportCode(os.path.join(PATH_SELF, 'check_PAM_parts_ex_fix.py'))
exe = check_PAM_parts_ex_fix.exe
fix = check_PAM_parts_ex_fix.fix

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check parts for NISSAN (ABA/PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks parts'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('Number of segments', '4')
checkDescription.add_str_param('Segment of thickness name', '3')
checkDescription.add_str_param('Number of digits for thickness', '1')
checkDescription.add_str_param('Max. number of chars', '80')
checkDescription.add_str_param('Contact thickness check', 'NO')
checkDescription.add_str_param('Thickness by part name check', 'YES')
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Delimiter for part name', '__')

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
