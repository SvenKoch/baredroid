#!/usr/bin/env python 

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.0.2"


import os
import re
import sys
import traceback
import subprocess

class AndroidDebugBridge(object):
    """Class used as wrapper to send commands through ADB to a device"""

    def __init__(self, deviceId=''):
        self._deviceId = deviceId
        self._isTest = False
    
    def setTest(self, arg):
        self._isTest = arg

    def isTest(self):
        return self._isTest

    def getFakeResult(self, command):
        print 'send command', command
        if 'devices' in command:
            return {'0697d5d7f0eae821':'device','093af3480222237e':'device'} #testing without devices 
        elif 'shell' in command:
            return ''
        elif 'get-state' in command:
            return 'device'
        elif 'reboot' in command:
            return ''
        elif 'push' in command:
            return ''
        elif 'pull' in command:
            return ''
        elif 'root' in command:
            return ''

    def call_adb(self, command, all=False):
        if self.isTest():
            return self.getFakeResult(command)

        try:
            command_result = ''
            if all:
                command_text = 'adb ' + command
            else:
                command_text = 'adb -s ' + self._deviceId + ' ' + command
            results = os.popen(command_text, 'r')
            while 1:
                line = results.readline()
                if not line: break
                command_result += line
            return command_result
        except:
            traceback.print_exc(file=sys.stdout)
            return ''

    # check for any fastboot device
    def fastboot(self, device_id):
        """not supported"""
        pass

    def cmd(self, cmd):
        """Send a command to a device"""
        result = self.call_adb('shell ' + cmd)
        return result
        
    def devices(self):
        """Send the adb devices command"""
        result = {}
        raw_result = self.call_adb('devices', True)
        if self.isTest():
            return raw_result
        devices = re.findall(r"\d[\w\d]+\t+\w+", raw_result)
        for i in devices:
            name, mode = i.split('\t')
            result.update({name:mode})
        # = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return result #[device for device in devices if len(device) > 2]
        
    def get_state(self):
        """Get the state of a device"""
        result = self.call_adb("get-state")
        if self.isTest():
            return result
        result = result.strip(' \t\n\r')
        return result or None
        
    def install(self, device_id, path_to_app, **kwargs):
        # check to see if correct device is connected
        # ensure path to app exists and is .apk
        # command = "install"
        # check for options in kwargs
        
        # result = self.call_adb(command)
        pass
        
    def reboot(self, option):
        command = 'reboot'
        if len(option) > 7 and option in ("bootloader", "recovery", "device"):
            command = "%s %s" % (command, option.strip())
        self.call_adb(command)
        
    def root(self):
        result = self.call_adb('root')
        return result

    def push(self, local, remote):
        result = self.call_adb('push ' + local + ' ' + remote)
        if self.isTest():
            return result
        while True:
            result = self.cmd('ls ' + remote + os.path.basename(local))
            if 'No such file or directory' in result:
                self.call_adb('push ' + local + ' ' + remote)
            else:
                break

        return result
        
    def pull(self, remote, local):
        result = self.call_adb('pull ' + local + ' ' + remote)
        return result
    
    def sync(self, directory, **kwargs):
        command = "sync %s" % directory
        if 'list' in kwargs:
            command += " -l"
        result = self.call_adb(command)
        return result

def main():
    adb = AndroidDebugBridge('092323bb012f57ed')
    print 'aa', adb.cmd('restorecon -Rv /data')
    print adb.reboot('recovery')

if __name__ == '__main__':
    main()