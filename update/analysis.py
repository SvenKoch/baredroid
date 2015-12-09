#!/usr/bin/env python

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.0.8"


import os
import imp
import sys
import adb
import json
import time
import pyclbr
import signal
import config
import logging
import traceback
import ConfigParser
from time import sleep
from multiprocessing import Process, Queue


class Analysis:
    """This class is used as wrapper for the analysis module provided by the user."""

    def __init__(self, folder, deviceId, shell, window):
        self._deviceId = deviceId
        self._folder = folder
        self._logger = logging.getLogger('Manager.Analysis - ' + deviceId)
        self._apks = None
        self._shell = shell
        self._window = window 
        self._pid = 99999
        self._queue = Queue()
        self._process = Process(target=self.experiment, args=(self._deviceId, self._logger,))
        
    def addApks(self, apks):
        self._apks = apks

    def getMessage(self):
        if not self._queue.empty():
            return self._queue.get()

    def experiment(self, deviceId, logger):
        """This function allows to retrieve the information about the module to use during the analysis.
        The information are stored in the configuration file"""

        cfg = ConfigParser.ConfigParser()
        cfg.read(config.configFile)
        module_path = cfg.get('Project', 'module_path')
        module_name = cfg.get('Project', 'module_name')
        class_name = cfg.get('Project', 'class')
        method = cfg.get('Project', 'method')

        foo = self.retrieveModule(module_name, module_path, class_name)
        
        exp_dict = {}
        exp_dict['folder'] = self._folder
        exp_dict['deviceId']= deviceId
        exp_dict['apks']= self._apks
        exp_dict['window']= self._window

        methodToCall = getattr(foo(exp_dict), method)
        if methodToCall():
            self._queue.put('OK')
            sleep(1)
            stringJ = json.dumps({'endAnalysis':True, 'Error':False,\
                'DeviceId':deviceId}, sort_keys=True, separators=(',', ': '))
            logger.info(stringJ)
        else:
            stringJ = json.dumps({'endAnalysis':True, 'Error':True,\
                'DeviceId':deviceId}, sort_keys=True, separators=(',', ': '))
            logger.info(stringJ)
            self._queue.put('ERROR')

    def shutDown(self):
        """Shutdown."""
        self._process.join()
        self._process.terminate()

    def getProcess(self):
        """Return the process object."""
        return self._process


    def setup(self):
        """This function is used to setup the device before the analysis."""

        stringJ = json.dumps({'StartSetup':True, 'DeviceId':self._deviceId},\
                             sort_keys=True, separators=(',', ': '))
        
        self._logger.info(stringJ)

        #do something
            
        stringJ = json.dumps({'EndSetup':True, 'DeviceId':self._deviceId},\
                             sort_keys=True, separators=(',', ': '))
        
        self._logger.info(stringJ)


    def start(self):
        """Start the analysis."""
        try:
            self._process.start()
        
            self._pid = os.getpid()
            stringJ = json.dumps({'ExperimentPID':self._pid,\
                                 'DeviceId':self._deviceId},\
                                 sort_keys=True, separators=(',', ': '))
        
            self._logger.info(stringJ)
            return self._process

        except:
            self._logger.error('Unable to run the experiment', exc_info=True)
            self._queue.put('ERROR')
            return None

    def retrieveModule(self, module_name, module_path, class_name):
        """Return an instance of the class given as parameter."""

        try:
            filename, pathname, description = imp.find_module(\
                                                              module_name,\
                                                              [module_path])
            foo = imp.load_module(module_name, filename, pathname, description)

            return getattr(foo, class_name)
        except:
            traceback.print_exc(file=sys.stdout)
            self._logger.error('Unable to retrieve the analysis class.', exc_info=True)
            raise SystemExit()

def test(module_name, module_path, class_name):
        """Return an instance of the class given as parameter."""

        try:
            filename, pathname, description = imp.find_module(module_name, [module_path])

            print filename, pathname, description

            foo = imp.load_module(module_name, filename, pathname, description)
            
            #check if the class exists
            #module = pyclbr.readmodule(module_name, [module_path])
            #clazz = module[class_name]

            return getattr(foo, class_name)
        except:
            traceback.print_exc(file=sys.stdout)
            return None

if __name__ == '__main__':
    cfg = ConfigParser.ConfigParser()
    cfg.read(config.configFile)
    module_path = cfg.get('Project', 'module_path')
    module_name = cfg.get('Project', 'module_name')
    print module_path, module_name
    class_name = cfg.get('Project', 'class')
    method = cfg.get('Project', 'method')


    foo = test(module_name, module_path, class_name)
    methodToCall = getattr(foo(), method)()
