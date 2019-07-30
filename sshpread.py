#!/usr/bin/env python3

from src.params import Extensions
from src.workspace import Workspace
import configparser
import cmd, sys, os
import re

import signal

def handler(signum, frame):
    pass

signal.signal(signal.SIGINT, handler)

def yesNo(prompt,default=None):
    if default is None:
        choices = "[y,n]"
    elif default:
        choices = "[Y,n]"
    else:
        choices = "[y,N]"
    a = ""
    while a not in ["y","n"]:
        a = input(prompt+" "+choices+" ")
        if a == "" and default is not None:
            a = "y" if default else "n"
    return a == "y"



class SshpreadShell(cmd.Cmd):
    intro = '\nWelcome to SSHpread. Type help or ? to list commands.\n'
    prompt = '> '

#################################################################
###################         WORKSPACE         ###################
#################################################################

    def do_workspace(self, arg):
        '''WORKSPACE: Manage workspaces
Available commands:
    - workspace help      show this help
    - workspace list      list existing workspaces
    - workspace add NAME  create new workspace
    - workspace use NAME  change current workspace
    - workspace del NAME  delete workspace
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.workspace_list()
        elif command == "add":
            self.workspace_add(params)
        elif command == "use":
            self.workspace_use(params)
        elif command == "del":
            #TODO
            print("Del workspace")
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.workspace_help()

    def workspace_list(self):
        print("Existing workspaces :")
        workspaces = [name for name in os.listdir(config['DEFAULT']['workspaces'])
            if os.path.isdir(os.path.join(config['DEFAULT']['workspaces'], name))]
        for workspace in workspaces:
            if workspace == self.workspace.getName():
                print(" -["+workspace+"]")
            else:
                print(" - "+workspace)

    def workspace_add(self, params):
        #Check if name was given
        if params == "":
            self.workspace_help()
            return
        if re.match('^[\w_\.-]+$', params) is None:
            print('Invalid characters in workspace name. Allowed characters are letters, numbers and ._-')
            return
        #Check if workspace already exists
        if os.path.exists(os.path.join(config['DEFAULT']['workspaces'],params)):
            print("Workspace already exists")
            return
        try:
            newWorkspace = Workspace.create(params)
        except:
            print("Workspace creation failed")
        else:
            self.workspace = newWorkspace

    def workspace_use(self,params):
        #Check if workspace already exists
        if not os.path.exists(os.path.join(config['DEFAULT']['workspaces'],params)):
            print("Workspace does not exist")
        try:
            newWorkspace = Workspace(params)
        except:
            print("Workspace change failed")
        else:
            self.workspace = newWorkspace

    def workspace_help(self):
        print('''Available commands:
    - workspace help      show this help
    - workspace list      list existing workspaces
    - workspace add NAME  create new workspace
    - workspace use NAME  change current workspace
    - workspace del NAME  delete workspace''')

    def complete_workspace(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['add','list','use','del','help']:
            if word[:n] == text:
                matches.append(word)
        return matches

#################################################################
###################           HOSTS           ###################
#################################################################

    def do_host(self, arg):
        '''HOST: Manage hosts
Available commands:
    - host help                 show this help
    - host list                 list existing hosts
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.host_list()
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.host_help()
    
    def host_list(self):
        print("Current hosts in workspace:")
        hosts = self.workspace.getHosts()
        if not hosts:
            print("No hosts in current workspace")
            return
        for host in hosts:
            print(host.toList())

    def host_help(self):
        print('''Available commands:
    - host help                 show this help
    - host list                 list existing hosts''')

    def complete_host(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['list','help']:
            if word[:n] == text:
                matches.append(word)
        return matches


#################################################################
###################          TARGETS          ###################
#################################################################

    def do_target(self, arg):
        '''TARGET: Manage targets
Available commands:
    - target help                 show this help
    - target list                 list existing targets
    - target add IP[:PORT]        add target
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.target_list()
        elif command == "add":
            self.target_add(params)
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.target_help()
    
    def target_list(self):
        print("Current targets in workspace:")
        targets = self.workspace.getTargets()
        if not targets:
            print("No targets in current workspace")
            return
        for target in targets:
            print(target.toList())
    
    def target_add(self,params):
        if params == "":
            self.target_help()
            return
        if len(params.split(':')) == 2:
            ip, port = params.split(':')
        else:
            ip = params
            port = "22"
        try:
            self.workspace.addTarget_Manual(ip,port)
        except Exception as e:
            print("Target addition failed: "+str(e))
        else:
            print("Target "+ip+":"+port+" added.")

    def target_help(self):
        print('''Available commands:
    - target help                 show this help
    - target list                 list existing targets
    - target add IP[:PORT]   create new target''')

    def complete_target(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['add','list','help']:
            if word[:n] == text:
                matches.append(word)
        return matches

#################################################################
###################           USERS           ###################
#################################################################

    def do_user(self, arg):
        '''USER: Manage users
Available commands:
    - user help                 show this help
    - user list                 list existing users
    - user add USERNAME         create new user
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.user_list()
        elif command == "add":
            self.user_add(params)
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.user_help()
    
    def user_list(self):
        print("Current users in workspace:")
        users = self.workspace.getUsers()
        if not users:
            print("No users in current workspace")
            return
        for user in users:
            print(user.toList())
    
    def user_add(self,params):
        if params == "":
            self.user_help()
            return
        params = params.split(' ')
        if len(params) != 1:
            self.user_help()
            return
        name = params[0]
        try:
            self.workspace.addUser_Manual(name)
        except Exception as e:
            print("User addition failed: "+str(e))
        else:
            print("User "+name+" added.")

    def user_help(self):
        print('''Available commands:
    - user help                 show this help
    - user list                 list existing users
    - user add USERNAME         create new user''')

    def complete_user(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['add','list','help']:
            if word[:n] == text:
                matches.append(word)
        return matches

#################################################################
###################           CREDS           ###################
#################################################################

    def do_creds(self, arg):
        '''CREDS: Manage creds
Available commands:
    - creds help                 show this help
    - creds list                 list existing creds
    - creds types                list available credential types
    - creds add TYPE             create new cred
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.creds_list()
        elif command == "types":
            self.creds_types()
        elif command == "add":
            self.creds_add(params)
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.creds_help()

    def creds_types(self):
        print("Supported credential types:")
        for key in Extensions.authMethodsAvail():
            print("    - "+key+": "+Extensions.getAuthMethod(key).descr())
    
    def creds_list(self):
        creds = self.workspace.getCreds()
        if not creds:
            print("No creds in current workspace")
            return
        for cred in creds:
            print(cred.toList())

    def creds_show(self,credId):
        #TODO
        pass

    
    def creds_add(self,params):
        if params == "":
            self.creds_help()
            return
        if params not in Extensions.authMethodsAvail():
            print(params+" is not a valid credentials type.")
            return
        try:
            self.workspace.addCreds_Manual(params)
        except Exception as e:
            print("Credentials addition failed: "+str(e))
        else:
            print("Credentials added.")

    def creds_help(self):
        print('''Available commands:
    - creds help                 show this help
    - creds list                 list existing creds
    - creds types                list available credential types
    - creds add TYPE             create new cred''')

    def complete_creds(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['add','list','types','help']:
            if word[:n] == text:
                matches.append(word)
        #TODO autocomplete creds types on ADD
        return matches


#################################################################
###################          PAYLOADS         ###################
#################################################################

    def do_payload(self, arg):
        '''PAYLOAD: Manage payload
Available commands:
    - payload help                 show this help
    - payload list                 list existing payload
'''
        command,sep,params = arg.partition(" ")
        if command == "list" or command == "":
            self.payload_list()
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.payload_help()

    def payload_list(self):
        print("Available payloads:")
        for key in Extensions.payloadsAvail():
            print("    - "+key+": "+Extensions.getPayload(key).descr())
    
    def payload_help(self):
        print('''Available commands:
    - payload help                 show this help
    - payload list                 list existing payload''')

    def complete_payload(self, text, line, begidx, endidx):
        matches = []
        n = len(text)
        for word in ['list','help']:
            if word[:n] == text:
                matches.append(word)
        return matches

#################################################################
###################          OPTIONS          ###################
#################################################################

    def do_set(self,arg):
        '''SET: Manage options
Available commands:
    - set help                 show this help
    - set                      list current options' values
    - set OPTION VALUE         change an option's value
'''
        command,sep,params = arg.partition(" ")
        if command == "":
            self.options_list()
        elif command in self.workspace.getOptions():
            try:
                self.workspace.setOption(command,params)
            except ValueError:
                print("Invalid value for "+command)
        else:
            if command != "help" and command != "?":
                print("Unrecognized command.")
            self.options_help()

    def options_list(self):
        print("Current options:")
        for key,val in self.workspace.getOptionsValues():
            print("    - "+key+": "+str(val))
    
    def options_help(self):
        print('''Available commands:
    - set help                 show this help
    - set                      list current options' values
    - set OPTION VALUE         change an option's value''')

    def complete_set(self, text, line, begidx, endidx):
        matches = []
        if len(line) != endidx:
            #Complete only at the end of commands
            return []
        command = line.split()
        if len(command) < 2 or len(command) == 2 and begidx != endidx:
            compKey = "cmd"
        elif text == "":
            if command[-1] == "#":
                compKey = command[-2]
            else:
                compKey = command[-1]

        elif command[-2]:
            compKey = command[-2]
        else:
            compKey = "none"
        n = len(text)
        if compKey == "cmd":
            comp = self.workspace.getOptions()
        elif compKey == "target":
            comp = self.workspace.getTargetsList()
        elif compKey == "user":
            comp = self.workspace.getUsersList()
        elif compKey == "creds":
            comp = self.workspace.getCredsIdList()
        else:
            comp = []
        for word in comp:
            if word[:n] == text:
                matches.append(word)
        return matches

#################################################################
###################          CONNECT          ###################
#################################################################

    def do_connect(self,arg):
        if arg != "":
            try:
                self.workspace.connectTarget(arg)
            except Exception as e:
                print("Targeted connect failed : "+str(e))
            else:
                return
        
        user = self.workspace.getOption("user")
        if user is None:
            users = self.workspace.getUsers()
            if len(users) > 1:
                if not yesNo("Try with all ("+str(len(users))+") users in scope ?",False):
                    return
            users = self.workspace.getUsers()
        else:
            users = [user]
        target = self.workspace.getOption("target")
        if target is None:
            targets = self.workspace.getTargets()
            if len(targets) > 1:
                if not yesNo("Try with all ("+str(len(targets))+") targets in scope ?",False):
                    return
            targets = self.workspace.getTargets()
        else:
            targets = [target]
        cred = self.workspace.getOption("creds")
        if cred is None:
            creds = self.workspace.getCreds()
            if len(creds) > 1:
                if not yesNo("Try with all ("+str(len(creds))+") credentials in scope ?",False):
                    return
            creds = self.workspace.getCreds()
        else:
            creds = [cred]

        nbIter = len(targets)*len(users)*len(creds)

        if nbIter > 1:
            if not yesNo("Will now attempt "+str(nbIter)+" connections. Proceed ?",False):
                return
        
        for target in targets:
            for user in users:
                for cred in creds:
                    if self.workspace.connect(target,user,cred):
                        break;



#################################################################
###################            CMD            ###################
#################################################################

    def do_exit(self, arg):
        'Quit SSHpread'
        self.workspace.close()
        return True
    
    def initPrompt(self):
        newPrompt = ""
        newPrompt = newPrompt+"["+self.workspace.getName()+"]"
        if self.workspace.getOption("target"):
            if self.workspace.getOption("user"):
                newPrompt = newPrompt+str(self.workspace.getOption("user"))
                if self.workspace.getOption("creds"):
                    newPrompt = newPrompt+":"+str(self.workspace.getOption("creds"))
                newPrompt = newPrompt+"@"
            newPrompt = newPrompt+str(self.workspace.getOption("target"))
        elif self.workspace.getOption("user"):
            newPrompt = newPrompt+str(self.workspace.getOption("user"))
            if self.workspace.getOption("creds"):
                newPrompt = newPrompt+":"+str(self.workspace.getOption("creds"))
            newPrompt = newPrompt+"@..."
        self.prompt = newPrompt+"> "

    def emptyline(self):
        pass

    def postcmd(self,stop,line):
        self.initPrompt()
        if line == "exit":
            return stop

    def __init__(self):
        super().__init__()
        self.workspace = Workspace("default")
        self.initPrompt()

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    if "DEFAULT" not in config or "workspaces" not in config['DEFAULT']:
        print("Invalid config file")
        exit()

    Extensions.load()
    
    if not os.path.exists(config['DEFAULT']['workspaces']):
        print("> First run ? Creating workspaces directory")
        os.makedirs(config['DEFAULT']['workspaces'])

    #Create default workspace if not exists
    if not os.path.exists(os.path.join(config['DEFAULT']['workspaces'],'default')):
        Workspace.create('default')

    SshpreadShell().cmdloop()

