# PYTHON script

'''
SKODA check elements
====================

Check the shell and solid elements based the Skoda rules.

Usage
-----

**Primary solver** - ABAQUS/PAMCRASH.

* Basic check of elements is realized xxx.ansa_qual file
* User defined check element: min_lenght = THICKNESS FACTOR * thickness
* User defined check element for skew: TRIA = 60.0, QUAD = 48.0
* Possible compress list bigger then e.g. 100 lines

'''

import os, time, ansa
from ansa import base, constants, mesh



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
    SOLVER_TYPE = constants.PAMCRASH
    ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']
    CHECK_TYPE = ['SKODA', 'DAIMLER', 'AUDI', 'SEAT']


@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):
    t0 = time.time()
    print('start measure time')
    mesh.ReadQualityCriteria(params['Quality mesh file'])

    type_check = params['Type of check']
    
    # Solver dependent variables    
    solver = params['Solver']
    solver_name = solver.upper()
    limit_lines = int(params['Detail list for number of errors'])
    if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH' or solver_name == 'LSDYNA':
        
        if solver_name == 'ABAQUS':
            solver = constants.ABAQUS
            properties_types = {'SHELL_SECTION':"SHELL_SECTION","SOLID_SECTION":"SOLID_SECTION",
                                "MEMBRANE_SECTION": "MEMBRANE_SECTION", 'COMPOSITE':'COMPOSITE'}
            thickness = 'T'
            remove_text = "_SECTION"
            name_part_key = 'PID'
            element_types = {'SHELL':'SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'ELEMENT_SOLID'}  
            
        if solver_name == 'PAMCRASH':
            solver = constants.PAMCRASH
            properties_types = {'SHELL_SECTION':"PART_SHELL","SOLID_SECTION":"PART_SOLID",
                                "MEMBRANE_SECTION":"PART_MEMBRANE", 'COMPOSITE':'COMPOSITE'}
            thickness = 'h'
            c_thickness = 'TCONT'
            name_part_key = 'IPART'
            element_types = {'SHELL':'SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'SOLID'}
       
        if solver_name == 'LSDYNA':
            solver = constants.LSDYNA
            properties_types = {'SHELL_SECTION':"SHELL_SECTION","SOLID_SECTION":"SOLID_SECTION",
                                "MEMBRANE_SECTION": "MEMBRANE_SECTION", 'COMPOSITE':'PART_COMPOSITE'}
            thickness = 'T1'
            c_thickness = 'OPTT'
            name_part_key = 'PID'
            element_types = {'SHELL':'ELEMENT_SHELL', 'MEMBRANE':'MEMBRANE','SOLID':'ELEMENT_SOLID'}                      
    else:
        session.Quit()
    
    properties_types_list = [typ_property for _, typ_property in properties_types.items() ] 
        
    print("SOLVER:", solver_name)
    print()

    # Basic criteria
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

    # Reorder criteria for checking
    for key, val in criterias.items():
        key = key.split(',')
        
        print('key[1]:',key[1], )
        print('element_types[SOLID]',element_types['SOLID'])
        print('element_types[SHELL]',element_types['SHELL'])
        
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

    # Collecting entities
    parts = base.CollectEntities(solver,
        entities, properties_types_list, prop_from_entities=True)
    # print("parts", parts)

    mats = base.CollectEntities(solver,
        parts, '__MATERIALS__',  mat_from_entities=True)

    elements = {}
    elements['SHELL'] = base.CollectEntities(deck = solver,
        containers = None,
        search_types = [element_types['SHELL']],
        filter_visible = True)
    elements['SOLID'] = base.CollectEntities(deck = solver,
        containers = None,
        search_types = [element_types['SOLID']],
        filter_visible = True)

    # Extracting the thickness parameter from PARTs
    
    thickness_dict = {}
    for part in parts:
        
        if part.ansa_type(solver) == properties_types['SHELL_SECTION']:
            thick = part.get_entity_values(solver, [thickness, c_thickness])
            
        if part.ansa_type(solver) == properties_types['MEMBRANE_SECTION']:
            thick = part.get_entity_values(solver, [thickness])
            thick[c_thickness] = thick[thickness]
        
        if thick[c_thickness]:
            thickness_dict[part] = thick[c_thickness]
        else:
            thickness_dict[part] = thick[thickness]

    # # Extracting the defined mats
    # flag_defined_mat = 'YES'
    # for mat in mats:
    #     defined = mat.get_entity_values(solver, ['DEFINED','Name'])
    #     if defined['DEFINED'] == 'NO':
    #         flag_defined_mat = 'NO'
    #         break
        
    # print("thickness_dict",thickness_dict)
    
    # Checking loops
    number_errors = {}
    text_errors = {}
    for element_type, elems in elements.items():
        t3 = time.time()
        for element in elems:
            if element_type == element_types['SHELL']:
                prop = element.get_entity_values(solver, [name_part_key])[name_part_key]
            typ = element.get_entity_values(solver, ['type'])['type']
            dict_text = element_type+','+typ
            qual = base.ElementQuality(element, criterias_type_ent[dict_text])
            crit = criterias_type_ent[dict_text]
            limit = criterias_type_val[dict_text]
            oper = criterias_type_oper[dict_text]
            for compare in zip(qual, limit, crit, oper):
                text = compare[2] + ',' + element_type


                # Additional check for lenght - thick * THICKNESS FACTOR
                if element_type == element_types['SHELL'] and type_check == 'SKODA':
                    
                    if compare[2] == "MIN HEI" or compare[2] == "MIN-LEN":
                        
                        if thickness_dict[prop]:
                            lim = float(thickness_dict[prop]) * float(params['THICKNESS FACTOR'])

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
                    if compare[2] == 'SKEW' and type_check == 'SKODA':
                        if typ == 'TRIA':
                            lim = float(params['SKEW,TRIA'])
                        elif typ == 'QUAD':
                            lim = float(params['SKEW,QUAD'])
                        if compare[0] > lim:
                            number_errors[text] = number_errors[text] + 1
                            if number_errors[text] < limit_lines:
                                diff = str(lim - compare[0])
                                t[text].add_issue(entities=[element],
                                        status='Error',
                                        description=compare[2]+','+element_type,
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
                
                        
                # Standard check for elements
                if text not in number_errors:
                    number_errors[text] = 0
                    text_errors[text] = []

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
                                    description=compare[2]+','+element_type,
                                    value=str(compare[0]), limit=str(compare[1]),
                                    diffe=diff)
                        else:
                            text_errors[text].append(element)
                else:
                    continue
                

        t4 = time.time()
        print('Time of checking the type of entity: ', element_type)
        print(t4 - t3)

    if number_errors != None:
        for key, val in number_errors.items():
            if val > limit_lines:
                t[key].add_issue(entities=text_errors[key],
                        status='Error',
                        description = key + '  number of errors: ' + str(len(text_errors[key])))

    t5 = time.time()
    print('End of execution of the check: ')
    print(t5 - t0)

    for key, val in t.items():
        CheckItem.reports.append(val)
        print()
    return CheckItem.reports


@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
    base.All()
    base.Invert()



# Update this dictionary to load check automatically
checkOptions = {'name': 'Check quality of elements (ABA/PAM/LSDYNA)',
    'exec_action': ('exe', os.path.realpath(__file__)),
    'fix_action': ('fix', os.path.realpath(__file__)),
    'deck': CheckItem.SOLVER_TYPE,
    'requested_types': CheckItem.ENTITY_TYPES,
    'info': 'Checks quality of shell elements'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('THICKNESS FACTOR', '1.1')
checkDescription.add_str_param('SKEW,TRIA', '60.0')
checkDescription.add_str_param('SKEW,QUAD', '48.0')
checkDescription.add_str_param('Type of check', 'SKODA')
checkDescription.add_str_param('Detail list for number of errors', '100')
checkDescription.add_str_param('Quality mesh file', '/data/fem/+software/NAVODKY/Navodky_SKODA/batch_mesh_sessions_quality/plast_5mm/Plast_5mm.ansa_qual')
checkDescription.add_str_param('Solver', 'PAMCRASH')

if __name__ == '__main__' and DEBUG:
    check_base_items._debugModeTestFunction(CheckItem)
