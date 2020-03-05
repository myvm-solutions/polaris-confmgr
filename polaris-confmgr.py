#!/usr/bin/python3

import ipaddress
import socket
from time import time,sleep
from yaml import load, dump
from deepdiff import DeepDiff
from copy import deepcopy

try:
    from yaml import CSafeLoader as Loader, CSafeDumper as Dumper
except ImportError:
    from yaml import SafeLoader as Loader, SafeDumper as Loader

SETTINGS_FILE = "settings.yaml"
DATA_FILE = "data.yaml"
LOG_LEVEL=1                             #0 = silent, 1 = important, 2 = informative, 3 = debug

SCRIPT_NAME = "polaris-confmgr"
CURRENT_VERSION = 0.1
ACCEPTABLE_CONFIG_VERSIONS = [CURRENT_VERSION]
WELCOME_MSG=f"Welcome to {SCRIPT_NAME} version {CURRENT_VERSION}!"


class ClientLocation:
    """Definition for a potential client location"""

    def __init__(self, obj):
        self.name = obj["name"]
        self.address = obj["address"]
        self.weight = obj["weight"]
        self.pools = obj["pools"]
        self.usedCount = 0
        self.ip = ipaddress.IPv4Address(0)

    def printMember(self):
        log(3, {'ip': str(self.ip), 'name': str(self.name), 'weight': str(self.weight)})
        return({'ip': str(self.ip), 'name': str(self.name), 'weight': str(self.weight)})

    def updateDNS(self):
        log(3, "Looking up ", self.address)
        try:
            self.ip = ipaddress.IPv4Address(socket.gethostbyname(self.address))
            return True
        except:
            self.ip = ipaddress.IPv4Address(0)
            return False
#end ClientLocation

        
def loadSettings(fileName):
    log(2, f"Loading settings frome file: {fileName}")
    
    with open(fileName, 'r') as stream:
        data_loaded = load(stream, Loader=Loader)

    settings = data_loaded['settings']
    log(3, settings)
    
    if settings['version'] in ACCEPTABLE_CONFIG_VERSIONS:
        log(2, f"Successfully loaded settings version {settings['version']}")
        return(data_loaded)
    else:
        #log(3, f"Settings file version does not match acceptable values!", settings['version'], ACCEPTABLE_CONFIG_VERSIONS)
        raise RuntimeError(f"Settings file version does not match acceptable values!", settings['version'], ACCEPTABLE_CONFIG_VERSIONS)
#end loadSettings


def loadData(fileName):
    log(2, f"Loading data from file: {fileName}")

    with open(fileName, 'r') as stream:
        data_loaded = load(stream, Loader=Loader)

    objList = []
    success=0
    failed=0
    total=0
    criteriaCount=3     #number of criteria we will check, not counting pools

    for l in data_loaded:
        total+=1
        goodCount=0
        try:
            if (l['weight'] >= 0) & (l['weight'] <= 10):
                goodCount+=1

            if len(l['name']) > 0:
                goodCount+=1

            if len(l['address']) > 0:
                goodCount+=1

            poolCount=0
            for p in l['pools']:
                poolCount+=1
                if len(p) > 0:
                    goodCount+=1

        except:
            log(3, "Exception in data load")
            goodCount=0
            poolCount=0

        if (goodCount == (criteriaCount + poolCount)) & (poolCount > 0):
            success+=1
            newL = ClientLocation(l)
            objList.append(newL)
        else:
            failed+=1
    #end for

    log(2, f"{total} objects scanned, {failed} failed, {success} imported")
    return objList
#end loadData

def log(level, entry1, entry2 = None, entry3 = None, entry4 = None):
    if level <= LOG_LEVEL:
        if entry4 is None:
            if entry3 is None:
                if entry2 is None:
                    print(entry1);
                else:
                    print(entry1, entry2)
            else:
                print(entry1, entry2, entry3)
        else:
            print(entry1, entry2, entry3, entry4)

                

def mainFunc():
    log(2, WELCOME_MSG)
    testObject=loadSettings(SETTINGS_FILE)
    settings = testObject['settings']
    pools = testObject['pools']
    globalnames = testObject['globalnames']
    lastPools={}
    lastPools = {'pools': {}}

    timeWait=settings['interval']
    log(2, f"Loop delay set to {timeWait} seconds")

    while True:
    #if True:
        allLocations = loadData(DATA_FILE)
        successfulLookups = 0

        start = time()
        for l in allLocations:
            if l.updateDNS():
                successfulLookups+=1
            else:
                log(1, "Lookup failed for ", l.address)
            log(3, l.name, l.pools, l.address, l.ip)
        end = time()
        log(2, f"{successfulLookups} of {len(allLocations)} DNS entries updated in {end - start} seconds")

        outPools = {'pools': {}}
        log(3, "Parsing pool members...")
        for p in pools:
            pools[p]['members'] = []
            for l in allLocations:
                if p in l.pools:
                    if l.ip.is_global:
                        pools[p]['members'].append(l.printMember())
            outPools['pools'].update({p: pools[p]})
            log(2, f"Pool {p} has {len(pools[p]['members'])} active members")
            log(3, pools[p]['members'])
            if len(pools[p]['members']) == 0:
                log(1, f"Warning! Pool {p} has no active members!")

        outPools.update({'globalnames': globalnames})
        log(3, "Generated file:\n", dump(outPools, Dumper=Dumper, default_flow_style=False))

        ddif = DeepDiff(outPools, lastPools, ignore_order=True)
        if ddif != {}:
            log(1, f"Pool change detected, writing new config file {settings['output_file']}")
            with open(settings['output_file'], 'w') as outfile:
                print("#\n# !! DO NOT EDIT THIS FILE !!", file = outfile)
                print(f"#  it was auto-generated by\n# {SCRIPT_NAME} version {CURRENT_VERSION}\n#\n", file = outfile)
                dump(outPools, outfile, Dumper=Dumper, default_flow_style=False)

            lastPools = deepcopy(outPools)

        #sleep(10)
        sleep(timeWait)
#end mainFunc

mainFunc()

