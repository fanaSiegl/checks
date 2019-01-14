# PYTHON script

'''
Check ABAQUS : CONTACTs
=======================

Checks foo.

* searches all foo
* checks something

Parameters
------------

* param 1 - efs
* param 2 - segfes

Fix function
------------

* w4fw4
* ew4f r4f


'''

import os
import ansa
from ansa import base, constants, mesh, session
import re
from datetime import date
import getpass

# ==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'check_el_ex_fix_tied_ABA.py'))

# ==============================================================================

ExecCheckQualityElements = check_el_ex_fix_tied_ABA.ExecCheckQualityElements
FixCheckQualityElements = check_el_ex_fix_tied_ABA.FixCheckQualityElements
		
# ==============================================================================

checkOptions = { 'name': 'Check ABAQUS : CONTACTs', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements',  os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['CONTACT_PAIR'], 
        'info': 'Check ABAQUS : CONTACTs '}

checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('type_check', 'CONTACT_PAIR')
checkDescription.add_str_param('INTERACTION', '>=1.0')  
checkDescription.add_str_param('ADJUST', 'POS_VAL')
checkDescription.add_str_param('POS_VAL', '>=0.0')  
checkDescription.add_str_param('IF-NOT-CHECK VALUE', '>=0.0')
  
# ==============================================================================