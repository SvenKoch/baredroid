#!/usr/bin/env python 

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.0.2"


import os
import adb
import logging
import analysis
import subprocess
from time import sleep
from multiprocessing import Process, Queue


class UpdateManagerDevice(object):
    """Class used to manage the analysis and restore process. Each device has its own."""
    
    def __init__(self, deviceId):
        self._deviceId = deviceId
        self._shell = adb.AndroidDebugBridge(deviceId)
        self._state = 'ready' # ready to start the analysis
        self._process = None
        self._pid = 999999
        self._logger = logging.getLogger('Manager.Update.Device - ' + self._deviceId)

    def getProcess(self):
        """Return the process associated to the specific device."""
        return self._process

    def getPID(self):
        """Return the pid associated to the the process used to manage a specific device"""
        self._logger.info('PID %d is associated to device %s' % (self._pid, self._deviceId))
        return self._pid

    def update(self):
        """Run the update process (i.e., mount the userdata_new partition and copy a clean version into it)"""
        sleep(2)
        while True:
            self._shell.cmd('sh /data/security/shell/copy')
            break

    def join(self):
        """Wait the process"""
        self._process.join()
        self._logger.info('update_device process joined') 

    def startUpdate(self):
        """Create a new subprocess which will be used to perform 
        the update of the new environment. Return the pid of the created process"""
        self._process = Process(target=self.update)
        self._process.start()
        self._pid = os.getpid()

        self._logger.info('Start update device process with PID %d' % self._pid)