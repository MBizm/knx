import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml

### verbosity mask
VERBOSITYDEF: Dict[str, int] = {
    "off": 0x00,
    "error": 0x01,
    "warning": 0x03,
    "change": 0x07,
    "info": 0xFF
}

__verbosity = VERBOSITYDEF['error']

HOMEDIR = "{0}/.knx/bridge/".format(Path.home())


def setLogLevel(level):
    global __verbosity
    __verbosity = VERBOSITYDEF[level]


def log(level, msg):
    """ logging functionality for KNX Bridge """
    global __verbosity
    logPath = HOMEDIR + ".log"

    # create central directory for Daemon script
    if not os.path.isdir(HOMEDIR):
        Path(HOMEDIR).mkdir(parents=True, exist_ok=True)
    # check activated log level
    # TODO switch to logging.handlers.RotatingFileHandler for size restriction
    if __verbosity & VERBOSITYDEF[level] == VERBOSITYDEF[level]:
        with open(logPath, 'a+') as stream:
            stream.write("{0} ###\t{1}\t###: {2}\n".format(datetime.now().strftime("%d.%b. %I:%M:%S"),
                                                           level.upper(),
                                                           msg))


def readConfig():
    """
    reads configuration for KNX Bridge.
    First attempt will be from home directory, otherwise local config as part of src repo will be taken

    :return: configuration in yaml representation or None if not found
    """
    configuration = None
    configPath = HOMEDIR + "CONFIG.yaml"

    try:
        if os.path.isfile(configPath):
            with open(configPath, 'r') as stream:
                log('info', 'Configuration file loaded: {0}'.format(configPath))
                configuration = yaml.safe_load(stream)
        else:
            with open("../CONFIG.yaml", 'r') as stream:
                log('info', 'Configuration file loaded: ../CONFIG.yaml')
                configuration = yaml.safe_load(stream)
    except OSError as ex:
        log('error',
            'Could not load configuration file [{0}]'.format(ex))

    return configuration


def getAttrSafe(attr, key):
    """
    fails safely for accessing optional parameters
    :returns    value defined for key or None if undefined
    """
    ret = None

    if key in attr:
        ret = attr[key]

    return ret

#################################
#   Numeric helper methods      #
#################################
def is_number(val):
    if isinstance(val, (int, float)):
        return True
    else:
        try:
            float(val)
            return True
        except ValueError:
            return False
    return False


def is_bool(val):
    if isinstance(val, bool):
        return True
    elif val.lower() == "true" or val.lower() == "false":
        return True
    return False

def convert_number(val):
    if isinstance(val, str):
        if val.isdigit():
            val = int(val)
        else:
            val = float(val)
    return val

def convert_bool(val):
    if val.lower() == "true":
        return True
    elif val.lower() == "false":
        return False
    else:
        return bool(val)