# PYTHON script

import os
import sys
import glob

import ansa
from ansa import base
from ansa import constants

# ==============================================================================

CHECK_PATTERN = 'check_*.py'
CHECKS_DOC_RST = 'checksDocString.rst'
PATH_PLIST = '/data/fem/+software/SKRIPTY/tools/python/ansaTools/checks/general_check/default'

PATH_BIN = os.path.dirname(os.path.realpath(__file__))
PATH_INI = os.path.normpath(os.path.join(PATH_BIN,'..', 'ini'))
PATH_DOC = os.path.normpath(os.path.join(PATH_BIN,'..', 'doc'))
PATH_RES = os.path.normpath(os.path.join(PATH_BIN,'..', 'res'))

PATH_CHECKS = PATH_PLIST#os.path.join(PATH_RES, 'checks')

# ==============================================================================

def loadChecks():

	checkDescriptions = list()
	checkDocString = ''
	for modulePath in glob.glob(os.path.join(PATH_CHECKS, CHECK_PATTERN)):
		
		moduleName = os.path.splitext(os.path.basename(modulePath))[0]
		ansa.ImportCode(modulePath)
		
		currentModule = globals()[moduleName]
		try:
			print('Loading: %s.' % currentModule.checkOptions['name'])
		except AttributeError as e:
			print('No checkDescription object found in: %s' % modulePath)
			continue	
		
		if currentModule.__doc__ is not None:
			checkDocString += currentModule.__doc__
		
		checkDescription = currentModule.checkDescription
		checkDescriptions.append(checkDescription)
	
	is_saved = base.CheckDescription.save(checkDescriptions, os.path.join(
		PATH_PLIST, 'ANSA_UserDefined.plist'))
	print('%s checks loaded.' % is_saved)
	
	saveDoc(checkDocString)

# ==============================================================================

def saveDoc(docString):
	
	fo = open(
		os.path.join(PATH_DOC, 'sphinx', 'source', CHECKS_DOC_RST), 'wt')
	fo.write(docString)
	fo.close()

# ==============================================================================

if __name__ == '__main__':
	
	loadChecks()

