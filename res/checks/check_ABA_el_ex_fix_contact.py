# PYTHON script

'''
Check ABAQUS: CONTACTs
=======================

The script check the ABAQUS contact pairs.

Usage
-----

**Primary solver** - ABAQUS.

* Automatic depenetration ADJUST = 0
* With exception small sliding and clearence = value

'''

import os, ansa
from ansa import base, constants



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['CONTACT_PAIR']



ansa.ImportCode(os.path.join(PATH_SELF, 'check_ABA_el_ex_fix_tied.py'))
exe = check_ABA_el_ex_fix_tied.exe
fix = check_ABA_el_ex_fix_tied.fix

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check CONTACTs (ABA)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'ABAQUS: check CONTACTs'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('type_check', 'CONTACT_PAIR')
checkDescription.add_str_param('INTERACTION', '>=1.0')
checkDescription.add_str_param('ADJUST', 'POS_VAL')
checkDescription.add_str_param('POS_VAL', '>=0.0')
checkDescription.add_str_param('IF-NOT-CHECK VALUE', '>=0.0')
checkDescription.add_str_param('IF-CHECK TYPE', 'CONTACT PAIR')

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
