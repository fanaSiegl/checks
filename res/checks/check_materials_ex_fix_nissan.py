# PYTHON script

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

checkOptions = { 'name': 'Check Materials with a checking list (ABA/PAM) - NISSAN', 
    'exec_action': ('ExecCheckMaterials', os.path.join(PATH_SELF, 'check_materials_ex_fix.py')), 
    'fix_action':  ('FixcCheckMaterials', os.path.join(PATH_SELF, 'check_materials_ex_fix.py')), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['SHELL','MEMBRANE','SOLID'], 
    'info': 'Checks Materials'}  
 
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('Number of segments', '4')
checkDescription.add_str_param('Segment of material name', '2')
checkDescription.add_str_param('Type of loadcase', 'PV1200')  
checkDescription.add_str_param('Solver', 'PAMCRASH')   
checkDescription.add_str_param('Matching list', '/data/ostatni/NISSAN/BATTERY_CASE/SCRIPTS/white_list')   
checkDescription.add_str_param('Delimiter for part name', '__')  
  
# ==============================================================================
