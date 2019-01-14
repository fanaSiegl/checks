# PYTHON script

import os
from ansa import base
from ansa import constants
import re
from datetime import date
import getpass

# ==============================================================================

class tied_cls (base.Entity):
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
     
    #-------------------------------------------------------------------------
	
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

# ==============================================================================

def ExecCheckTiedsSkoda(entities, params):
    
    part_duplicity = {}
    
    to_report = []
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
                part_duplicity [tied.tied_part_ent] = part_duplicity [tied.tied_part_ent] + 1
            else:
                part_duplicity [tied.tied_part_ent] = 0

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
              
    to_report.append(t5)                                      
    to_report.append(t1)
    to_report.append(t2)    
    to_report.append(t3)
    to_report.append(t4) 
                                     
    return to_report

# ==============================================================================

def FixCheckTiedsSkoda(issues):

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

# ==============================================================================

checkOptions = { 'name': 'Check TIEDs for SKODA (PAM)', 
    'exec_action': ('ExecCheckTiedsSkoda', os.path.realpath(__file__)), 
    'fix_action':  ('FixCheckTiedsSkoda',  os.path.realpath(__file__)), 
    'deck': constants.PAMCRASH, 
    'requested_types': ['CNTAC'], 
    'info': 'Checks TIEDs'}
    
checkDescription = base.CheckDescription(**checkOptions)

# ==============================================================================
