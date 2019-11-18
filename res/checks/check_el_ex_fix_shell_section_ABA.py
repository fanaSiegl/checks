# PYTHON script

'''
ABAQUS check shells
===================

Checks reduced shell elements.
 
**Fix function**: add optional1 = R

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

checkOptions ={ 'name': 'Check SHELL section ', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements', os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['SHELL_SECTION'], 
        'info': 'Check SHELL section - reduced elements'}

checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('optional1', 'R')
checkDescription.add_str_param('type_check', 'SHELL_SECTION')
  
# ==============================================================================