# PYTHON script
'''
ABAQUS/PAMCRASH/NASTRAN check materials  
=======================================
Description:
* check materials based matching list and name in properties name 
* user defined parameters:
- delimiter for part name of segment e.g. __
- number of segments of names of properties e.g. 5
- type of loadcase e.g. COMMON 
  in case of empty parametr, the list of loadcases is popup
  in case of only one loadcase in matching list is appied just this
- segment of material name e.g. 5
- matching list - /data/fem/+software/SKODA_INCLUDE/white_list
- solver can be ABAQUS/PAMCRASH/NASTRAN

Fix:
* function of fix is available for some warnings
'''

import os
from ansa import base
from ansa import constants
from ansa import  mesh
from ansa import session
from ansa import guitk
from ansa import utils
# ==============================================================================

def ExecCheckMaterials(entities, params):
    file = params['Matching list']
    
    solver = params['Solver']
    solver_name = solver.upper()
    
    if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH' or solver_name == 'NASTRAN':
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
        if solver_name == 'NASTRAN':
          solver = constants.NASTRAN      
          ent = ["PSHELL","PSOLID"]
          id_mat = 'MID1'
          id_mat_nastran = ['MID1', 'MID2', 'MID3']
          remove_text = "P"
    else:
        print('Check works only for ABAQUS, PAMCRASH and NASTRAN')
        return 0 
    
    if not os.path.isfile(file):
        m = utils.SelectOpenFile(0, 'Matching list (*)')
        file = m[0]
        if not os.path.isfile(file):
            return 0

    configuration_line, configuration_line_short, loadcase_list = read_configuration_file(file)
    
    
    
    if (params['Type of loadcase'] not in loadcase_list) and len(loadcase_list) > 1:
        print(loadcase_list)
        TopWindow = guitk.BCWindowCreate("Fill the  text from the combo box", guitk.constants.BCOnExitDestroy)
        ComboBox = guitk.BCComboBoxCreate(TopWindow,loadcase_list )
        guitk.BCComboBoxSetActivatedFunction( ComboBox, ComboActivated, None )
        guitk.BCShow(TopWindow)
        loadcase = loadcase_choose

    if len(loadcase_list) == 1:
        loadcase = loadcase_list[0]
    
    #print('loadcase',loadcase)
    to_report = []
    t1 = base.CheckReport('ID of material doesn\'t match with ID in the matching list')
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

            material = name_list [int(params['Segment of material name']) - 1]
            material_ident = loadcase + ',' + material + ',' + type_part

            material_ent = part.get_entity_values(solver, [id_mat])            
            material_id = material_ent[id_mat]._id
            
            if solver == constants.NASTRAN and type_part == 'SHELL':
                material_ent = part.get_entity_values(solver, id_mat_nastran)
                if material_ent[id_mat_nastran[0]]._id == material_ent[id_mat_nastran[1]]._id and \
                    material_ent[id_mat_nastran[0]]._id == material_ent[id_mat_nastran[2]]._id:
                    flag_nastran_same_mat = True
                else:
                    flag_nastran_same_mat = False
                    
                    
            
# the material was find at in matching list            
            if material_ident in configuration_line:
# the material was find at in matching list, but with wrong id  
                if solver == constants.NASTRAN and type_part == 'SHELL':
                    if int(configuration_line[material_ident]) != int(material_id) or not flag_nastran_same_mat:
                        t1.add_issue(entities = [part], status = 'Error', description = 'Wrong assigning ID or MIDx are not same ',
                            material = material,
                            loadcase = str(loadcase),
                            matching_mat_ID = str(configuration_line[material_ident]),
                            mat_card_ID = str(material_ent[id_mat_nastran[0]]._id) +
                            '/' + str(material_ent[id_mat_nastran[1]]._id) +  '/' +
                            str(material_ent[id_mat_nastran[2]]._id),
                            solver_name =  solver_name,
                            _solver = str(solver),
                            mat = id_mat )

                else:
                    if int(configuration_line[material_ident]) != int(material_id):
                        t1.add_issue(entities = [part], status = 'Error', description = 'Wrong assigning ID',
                            material = material,
                            loadcase = str(loadcase),
                            matching_mat_ID = str(configuration_line[material_ident]),
                            mat_card_ID = str(material_id),
                            solver_name =  solver_name,
                            _solver = str(solver),
                            mat = id_mat,
                            )
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
def ComboActivated(combo, index, data):
    global loadcase_choose
    loadcase_choose = guitk.BCComboBoxGetText( combo, index )
    return 0
    
    
# reading the configuration file
def read_configuration_file(file):
    f = open(file,'r')
    configuration_line = {}
    configuration_line_short = {}
    list_of_loadcases = []
    row_list_of_loadcases = []
    row_list_of_loadcases_order = []    
    for line in f:
        m = line.split()  
        if (( line[0] == "#" or line[0] == "$" ) and (m[0] != "$NAME" and m[0] != "$MATERIAL_NAME" )):
            continue
        if  (m[0] == "$NAME") or (m[0] == "$MATERIAL_NAME")  :
            configuration = []
            row_list_of_loadcases = []
            row_list_of_loadcases_order = []
            for k, segment in enumerate(m):
                configuration.append(segment)
                if segment != 'COMMENT' \
                    and segment != '$NAME'  \
                    and segment != '$MATERIAL_NAME' \
                    and segment != 'MAP_KEY' \
                    and segment != 'TYPE':
                    if segment not in list_of_loadcases:
                        list_of_loadcases.append(segment)
                    row_list_of_loadcases.append(segment)
                    row_list_of_loadcases_order.append(k)
        else:
            if len(row_list_of_loadcases) == 0 or  line.startswith( '$' ) :
                continue
            else:
                type_index = configuration.index ('TYPE')
                map_key_index = configuration.index ('MAP_KEY')

                for order, loadcase in enumerate(row_list_of_loadcases):
#dictionary with configuration values    
                    value_of_mat_id = m[row_list_of_loadcases_order[order]] 
                    item_list = str(loadcase)+','+str(m[map_key_index])+','+str(m[type_index])                
                    configuration_line [item_list] = value_of_mat_id
                     
#dictionary with configuration values - without information about loadcase
                    item_list_short = str(m[map_key_index])+','+str(m[type_index])                  
                    if item_list_short in configuration_line_short:
                        pass
                    else:
                        configuration_line_short [item_list_short] = list()
                    configuration_line_short [item_list_short].append([value_of_mat_id,loadcase])
    f.close()
    return configuration_line,configuration_line_short, list_of_loadcases

# ==============================================================================

def FixcCheckMaterials(issues):

    for issue in issues:
        ents = issue.entities
        field = {issue.mat:issue.matching_mat_ID}
            
        for ent in ents:
            if int(issue._solver) == constants.NASTRAN: 
                type_part = ent.ansa_type(constants.NASTRAN)
                if type_part == 'PSHELL':
                    field = {issue.mat:issue.matching_mat_ID,'MID2':issue.matching_mat_ID,'MID3':issue.matching_mat_ID }
            success = ent.set_entity_values(int(issue._solver), field)
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

if __name__ == '__main__':
	
	entities = base.CollectEntities(constants.PAMCRASH, None, "__MATERIALS__")
	params = {
		'Delimiter for part name' : '__',
		'Matching list'	: '/data/fem/users/siegl/eclipse/ansaTools/ansaChecksPlistUpdater/res/test_files/white_list',
		'Solver'		:	'PAMCRASH',
		'Type of loadcase', 'SK3165_-10',
		'Segment of material name' : '5',
		'Number of segments', '5'}
	
	ExecCheckMaterials(entities, params)
	
