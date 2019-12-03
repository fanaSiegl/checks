# PYTHON script

import os, ansa, re, getpass
from ansa import base, constants
from datetime import date



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['GROUP']



class include_comment:

	def __init__(self):
		self.entity = None


	def add_comment_change(self, entity):
		if entity:
			include = base.GetEntityInclude(entity)
			user = getpass.getuser()
			today = date.today()
			dat = today.strftime('- date: %d.%m.%Y')
			field = {'Comment':'The include was changed: '+dat+'  - user:'+user}
			include.set_entity_values(constants.PAMCRASH,field )



class rbody_cls (base.Entity):

	def __init__(self, id):
		super().__init__( constants.PAMCRASH, id, 'GROUP')
		self.part_name = " "
		self.entities = list()
		vals_group = ['Name']


	def get_content_of_group(self, group):
		group_content = None
		type_group = None
		self.group_content = None   # output atribute - ansa entity in group
		self.type_group = None      # output atribute - type of group (combine group/mesh group)
		type_group = "MESH GROUP"
		if group and group != ' ':
			print('group content:', group,'\'')
			group_content = base.CollectEntities(constants.PAMCRASH,group, None )
			for entity in  group_content:
				type_group_tmp = entity.ansa_type(constants.PAMCRASH)
				if type_group_tmp == 'GROUP':
					type_group = "COMBINE GROUP"
					break
		self.group_content = group_content
		self.type_group = type_group


	def realize(self):
		group_name = self._name
		self.mesh_group_content = list ()   #atribute for mesh group
		self.combine_group_content = None    #atribute for mesh group

		if '-' in group_name and 'Scr' in group_name and not('vs' in group_name):
			contain_group = self.get_content_of_group(self)   #extract combine group content
			if self.type_group == "MESH GROUP":
				self.mesh_group_content = None
				self.combine_group_content = None
				return
			# find the component ids for combine group
			self.combine_group_content = self.get_entity_component_id(self.group_content, self.type_group, self )

			# iterate for mesh groups in combine group
			if self.combine_group_content['groups']:
				c_g_c = self.combine_group_content['groups']
				if type(c_g_c) != list():
					c_g_c = [c_g_c]
				for group in c_g_c:
					contain_group = self.get_content_of_group(group)   #extract content of mesh group
					mesh_component_id = self.get_entity_component_id(self.group_content, self.type_group, group)

					# find the component ids for mesh group
					self.mesh_group_content.append(mesh_component_id)


	def get_entity_component_id(self,entities, type_group,group):
		groups = list()
		entities_all_in_groups = list()
		groups_all = list()
		entities_all = list()
		entities_without_groups_e = list()
		component_ids= list()
		component_id = ''
		groups_all = list()
		if entities and type_group:
			if type_group == 'COMBINE GROUP':
				component_id =[]
				final_entity = []
				read_ent_stop = False

				for entity in entities:

					if  entity.ansa_type(constants.PAMCRASH) != "GROUP":
						entities_all.append(entity)
						final_entity.append(entity)
					else:
						groups_all.append(entity)
						entities_all_in_groups.extend(base.CollectEntities(constants.PAMCRASH,entity,None ))
				i = 0
				for entity in final_entity:
					if not(entity in entities_all_in_groups):
						if entity.ansa_type(constants.PAMCRASH) == 'CNODE' and i<1:
							i = i + 1
							name = self.get_part_name_from_entity(entity)['part_id']
							component_id.append('PID'+str(name))
						if entity.ansa_type(constants.PAMCRASH) != 'CNODE':
							name = self.get_part_name_from_entity(entity)['part_id']
							component_id.append(str(name))

				if not groups_all:
					groups_all = " "
				if not component_id:
					component_id = " "
				print ('COMBINE GROUP part id:   ', component_id)
				return {'component_id':component_id, 'groups':groups_all}

			if type_group == 'MESH GROUP'	:
				i= 0
				for entity in entities:
					if entity.ansa_type(constants.PAMCRASH) == 'CNODE':
						i = i + 1
					if entity.ansa_type(constants.PAMCRASH) != 'CNODE' or i== 1:
						name = self.get_part_name_from_entity(entity)['part_name']
						component_id = text_analyse.analyse(text=name,delimiter ='_',start = 'Part', end = 'screw_to',index = 1)
						component_ids.append(component_id ['text_list'])
						break

				print ('MESH GROUP:   ', component_ids)
				if not groups_all:
					groups_all = " "
				if not component_id:
					component_id = " "
				return {'component_id':component_ids,  'groups':group}
		else:
			if not groups_all:
				groups_all = " "
			if not component_id:
				component_id = " "
			return {'component_id':component_id, 'groups':group}


	def get_part_name_from_shell(self,shells):
		part_name = " "
		part_id = " "
		if shells:
			if type(shells) is not list:
				shells = [shells]
			for shell in shells:
				shell=shells[0]
				vals = [ 'IPART']
				part = shell.get_entity_values(constants.PAMCRASH, vals)
				part_name = part['IPART']._name
				if not part_name:
					part_name = " "
				part_id  = part['IPART']._id
				break
			else:
				part_name = " "
				part_id = " "

		return {'part_name':part_name, 'part_id':part_id}


	def get_part_name_from_entity(self, entity):
		type = entity.ansa_type(constants.PAMCRASH)
		part_return = {'part name':' ', 'part id':' '}
		exit_loop = False

		if type == 'COMPOSITE' or type == 'PART_SHELL':
			part_name = entity._name
			if not part_name:
				part_name = " "
			part_id  = entity._id
			part_return = {'part_name':part_name, 'part_id':part_id}
			print("reference part shell-like:   ", entity._id)

		if type  == "SHELL":
			part_return = self.get_part_name_from_shell(entity)
			print("shell: ",entity._id)

		if type  == "NODE":
			shells = base.NodesToElements(entity)
			for from_node in shells[entity]:
				type_content = from_node.ansa_type(constants.PAMCRASH)
				if type_content == "SHELL":
					print("node: ",entity._id,"  -reference shell:   ", from_node._id)
					part_return = self.get_part_name_from_shell(from_node)
					break

		if type  == "CNODE":
			print('cnode: ', entity._id )
			shells = base.NodesToElements(entity)
			flag_shell = False
			for from_cnode in shells[entity]:
				if exit_loop == True:
					break
				type_elem = from_cnode.ansa_type(constants.PAMCRASH)

				if type_elem == "SHELL" :
					part_return = self.get_part_name_from_shell(from_cnode)
					flag_shell = True
					print('cnode: ', cn._id ,' - directy connected to reference shell:', from_cnode._id)
					break

			if not flag_shell:
				print("cnode: ", entity._id ," without shell reference - will be try to find a close cnode entity ")
				coords = (entity.position)
				near_elem = base.NearElements(coordinates=coords, tolerance=1)
				type_content = "CNODE"
				cnodes = base.CollectEntities(constants.PAMCRASH,near_elem[0] , type_content)
				cnodes.remove(entity)
				list_lenghts = list()
				i = 0
				for cnode in cnodes:
					i = i +1
					pos = cnode.position
					lenght = ((coords[0]-pos[0])**2 + (coords[1]-pos[1])**2 + (coords[2]-pos[2])**2)**0.5
					list_lenghts.append(lenght)
				if i == 1:
					list_lenghts = [list_lenghts]
				min_lenght = min(list_lenghts)
				index = list_lenghts.index(min_lenght)
				# print('index', index)
				if cnodes[index]:
					cn = cnodes[index]
					print('cnode: ', entity._id ,' - was found close cnode: ', cn._id)
					shells = base.NodesToElements(cn)
					for elem in shells[cn]:
						exit_loop = True
						type_elem = elem.ansa_type(constants.PAMCRASH)
						print('cnode: ', entity._id ,' - was found close cnode and a connected entity  :',elem._id )

						if 'KJOIN' in type_elem:
							print('cnode: ', entity._id ,' - was found close cnode and connected entity is KJOIN-ish :', elem._id)
							vals = [ 'N1','N2']
							kjoint = elem.get_entity_values(constants.PAMCRASH, vals)
							if kjoint['N1'] == cn:
								node = kjoint['N2']
							else:
								node = kjoint['N1']

							from_kjoint = base.NodesToElements(node)

							for to_rbody in from_kjoint[node]:
								type_elem = to_rbody.ansa_type(constants.PAMCRASH)
								if type_elem == 'RBODY' or type_elem == 'MTOCO' or type_elem == 'OTMCO':
									print('cnode: ', entity._id ,' was found close cnode and connected entity is KJOIN-ish and was found some RBODY :', to_rbody._id)
									vals = [ 'NOD1','NOD2','NSET']
									node = to_rbody.get_entity_values(constants.PAMCRASH, vals)
									if node:
										node = node[ 'NOD1']
										if node == cn:
											node = node[ 'NOD2']
										shells = base.NodesToElements(node)
										for from_node in shells[node]:
											type_content = from_node.ansa_type(constants.PAMCRASH)
											if type_content == "SHELL":
												print('cnode: ', entity._id ,' - was found close cnode and connected entity is KJOIN-ish and was found some RBODY and connected SHELL is :', from_node._id)
												part_return = self.get_part_name_from_shell(from_node)
												exit_loop = True
												break

						if type_elem == 'RBODY' or type_elem =='MTOCO' or type_elem =='OTMCO':
							print('cnode: ', entity._id ,' was found close cnode and connected entity is RBODY',elem._id	)
							vals = [ 'NOD1','NOD2','NSET']
							node = elem.get_entity_values(constants.PAMCRASH, vals)
							if node and ('NOD1' in  node.keys()):
								node = node[ 'NOD1']
								if node == cn:
									node = node[ 'NOD2']
									shells = base.NodesToElements(node)
									for from_node in shells[node]:
										type_content = from_node.ansa_type(constants.PAMCRASH)
										if type_content == "SHELL":
											print('cnode: ', entity._id ,' was found close cnode and connected entity is RBODY and connected SHELL is:', from_node._id)
											part_return = self.get_part_name_from_shell(from_node)
											exit_loop = True
											break

							elif node and ('NSET' in  node.keys()):
								self.get_content_of_group(node[ 'NSET'])
								entities_from_group_e = self.group_content
								for e in entities_from_group_e:
									type_elem = e.ansa_type(constants.PAMCRASH)
									if type_elem == "SHELL":
										part_return = self.get_part_name_from_shell(e)
										exit_loop = True
										break

						if type_elem == 'SHELL':
							print("cnode: ", entity._id ," - reference cnode shell:",elem._id)
							part_return = self.get_part_name_from_shell(elem)
							exit_loop = True
							break

		return part_return



class text_analyse:

	def __init__(self):
		self.text = " "

	@staticmethod
	def analyse(**kwargs):
		text_selection = list()
		text_selection_special = list()
		text_selection_special_inv = list()
		# text_matix = kwargs['text'].split(kwargs['delimiter'])
		text_matix = re.split(kwargs['delimiter'], kwargs['text'])
		read = False
		exclude = False

		for strings in text_matix:

			if 'exclude' in kwargs.keys():
				if kwargs['exclude'] in strings:
					exclude = True
				else:
					exclude = False

			if 'start' in kwargs.keys():

				if (kwargs['start'] in strings) and (read == False) and (exclude == False):
					read = True
			# else:
				# read = True

			if 'end' in kwargs.keys():

				if (kwargs['end'] in strings) and (read == True) and (exclude == False):
					read = False
			# else:
				# read = True

			if (read  == True) and (exclude == False):
				text_selection.append(strings)

				if 'special' in kwargs.keys():
					if kwargs['special'] in strings:
						text_selection_special.append(strings)
						if kwargs['special_inv']:
							a = strings
							b= a.replace(kwargs['special'],"")
							if kwargs['special_inv'] == True:
								text_selection_special_inv.append(b)


		if 'index' in kwargs.keys():
			index = kwargs['index']

			if len(text_selection) <= index or not(text_selection):
				return {'text_list':" ",
						'special_list':text_selection_special,
						'special_list_inv':text_selection_special_inv}
			else:
				return {'text_list':text_selection[index],
						'special_list':text_selection_special,
						'special_list_inv':text_selection_special_inv}

		else:
			return {'text_list':text_selection,
					'special_list':text_selection_special,
					'special_list_inv':text_selection_special_inv}



@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):
	t1 = base.CheckReport('GROUP groups check - 1. wawe - COMBINE GROUP name - components number')
	t2 = base.CheckReport('GROUP groups check - 2. wawe - Screw number in MESH GROUP name vs. COMBINE GROUP name')
	t3 = base.CheckReport('GROUP groups check - 3. wawe - MESH GROUP name vs. COMBINE GROUP name')
	t4 = base.CheckReport('RBODY groups check - 4. wawe - MESH GROUP name - order of components')
	t5 = base.CheckReport('RBODY groups check - 5. wawe - RBODY name and COMBINE GROUP name')
	t6 = base.CheckReport ('RBODY groups check - all is OK')

	t1.has_fix = True
	t2.has_fix = True
	t3.has_fix = True
	t4.has_fix = True
	t5.has_fix = True
	t6.has_fix = False

	if entities:
		if type(entities) == list:
			for group in entities:
				if base.IsEntityVisible(group) and 'Scr' in group._name and '-' in group._name:

					groups = list()
					groups_name = list()
					index = 0
					index_miss = 0
					index_add = 0
					index_invert = 0
					name_group = group._name
					id_miss = list()
					id_add = list()
					ids_from_parts = list()
					name_list = text_analyse.analyse(text=name_group,delimiter ='_|-',start = 'Scr', special = 'Scr',
													 special_inv = True)
					number_parts = len(name_list['text_list'])-1

					group_obj = rbody_cls (group._id)
					group_obj.realize()
					mesh_component_ids = group_obj.mesh_group_content
					temp = group_obj.combine_group_content

					if temp != None:
						for mesh_component_id in mesh_component_ids:
							ids = mesh_component_id['component_id']
							group_mesh = mesh_component_id['groups']
							groups.append(group_mesh)
							groups_name.append(group_mesh._name)
							id = ids[0]
							ids_from_parts.append(id)

						id = [temp['component_id'][0]]
						ids_from_parts.extend(id)

						flag_1_level_error = True
						flag_2_level_error = True
						flag_3_level_error = True
						flag_4_level_error = True
						flag_5_level_error = True
						flag_6_level_error = True

						# component numbers from parts vs. combine group name
						name_list = text_analyse.analyse (text=name_group , delimiter='_|-' , start='Scr' )
						name_sort = sorted (name_list['text_list'][1:])
						name_component_sort = sorted(ids_from_parts)
						if name_component_sort == name_sort:
							pass
						else:
							lenght = len (ids_from_parts)
							name_info = 'Component number vs. name of COMBINE GROUP: ' + str (name_group) + \
										' doesnt match with components' + str (ids_from_parts)
							t1.add_issue (entities=[group] , status='Error' , description=name_info)
							flag_1_level_error = False

						# kontrola cisla scr v group - shoda mesh group a combine group
						if flag_1_level_error :
							name_list = text_analyse.analyse(text=name_group,delimiter ='_|-',start = 'Scr',
															special = 'Scr', special_inv = True)
							for egroup in groups:
								name_list_g = text_analyse.analyse(text=egroup._name,delimiter ='_',start = 'Scr',
															special = 'Scr', special_inv = True, Exclude = 'vs')

								if name_list_g['special_list_inv'] ==name_list['special_list_inv']:
									pass
								else:
									name_info = 'Different number of screw in group names. '\
												+str( name_list_g['special_list_inv'])+ \
												'   '+ str(name_list['special_list_inv'])

									t2.add_issue(entities = [group]+groups, status = 'Warning' , description = name_info)
									flag_2_level_error = False

						# kontrola jmen group - shoda mesh group a combine group
						if flag_1_level_error and flag_2_level_error :
							name_list = text_analyse.analyse (text=name_group , delimiter='_|-' , start='Scr' )
							name_sort = sorted (name_list['text_list'][1:])

							for egroup in groups:
								name_list_g = text_analyse.analyse(text=egroup._name,delimiter ='_',start = 'Scr',exclude = 'vs')
								name_sort_g = sorted (name_list_g['text_list'][1:])
								if name_sort_g == name_sort:
									pass
								else:
									lenght = len (ids_from_parts)
									name_info = 'Different name COMBINE GROUP: '+ str(name_list['text_list'][1:])+ \
										'MESH GROUP:' + str(name_list_g ['text_list'][1:])
									t3.add_issue (entities=[group]+[egroup] , status='Warning' , description=name_info)
									flag_3_level_error = False

						# kontrola jmen group - order of components
						if flag_1_level_error and flag_2_level_error and flag_3_level_error :
							name_list = text_analyse.analyse (text=name_group , delimiter='_|-' , start='Scr')
							i = 0
							for egroup in groups:
								name_list_g = text_analyse.analyse (text=egroup._name , delimiter='_' , start='Scr' ,
																	exclude='vs')
								if name_list_g['text_list'][1] ==  ids_from_parts[i]:
									pass
								else:
									lenght = len (ids_from_parts)
									name_info = 'Different name MESH GROUP: ' + str (egroup._name) + \
												' the first component should be: ' + "\""+str (ids_from_parts[i])+"\""
									t4.add_issue (entities=[egroup] , status='Warning' , description=name_info)
									flag_4_level_error = False
								i = i + 1

						# kontrola jmen RBODY
						if flag_1_level_error and flag_2_level_error and flag_3_level_error and flag_4_level_error:
							ents = base.ReferenceEntities (group)
							name_rbody = None
							rbody_ent = None
							name_info = None
							for entities_ref in ents:
								if entities_ref.ansa_type (constants.PAMCRASH) == 'RBODY':
									name_rbody = entities_ref._name
									name_info = " "
									rbody_ent = entities_ref
									if 	rbody_ent:
										if name_group == name_rbody:
											pass
										else:
											name_info = 'Different name COMBINE GROUP: ' + name_group + ' RBODY name: '+ name_rbody
											t5.add_issue (entities=[group , rbody_ent] , status='Warning' ,
														  description=name_info)
											flag_5_level_error = False
									else:
										name_info = 'Missing reference RBODY: ' + name_group
										t5.add_issue (entities=[group] , status='Error' , description=name_info)
										flag_5_level_error = False

							if 	flag_5_level_error == True:
								name_info = 'RBODY is OK: ' + name_group
								t6.add_issue (entities=[group] , status='Warning' , description=name_info)
		else:
			entities = [entities]

	CheckItem.reports.append(t1)
	CheckItem.reports.append(t2)
	CheckItem.reports.append(t3)
	CheckItem.reports.append(t4)
	CheckItem.reports.append(t5)
	CheckItem.reports.append(t6)

	return CheckItem.reports



@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
	for issue in issues:
		# print(issue.has_fix)
		problem_description = issue.description
		ents = issue.entities
		print(problem_description)
		print(ents)

		if 'Component number vs. name of COMBINE GROUP' in problem_description:
			group_combine = ents[0]
			name_list   = text_analyse.analyse (text=problem_description , delimiter='\'',
												start='Component number vs. name of COMBINE GROUP' )
			lenght = len(name_list['text_list'])
			name_list_n = text_analyse.analyse (text=group_combine._name , delimiter='_|-' , start='Scr' ,
											  special='Scr' , special_inv=True)
			print('name_list_n:  ',name_list_n)
			text = 'Scr' + str (name_list_n['special_list_inv'][0])+ '_'
			ran = range(1,lenght,2)

			for i in ran:
				print('name_list[i]:    ',name_list['text_list'][i])
				text = text + str(name_list['text_list'][i]) + '-'
			text = text [:-1]
			field = {'Name':text}
			success = group_combine.set_entity_values (constants.PAMCRASH , field)
			if success == 0:
				ic = include_comment ()
				ic.add_comment_change (group_combine)
				issue.is_fixed = True
				issue.update ()

		if 'Missing reference RBODY' in problem_description:
			success = None
			vals = {'Name': name_group  , 'NSET': group._id , 'ITRB': 0} # , 'NCOG': node._id
			rbody = base.CreateEntity (constants.PAMCRASH , "RBODY" , vals)
			if rbody:
				success = 0
			if success == 0:
				ic = include_comment ()
				ic.add_comment_change (rbody)
				issue.is_fixed = True
				issue.update ()

		if 'Different name COMBINE GROUP' in problem_description:
			group_entity = ents[0]
			rbody_entity = ents[1]
			for e in ents:
				if e.ansa_type(constants.PAMCRASH) == "GROUP":
					group_entity = e
				if e.ansa_type(constants.PAMCRASH) == "RBODY":
					rbody_entity = e

			field = {'Name':group_entity._name}
			success = rbody_entity.set_entity_values(constants.PAMCRASH, field)
			if success == 0:
				ic = include_comment ()
				ic.add_comment_change (rbody_entity)
				issue.is_fixed = True
				issue.update ()

		if 'Different number of screw' in problem_description:
			for e in ents:
				if 'Scr' in e._name and '-' in e._name:
					group_combine = e
				else:
					groups_mesh = e
			name_list = text_analyse.analyse (text=group_combine._name , delimiter='_' , start='Scr' , special='Scr' ,
												special_inv=True , Exclude='vs')
			name_ids = name_list['special_list_inv'][0]
			success = list ()

			gr_mesh_name = groups_mesh._name
			if not("Scr" in gr_mesh_name):
				gr_mesh_name = "Scr01_" + gr_mesh_name
			name_list_g = text_analyse.analyse(text=gr_mesh_name,delimiter ='_',start = 'Scr', special = 'Scr', special_inv = True, Exclude = 'vs')
			name_id = name_list_g['special_list_inv'][0]

			new_group_name = gr_mesh_name.replace ("Scr"+str(name_id) , "Scr"+str(name_ids))
			print('new_group_name:  ',new_group_name)
			field = {'Name':new_group_name}
			success = groups_mesh.set_entity_values(constants.PAMCRASH, field)
			if success == 0:
				ic = include_comment ()
				ic.add_comment_change (groups_mesh)
				issue.is_fixed = True
				issue.update ()

		# name COMBINE GROUP vs. MESH GROUP name
		if 'Different name COMBINE GROUP' in problem_description and 'MESH GROUP' in problem_description:
			for e in ents:
				if 'Scr' in e._name and '-' in e._name:
					group_combine = e
				else:
					groups_mesh = e

			name_list = text_analyse.analyse (text=group_combine._name , delimiter='_|-' , start='Scr')
			name_list_c = name_list['text_list']
			success = list ()
			i = 0
			new_group_name = ''
			for conp in name_list_c:
				if i == 1:
					new_group_name = new_group_name + str (conp) + '_vs_'
				else:
					new_group_name = new_group_name +str (conp) + '_'
				i = i +1

			new_group_name = new_group_name[:-1]
			field = {'Name':new_group_name}
			success = groups_mesh.set_entity_values(constants.PAMCRASH, field)
			if  success == 0:
				ic = include_comment ()
				ic.add_comment_change (groups_mesh)
				issue.is_fixed = True
				issue.update ()

		# name order componets in MESH GROUP name
		if 'the first component' in problem_description and 'MESH GROUP' in problem_description:
			groups_mesh = ents[0]
			name_list = text_analyse.analyse (text=groups_mesh._name , delimiter='_' , start='Scr', exclude='vs')
			name_list_m = name_list['text_list']
			name_list_c = text_analyse.analyse (text=problem_description , delimiter='\"', start='' )
			name_list_1 = name_list_c['text_list'][1]
			success = list ()

			i = 0
			new_group_name = ''
			index = name_list_m.index (name_list_1)
			del name_list_m[index]
			name_list_m.insert (1 , name_list_1)
			for conp in name_list_m:
				if i == 1:
					new_group_name = new_group_name + str (conp) + '_vs_'
				else:
					new_group_name = new_group_name +str (conp) + '_'
				i = i +1

			new_group_name = new_group_name[:-1]
			field = {'Name':new_group_name}
			success = groups_mesh.set_entity_values(constants.PAMCRASH, field)
			if  success == 0:
				ic = include_comment ()
				ic.add_comment_change (groups_mesh)
				issue.is_fixed = True
				issue.update ()



# Update this dictionary to load check automatically
checkOptions = {'name': 'Check RBODY elements for NISSAN (PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks RBODY elements'}
checkDescription = base.CheckDescription(**checkOptions)

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
