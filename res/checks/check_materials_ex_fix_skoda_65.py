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

import os
import ansa
from ansa import base, constants, mesh, session
import re

# ==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

ansa.ImportCode(os.path.join(PATH_SELF, 'check_materials_ex_fix.py'))

# ==============================================================================

ExecCheckMaterials = check_materials_ex_fix.ExecCheckMaterials
read_configuration_file = check_materials_ex_fix.read_configuration_file
FixcCheckMaterials = check_materials_ex_fix.FixcCheckMaterials

# ==============================================================================

checkOptions = { 'name': 'Check Materials with a checking list (ABA/PAM) - SKODA: 65', 
    'exec_action': ('ExecCheckMaterials', os.path.realpath(__file__)), 
    'fix_action':  ('FixcCheckMaterials', os.path.realpath(__file__)), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['SHELL','MEMBRANE','SOLID'], 
    'info': 'Checks Materials'}
    
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('Number of segments', '5')
checkDescription.add_str_param('Segment of material name', '5')  
checkDescription.add_str_param('Type of loadcase', 'SK3165_+65')  
checkDescription.add_str_param('Solver', 'PAMCRASH')   
checkDescription.add_str_param('Matching list', '/data/fem/+software/SKODA_INCLUDE/white_list_bumpers_SK316')   
checkDescription.add_str_param('Delimiter for part name', '__')  
  
# ==============================================================================
