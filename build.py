#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Python script for '''

import os
import sys
import shutil
import string
import subprocess
import argparse

#==============================================================================

PATH_SELF = os.path.dirname(os.path.realpath(__file__))

EXECUTABLE = 'bin/main.py'
PRODUCTIVE_VERSION_BIN = '/data/fem/+software/SKRIPTY/tools/bin'
PRODUCTIVE_VERSION_HOME = '/data/fem/+software/SKRIPTY/tools/python'
VERSION_FILE = 'ini/version.ini'
DOCUMENTATON_PATH = '/data/fem/+software/SKRIPTY/tools/python/tool_documentation/default'

#==============================================================================

sys.path.append(os.path.join(PATH_SELF, 'bin'))

import main
from main import APPLICATION_NAME, DOCUMENTATON_GROUP, DOCUMENTATON_DESCRIPTION

#==============================================================================

def runSubprocess(command, cwd=None):
    
    process = subprocess.Popen(
        command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        cwd=cwd)
    
    return process.communicate()


#==============================================================================

def createVersionFile():
    
    print 'Updating a version file'
    
    VERSION_FILE_TEMPLATE = '''[VERSION]
REVISION = ${revision}
AUTHOR = ${modifiedBy}
MODIFIED = ${lastModified}'''
    
    template = string.Template(VERSION_FILE_TEMPLATE)
    
    outputString = template.substitute(
        {'revision' : args.revision,
         'modifiedBy' : modifiedBy,
         'lastModified': lastModified})
    
    versionFile = open(os.path.join(targetDir, VERSION_FILE), 'wt')
    versionFile.write(outputString)
    versionFile.close()
    
#==============================================================================

def createRevisionContents():
    
    print 'Creating a revision content in: "%s"' % targetDir
    
    if os.path.isdir(targetDir):
        print 'Current revision exists already.'
        sys.exit()
    else:
        os.makedirs(targetDir)
    
    runSubprocess('git clone . %s' % (targetDir))
    runSubprocess('git checkout %s' % (args.revision), targetDir)

#==============================================================================

def cleanUp():
    
    print 'Cleaning up files'
    
    repositoryPath = os.path.join(targetDir, '.git')
    shutil.rmtree(repositoryPath)
        
    buildScript = os.path.join(targetDir, 'build.py')
    os.remove(buildScript)

    
#==============================================================================

def getRevisionInfo():
    
    print 'Gathering revision information'
    
    output, _ = runSubprocess('git log %s -n 1' % args.revision)
    
    lines = output.split('\n')
    
    modifiedBy = lines[1].split(':')[1].strip()
    lastModified = ':'.join(lines[2].split(':')[1:]).strip()
    
    return modifiedBy, lastModified

#==============================================================================

def install():
    
    print 'Releasing to the productive version'
    
    defaultDir = os.path.join(applicationPath, 'default')
    
    if os.path.islink(defaultDir):
        os.unlink(defaultDir)
    os.symlink(args.revision, defaultDir)
    
    symLink = os.path.join(PRODUCTIVE_VERSION_BIN, APPLICATION_NAME)
    executable = os.path.join(defaultDir, EXECUTABLE)
    if os.path.islink(symLink):
        os.unlink(symLink)
    os.symlink(executable, symLink)
    
    os.chmod(symLink, 0775)

#==============================================================================

def createDocumentation():
    
    print 'Creating local sphinx documentation'
    
    SPHINX_DOC = os.path.join(targetDir, 'doc', 'sphinx')
    SPHINX_SOURCE = os.path.join(SPHINX_DOC, 'source')
    SPHINX_DOCTREES = os.path.join(SPHINX_DOC, 'build', 'doctrees')
    SPHINX_HTML = os.path.join(SPHINX_DOC, 'build', 'html')
    SPHINX_BUILD = os.path.join(SPHINX_DOC, 'sphinx-build.py')
    GIT_REVISION_HISTORY = os.path.join(SPHINX_SOURCE, 'revision_history.rst')
    
    HEADER = '''
Revision history
================

Revision history graph::

'''
    
    # create revision history
    stdout, _ = runSubprocess('git log --graph --all --decorate --abbrev-commit')
    lines = stdout.splitlines()
        
    fo = open(GIT_REVISION_HISTORY, 'wt')
    fo.write(HEADER)
        
    for line in lines:
        fo.write('   %s\n' % line)
    fo.close()
    
    # create local documentation
    runSubprocess('python %s -b html -d %s %s %s' % (
        SPHINX_BUILD, SPHINX_DOCTREES, SPHINX_SOURCE, SPHINX_HTML))

#==============================================================================

def publishDocumentation():
    
    print 'Updating tool documentation'
    
    SPHINX_LOCAL_DOC_SOURCE = os.path.join(targetDir, 'doc', 'sphinx', 'source')
    
    SPHINX_INDEX = os.path.join(
        DOCUMENTATON_GROUP.replace(' ', '_'), APPLICATION_NAME,
        '%s.html' % APPLICATION_NAME)
    
    # copy to tool documentation
    # create main link file
    SPHINX_GLOBAL_DOC_SOURCE = os.path.join(DOCUMENTATON_PATH, 'source',
        DOCUMENTATON_GROUP.replace(' ', '_'), APPLICATION_NAME)
    docFileName = os.path.join(SPHINX_GLOBAL_DOC_SOURCE,
        '%s.txt' % APPLICATION_NAME)
        
    if os.path.exists(SPHINX_GLOBAL_DOC_SOURCE):
        shutil.rmtree(SPHINX_GLOBAL_DOC_SOURCE)
    
    # copy doc source files
    shutil.copytree(SPHINX_LOCAL_DOC_SOURCE, SPHINX_GLOBAL_DOC_SOURCE)
    
     
    fo = open(docFileName, 'wt')
    fo.write('.. _%s: ./%s\n\n' % (APPLICATION_NAME, SPHINX_INDEX))
    fo.write('`%s`_ - %s\n\n' % (APPLICATION_NAME, DOCUMENTATON_DESCRIPTION))
    fo.close()

    # update index file
    newIndexLines = list()
    fi = open(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst'), 'rt')
    for line in fi.readlines():
        if line.startswith('.. automodule:: main'):
            newIndexLines.append('\n%s\n' % main.__doc__)
        else:
            newIndexLines.append(line)
    fi.close()
    
    fo = open(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, '%s.rst' % APPLICATION_NAME), 'wt')
    for line in newIndexLines:
        fo.write(line)
    fo.close()
        
    # delete redundant files
    if os.path.isfile(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'conf.py')):
        os.remove(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'conf.py'))
    if os.path.isfile(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst')):
        os.remove(os.path.join(SPHINX_GLOBAL_DOC_SOURCE, 'index.rst'))
    
    # update tool documentation
    updateScriptPath = os.path.join(DOCUMENTATON_PATH, 'buildHtmlDoc.py')
    runSubprocess(updateScriptPath)
    

#==============================================================================
    
parser = argparse.ArgumentParser(description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('revision', help='Revision number to be build.')
parser.add_argument('-i', action='store_true',  dest='install',
    help='Makes a build revision default.')

args = parser.parse_args()

applicationPath = os.path.join(PRODUCTIVE_VERSION_HOME, APPLICATION_NAME)
targetDir = os.path.join(applicationPath, args.revision)

createRevisionContents()
modifiedBy, lastModified = getRevisionInfo()
createVersionFile()
createDocumentation()
cleanUp()

if args.install:
#     install()
    publishDocumentation()
    
print 'Done'