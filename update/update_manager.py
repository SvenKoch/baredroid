#!/usr/bin/env python 

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.0.1"

import os
import adb
import util
import shutil
import config
import logging
import traceback
import subprocess
import ConfigParser
from time import sleep
from analysis import Analysis
from multiprocessing import Process, Queue
from update_manager_device import UpdateManagerDevice
from update_manager_recovery import UpdateManagerRecovery

##
#   
#   
##
class UpdateManager(object):
    """This class is used to manage the analysis and restore process. 
    ach process has it own device to manage."""

    def __init__(self, device):
        self._device = device
        self._shell = adb.AndroidDebugBridge(self.getDeviceId())
        self._dict = {} #each device has its own list of apps to test (reason: different device)
        self._process = None
        self._pid = 999999
        label = 'Manager.Update - ' + self.getDeviceId()
        self._logger = util.init_logger(config.configFile, label)

        self._queue = Queue() # used to share message (for now only exit)

    def getDeviceId(self):
        """Return deviceId."""
        return self._device.getDeviceId()

    def getShell(self):
        """Return deviceId."""
        return self._shell

    def getProcess(self):
        """Return the process object."""
        return self._process

    def getPID(self):
        """return the PID associated to the process."""
        self._logger.info('getPID -> %s' % self._pid)
        return self._pid

    def addAppsToAnalyze(self, key, apps):
        """Add the apps to analyze and define an order (the dict key represents the order)."""
        self._dict[key] = apps

    def waitFor(self, mode=None):
        """This function permits to wait until the device reach the mode (e.g., recovery, device) desired."""

        count = 0
        while True:
            self._logger.info('<waiting device>')
            sleep(3)
            count = count + 1
            if mode:
                if self.getDeviceId in self.getShell().devices().keys() and\
                    self.getShell().devices().get(self.getDeviceId()) == mode:
                    break
            else:
                if self.getDeviceId in self.getShell().devices().keys():
                    break
            
            #[bugfix] sometimes the script does not reboot. be sure to reboot the system 
            if count == 10: #wait 30 seconds
                self.getShell().reboot('device')
                count = 0

        self._logger.info('device is alive')

    def reboot(self, mode):
        """This function allows to reboot the device in recovery mode.
        The parameter 'mode' is used to determine the expected mode after the reboot."""
        self._logger.info('reboot and wait for %s' % mode)
        self.getShell().reboot('recovery')
        self.waitFor(mode)

    def copyFiles(self):
        """This function permits a) copy the files needed to restore the device and 
        b) run the restore script."""
        
        #./update/swap
        self._logger.info('adb push swap')
        self.getShell().push('./update/swap','/cache/recovery/')

        self.getShell().cmd('chmod 755 /cache/recovery/swap')
        self._logger.info('chmod 755 /cache/recovery/swap')

        #./update/parted
        self.getShell().push('./update/parted','/cache/recovery/')
        self._logger.info('adb push parted')

        self.getShell().cmd('chmod 755 /cache/recovery/parted')
        self._logger.info('chmod 755 /cache/recovery/parted')
        
        #perform restore
        self._logger.info('run swap script')
        recovery = UpdateManagerRecovery(self.getDeviceId)
        recovery.startUpdate()
        self._logger.info('running...')
        recovery.join()

        self.getShell().reboot('device')

    def restore(self):
        """This function permits perform the restore process.
        It is used by the update process after the analysis."""

        currentPart = self.getShell().cmd('ls -la /dev/block/platform/msm_sdcc.1/by-name/userdata')
        self.reboot('recovery')
        self._logger.info('copy files')
        self.copyFiles()

        self.waitFor('device')

        newPart = self.getShell().cmd('ls -la /dev/block/platform/msm_sdcc.1/by-name/userdata')
        if currentPart == newPart:
            self._logger.info('Unable to restore the device correctly')
            self.stopUpdate()
        else:
            self._logger.info('Restore performed successfully')

    ##
    #   This function permits to check if there is a message (for now only 'exit') in the queue.
    ##
    def exit(self):
        """This function permits to check if there is a message (for now only 'exit') in the queue."""

        if not self._queue.empty():
            sms = self._queue.get()
            if sms == 'exit':
                self._logger.info('received exit command from the user')
                return True
        return False

    def reportCrash(self):
        """TODO. After a crash this function should get all the info about what happened."""
        pass
        #delete the folder
        #name = os.path.basename(appName)[:-4]
        #rExperiment = os.path.join(os.getcwd(), 'experiment')
        #experiment = os.path.join(rExperiment, 'experiment__' + name)
        #shutil.rmtree(experiment)

        #write in manager_error.log
        #self._logger.error('Possible ransomware for { ' + appName + ' }')

    def createFolder(self, deviceId, folder, count):
        """Create folder used to store the logs."""
        
        expId = 'device__' + deviceId
        fPath = os.path.join(folder, expId)
        if not os.path.exists(fPath):
            os.mkdir(fPath)

        aPath = os.path.join(fPath, str(count))
        if not os.path.exists(aPath):
            os.mkdir(aPath)

        return aPath

    def update(self, folder, window):
        """This function represents the analysis and restore process core."""

        count = 0
        cfg = ConfigParser.ConfigParser()
        cfg.read(config.configFile)
        duration = cfg.get('Analysis', 'duration')

        while True:
            if self.exit() or not bool(self._dict):
                break

            self._logger.info('current state -> %s' % 'running')

            #create folder to store analysis results
            count += 1
            exp_f = self.createFolder(self.getDeviceId(), folder, count)

            #create the wrapper class
            key, l_app = self._dict.popitem()
            exp = Analysis(exp_f, self.getDeviceId(), self._shell, window)
            exp.addApks(l_app)

            #self._logger.info('give root privileges to shell')
            #self.getShell().root()
            #sleep(2)

            ###
            try:
                #update the partitions
                ###runtime = UpdateManagerDevice(self.getDeviceId())
                ###runtime.startUpdate()
                
                #perform the experiment setup
                exp.setup()

                #perform the analysis
                exp.start()
            except:
                self._logger.error('Unable to perform the analysis', exc_info=True)
                #do something
            
            finally:

                #wait the update process
                self._logger.info('Wait update_device process') 
                #runtime.join()
                self._logger.info('update_device process joined') 

                self._logger.info('Wait experiment process')
                exp.getProcess().join(int(duration))
                #if exp.getMessage() == 'ERROR':
                #    self.reportCrash()
                #    try:
                #        exp.join()
                #        exp.terminate()
                #    except:
                #        pass

                self._logger.info('experiment process joined')

                #before to perform the restore process check if the user has stopped the analysis
                if self.exit():
                    break

                self._logger.info('Start restore process') 
                ###self.restore()
                self._logger.info('End restore process') 

                #slow down the process
                self._logger.info('wait 15 seconds')
                sleep(15) # wait the device
        
        print 'Analysis finished for DeviceId', self.getDeviceId()
        self._logger.info('current state -> %s' % 'ready')

    def stopUpdate(self):
        """This function sends the 'exit' message to the subprocess."""
        
        self._queue.put('exit')
        self._process.join()
        #self.getProcess().terminate() # kill the process

    def kill(self):
        #stop the execution
        self._queue.put('exit')
        self._process.join()

    def startUpdate(self, folder, window):
        """This function permits to create a new subprocess which will be used to perform the analysis."""

        self._process = Process(target=self.update, args=(folder,window,))
        self._process.start()
        
        self._pid = os.getpid()
        self._logger.info('Start update process with PID -> %d' % self._pid)
        
        return