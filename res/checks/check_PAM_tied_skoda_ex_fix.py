# PYTHON script

'''
Check TIEs for Skoda
====================

Check the TIE for entities names consistency.

Usage
-----

Same name in hierarchy

* Tied name - properties name - groups names

'''

import os, ansa
from ansa import base, constants



DEBUG = False
PATH_SELF = os.path.dirname(os.path.realpath(__file__))
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))



class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.PAMCRASH
	ENTITY_TYPES = ['CNTAC']



class tied_cls(base.Entity):
	def __init__(self, id):
		super().__init__( constants.PAMCRASH, id, 'CNTAC')

		vals_tied = ['NTYPE', 'NSS', 'NMS','IDPRT']

		tied_ent = self.get_entity_values(constants.PAMCRASH, vals_tied)

		self.tied_name = ""

		self.tied_part_ent = ""
		self.tied_part_name = ""

		self.group_ent_master = ""
		self.group_ent_slave = ""

		self.group_master_name= ""
		self.group_slave_name= ""

		self.prefix_include = ""

		if  tied_ent['NTYPE'] == 'TIED':
			self.tied_flag = True

			self.tied = self._name
			self.tied_name = self._name.replace(" ", "")

			self.tied_part_ent = tied_ent ['IDPRT']
			self.tied_part_name = self.tied_part_ent._name

			self.group_ent_master = tied_ent ['NMS']
			self.group_ent_slave =  tied_ent ['NSS']

			self.group_master_name = self.group_ent_master._name
			self.group_slave_name =  self.group_ent_slave._name
		else:
			self.tied_flag = False



	def realize(self,prefix_include):

		self.prefix_entity = "TIED"
		self.prefix_entity_slave_comment = "S"
		self.prefix_entity_master_comment = "M"

		self.suggest_group_master_name = prefix_include + '_' + \
			self.prefix_entity + '_' + \
			self.prefix_entity_master_comment + '_' + \
			self.tied_name

		self.suggest_group_slave_name = prefix_include + '_' +  \
			self.prefix_entity + '_' +  \
			self.prefix_entity_slave_comment + '_' +  \
			self.tied_name

		self.suggest_part_tied_name =  ' xxx_xxx_xxx__xxx__' + \
			self.tied_name + '__xx_xx_xxx__TIED'



@check_base_items.safeExecute(CheckItem, 'An error occured during the exec procedure!')
def exe(entities, params):
	part_duplicity = {}

	t1 = base.CheckReport('Wrong master group name')
	t2 = base.CheckReport('Wrong slave group name')
	t3 = base.CheckReport('Wrong part tied name')
	t4 = base.CheckReport('Missing space for tied name')
	t5 = base.CheckReport('Assigning of parts is duplicated')

	t1.has_fix = True
	t2.has_fix = True
	t3.has_fix = True
	t4.has_fix = True
	t5.has_fix = False

	for tied_ent in entities:

		tied = tied_cls(tied_ent._id)

		if tied.tied_flag == True:
			tied.realize(params['Include prefix'])

			if  tied.tied_part_ent in part_duplicity:
				part_duplicity[tied.tied_part_ent] = part_duplicity[tied.tied_part_ent] + 1
			else:
				part_duplicity[tied.tied_part_ent] = 0

			if not tied.tied.startswith(' '):
				t4.add_issue(entities = [tied], status = 'Error',
					description = 'Missing space for tied name',
					entity_name = tied.tied_name,
					suggest_name = ' ' + tied.tied_name)

			if tied.group_master_name != tied.suggest_group_master_name:
				t1.add_issue(entities = [tied.group_ent_master], status = 'Error',
					description = 'Wrong master group name',
					entity_name = tied.group_master_name,
					suggest_name = tied.suggest_group_master_name)

			if tied.group_slave_name != tied.suggest_group_slave_name:
				t2.add_issue(entities = [tied.group_ent_slave], status = 'Error',
					description = 'Wrong slave group name',
					entity_name = tied.group_slave_name,
					suggest_name = tied.suggest_group_slave_name)

			if tied.tied_part_name != tied.suggest_part_tied_name:
				t3.add_issue(entities = [tied.tied_part_ent], status = 'Error',
					description = 'Wrong tied group name',
					entity_name = tied.tied_part_name,
					suggest_name = tied.suggest_part_tied_name)

	for var in part_duplicity:
		if part_duplicity[var] >= 1:
		  t5.add_issue(entities = [var], status = 'Error',
			  description = 'Assigning of parts is duplicated ' + str(part_duplicity[var]) + 'x')

	CheckItem.reports.append(t5)
	CheckItem.reports.append(t1)
	CheckItem.reports.append(t2)
	CheckItem.reports.append(t3)
	CheckItem.reports.append(t4)

	return CheckItem.reports



@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
	for issue in issues:
		problem_description = issue.description
		ents = issue.entities
		field = {'Name':issue.suggest_name}

		if len(issue.suggest_name) > 79:
			print('The lenght of name is too long > 79 chars')
			continue

		for ent in ents:
			success = ent.set_entity_values(4, field)
			if success == 0:
				print ('The name was fixed' + issue.suggest_name)
				issue.is_fixed = True



# Update this dictionary in order to load this check automatically!
checkOptions = {'name': 'Check TIEDs for SKODA (PAM)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Checks TIEDs'}
checkDescription = base.CheckDescription(**checkOptions) # load check into ANSA

# Add parameter
checkDescription.add_str_param('Include prefix', 'FEN')

if __name__ == '__main__' and DEBUG:
	check_base_items._debugModeTestFunction(CheckItem)
