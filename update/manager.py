#!/usr/bin/env python

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.1.3"

import os
import re
import sys
import adb
import json
import time
import util
import tmuxp
import psutil
import config
import logging
import argparse
import traceback
import subprocess
import ConfigParser
from device import Device
from tmux_manager import tmux_init
from update_manager import UpdateManager

def quit():
    """Close the program"""
    raise SystemExit()

def getIds():
    """Get the DeviceId of the attached devices."""
    return adb.AndroidDebugBridge().devices().keys()

def showInfo(ids, file):
    """Show the DeviceId and the info in the configuration file"""
    with open(file) as f:
        print f.readline().rstrip()# get the title
        for i, l in enumerate(f): #is the device attached?
            if l.split('\t')[0] in ids:
                print l.rstrip()

def listDevices(cFile, logger):
    """List the attached devices and show them"""
    logger.info('Show attached devices')
    showInfo(getIds(), cFile)


def init_list(apps, logger):
    """Initialize the queue containing the apps to analyze"""
    res = map(lambda x:os.path.join(apps, x), [a for a in os.listdir(apps) 
        if a.endswith('.apk')])
    logger.info('Added %d apps to the analysis queue' % len(res))
    return res


def initDevice(logger):
    """Initialize the attached devices. Retrieve the info from the config file
    and create the respective objects."""

    devices = {}
    ids = getIds()

    with open(config.deviceInfoFile) as f:
        f.readline()# skip the first line
        for i, l in enumerate(f): #is the device attached?
            id, color, port, user = l.split('\t')
            if id in ids and (not id in devices):
                logger.info('Found a device with id: %s'%id)
                devices[id] = Device(id, color, port, user)

    if not devices:
        logger.info('No devices attached...')
        return {}

    return devices

def stop(device):
    """Used to stop the processes used to manage the devices."""
    device.getUpdateManager().stopUpdate()
    logger.info('Stop analysis')


def assignApps(lApps, numAppsPerAnalysis, uManagers, logger):
    """Assign to each device its own set of apps to analyze.
    """
    analysis = 1
    for manager in uManagers:
        try:
            if not len(lApps) == 0:
                apps = lApps[: numAppsPerAnalysis]
                manager.addAppsToAnalyze(analysis, apps)
                logger.info('Added %d apps to device id %s' % (len(apps), manager.getDeviceId()))
                lApps = lApps[numAppsPerAnalysis:]

                logger.info(json.dumps({'Analysis': analysis,
                'DeviceId': manager.getDeviceId(), 'apps': apps}, sort_keys=True,
                separators=(',', ': ')))
        except:
            traceback.print_exc(file=sys.stdout)

def initAnalysis(directory, numAppsPerAnalysis, logger, devices):
    """Each device is associated to an updateManager process.
    The process manages the devices and the analysis lifecycle."""
    
    uManagers = []
    lApps = init_list(directory, logger) # contains all the apps to analyze
    
    if not len(lApps):
            logger.info('The folder does not contain any app...')
            return uManagers

    for key, dev in devices.iteritems():
        #Select only the devices in 'ready' state
        if dev.getState() == 'ready':
            uManagers.append(UpdateManager(dev))

    # assign the list of apps to analyze to a device
    assignApps(lApps, numAppsPerAnalysis, uManagers, logger)

    return uManagers


def startAnalysis(uManagers, folder, windows, logger):
    """For each device in a 'ready' state start the analysis."""

    for count, manager in enumerate(uManagers):
        manager.startUpdate(folder, windows[count+1])
        stringJ = json.dumps({'startAnalysis':True, 'DeviceId':manager.getDeviceId()}, sort_keys=True,
                        separators=(',', ': '))
        logger.info(stringJ)

def stopAnalysis(uManagers):
    """Stop the analysis."""
    for key in uManagers:
        uManagers[key].stopUpdate()

def check(directory, logger):
    """Check wheter all the apps were analyzed or not."""

    folder = os.path.join(os.getcwd(), 'experiment')
    exps = [ name.replace('experiment__','') for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) ]
    app = [a for a in os.listdir(directory) if a.endswith('.apk')]
    for a in app:
        if not a[:-4] in exps: #find exact match (maybe best match is also ok)
            logger.info('Attention the system was unable to analyze: %s' % a)

def createFolder(logger):
    """When an analysis is started create the corresponding folder. 
    The folder 'experiment__date' contains all the info about the analysis."""
    
    rootExp = os.path.join(os.getcwd(),'experiment')
    if not os.path.exists(rootExp):
        os.mkdir(rootExp)

    strtime = time.strftime('%Y.%m.%d-%H.%M.%S')
    exp = '%s__%s'%('experiment', strtime)
    path = os.path.join(rootExp, exp)
    os.mkdir(path)

    logger.info('Folder created successfully')
    return path

# For each device create a window in the tmux session
#
def divide_et_impera(devices, session_name):
    """Create new tmux windows and panes."""
    windows = []
    #init tmux session
    session = tmux_init(devices, session_name)
    #get the windows attached to the session
    windows = session.list_windows()

    return windows

def user_menu(session, directory):
    """ Show the menu in the first tmux window.
    Retrieve the information about the devices to use for the analysis
    and the folder containig the apps to analyze."""
    devices = {}
    uManagers = []

    logger = util.init_logger(config.configFile, 'Manager')
    logger.info('BareDroid init')
    devices = initDevice(logger)

    windows = divide_et_impera(devices, session)

    #watch log and errors
    logFolder = os.path.join(os.getcwd(),\
                    util.read_config(config.configFile, 'Log', 'folder'))
    windows[1].list_panes()[0].send_keys('tail -F %smanager.log'%logFolder)
    windows[1].list_panes()[1].send_keys('tail -F %smanager_error.log'%logFolder)

    ans=True
    while ans:
        print '-----------------'
        print ("""
    1) List devices
    2) Start Analysis
    3) Stop Analysis
    4) Select Devices
    q) Quit
    m) Menu
        """)
        print ''
        ans=raw_input(">> ")
        if ans=="1":
            listDevices(config.deviceInfoFile, logger)
        elif ans=="2":
            folder = createFolder(logger)
            #initialize
            uManagers = initAnalysis(directory,\
                int(util.read_config(config.configFile,'Analysis', 'apps')),\
                logger, devices)
            #start
            startAnalysis(uManagers, folder, windows, logger)
        elif ans=="3":
            stopAnalysis(uManagers)
        elif ans=="4":
            #TODO select devices
            print 'TODO'
        elif ans=='m' or ans == 'M':
            print ''
        elif ans=='q' or ans == 'Q':
            check(directory, logger)
            logger.info('exit')
            #print print_on_window(windows[0], '\nExit')
            quit()
        elif ans !="":
            print("\n Not valid, try again...")
            ans = True
        else:
            print("\n Not valid, try again...")
            ans = True

def main_menu(args):
    """Clean the screen and print the command line interface"""
    os.system('clear')
    user_menu(args.session, args.directory)

def main():
    """Parse the arguments passed in the command line and
    starts the command line interface"""

    cmdLine = argparse.ArgumentParser(description='BareDroid manager')
    cmdLine.add_argument('-s', dest="session", required=True,
        help='name of the tmux session')
    cmdLine.add_argument('-d', dest="directory", required=True, action='store',
        help='Select the directory containing the apps to analyze')
    args = cmdLine.parse_args()
    main_menu(args)
    args.input.close()

if __name__ == '__main__':
    main()
