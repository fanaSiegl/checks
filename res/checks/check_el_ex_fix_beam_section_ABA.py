# PYTHON script

'''
Check BEAM section Elements
===========================

Checks foo.

* searches all foo
* checks somethings

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

checkOptions = { 'name': 'Check BEAM section Elements', 
        'exec_action': ('ExecCheckQualityElements', os.path.realpath(__file__)), 
        'fix_action':  ('FixCheckQualityElements', os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['BEAM_SECTION'], 
        'info': 'Check BEAM Elements - hybrid elements'}

checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('optional2', 'H')
checkDescription.add_str_param('type_check', 'BEAM_SECTION')  
  
# ==============================================================================