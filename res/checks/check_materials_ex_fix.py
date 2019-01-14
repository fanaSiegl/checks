# PYTHON script

import os
from ansa import base
from ansa import constants
from ansa import  mesh
import re
from ansa import session

# ==============================================================================

def ExecCheckMaterials(entities, params):
    file = params['Matching list']
    
    solver = params['Solver']
    solver_name = solver.upper()
    if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH':
        if solver_name == 'ABAQUS':
          solver = constants.ABAQUS
          ent = ["SHELL_SECTION","SOLID_SECTION", "MEMBRANE_SECTION"]
          id_mat = 'MID'
          remove_text = "_SECTION"
        if solver_name == 'PAMCRASH':
          solver = constants.PAMCRASH      
          ent = ["PART_SHELL","PART_SOLID", "PART_MEMBRANE"]
          id_mat = 'IMAT'
          remove_text = "PART_"
    else:
        session.Quit()
        
    configuration_line, configuration_line_short = read_configuration_file(file)
#    print(configuration_line)
    to_report = []
    t1 = base.CheckReport('The material doesn\'t match with list')
    t2 = base.CheckReport('Wrong format of part')
    t3 = base.CheckReport('The material isn\'t in list')  
     
    t1.has_fix = True  
    t2.has_fix = False  
    t3.has_fix = False
    
    parts = base.CollectEntities(solver, entities, ent, prop_from_entities=True)  

    for part in parts:
        name = part._name
        name_list = name.split(params['Delimiter for part name'])
        if len(name_list) == int(params['Number of segments']):
            type_part = part.ansa_type(solver)
            type_part = type_part.replace(remove_text, "")

            loadcase = params['Type of loadcase']
            material = name_list [int(params['Segment of material name']) - 1]
            material_ident = loadcase + ',' + material + ',' + type_part
            material_ent = part.get_entity_values(solver, [id_mat])
            material_id = material_ent[id_mat]._id
            
# the material was find at in matching list            
            if material_ident == configuration_line:
# the material was find at in matching list, but with wrong name            
                if int(configuration_line[material_ident]) != int(material_id):
                    t1.add_issue(entities = [part], status = 'Error', description = 'Wrong assigning ID',
                        material = material,
                        loadcase = str(loadcase),
                        matching_mat_ID = str(configuration_line[material_ident]),
                        mat_card_ID = str(material_id),
                        solver_name =  solver_name,
                        solver = str(solver),
                        mat = id_mat )
            else:
# the material wasnt able to find at in matching list             
                material_ident_short = material + ',' + type_part         
                if material_ident_short in configuration_line_short:
                    suggest = configuration_line_short [material_ident_short]
                else:
                    suggest = ['xxx','xxx']
                    
                t3.add_issue(entities = [part], status = 'Error',
                    description = 'The material isn\'t in list',
                    material = material,
                    suggest = str(suggest),
                    loadcase = str(loadcase), 
                    solver_name =  solver_name,  
                    mat_card_ID = str(material_id),                
                    )
        else:
#Wrong numer of segments         
            t2.add_issue(entities = [part], status = 'Error', description = 'Wrong numer of segments')
    
    to_report.append(t1)
    to_report.append(t2)  
    to_report.append(t3)   
    return to_report

# ==============================================================================

# reading the configuration file
def read_configuration_file(file):
    f = open(file,'r')
    configuration_line = {}
    configuration_line_short = {}
    for line in f:
        m = line.split()            
        if (( line[0] == "#" or line[0] == "$" ) and (m[0] != "$NAME" )):
            continue
        if  (m[0] == "$NAME") or (m[0] == "$MATERIAL_NAME")  :
            k=0
            configuration = []
            for segment in m:
                configuration.append(segment)
                k=k+1
        else:
            type_index = configuration.index ('TYPE')
            map_key_index = configuration.index ('MAP_KEY')

            for order,val in enumerate(m):
                if val == '$' or val.startswith( '$' ):
                    break
                if configuration[order] != 'COMMENT' \
                    and configuration[order] != '$NAME'  \
                    and configuration[order] != '$MATERIAL_NAME' \
                    and configuration[order] != 'MAP_KEY' \
                    and configuration[order] != 'TYPE':
                  
#dictionary with configuration values    
                    item_list = str(configuration[order])+','+str(m[map_key_index])+','+str(m[type_index])                
                    configuration_line [item_list] = val 
                     
#dictionary with configuration values - without information about loadcase
                    item_list_short = str(m[map_key_index])+','+str(m[type_index])                  
                    if item_list_short in configuration_line_short:
                        pass
                    else:
                        configuration_line_short [item_list_short] = list()
                    configuration_line_short [item_list_short].append([val,configuration[order]])
    f.close()
    return configuration_line,configuration_line_short
 
# ==============================================================================

def FixcCheckMaterials(issues):

    for issue in issues:
        ents = issue.entities
        field = {issue.mat:issue.matching_mat_ID}
        for ent in ents:
            success = ent.set_entity_values(int(issue.solver), field)
            if success == 0:
                issue.is_fixed = True

# ==============================================================================

checkOptions = { 'name': 'Check Materials with a checking list (ABA/PAM)', 
    'exec_action': ('ExecCheckMaterials', os.path.realpath(__file__)), 
    'fix_action':  ('FixcCheckMaterials', os.path.realpath(__file__)), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['SHELL','MEMBRANE','SOLID'], 
    'info': 'Checks Materials'}
 
checkDescription = base.CheckDescription(**checkOptions)

checkDescription.add_str_param('Number of segments', '5')
checkDescription.add_str_param('Segment of material name', '5')  
checkDescription.add_str_param('Type of loadcase', 'MAP_KEY')  
checkDescription.add_str_param('Solver', 'PAMCRASH')   
checkDescription.add_str_param('Matching list', '/data/fem/+software/SKODA_INCLUDE/white_list')   
checkDescription.add_str_param('Delimiter for part name', '__')    

# ==============================================================================
