"""
Installs and configures ssh keys
"""

import glob
import logging
import os

import engine_validators as validate
import basedefs
import common_utils as utils

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-SSHKEYS"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding SSH KEY configuration")
    paramsList = [
                  {"CMD_OPTION"      : "ssh-public-key",
                   "USAGE"           : "Public key to install on servers",
                   "PROMPT"          : "Public key to install on servers",
                   "OPTION_LIST"     : glob.glob(os.path.join(os.environ["HOME"], ".ssh/*.pub")),
                   "VALIDATION_FUNC" : validate.validateFile,
                   "DEFAULT_VALUE"   : (glob.glob(os.path.join(os.environ["HOME"], ".ssh/*.pub"))+[""])[0],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_SSH_KEY",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "SSHKEY",
                  "DESCRIPTION"           : "SSH Configs ",
                  "PRE_CONDITION"         : utils.returnYes,
                  "PRE_CONDITION_MATCH"   : "yes",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    puppetsteps = [
             {'title': 'Setting Up ssh keys',
              'functions':[installKeys]}
    ]
    controller.addSequence("ssh key setup", [], [], puppetsteps)

def installKeys():
    
    with open(controller.CONF["CONFIG_SSH_KEY"]) as fp:
        sshkeydata = fp.read().strip()

    for hostname in utils.gethostlist(controller.CONF):
        if '/' in hostname:
            hostname = hostname.split('/')[0]
        server = utils.ScriptRunner(hostname)

        server.append("mkdir -p ~/.ssh")
        server.append("grep '%s' ~/.ssh/authorized_keys > /dev/null 2>&1 || echo %s > ~/.ssh/authorized_keys"%(sshkeydata, sshkeydata))
        server.append("restorecon -r ~/.ssh")
        server.execute()

