# PYTHON script

'''
SKODA check elements
====================

Check the shell and solid elements based the Skoda rules.

Usage
-----

**Primary solver** - both PAMCRASH and ABAQUS.

* Basic check of elements is realized xxx.ansa_qual file
* User defined check element: min_lenght = THICKNESS FACTOR * thickness
* User defined check element for skew : TRIA = 60.0, QUAD = 48.0
* Possible compress list bigger then e.g. 100 lines 

'''

import os
from ansa import base
from ansa import constants
from ansa import  mesh
import re
import operator
import copy
import time

# ==============================================================================
		
def ExecCheckQualityElementsSkoda(entities, params):
    t0 = time.time()
    print('start measure time')
    mesh.ReadQualityCriteria(params['Quality mesh file'])
    
################################################################################    
#                          Solver dependent variable
################################################################################    
    solver = params['Solver']
    solver_name = solver.upper()
    limit_lines = int(params['Detail list for number of errors'])
    if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH':
        if solver_name == 'ABAQUS':
          solver = constants.ABAQUS
          ent = ["SHELL_SECTION","SOLID_SECTION", "MEMBRANE_SECTION"]
          thickness = 'T'
          remove_text = "_SECTION"
          name_part_key = 'PID'
        if solver_name == 'PAMCRASH':
          solver = constants.PAMCRASH      
          ent = ["PART_SHELL","PART_SOLID", "PART_MEMBRANE"]
          thickness = 'h'
          c_thickness= 'TCONT'
          name_part_key = 'IPART'
    else:
        session.Quit()
        
################################################################################    
#                          Basic criteria
################################################################################    
    criterias = { \
        'ASPECT,SHELL,QUAD,TRIA':{'criteria name F11': 'aspect ratio', 'comparison':'<','type':'QUAD,TRIA'},
        'SKEW,SHELL,QUAD,TRIA':{'criteria name F11':"skewness",'comparison':'<','type':'QUAD,TRIA'},
        'WARP,SHELL,QUAD':{'criteria name F11':"warping",'comparison':'<','type':'QUAD'},
        'TAPER,SHELL,QUAD':{'criteria name F11':"taper",'comparison':'>','type':'QUAD'},
        'CRASH,SHELL,QUAD,TRIA':{'criteria name F11':"crash time step",'comparison':'>','type':'QUAD,TRIA'},
        'MIN HEI,SHELL,QUAD,TRIA':{'criteria name F11':"min height",'comparison':'>','type':'QUAD,TRIA'},
        'MIN-LEN,SHELL,QUAD,TRIA':{'criteria name F11':"min length",'comparison':'>','type':'QUAD,TRIA'},
        'MINANGLE,SHELL,QUAD':{'criteria name F11':"min angle quads",'comparison':'>','type':'QUAD'},
        'MAXANGLE,SHELL,QUAD':{'criteria name F11':"max angle quads",'comparison':'<','type':'QUAD'},
        'MINANGLE,SHELL,TRIA':{'criteria name F11':"min angle trias",'comparison':'>','type':'TRIA'},
        'MAXANGLE,SHELL,TRIA':{'criteria name F11':"max angle trias",'comparison':'<','type':'TRIA'},
        'TRIANGLES PER NODE,SHELL,QUAD,TRIA':{'criteria name F11':"triangles per node",'comparison':'<=','type':'QUAD,TRIA'},
        'ASPECT,SOLID,TETRA,HEXA,PENTA':{'criteria name F11': 'aspect ratio', 'comparison':'<','type':'TETRA,HEXA,PENTA'},
        'SKEW,SOLID,TETRA,HEXA,PENTA':{'criteria name F11':"skewness",'comparison':'<','type':'TETRA,HEXA,PENTA'},
        'WARP,SOLID,TETRA,HEXA,PENTA':{'criteria name F11':"warping",'comparison':'<','type':'TETRA,HEXA,PENTA'},
        'CRASH,SOLID,TETRA,HEXA,PENTA':{'criteria name F11':"crash time step",'comparison':'>','type':'TETRA,HEXA,PENTA'},
        'MIN-LEN,SOLID,TETRA,HEXA,PENTA':{'criteria name F11':"min length",'comparison':'>','type':'TETRA,HEXA,PENTA'},
        'MINANGLE,SOLID,TETRA':{'criteria name F11':"min angle tetras",'comparison':'>','type':'TETRA'},
        'MAXANGLE,SOLID,TETRA':{'criteria name F11':"max angle tetras",'comparison':'<','type':'TETRA'},
        'MINANGLE,SOLID,HEXA':{'criteria name F11':"min angle hexas",'comparison':'>','type':'HEXA'},
        'MAXANGLE,SOLID,HEXA':{'criteria name F11':"max angle hexas",'comparison':'<','type':'HEXA'},
        'MINANGLE,SOLID,PENTA':{'criteria name F11':"min angle pentas",'comparison':'>','type':'PENTA'},
        'MAXANGLE,SOLID,PENTA':{'criteria name F11':"max angle pentas",'comparison':'<','type':'PENTA'}}    
   
    criterias_type_ent = {}
    criterias_type_val = {}
    criterias_type_oper = {}
    criterias_val = {}
    t = {}
################################################################################    
#                          Reorder criteria for checking
################################################################################
    for key, val in criterias.items():
        key = key.split(',')
        if key[1] == 'SOLID':   
            m = base.F11SolidsOptionsGet(val['criteria name F11'])
        if key[1] == 'SHELL': 
 
            m = base.F11ShellsOptionsGet(val['criteria name F11'])
        if m['status'] == 1:
            val ['val'] = m['value']
            criterias_val [key[0]+','+key[1]] = val

            for ty in val['type'].split(','):
                disct_text = key[1]+','+ty
# type of entity
                if disct_text in criterias_type_ent:
                    criterias_type_ent [disct_text]=criterias_type_ent [disct_text]+[key[0]]       
                else:         
                    criterias_type_ent [disct_text] = [key[0]]
# value of limit                    
                if disct_text in criterias_type_val: 
                    criterias_type_val [disct_text] = criterias_type_val [disct_text]+[m['value']]
                else:                   
                    criterias_type_val [disct_text] = [m['value']]
# operatore for comparison                    
                if disct_text in criterias_type_oper:  
                    criterias_type_oper [disct_text] = criterias_type_oper [disct_text]+[val['comparison']]
                else:                  
                    criterias_type_oper [disct_text] = [val['comparison']]

            t [','.join(key[0:2])] = base.CheckReport(key[1]+','+key[0])
            t [','.join(key[0:2])].has_fix = False
################################################################################    
#                          Collecting entities
################################################################################  
    parts = base.CollectEntities(solver, 
    entities, ent, prop_from_entities=True) 
    
    mats = base.CollectEntities(solver, 
    parts, '__MATERIALS__',  mat_from_entities=True)    
    
    elements = {}
    elements['SHELL'] = base.CollectEntities(deck = solver,
        containers = None, 
        search_types =  ['SHELL'], 
        filter_visible = True)
    elements['SOLID'] = base.CollectEntities(deck = solver, 
        containers = None, 
        search_types =  ['SOLID'], 
        filter_visible = True)
################################################################################    
#               Extracting the thickness parameter from PARTs
################################################################################ 
    thickness_dict = {}
    for part in parts:
        if part.ansa_type(solver) == 'PART_SHELL':
            thick = part.get_entity_values(solver, [thickness, c_thickness])
        if part.ansa_type(solver) == 'PART_MEMBRANE':  
            thick = part.get_entity_values(solver, [thickness])
            thick[c_thickness] = thick [thickness]
        if not thick[c_thickness]:
            thickness_dict [part] = thick[thickness]
        else:
            thickness_dict [part] = thick[c_thickness]
################################################################################    
#               Extracting the defined mats 
################################################################################ 
    flag_defined_mat = 'YES'
    for mat in mats:
        defined = mat.get_entity_values(solver, ['DEFINED','Name'])   
        if defined['DEFINED'] == 'NO':
            flag_defined_mat = 'NO'
            break
################################################################################    
#                 Checking loops
################################################################################ 
    i = {} 
    en = {}     
    for type, elems in elements.items():
        t3 = time.time()
        for ent in elems:
            if type == 'SHELL':
                prop = ent.get_entity_values(solver, ['IPART'])['IPART'] 
            typ = ent.get_entity_values(solver, ['type'])['type'] 
            dict_text = type+','+typ
            qual = base.ElementQuality(ent, criterias_type_ent [dict_text] )
            crit = criterias_type_ent [dict_text]
            limit= criterias_type_val [dict_text]
            oper = criterias_type_oper [dict_text]
            for compare in zip(qual, limit, crit, oper):
                text = compare [2]+','+type   
                
################################################################################                   
#                        standard check for elements
################################################################################
                if text not in i:
                    i [text] = 0
                    en [text] = []

                #if flag_defined_mat == 'NO' and compare [2] == "CRASH":
                    #continue
                flag_error = False
                if compare [0] != 'error':
                    if compare [3] == '>':
                        if float(compare [0]) < float(compare [1]):
                            flag_error = True
                            diff = str(compare [1] - compare [0])
                            
                    if compare [3] == '<':
                      
                        if float(compare [0]) > float(compare [1]): 
                            flag_error = True
                            diff = str(compare [0] - compare [1])  
                            
                    if compare [3] == '<=':                            
                            if  float(compare [0]) >= float(compare [1]): 
                                    flag_error = True
                                    diff = str(compare [0] - compare [1])     
                    
                    if flag_error == True:  
                        i [text] = i [text] + 1
                        if i [text] < limit_lines:
                            t [text].add_issue(entities = [ent],
                                status = 'Error',
                                description = compare [2] + '  '+type,
                                value = str(compare [0]), limit = str(compare [1]),
                                diffe = diff ) 
                        else:
                            en [text].append(ent)
                else:
                    continue
                                                     
################################################################################                   
#          additional check for lenght - thick * THICKNESS FACTOR
################################################################################
                if type == 'SHELL':
                    if compare [2] == "MIN HEI" or compare [2] == "MIN-LEN":
                        lim = float(thickness_dict [prop]) * float(params['THICKNESS FACTOR'])
#                        if lim < 2.0 : lim = 2.0
                        if compare [0] < lim:
                            i [text] = i [text] + 1
                            if i [text] < limit_lines:
                                diff = str(lim - compare [0])                 
                                t [text].add_issue(entities = [ent],
                                    status = 'Error',
                                    description = compare [2] + ' THICKNESS FACTOR',
                                    value = str(compare [0]), limit = str(lim),
                                    diff = diff )
                            else:
                                en [text].append(ent)
                                
################################################################################                   
#                        check for skewness - user defined
################################################################################         
                    if compare [2] == "SKEW":
                        if typ == 'TRIA':
                            lim = float(params['SKEW,TRIA'])
                        elif typ == 'QUAD':
                            lim = float(params['SKEW,QUAD'])
                        if compare [0] > lim:
                            i [text] = i [text] + 1
                            if i [text] < limit_lines: 
                                diff = str(lim - compare [0])                                             
                                t [text].add_issue(entities = [ent],
                                    status = 'Error',
                                    description = compare [2] + '  '+type,
                                    value = str(compare [0]), limit = str(lim),
                                    diff = diff )
                            else:
                                en [text].append(ent)
        t4 = time.time()
        print('Time of checking the type of entity : ', type)    
        print(t4 - t3)      

    if i != None:
        for key, val in i.items():
            #print(key, val)
            if val > limit_lines:
                t [key].add_issue(entities = en [key],
                    status = 'Error',
                    description = key + '  number of errors: '+str(len(en [key])))     
   
    t5 = time.time()
    print('End of execution of the check: ')    
    print(t5 - t0) 
    
    to_report = []         
    for key, val in t.items():
        to_report.append(val)
    return to_report       

# ==============================================================================

def FixCheckQualityElementsSkoda(issues):
	base.All()   
	base.Invert()

# ==============================================================================

checkOptions = { 'name': 'Check Quality of Elements for SKODA  (ABA/PAM)', 
    'exec_action': ('ExecCheckQualityElementsSkoda', os.path.realpath(__file__)), 
    'fix_action':  ('FixCheckQualityElementsSkoda',  os.path.realpath(__file__)), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['SHELL',"MEMBRANE"], 
    'info': 'Checks Quality of Shell Elements'}

checkDescription = base.CheckDescription(**checkOptions)
checkDescription.add_str_param('THICKNESS FACTOR', '1.1')
checkDescription.add_str_param('SKEW,TRIA', '60.0')
checkDescription.add_str_param('SKEW,QUAD', '48.0')
checkDescription.add_str_param('Detail list for number of errors', '100')   
checkDescription.add_str_param('Quality mesh file', '/data/fem/+software/NAVODKY/Navodky_SKODA/batch_mesh_sessions_quality/plast_5mm/Plast_5mm.ansa_qual')
checkDescription.add_str_param('Solver', 'PAMCRASH')  