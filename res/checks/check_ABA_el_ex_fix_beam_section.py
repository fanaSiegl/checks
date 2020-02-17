# PYTHON script

'''
ABAQUS check BEAM section Elements
==================================

The script checks if the hybrid elements are used for beams.

Usage
-----

**Primary solver** - ABAQUS.

**Fix function**:

* Add definition type element for BEAM.
* Parameter: optional2 = 'H'.

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

# ==============================================================================

class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['BEAM_SECTION']

# ==============================================================================

ansa.ImportCode(os.path.join(PATH_SELF, 'check_ABA_el_ex_fix_tied.py'))
exe = check_ABA_el_ex_fix_tied.exe
fix = check_ABA_el_ex_fix_tied.fix

# ============== this "checkDescription" is crucial for loading this check into ANSA! =========================

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check BEAM section elements (ABA)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'ABAQUS: check BEAM elements - hybrid elements'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('optional2', 'H')
checkDescription.add_str_param('type_check', 'BEAM_SECTION')

# ==============================================================================

if __name__ == '__main__' and DEBUG:
	
	testParams = {
		'optional2' : 'H',
		'type_check': 'BEAM_SECTION'}
	check_base_items.debugModeTestFunction(CheckItem, testParams)

# ==============================================================================
