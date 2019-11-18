# PYTHON script

'''
ABAQUS check GAP penetrations
======================================

checks the penetration of GAP elements

* compares relative node position (GAP: GA, GB) with the vector (GAP_PROP: C1, C2, C3) 
and raises an error when Gap node position is incorrect.

Usage
-----

**Primary solver**

* ABAQUS


**Fix function**

* switches Gap node order (GA<==>GB).

'''

import os
import numpy as np
import ansa
from ansa import base
from ansa import constants
import re
from ansa import calc
from datetime import date
import getpass

# ==============================================================================

DEBUG  = 0

# ==============================================================================

class CheckedGap(object):
	
	def __init__(self, parentGapEntity, checkReportTable):
		
		self.gapEntity = parentGapEntity
		self.checkReportTable = checkReportTable
		
		self.findProjection()
							
	#-------------------------------------------------------------------------

	def findProjection(self):
		
		self.attributes =  self.getEntityAttributes(self.gapEntity, 'GAP')
		
		self.property = base.GetEntity(constants.ABAQUS, 'GAP_PROP', self.attributes['PID'])
		self.propAttributes = self.getEntityAttributes(self.property, 'GAP_PROP')

		pos_A = self.getNodePosition(self.attributes['GA'])
		pos_B = self.getNodePosition(self.attributes['GB'])
		
		vectorNodes = np.array(pos_B) - np.array(pos_A)
		vectorDirection = np.array([self.propAttributes['C1'], self.propAttributes['C2'], self.propAttributes['C3']])
		vectorDirectionNorm = vectorDirection/np.linalg.norm(vectorDirection)

		self.projection = ansa.calc.DotProduct(vectorNodes, vectorDirectionNorm)
				
	#-------------------------------------------------------------------------

	def check(self):

#		if projection < float(self.propAttributes['d']):
#			descriptions = 'GAP in penetration! (value=%s < %s)' % (projection, self.propAttributes['d'])
#			self.checkReportTable.add_issue(entities=[self.gapEntity], status="error" , description=descriptions)
##			print(descriptions, self.gapEntity._id)
			
		if self.projection < 0:
			descriptions = "Vector doesn't correspond to node order!"
			self.checkReportTable.add_issue(entities=[self.gapEntity], status="error" , description=descriptions,
				has_fix=True)
#			print(descriptions, self.gapEntity._id)
	
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
				{'GA' : gapItem.attributes['GB'],	'GB' : gapItem.attributes['GA']})		
		
			# check if the result is ok
			gapItem.findProjection()
			if gapItem.projection > 0:
				issue.status = 'ok'
	
# ==============================================================================

def ExecCheckQualityGap(entities, params):

	checkReportTable = base.CheckReport('Check GAP Penetrations')	

	if entities:
		if not type(entities) is list:
			entities = [entities]
		else:
			for entity in entities:
				checkedGap = CheckedGap(entity, checkReportTable)
				checkedGap.check()             
				
	return [checkReportTable]

# ==============================================================================

def fixGap(issues):
	
	for issue in issues:
		if issue.has_fix:
			CheckedGap.fixGapNodeDefinitionOrder(issue)
			issue.update()

# ==============================================================================

checkOptions = { 'name': 'Check GAP Penetrations', 
        'exec_action': ('ExecCheckQualityGap', os.path.realpath(__file__)), 
        'fix_action':  ('fixGap', os.path.realpath(__file__)), 
        'deck': constants.ABAQUS, 
        'requested_types': ['GAP'], 
        'info': 'Check GAP Elements - penetration'}
checkDescription = base.CheckDescription(**checkOptions)

# ==============================================================================

def main():
	
	types = ("GAP")
	gaps = base.PickEntities(constants.ABAQUS, types)
	
	checkReportTable = base.CheckReport('Check GAP Penetrations')
	
	for gap in gaps:
		checkedGap = CheckedGap(gap, checkReportTable)
		checkedGap.check()
	
	for issue in checkReportTable.issues: 
		print(issue.status, issue.description)
		if issue.has_fix:
			print('Trying to fix...')
			CheckedGap.fixGapNodeDefinitionOrder(issue)
			issue.update()
			print('Fix status:', issue.status)
	
# ==============================================================================
	
if __name__ == '__main__' and DEBUG:
	main()