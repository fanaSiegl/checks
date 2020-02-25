# PYTHON script

'''
Check elements 
====================

Check the shell and solid elements.

Usage
-----

**Primary solver** - ABAQUS/PAMCRASH/LSDYNA
**Car maker** - SKODA, AUDI and DAYMLER

* The ANSA quality file is choosed based:
   -  The use can choose own User quality mesh file
   -  Default mesh length value: 5 and Material type (polymer/steel): polymer (only for Skoda and Daimler and for setting above is predefined an ANSA quality file)
   -  In case that user dont fill User quality mesh file and parameters from above are different then default then will be uses the current F11 quality parameters
* Basic check of elements is realized xxx.ansa_qual file
* Special rules are applied for SKODA:
   -  User defined check element: min_lenght = THICKNESS FACTOR * thickness
   -  User defined check element for skew: TRIA = 60.0, QUAD = 48.0
* Special rules are applied for DAIMLER:
   - check MIN HEI only for TETRA
* Possible compress list bigger then e.g. 100 lines

'''

import os, time, ansa
from ansa import base, constants, mesh

# ==============================================================================

DEBUG = False

if DEBUG:
    PATH_SELF = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'
    # PATH_SELF = os.path.dirname(os.path.realpath(__file__))
else:
    PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')

ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

# ==============================================================================

class CheckItem(check_base_items.BaseEntityCheckItem):
    SOLVER_TYPE = constants.PAMCRASH
    ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']
#    CHECK_TYPE = ['SKODA', 'DAIMLER', 'AUDI', 'SEAT']

# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):

    type_check = params['Car - SKODA/DAIMLER']
    element_length = params['Default mesh length']	
    THICKNESS_FACTOR=1.1
    SKEW_TRIA=60.0
    SKEW_QUAD=48.0

    t0 = time.time()
#    print('Start measure time....')
    
    if params['User quality mesh file'] != '':
        user_define_qual = True
        success = mesh.ReadQualityCriteria(params['User quality mesh file'])
        if success == 1:
            print('User defined mesh quality file was loaded')
        else:
            print('User defined mesh quality file was\'n loaded')
            session.Quit()       
                 
    else:
        if type_check == 'DAIMLER' and params['Material type (polymer/steel)'] == 'polymer' and element_length == '5':
            success = mesh.ReadQualityCriteria(PATH_SELF + '/res/DAIMLER/O5mm.ansa_qual')
            if success == 1:
                print('Mesh quality file was loaded - DAIMLER - O5mm.ansa_qual')
            else:
                print('User defined mesh quality file was\'n loaded')
                session.Quit()    

        if type_check == 'SKODA' and params['Material type (polymer/steel)'] == 'polymer' and element_length == '5':
            success =  mesh.ReadQualityCriteria(PATH_SELF + '/res/SKODA/Plast_5mm.ansa_qual')
            if success == 1:
                print('Mesh quality file was loaded - SKODA - Plast_5mm.ansa_qual')
            else:
                print('User defined mesh quality file was\'n loaded')
                session.Quit()             
                
    if success == 0:
        print('Any mesh quality file was\'n loaded - current mesh quality element will be used')
       
    # Solver dependent variables    
    solver = params['Solver']
    solver_name = solver.upper()
    limit_lines = int(params['Detail list for number of errors'])
    if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH' or solver_name == 'LSDYNA':
        
        if solver_name == 'ABAQUS':
            solver = constants.ABAQUS
            properties_types = {'SHELL_SECTION':"SHELL_SECTION","SOLID_SECTION":"SOLID_SECTION",
                                "MEMBRANE_SECTION": "MEMBRANE_SECTION", 'COMPOSITE':'COMPOSITE','LAMINATE':'LAMINATE'}
            thickness = 'T'
            c_thickness = 'T'            
            name_part_key = 'PID'
            element_types = {'SHELL':'SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'SOLID'}
            material_key = 'MID'
            material_key_comp = 'MID(1)'      
                        
        if solver_name == 'PAMCRASH':
            solver = constants.PAMCRASH
            properties_types = {'SHELL_SECTION':"PART_SHELL","SOLID_SECTION":"PART_SOLID",
                                "MEMBRANE_SECTION":"PART_MEMBRANE", 'COMPOSITE':'COMPOSITE','LAMINATE':'LAMINATE'}
            thickness = 'h'
            c_thickness = 'TCONT'
            name_part_key = 'IPART'
            material_key = 'IMAT'    
            material_key_comp = 'IMAT'           
            element_types = {'SHELL':'SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'SOLID'}
       
        if solver_name == 'LSDYNA':
            solver = constants.LSDYNA
            properties_types = {'SHELL_SECTION':"SECTION_SHELL","SOLID_SECTION":"SECTION_SOLID",
                                "MEMBRANE_SECTION": "SECTION_MEMBRANE", 'COMPOSITE':'PART_COMPOSITE','LAMINATE':'LAMINATE'}
            thickness = 'T1'
            material_key_comp = 'mid1'                  
            c_thickness = 'OPTT'
            name_part_key = 'PID'
            material_key = 'MID'               
            element_types = {'SHELL':'ELEMENT_SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'ELEMENT_SOLID'}                      
    else:
        session.Quit()
    
    properties_types_list = [typ_property for _, typ_property in properties_types.items() ]
        
    print("SOLVER:", solver_name)

    # Basic criteria
    criterias = { 
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
        'TRIANGLES PER NODE,SHELL,QUAD,TRIA':{'criteria name F11':"triangles per node",'comparison':'>=','type':'QUAD,TRIA'},
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

    # Reorder criteria for checking
    for key, val in criterias.items():
        key = key.split(',')
        
        if key[1] == 'SOLID':
            criteria_from_f11 = base.F11SolidsOptionsGet(val['criteria name F11'])
            
        if key[1] == 'SHELL':
            criteria_from_f11 = base.F11ShellsOptionsGet(val['criteria name F11'])
            
        if criteria_from_f11['status'] == 1:
            val['val'] = criteria_from_f11['value']
            criterias_val[key[0]+','+key[1]] = val
            
            for ty in val['type'].split(','):
                disct_text = key[1]+','+ty

                # Type of entity
                if disct_text in criterias_type_ent:
                    criterias_type_ent[disct_text] = criterias_type_ent[disct_text] + [key[0]]
                else:
                    criterias_type_ent[disct_text] = [key[0]]
                # Value of limit
                if disct_text in criterias_type_val:
                    criterias_type_val[disct_text] = criterias_type_val[disct_text] + [criteria_from_f11['value']]
                else:
                    criterias_type_val[disct_text] = [criteria_from_f11['value']]


                # Operator for comparison
                if disct_text in criterias_type_oper:
                    criterias_type_oper[disct_text] = criterias_type_oper[disct_text] + [val['comparison']]
                else:
                    criterias_type_oper[disct_text] = [val['comparison']]
            
            t[','.join(key[0:2])] = base.CheckReport(key[1]+','+key[0])
            t[','.join(key[0:2])].has_fix = False

    t['Check of materials DEFINED = YES'] = base.CheckReport('Check of materials DEFINED = YES')
    t['Check of materials DEFINED = YES'].has_fix = False
    
    # Collecting entities
    parts = base.CollectEntities(solver,
        entities, properties_types_list, prop_from_entities=True)

    mats = base.CollectEntities(solver,
        parts, '__MATERIALS__',  mat_from_entities=True)

    # Extracting the thickness parameter from PARTs
    
    thickness_dict = dict()
    defined_material = dict()
    text_errors_mat = list()
    thick = dict()
        
    for part in parts:

        if part.ansa_type(solver) == properties_types['SOLID_SECTION'] :
            continue

        if part.ansa_type(solver) == properties_types['SHELL_SECTION']:
            thick = part.get_entity_values(solver, [thickness, c_thickness])

        if part.ansa_type(solver) == properties_types['LAMINATE'] or part.ansa_type(solver) == properties_types['COMPOSITE']:
            thick [thickness] = 10000
            
        if part.ansa_type(solver) == properties_types['MEMBRANE_SECTION']:
            thick = part.get_entity_values(solver, [thickness])
            thick[c_thickness] = thick[thickness]

        if c_thickness in thick:
            thickness_dict[part] = thick[c_thickness]
        else:
            thickness_dict[part] = thick[thickness]
            
        # # Extracting the defined mats    
        if type_check == 'SKODA' :
            part_type = part.ansa_type(solver)
            if part_type == 'LAMINATE':
                material_key = material_key_comp
#            print('part', part)
            
            mat = part.get_entity_values(solver, [material_key])[material_key]
            defined = mat.get_entity_values(solver, ['DEFINED'])
            
            if defined['DEFINED'] == 'NO':
                defined_material [part] = False
                text = 'The material id = ' + str(mat._id) + ' wasn\'t defined - the check the CRASH TIME STEP was skipped'
                
                if not (text in text_errors_mat):
                    t['Check of materials DEFINED = YES'].add_issue(entities=[mat],
                         status='Error',
                         description= text,
                         value="",
                         diff="")
                text_errors_mat.append(text) 
            else:
                defined_material [part] = True         

    # Checking loops
    number_errors = {}
    text_errors = {}
    for element in entities:
        
        element_type = element.ansa_type(solver)
        
        if element_type == element_types['SHELL']:
            prop = element.get_entity_values(solver, [name_part_key])[name_part_key]
            element_type_universal = 'SHELL'
        elif element_type == element_types['SOLID']:
            element_type_universal = 'SOLID'
        elif element_type == element_types['MEMBRANE']:
            element_type_universal = 'MEMBRANE'       	

        typ = element.get_entity_values(solver, ['type'])['type']
        dict_text = element_type_universal+','+typ

        qual = base.ElementQuality(element, criterias_type_ent[dict_text])
        crit = criterias_type_ent[dict_text]
        limit = criterias_type_val[dict_text]
        oper = criterias_type_oper[dict_text]
        
        for compare in zip(qual, limit, crit, oper):
            text = compare[2] + ',' + element_type_universal
            
            if text not in number_errors:
                number_errors[text] = 0
                text_errors[text] = []
                
            # Additional check for lenght - thick * THICKNESS FACTOR
            if element_type == element_types['SHELL'] and type_check == 'SKODA':
                
                if compare[2] == "MIN HEI" or compare[2] == "MIN-LEN":
                    
                    if thickness_dict[prop]:
                        lim = float(thickness_dict[prop]) * float(THICKNESS_FACTOR)

                        if compare[0] < lim:

                            number_errors[text] = number_errors[text] + 1
                            
                            if number_errors[text] < limit_lines:
                                diff = str(lim - compare[0])
                                t[text].add_issue(entities = [element],
                                        status='Error',
                                        description=compare[2]+' THICKNESS FACTOR',
                                        value=str(compare[0]), limit=str(lim),
                                        diff=diff)
                            else:
                                text_errors[text].append(element)
                    continue

                # Check for skewness - user defined
                if compare[2] == 'SKEW':
                    if typ == 'TRIA':
                        lim = float(SKEW_TRIA)
                    elif typ == 'QUAD':
                        lim = float(SKEW_QUAD)
                    if compare[0] > lim:

                        number_errors[text] = number_errors[text] + 1
                        if number_errors[text] < limit_lines:
                            diff = str(lim - compare[0])
                            t[text].add_issue(entities=[element],
                                    status='Error',
                                    description=compare[2]+','+element_type_universal,
                                    value=str(compare[0]), limit=str(lim),
                                    diff=diff)
                        else:
                            text_errors[text].append(element)
                    continue

            # Check for solid angle MIN HEI only for TETRA
            if (compare[2] == 'MIN HEI' 
                    and typ != 'TETRA' 
                    and type_check == 'DAIMLER' 
                    and element_type == element_types['SOLID']):
                continue
            
            if (compare[2] == 'CRASH' 
                     and not(defined_material[prop])
                     and type_check == 'SKODA' 
                     and element_type == element_types['SHELL']):
                continue           
            
                    
            # Standard check for elements


            flag_error = False
            if compare[0] != 'error':
                if compare[3] == '>':
                    if float(compare[0]) < float(compare[1]):
                        flag_error = True
                        diff = str(compare[1] - compare[0])

                if compare[3] == '<':

                    if float(compare[0]) > float(compare[1]):
                        flag_error = True
                        diff = str(compare[0] - compare[1])

                if compare[3] == '<=':
                    
                        if  float(compare[0]) >= float(compare[1]):
                                flag_error = True
                                diff = str(compare[0] - compare[1])

                if flag_error == True:

                    number_errors[text] = number_errors[text] + 1
                    
                    if number_errors[text] < limit_lines:
                        
                        t[text].add_issue(entities=[element],
                                status='Error',
                                description=compare[2]+','+element_type_universal,
                                value=str(compare[0]), limit=str(compare[1]),
                                diffe=diff)
                    else:
                        text_errors[text].append(element)
                
    if number_errors != None:
        for key, val in number_errors.items():
            if val > limit_lines:
                t[key].add_issue(entities=text_errors[key],
                        status='Error',
                        description = key + '  number of errors: ' + str(len(text_errors[key])))

    t5 = time.time()
    print('End of execution of the check: ')
    print(t5 - t0)

    return list(t.values())

# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
  pass

# ============== this "checkDescription" is crucial for loading this check into ANSA! =========================

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check quality of elements (ABA/PAM/LSDYNA)',
    'exec_action': ('exe', os.path.realpath(__file__)),
    'fix_action': ('fix', os.path.realpath(__file__)),
    'deck': CheckItem.SOLVER_TYPE,
    'requested_types': CheckItem.ENTITY_TYPES,
    'info': 'Checks quality of shell elements'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('Car - SKODA/DAIMLER', 'SKODA')
checkDescription.add_str_param('Detail list for number of errors', '100')
checkDescription.add_str_param('User quality mesh file', '')
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Material type (polymer/steel)', 'polymer')
checkDescription.add_str_param('Default mesh length','5')
# ==============================================================================

if __name__ == '__main__' and DEBUG:

    testParams = {
       'Car - SKODA/DAIMLER': 'DAIMLER',
       'Detail list for number of errors': '100',
       'User quality mesh file': '',
       'Solver': 'ABAQUS',
       'Material type (polymer/steel)':'polymer',
       'Default mesh length':'5'}
    check_base_items.debugModeTestFunction(CheckItem, testParams)

# ==============================================================================