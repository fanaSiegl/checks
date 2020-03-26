#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
IDIADA checks
=============

Additional ANSA check can be implemented into ANSA by pyProjectInstaller. In
order to do so a new ANSA check template should be generated by newPyProject
(check "newPyProject --help" for further details).

.. note::
    ANSA_UserDefined.plist is generated by "ansaChecksPlistUpdater" script.
    It wraps all ANSA check scripts and handles their
    documentation and versions as one single tool.

'''

#=========================== to be modified ===================================

APPLICATION_NAME = 'update_ansa_checks'
DOCUMENTATON_GROUP = 'ANSA tools'
DOCUMENTATON_DESCRIPTION = 'IDIADA ANSA checks documentation.'

#==============================================================================

import os
import sys
import argparse
import shutil

from domain import util

#==============================================================================

class AnsaChecksPlistUpdater(object):

    #--------------------------------------------------------------------------
    @staticmethod
    def createPlist():

        # create plist for available checks and the documentation string
        command = '%s -nogui -execscript %s' % (util.getPathAnsaExecutable(),
            os.path.join(util.PATH_BIN, util.PLIST_GENERATOR_NAME))

        stdout, stderr = util.runSubprocess(command, cwd=util.PATH_BIN)

        for line in stdout.splitlines():
            print(line)

    #--------------------------------------------------------------------------
    @staticmethod
    def copyChecks(path):

        ''' Copies all checks from RES to installation target directory.'''

        for checkFileName in os.listdir(os.path.join(util.PATH_RES, 'checks')):
            src = os.path.join(util.PATH_RES, 'checks', checkFileName)
            
            if checkFileName.startswith('_'):
                continue
            elif os.path.isdir(src):
                dst = os.path.join(path, checkFileName)

                # replace existing
                if os.path.isfile(dst):
                    os.remove(dst)

                print('Copying: %s' % checkFileName)
                shutil.copytree(src, dst)
                
            elif checkFileName.startswith('check_'):
                dst = os.path.join(path, checkFileName)

                # replace existing
                if os.path.isfile(dst):
                    os.remove(dst)

                print('Copying: %s' % checkFileName)
                shutil.copy(src, dst)

#==============================================================================

def main():

    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-copy', nargs=1, dest='destPath',
        help='Destination path where to copy all checks.')
    parser.add_argument('-init', action='store_true',
        help='Copy all checks to default directory and create plist.')

    args = parser.parse_args()

    # copy all check_*.py files to /default/ path
    if args.destPath:
        if os.path.isdir(args.destPath[0]):
            AnsaChecksPlistUpdater.copyChecks(args.destPath[0])
        else:
            print('Given path does not exist!')
            sys.exit(1)
    elif args.init:
        AnsaChecksPlistUpdater.copyChecks(util.getPathChecks())

    AnsaChecksPlistUpdater.createPlist()

#==============================================================================

if __name__ == '__main__':
    main()
