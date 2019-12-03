# PYTHON script

import os, ansa, re, getpass
from ansa import base, constants
from datetime import date



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['CNTAC']



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
			if include:
				include.set_entity_values(constants.PAMCRASH,field )
			return 1



class text_analyse:

	def __init__(self):
		self.text = "?"


	@staticmethod
	def analyse(**kwargs):
		text_selection = list()
		text_selection_special = list()
		text_selection_special_inv = list()
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
				return {'text_list':"?",
						'special_list':text_selection_special,
						'special_list_inv':text_selection_special_inv}
			else:
				if not(text_selection[index]) or text_selection[index] == '' or text_selection[index] == ' ':
					text_selection[index] = '?'
				return {'text_list':text_selection[index],
						'special_list':text_selection_special,
						'special_list_inv':text_selection_special_inv}

		else:
			return {'text_list':text_selection,
					'special_list':text_selection_special,
					'special_list_inv':text_selection_special_inv}



class tied_cls (base.Entity):

	def __init__(self, id):
		super().__init__( constants.PAMCRASH, id, 'CNTAC')
		self.part_slave_name = "?"
		self.part_master_name = "?"
		self.entities = list()
		vals_tied = ['NTYPE', 'NSS', 'NMS','IDPRT']
		t = self.get_entity_values(constants.PAMCRASH, vals_tied)
		self.tied_name = "?"
		self.tied_part_name = "?"
		self.tied_part_ent = "?"
		self.master_name_id_group = "?"
		self.slave_name_id_group = "?"
		self.group_master_name= "?"
		self.group_slave_name= "?"
		self.group_master_id= " ?"
		self.group_slave_id= "?"
		self.master_name_id_part= "?"
		self.slave_name_id_part= "?"
		self.tied_name_component_id_1= "?"
		self.tied_name_component_id_2 = "?"
		self.part_master_composite = False
		self.part_slave_composite = False
		self.part_slave_h = 0
		self.part_slave_name = "?"
		self.part_master_h = 0
		self.part_master_name = "?"
		if t['NTYPE'] == 'TIED':

			self.tied_name = self._name

			self.tied_part_ent = t ['IDPRT']
			self.tied_part_name = t ['IDPRT']._name

			self.group_ent_master = t ['NMS']
			self.group_ent_slave = 	t ['NSS']

			string_part = ['Name', 'SID']
			self.group_master= self.group_ent_master.get_entity_values(constants.PAMCRASH, string_part)
			self.group_slave=	self.group_ent_slave.get_entity_values(constants.PAMCRASH, string_part)

			self.group_master_name = self.group_ent_master._name

			self.group_slave_name =	self.group_ent_slave._name

			self.group_master_id = self.group_master['SID']
			self.group_slave_id =	self.group_slave['SID']

			type = ["PART_SHELL", "COMPOSITE"]
			parts_master = base.CollectEntities(constants.PAMCRASH,self.group_ent_master , type )
			parts_slave =	base.CollectEntities(constants.PAMCRASH,self.group_ent_slave , type )
			if not parts_master:
				parts_master = base.CollectEntities(constants.PAMCRASH,self.group_ent_master , type, prop_from_entities = True )
			if not parts_slave:
				parts_slave =	base.CollectEntities(constants.PAMCRASH,self.group_ent_slave , type, prop_from_entities = True )


			h_s = 0.0
			h_m = 0.0
			m_i = 0
			s_i = 0
			if parts_master:
				for self.part_master in parts_master:

					if self.part_master:
						m = self.part_master.get_entity_values(constants.PAMCRASH, ['h', 'Name','IMAT'])

						if self.part_master.ansa_type(constants.PAMCRASH) == 'PART_SHELL':
							self.part_master_h = m ['h']
							h_m = h_m + float(self.part_master_h)
							#print('self.part_master_h:', self.part_master_h)
							m_i = m_i +1.0
							self.part_master_composite = False
						elif self.part_master.ansa_type(constants.PAMCRASH) == 'COMPOSITE':
							self.part_master_h = m ['h']
							self.part_master_composite = True
							h_m = h_m + float(self.part_master_h	)
							print('self.part_master_h:', self.part_master_h)
							print('h_m:', h_m)
							m_i = m_i +1.0
						self.part_master_name =m ['Name']
						#print('m_i:', m_i)
					else:
						self.part_master_h = 0
						self.part_master_name = " "
				self.part_master_h = h_m/m_i
				print('self.part_master_h:', self.part_master_h)
			else:
				self.part_master_h = 0
				self.part_master_name = " "

			if parts_slave:
				for  self.part_slave in parts_slave:
					if  self.part_slave:
						m =  self.part_slave.get_entity_values(constants.PAMCRASH, ['h', 'Name','IMAT'])

						if self.part_slave.ansa_type(constants.PAMCRASH) == 'PART_SHELL':
							self.part_slave_h = m ['h']
							#print(self.part_slave_h)
							self.part_slave_composite = False
							h_s = h_s + float(self.part_slave_h)
							s_i = s_i +1.0
						elif self.part_slave.ansa_type(constants.PAMCRASH) == 'COMPOSITE':
							self.part_slave_h = m ['h']
							self.part_slave_composite = True
							h_s = h_s + float(self.part_slave_h)
							#print(self.part_slave_h)
							s_i = s_i +1.0
						self.part_slave_name =	m ['Name']
					else:
						self.part_slave_h = 0
						self.part_slave_name = " "
				self.part_slave_h = h_s/s_i
			else:
				self.part_slave_h = 0
				self.part_slave_name = " "


	def get_component_ids(self):
		self.master_name_id_group =text_analyse.analyse(
			text=self.group_master_name,
			delimiter ='_',
			start = 'Tms',
			end = 'vs',
			index = 1)

		self.slave_name_id_group = text_analyse.analyse(
			text=self.group_slave_name,
			delimiter ='_',
			start = 'Tsl',
			end = 'vs',
			index = 1)
		# print(self.group_master_name)
		self.master_name_id_group_slave =text_analyse.analyse(
			text=self.group_master_name,
			delimiter ='_',
			start = 'Tms',
			index = 3)
		# print('self.master_name_id_group_slave:', self.master_name_id_group_slave)

		self.slave_name_id_group_master = text_analyse.analyse(
			text=self.group_slave_name,
			delimiter ='_',
			start = 'Tsl',
			index = 3)
		# print('self.slave_name_id_group_master:', self.slave_name_id_group_master)

		self.master_name_id_part = text_analyse.analyse(
			text=self.part_master_name,
			delimiter ='_',
			start = 'Part',
			end = 'glue',
			index = 1)

		self.slave_name_id_part =text_analyse.analyse(
			text=self.part_slave_name,
			delimiter ='_',
			start = 'Part',
			end = 'glue',
			index = 1)

		if 	'_OL_' in self.part_slave_name and '_OL_' in self.part_master_name and self.master_name_id_part['text_list'] == self.slave_name_id_part['text_list'] :
			variable = re.search (r".*_L(?P<L1>\d\d)_OL_L(?P<L2>\d\d)_.*" ,self.part_slave_name)
			if variable:
				if variable.group('L1') and variable.group('L2'):
					self.slave_name_id_part['text_list'] = str(self.slave_name_id_part['text_list'])	+'OL'+ 	str(variable.group('L1')) + '-'  + str(variable.group('L2'))

			variable = re.search (r".*_L(?P<L1>\d\d)_OL_L(?P<L2>\d\d)_.*" ,self.part_master_name)
			if variable:
				if variable.group('L1') and variable.group('L2'):
					self.master_name_id_part['text_list'] = str(self.master_name_id_part['text_list'])	+'OL'+ 	str(variable.group('L1')) + '-'  + str(variable.group('L2'))

		self.master_name_id_part__slave = text_analyse.analyse(
			text=self.part_slave_name,
			delimiter ='_',
			start = 'glue',
			exclude = 'mm')

		self.slave_name_id_part__master =text_analyse.analyse(
			text=self.part_master_name,
			delimiter ='_',
			start = 'glue',
			exclude = 'mm')

		self.tied_name_component_id_1 = text_analyse.analyse(
			text=self.tied_name,
			delimiter ='_',
			start = 'TIE',
			exclude = 'vs',
			index = 1)
		self.tied_name_component_id_2 =text_analyse.analyse(
			text=self.tied_name,
			delimiter ='_',
			start = 'TIE',
			exclude = 'vs',
			index = 2)
		self.tied_part_name_component_id_1 = text_analyse.analyse(
			text=self.tied_part_name,
			delimiter ='_',
			start = 'PART',
			exclude = 'vs',
			index = 1)

		self.tied_part_name_component_id_2 =text_analyse.analyse(
			text=self.tied_part_name,
			delimiter ='_',
			start = 'PART',
			exclude = 'vs',
			index = 2)


	def thickness_from_mat(self, mat):
		no_of_ply = mat.get_entity_values(constants.PAMCRASH,['NOPER'])
		field = list()
		h_sum = 0.0

		for id in range(int(no_of_ply['NOPER'])):
			field.append( 'THKPL'+str(id+1))
		dist_h = mat.get_entity_values(constants.PAMCRASH,field)
		for h, val in dist_h.items():
			h_sum = h_sum + float(val)

		return h_sum



@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):
	t0 = base.CheckReport('Tied check - 1. wave - master and slave roles')
	t1 = base.CheckReport('Tied check - 2. wave - check of GROUPs names - identification of master or slave role - Tms or Tsl')
	t2 = base.CheckReport('Tied check - 3. wave - check of GROUPs names - check component numbers from PARTs')
	t3 = base.CheckReport('Tied check - 3. wave - check of GROUPs names - check component numbers from PARTs - not possible auto fix')
	t4 = base.CheckReport('Tied check - 4. wave - check of consistency of GROUP names and TIEDs  names')
	t5 = base.CheckReport('Tied check - 5. wave - check of consistency of TIED names and PART TIED  names')
	t100 = base.CheckReport('Tied check - TIEDs are OK')
	t0.has_fix = True
	t1.has_fix = True
	t2.has_fix = True
	t3.has_fix = False
	t4.has_fix = True
	t5.has_fix = True

	if entities:
		if not(type(entities) == list):
			entities = [entities]

		if type(entities) == list:
			for tied_ent in entities:

				tied = tied_cls(tied_ent._id)
				tie = [base.GetEntity(constants.PAMCRASH, "CNTAC", tied_ent._id)]
				tied.get_component_ids()
				# TODO OSError: [Errno5] Input/output error - can't fix
				print('----------------------------------------------------------')
				print('tied name:', tied._name)
				print('tied_part_name:', tied.tied_part_name)
				print('master_name_id_part:', tied.master_name_id_part['text_list'])
				print('slave_name_id_part:', tied.slave_name_id_part['text_list'])
				print("part slave_name:", tied.part_slave_name)
				print("part master_name: ", tied.part_master_name)
				print("group master_name: ", tied.group_master_name)
				print("group slave_name: ", 	tied.group_slave_name	)
				print("part_slave_composite: ", tied.part_slave_composite	)
				print("part_master_composite: ", 	tied.part_master_composite	)
				print("part_master_h: ", 	tied.part_master_h	)
				print("part_slave_h: ", 	tied.part_slave_h	)

				############# zero level

				if tied.part_slave_name == " " and tied.part_master_name == " ":
					name_info = 'Tied ID: \"'+ str(tied._id)+  "\" Name: \""+ tied._name +'\" - both master and slave group are empty'
					t1.add_issue(entities = tie, status = "error", description = name_info)

				elif  tied.part_master_name == " ":
					name_info = 'Tied ID: \"'+ str(tied._id)+  "\" Name: \""+ tied._name +'\" - master group is empty'
					t1.add_issue(entities = tie, status = "error", description = name_info)

				elif tied.part_slave_name == " " :
					name_info = 'Tied ID: \"'+ str(tied._id)+  "\" Name: \""+ tied._name +'\" - slave group is empty'
					t1.add_issue(entities = tie, status = "error", description = name_info)

				else:
					if (not(tied.part_slave_composite) and tied.part_master_composite):
							status = False
					if (not(tied.part_master_composite) and (tied.part_slave_composite)):
							status = True
					if (not(tied.part_slave_composite) and not(tied.part_master_composite)):
						if (tied.part_slave_h <= tied.part_master_h):
							status = True
						else:
							status = False
					if ((tied.part_slave_composite) and (tied.part_master_composite)):
						if (tied.part_slave_h <= tied.part_master_h):
							status = True
						else:
							status = False
					if status == False:
						name_info = 'Tied ID: \"' + str(tied._id)+ "\" Name: \""+ tied._name +'\" - you should switch the master and slave group'
						t0.add_issue(entities = tie, status = "error", description = name_info)
						status_groups = "Error"
					name_info = ""
					if status == True:
						status_groups = "OK"
						name_info = 'Tied ID: \"' + str(tied._id)+ "\" Name: \""+ tied._name + '\"  '

						############# first level

						flag_1_level_error = True
						flag_2_level_error = True
						flag_3_level_error = True
						flag_4_level_error = True
						flag_5_level_error = True

						if not("Tms" in tied.group_master_name):
							name_info = name_info +' in master \"GROUP  NAME \" missing Tms |'
							status_groups = "Warning"
							flag_1_level_error = False
							print('----------------------------')

						if not("Tsl" in tied.group_slave_name):
							name_info = name_info + ' in slave \"GROUP  NAME \" missing Tsl |'
							status_groups = "Warning"
							flag_1_level_error = False
							print('----------------------------')

						############# second level

						if flag_1_level_error:
							if ((str(tied.master_name_id_part["text_list"]) != str(tied.master_name_id_group["text_list"]))):
								name_info = name_info + 'Component id doesn\'t match with master \"GROUP NAME\" ' +str(tied.master_name_id_group["text_list"])+ \
									' and master part name '+ str (tied.master_name_id_part["text_list"]) + ' | '
								status_groups = "Warning"
								flag_2_level_error = False

							if ((str(tied.slave_name_id_part["text_list"]) != str(tied.slave_name_id_group["text_list"]))):
								name_info = name_info + 'Component id doesn\'t match with slave \"GROUP NAME\" '+str(tied.slave_name_id_group["text_list"])+ \
									' and slave part name ' + str (tied.slave_name_id_part["text_list"]) + ' | '
								status_groups = "Warning"
								flag_2_level_error = False

							if ((str(tied.master_name_id_part["text_list"]) != str(tied.slave_name_id_group_master["text_list"]))):
								name_info = name_info + 'Second component id doesn\'t match with slave \"GROUP NAME\" ' +str(tied.slave_name_id_group_master["text_list"])+ \
									' and master part name '+ str (tied.master_name_id_part["text_list"]) + ' | '
								status_groups = "Warning"
								flag_2_level_error = False

							if ((str(tied.slave_name_id_part["text_list"]) != str(tied.master_name_id_group_slave["text_list"]))):
								name_info = name_info + 'Component id doesn\'t match with master \"GROUP NAME\" '+str(tied.master_name_id_group_slave["text_list"])+ \
									' and slave part name ' + str (tied.slave_name_id_part["text_list"]) + ' | '
								status_groups = "Warning"
								flag_2_level_error = False
						############# third level
						if flag_2_level_error and flag_1_level_error:
							if (not(str(tied.master_name_id_part["text_list"]) in tied.master_name_id_part__slave["text_list"]) ):
								status_groups = "Warning"
								name_info = name_info + 'Component id from master \"GROUP NAME\" '+ str(tied.master_name_id_part["text_list"])+\
											' doesn\'t match component id from slave part name behind the \"glue_to\"'+ str(tied.master_name_id_part__slave["text_list"]) + ' | '
								flag_3_level_error = False

							if (not(str(tied.slave_name_id_part["text_list"]) in tied.slave_name_id_part__master["text_list"]) ):
								status_groups = "Warning"
								name_info = name_info + ' Component id from slave \"GROUP NAME\" '+ str(tied.slave_name_id_part["text_list"])+\
											' doesn\'t match component id from master part name behind the \"glue_to\" '+ str(tied.slave_name_id_part__master["text_list"])
								flag_3_level_error = False

						############# fourth level ####### check the TIED name
						if flag_2_level_error and flag_1_level_error:
							if (str(tied.tied_name_component_id_1["text_list"]) != str(tied.master_name_id_group["text_list"]) ):
								status_groups = "Warning"
								name_info = name_info + 'The first component id from \"TIED NAME\" '+tied.tied_name_component_id_1["text_list"]+\
											' doesn match with master name group '+ str (tied.master_name_id_group["text_list"])+'. '
								flag_4_level_error = False

							if (str(tied.tied_name_component_id_2["text_list"]) != str(tied.slave_name_id_group["text_list"]) ):
								status_groups = "Warning"
								name_info = name_info + 'The second  component id from \"TIED NAME\" '+str(tied.tied_name_component_id_2["text_list"])+\
											' doesn match with slave name group '+str (tied.slave_name_id_group["text_list"])+'. '
								flag_4_level_error = False

						############# fifth level ###### check the PART TIED name
						if flag_2_level_error and flag_1_level_error and flag_4_level_error:
							if (tied.tied_part_name_component_id_1["text_list"] != str(tied.master_name_id_group["text_list"]) ):

								status_groups = "Warning"
								name_info = name_info + 'The first component id from \"PART TIED NAME\" name: '+tied.tied_part_name_component_id_1["text_list"]+\
											' doesn match with  component of master GROUP NAME: '+str(tied.master_name_id_group["text_list"])
								flag_5_level_error = False

							if (tied.tied_part_name_component_id_2["text_list"] != str(tied.slave_name_id_group["text_list"]) ):

								status_groups = "Warning"
								name_info = name_info + 'The second component id from \"PART TIED NAME\" name: '+tied.tied_part_name_component_id_2["text_list"]+\
											' doesn match with  component of slave GROUP NAME: '+str(tied.slave_name_id_group["text_list"])
								flag_5_level_error = False

						if status_groups == "OK":
							name_info = 'Tied is OK - ID: \"' + str(tied._id)+ "\" Name: \""+ tied._name + '\"  '
							status_groups = "Warning"
							t100.add_issue(entities = tie, status = status_groups , description = name_info)
						if status_groups == "Error":
							t0.add_issue(entities = tie, status = status_groups , description = name_info)
						elif not(flag_1_level_error):
							t1.add_issue(entities = tie, status = status_groups , description = name_info)
						elif not(flag_2_level_error):
							t2.add_issue(entities = tie, status = status_groups , description = name_info)
						elif not(flag_4_level_error):
							t4.add_issue(entities = tie, status = status_groups , description = name_info)
						elif not(flag_5_level_error):
							t5.add_issue(entities = tie, status = status_groups , description = name_info)
						if not(flag_3_level_error):
							t3.add_issue(entities = tie, status = status_groups , description = name_info)

	CheckItem.reports.append(t0)
	CheckItem.reports.append(t1)
	CheckItem.reports.append(t2)
	CheckItem.reports.append(t3)
	CheckItem.reports.append(t4)
	CheckItem.reports.append(t5)
	CheckItem.reports.append(t100)
	return CheckItem.reports



@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):

	for issue in issues:
		# print(issue.has_fix)
		problem_description = issue.description
		ents = issue.entities
		print(problem_description)
		print(ents)
		tied = tied_cls(ents[0]._id)
		tied.get_component_ids()

		if " switch the master and slave group" in problem_description:

			val_tied = {'Name': 'TIED_' + str (tied.slave_name_id_group["text_list"]) + "_vs_" + str (
				tied.master_name_id_group["text_list"]) ,
						'NSS': tied.group_ent_master , 'NMS': tied.group_ent_slave}
			success_tied = tied.set_entity_values (constants.PAMCRASH , val_tied)

			val_group_m = {'Name': 'Tms_' + str (tied.slave_name_id_group["text_list"]) + "_vs_" + str (
				tied.master_name_id_group["text_list"])}
			val_group_m_temp = {'Name': 'Tms_' + str (tied.slave_name_id_group["text_list"]) + "_vs_" + str (
				tied.master_name_id_group["text_list"]) + "----temp"}
			val_group_s = {'Name': 'Tsl_' + str (tied.master_name_id_group["text_list"]) + "_vs_" + str (
				tied.slave_name_id_group["text_list"])}

			success_rename_group_m_temp = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_m_temp)
			success_rename_group_s = tied.group_ent_master.set_entity_values (constants.PAMCRASH , val_group_s)
			success_rename_group_m = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_m)

			if success_rename_group_m == 0 and success_rename_group_m_temp == 0 and success_rename_group_s == 0:
				ic = include_comment ()
				ic.add_comment_change (tied)
				ic.add_comment_change (tied.group_ent_master)
				ic.add_comment_change (tied.group_ent_slave)
				issue.is_fixed = True
				issue.update ()
			else:
				print('Final name should be for master:',  val_group_m['Name'], 'and for slave:', val_group_s['Name'])
				print('Check the GROUPs !!')

		if "\"GROUP  NAME \" missing" in problem_description:
			print('ahoj')
			new_text_master = 'Tms_' + tied.group_master_name[4:]
			new_text_slave = 'Tsl_' + tied.group_slave_name[4:]

			val_group_s_temp = {'Name': new_text_slave + "----temp_01"}
			val_group_m_temp = {'Name': new_text_master + "----temp_01"}
			val_group_m = {'Name': new_text_master}
			val_group_s = {'Name': new_text_slave}
			print('val_group_s_temp',val_group_s_temp)
			print('val_group_m_temp',val_group_m_temp)
			success_rename_group_s_temp = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_s_temp)
			success_rename_group_m_temp = tied.group_ent_master.set_entity_values (constants.PAMCRASH , val_group_m_temp)
			success_rename_group_s = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_s)
			success_rename_group_m = tied.group_ent_master.set_entity_values (constants.PAMCRASH , val_group_m)
			if success_rename_group_m == 0 and success_rename_group_m_temp == 0 and success_rename_group_s_temp == 0 and success_rename_group_s == 0:
				ic = include_comment ()
				ic.add_comment_change (tied.group_ent_master)
				ic.add_comment_change (tied.group_ent_slave)
				issue.is_fixed = True
				issue.update ()

		if "\"GROUP NAME\"" in problem_description:

			master_name_id_part = str (tied.master_name_id_part["text_list"])
			slave_name_id_part = str (tied.slave_name_id_part["text_list"])

			val_group_m_temp = {'Name': 'Tms_' + master_name_id_part + '_vs_' + slave_name_id_part + "----temp"}
			val_group_m = {'Name': 'Tms_' + master_name_id_part + '_vs_' + slave_name_id_part}
			val_group_s_temp = {'Name': 'Tsl_' + slave_name_id_part + '_vs_' + master_name_id_part + "----temp"}
			val_group_s = {'Name': 'Tsl_' + slave_name_id_part + '_vs_' + master_name_id_part}

			success_rename_group_m_temp = tied.group_ent_master.set_entity_values (constants.PAMCRASH , val_group_m_temp)
			success_rename_group_s_temp = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_s_temp)
			success_rename_group_s = tied.group_ent_slave.set_entity_values (constants.PAMCRASH , val_group_s)
			success_rename_group_m = tied.group_ent_master.set_entity_values (constants.PAMCRASH , val_group_m)
			if success_rename_group_m == 0 and success_rename_group_m_temp == 0 and success_rename_group_s == 0 and success_rename_group_s_temp == 0:

				field = {'Comment':val_group_s['Name']+'_target_name'}
				tied.group_ent_slave.set_entity_values (constants.PAMCRASH, field)
				field = {'Comment':val_group_m['Name']+'_target_name'}
				tied.group_ent_master.set_entity_values (constants.PAMCRASH, field)
				ic = include_comment ()
				ic.add_comment_change (tied.group_ent_master)
				ic.add_comment_change (tied.group_ent_slave)
				issue.is_fixed = True
				issue.update ()
			else:
				if success_rename_group_m != 0:
					print('Final name should be for master:', val_group_m['Name'], '   the group is already used')
				if success_rename_group_m_temp != 0:
					print('Final name should be for master temporary:', val_group_m_temp['Name'],'   the group is already used')
				if success_rename_group_s_temp != 0:
					print('Final name should be for slave temporary:', val_group_s_temp['Name'], '   the group is already used')
				if success_rename_group_s != 0:
					print('Final name should be for slave:', val_group_s['Name'], '   the group is already used')
				print('Check the GROUPs !! - maybe the group is unused - then you can delete it or the group is used in another entities - rename it !')

		if "\"TIED NAME\"" in problem_description:
			val_tied_name = {'Name':'TIED_'+ str(tied.master_name_id_group["text_list"]) + "_vs_" + str(tied.slave_name_id_group["text_list"])}
			success = tied.set_entity_values(constants.PAMCRASH, val_tied_name)
			if success == 0:
				ic = include_comment()
				ic.add_comment_change(tied)
				issue.is_fixed = True
				issue.update()

		if "\"PART TIED NAME\"" in problem_description:
			part_tied = tied.tied_part_ent
			val_part_name = {'Name': 'PART_' + str (tied.tied_name_component_id_1["text_list"]) + "_vs_" + str (
				tied.tied_name_component_id_2["text_list"])}
			success = part_tied.set_entity_values (constants.PAMCRASH , val_part_name)
			if success == 0:
				ic = include_comment ()
				ic.add_comment_change (part_tied)
				issue.is_fixed = True
				issue.update ()



# Update this dictionary to load check automatically
checkOptions = {'name': 'Check TIEDs for NISSAN (PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix',  os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks TIEDs'}
checkDescription = base.CheckDescription(**checkOptions)

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
