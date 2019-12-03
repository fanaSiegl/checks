# PYTHON script

'''
Check part names based on xlsx file for Nissan
==============================================

Check parts for the following rules based on part name:

* thickness
* material

Usage
-----

**Primary solver** - PAMCRASH.

**User defined parameters**:

* Segment of part name
* Segment of material name
* Segment of thickness name
* Number of segments
* Thickness by part name check - YES
* Material by part name check - YES
* Excel sheet name e.g. BCC18FU_Var_B_Cost
* Excel part name identifier e.g. Component
* Excel part number name identifier e.g. P/N
* Excel material name identifier e.g. Material
* Excel thickness name identifier e.g. t [mm]
* Delimiter for part name __

'''

import os, ansa
from ansa import base, constants, utils, session



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['SHELL', 'MEMBRANE', 'SOLID']



@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):
	solver = params['Solver']
	solver_name = solver.upper()
	if solver_name == 'ABAQUS' or solver_name == 'PAMCRASH':
		if solver_name == 'ABAQUS':
			solver = constants.ABAQUS
			ent = ["SHELL_SECTION","SOLID_SECTION", "MEMBRANE_SECTION"]
			id_mat = 'MID'
			thickness = 'T'
			remove_text = "_SECTION"
		if solver_name == 'PAMCRASH':
			solver = constants.PAMCRASH
			ent = ["PART_SHELL","PART_SOLID", "PART_MEMBRANE"]
			id_mat = 'IMAT'
			remove_text = "PART_"
			thickness = 'h'
			c_thickness = 'TCONT'
	# else:
		# session.Quit()

	t5 = base.CheckReport('Thickness same as in part name')
	t7 = base.CheckReport('Material same as in part name')

	t5.has_fix = False
	t7.has_fix = False

	m = utils.SelectOpenFile(0, 'Excel files (*.xlsx)')
	if len(m):
		print('Used :', m[0])
		xl_parts = utils.XlsxOpen(m[0])

		# read excel, find cell position of part name params['Excel part name identifier']
		row=0
		empty_row=0
		Component_column=-1
		Component_row=0
		Component_name=params['Excel part name identifier']
		Component_name = Component_name.replace("\r","")
		Component_name = Component_name.replace("\n", "")
		Component_name = Component_name.replace(" ", "")
		while (empty_row < 20 and Component_column==-1):
			empty_column=0
			column=0
			while (empty_column < 20 and Component_column==-1):
				value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , column)
				if value!= None and value!='':
					value = value.replace("\r","")
					value = value.replace("\n", "")
					value = value.replace(" ", "")
					empty_column=0
					if value == Component_name:
						Component_column=column
						Component_row=row
				else:
					empty_column+=1
				column+=1
			if column == empty_column:
				empty_row+=1
			row+=1
		# print('Component_column:',Component_column)
		# print('Component_row:',Component_row)
		if Component_column==-1:
			print('NOT FOUND cell with name "',params['Excel part name identifier'],'" in file ',m[0],'in sheet ',params['Excel sheet name'])
			# session.Quit()

		# read excel, find cell position of part nummer name params['Excel part number name identifier']
		empty_column=0
		column=0
		P_N_column=-1
		P_N_name=params['Excel part number name identifier']
		P_N_name = P_N_name.replace("\r","")
		P_N_name = P_N_name.replace("\n", "")
		P_N_name = P_N_name.replace(" ", "")
		while (empty_column < 20 and P_N_column==-1):
			value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], Component_row , column)
			if value!= None and value!='':
				value = value.replace("\r","")
				value = value.replace("\n", "")
				value = value.replace(" ", "")
				empty_column=0
				if value == P_N_name:
					P_N_column=column
			else:
				empty_column+=1
			column+=1
		# print('P_N_column:',P_N_column)
		if P_N_column==-1:
			print('NOT FOUND cell with name "',params['Excel part number name identifier'],'" in file ',m[0],'in sheet ',params['Excel sheet name'])
			# session.Quit()

		# read excel, find cell position of part material name params['Excel material name identifier']
		empty_column=0
		column=0
		Material_column=-1
		Material_name=params['Excel material name identifier']
		Material_name = Material_name.replace("\r","")
		Material_name = Material_name.replace("\n", "")
		Material_name = Material_name.replace(" ", "")
		while (empty_column < 20 ):
			value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], Component_row , column)
			if value!= None and value!='':
				value = value.replace("\r","")
				value = value.replace("\n", "")
				value = value.replace(" ", "")
				empty_column=0
				if value == Material_name:
					Material_column=column
			else:
				empty_column+=1
			column+=1
		# print('Material_column:',Material_column)
		if Material_column==-1:
			print('NOT FOUND cell with name "',params['Excel material name identifier'],'" in file ',m[0],'in sheet ',params['Excel sheet name'])
			# session.Quit()

		# read excel, find cell position of part thickness name 't \r\n[mm]'
		empty_column=0
		column=0
		Th_column=-1
		Th_name=params['Excel thickness name identifier']
		Th_name = Th_name.replace("\r","")
		Th_name = Th_name.replace("\n", "")
		Th_name = Th_name.replace(" ", "")
		while (empty_column < 20 ):
			value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], Component_row , column)
			if value!= None and value!='':
				value = value.replace("\r","")
				value = value.replace("\n", "")
				value = value.replace(" ", "")
				empty_column=0
				if value == Th_name:
					Th_column=column
			else:
				empty_column+=1
			column+=1
		# print('Th_column:',Th_column)
		if Th_column==-1:
			print('NOT FOUND cell with name of thickness in file ',m[0],'in sheet ',params['Excel sheet name'])
			# session.Quit()
		row=Component_row+1
		empty=0
		parts=0
		excel_part_id=list()
		excel_part_name=list()
		excel_part_thickness=list()
		excel_part_mat=list()

		value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , Component_column)
		while empty < 20 :
			if value!= None and value!='':
				part_name=value
				print('excel_part_name:',part_name)
				part_id=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , P_N_column)
				print('excel_part_id:',part_id)
				value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , Th_column)
				try :
					part_thickness=float(value)
					print('excel_part_thickness:',part_thickness)
				except ValueError:
					part_thickness=float(0.)
				part_mat=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , Material_column)
				print('excel_part_mat:',part_mat)
				empty=0
				excel_part_id.append(part_id)
				excel_part_name.append(part_name)
				excel_part_thickness.append(part_thickness)
				excel_part_mat.append(part_mat)
			else:
				empty+=1
			row+=1
			value=utils.XlsxGetCellValue(xl_parts,params['Excel sheet name'], row , Component_column)
			name_list = value.split('Battery Case Assembly')
			if len(name_list) > 1:
				empty=20

		parts = base.CollectEntities(solver, entities, ent, prop_from_entities=True)
		deck = base.CurrentDeck()

		for part in parts:
			name = part._name
			name_list = name.split(params['Delimiter for part name'])
			pid_name=name_list[int(params['Segment of part name'])-1]
			identifier=-1
			for interval in range(len(excel_part_name)):
				if (len(pid_name.split(excel_part_name[interval])) > 1 and len(pid_name.split(excel_part_id[interval])) > 1):
					print('find_excel_part_name:',pid_name,' vs.:',excel_part_id[interval],'_',excel_part_name[interval])
					identifier = interval

			if identifier != -1:

				# check of thickness by info from part name
				if str(params['Thickness by part name check']) == 'YES':
					# print('Segment of thickness name :',params['Segment of thickness name'])
					# print('excel value :',excel_part_thickness[identifier])
					if (str(params['Segment of thickness name']) != "0" and str(params['Segment of thickness name']) != "var") and str(params['Segment of thickness name']) != "" :
						thickness_from_part_name = name_list[int(params['Segment of thickness name'])-1]
						thickness_from_part_name = thickness_from_part_name.replace("mm","")
						thickness_from_part_name = thickness_from_part_name.replace("t", "")
						thickness_from_part_name = thickness_from_part_name.replace("_", "")
						if float(excel_part_thickness[identifier]) != float(thickness_from_part_name):
							if float(excel_part_thickness[identifier]) > 0.:
								t5.add_issue(entities = [part], status = 'Error',
									description = 'Thickness is different than '+str(excel_part_thickness[identifier]),
									thickness = str(thickness_from_part_name),
									thickness_suggest = str(excel_part_thickness[identifier]),
									key  = thickness,
									solver = str(solver))
							else:
								t5.add_issue(entities = [part], status = 'Warning',
									description = 'Thickness is different than '+str(excel_part_thickness[identifier]),
									thickness = str(thickness_from_part_name),
									key  = thickness,
									solver = str(solver))

				# check of material by info from part name
				if str(params['Material by part name check']) == 'YES':
					# print('Segment of material name :',params['Segment of material name'])
					# print('excel value :',excel_part_mat[identifier])
					if (str(params['Segment of material name']) != "0" and str(params['Segment of material name']) != "var") and str(params['Segment of material name']) != "" :
						material_from_part_name = name_list[int(params['Segment of material name'])-1]
						if excel_part_mat[identifier] != material_from_part_name:
							t7.add_issue(entities = [part], status = 'Error',
								description = 'Material is different than '+str(excel_part_mat[identifier]),
								thickness = str(material_from_part_name),
								thickness_suggest = str(excel_part_mat[identifier]),
								key  = thickness,
								solver = str(solver))

		CheckItem.reports.append(t5)
		CheckItem.reports.append(t7)
	else:
		print ('Excel file was not chosen.')
		# session.Quit()

	return CheckItem.reports



@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
	for issue in issues:
		ents = issue.entities
		if issue.description.startswith( 'Contact thickness' ):
			field = {issue.key:issue.c_thickness_suggest}

		if issue.description.startswith( 'Thickness' ):
			field = {issue.key:issue.thickness_suggest}
		for ent in ents:
			success = ent.set_entity_values(int(issue.solver), field)
			if success == 0:
				issue.is_fixed = True



# Update this dictionary to load check automatically
checkOptions = {'name': 'Check parts by xlsx file (PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks parts'}
checkDescription = base.CheckDescription(**checkOptions)

# Add parameters
checkDescription.add_str_param('Segment of part name', '1')
checkDescription.add_str_param('Segment of material name', '2')
checkDescription.add_str_param('Segment of thickness name', '3')
checkDescription.add_str_param('Number of segments', '4')
checkDescription.add_str_param('Thickness by part name check', 'YES')
checkDescription.add_str_param('Material by part name check', 'YES')
checkDescription.add_str_param('Excel sheet name', 'BCC18FU_Var_B_Cost')
checkDescription.add_str_param('Excel part name identifier', 'Component')
checkDescription.add_str_param('Excel part number name identifier', 'P/N')
checkDescription.add_str_param('Excel material name identifier', 'Material')
checkDescription.add_str_param('Excel thickness name identifier', 't [mm]')
checkDescription.add_str_param('Solver', 'PAMCRASH')
checkDescription.add_str_param('Delimiter for part name', '__')

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
