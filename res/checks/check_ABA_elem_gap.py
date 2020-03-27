# PYTHON script

'''
ABAQUS check GAP penetrations
======================================

Checks the penetration of GAP elements.

Compares relative node position (GAP: GA, GB) with the vector (GAP_PROP: C1, C2, C3)
and raises an error when Gap node position is incorrect.

Usage
-----

**Primary solver** - ABAQUS.

**Fix function** switches Gap node order (GA<==>GB).

'''

import os, ansa
import numpy as np
from ansa import base, constants, calc

# ==============================================================================

DEBUG = 0

if DEBUG:
	PATH_SELF = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'
#	PATH_SELF = os.path.dirname(os.path.realpath(__file__))
else:
	PATH_SELF = os.path.join(os.environ['ANSA_TOOLS'], 'checks','general_check','default')
ansa.ImportCode(os.path.join(PATH_SELF, 'check_base_items.py'))

# ==============================================================================

class CheckItem(check_base_items.BaseEntityCheckItem):
	SOLVER_TYPE = constants.ABAQUS
	ENTITY_TYPES = ['GAP']

# ==============================================================================

class CheckedGapException(Exception): pass

# ==============================================================================

class CheckedGap:

	def __init__(self, parentGapEntity, checkReportTable):
		self.gapEntity = parentGapEntity
		self.checkReportTable = checkReportTable
		self.findProjection()

	#-------------------------------------------------------------------------
	
	def findProjection(self):
		self.attributes =  self.getEntityAttributes(self.gapEntity, 'GAP')
		self.property = base.GetEntity(constants.ABAQUS, 'GAP_PROP', self.attributes['PID'])
		self.propAttributes = self.getEntityAttributes(self.property, 'GAP_PROP')
		
		if self.propAttributes['C1'] is None or self.propAttributes['C2'] is None or self.propAttributes['C3'] is None:
#			self.checkReportTable.add_issue(entities=[self.gapEntity], status="warning" , description='Contact direction missing!')
			raise CheckedGapException('Contact direction missing!')
		
		pos_A = self.getNodePosition(self.attributes['GA'])
		pos_B = self.getNodePosition(self.attributes['GB'])

		vectorNodes = np.array(pos_B) - np.array(pos_A)
		vectorDirection = np.array([self.propAttributes['C1'], self.propAttributes['C2'], self.propAttributes['C3']])
		vectorDirectionNorm = vectorDirection/np.linalg.norm(vectorDirection)

		self.projection = ansa.calc.DotProduct(vectorNodes, vectorDirectionNorm)

	#-------------------------------------------------------------------------

	def check(self):
		if self.projection < 0:
			descriptions = "Vector doesn't correspond to node order!"
			self.checkReportTable.add_issue(entities=[self.gapEntity], status="error" , description=descriptions,
				has_fix=True)

	#-------------------------------------------------------------------------

	def getEntityAttributes(self, entity, type):
		fields = base.GetKeywordFieldLabels(constants.ABAQUS, type)
		return base.GetEntityCardValues(constants.ABAQUS, entity, fields)

	#-------------------------------------------------------------------------

	def getNodePosition(self, nodeId):
		node = base.GetEntity(constants.ABAQUS, 'NODE', nodeId)
		vals = base.GetEntityCardValues(constants.ABAQUS, node, ['X', 'Y', 'Z'])
		return vals['X'], vals['Y'], vals['Z']

	#-------------------------------------------------------------------------
	@classmethod
	def fixGapNodeDefinitionOrder(cls, issue):
		gaps = issue.entities
		for gap in gaps:
			gapItem = CheckedGap(gap, None)

			base.SetEntityCardValues(constants.ABAQUS, gap,
				{'GA': gapItem.attributes['GB'],	'GB': gapItem.attributes['GA']})

			# Check if the result is ok
			gapItem.findProjection()
			if gapItem.projection > 0:
				issue.status = 'ok'

# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the exe procedure!')
def exe(entities, params):
	checkReportTable = base.CheckReport('Check GAP Penetrations')

	if entities:
		if not type(entities) is list:
			entities = [entities]
		else:
			for entity in entities:
				try:
					checkedGap = CheckedGap(entity, checkReportTable)
					checkedGap.check()
				except CheckedGapException as e:
					continue

	return [checkReportTable]


# ==============================================================================
@check_base_items.safeExecute(CheckItem, 'An error occured during the fix procedure!')
def fix(issues):
	for issue in issues:
		if issue.has_fix:
			CheckedGap.fixGapNodeDefinitionOrder(issue)
			issue.update()

# ============== this "checkDescription" is crucial for loading this check into ANSA! =========================

# Update this dictionary to load check automatically
checkOptions = {'name': 'Check GAP penetrations (ABA)',
	'exec_action': ('exe', os.path.realpath(__file__)),
	'fix_action': ('fix', os.path.realpath(__file__)),
	'deck': CheckItem.SOLVER_TYPE,
	'requested_types': CheckItem.ENTITY_TYPES,
	'info': 'Check GAP elements - penetration'}
checkDescription = base.CheckDescription(**checkOptions)

# ==============================================================================

if __name__ == '__main__' and DEBUG:
	
	check_base_items.debugModeTestFunction(CheckItem)

# ==============================================================================
