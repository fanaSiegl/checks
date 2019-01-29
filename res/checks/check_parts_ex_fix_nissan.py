# PYTHON script

'''
PAMCRASH check parts for Nissan
======================================
Description:
Check the parts for following rules:
* Number of segments = 4
* Delimiter for part name = __
* Number of digits for thickness = 1
* Max. number of chars = 80
* Contact thickness check = NO (YES for Skoda)
* Thickness by part name check = YES 
* Segment of thickness name = 2 
* Solver - PAMCRASH

Fix:
* function of fix is available for some warnings
'''

import os
import ansa
from ansa import base, constants, mesh, session
import re

# ==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'check_parts_ex_fix.py'))

# ==============================================================================

ExecCheckParts = check_parts_ex_fix.ExecCheckParts
FixcCheckParts = check_parts_ex_fix.FixcCheckParts

# ==============================================================================

checkOptions = { 'name': 'Check Parts for NISSAN (ABA/PAM)', 
    'exec_action': ('ExecCheckParts', os.path.realpath(__file__)), 
    'fix_action':  ('FixcCheckParts', os.path.realpath(__file__)), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['SHELL','MEMBRANE','SOLID'], 
    'info': 'Checks Parts'} 
    
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('Number of segments', '4')
checkDescription.add_str_param('Segment of thickness name', '3')  
checkDescription.add_str_param('Number of digits for thickness', '1') 
checkDescription.add_str_param('Max. number of chars', '80')  
checkDescription.add_str_param('Contact thickness check', 'NO')   
checkDescription.add_str_param('Thickness by part name check', 'YES')   
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Delimiter for part name', '__')  
  
# ==============================================================================
