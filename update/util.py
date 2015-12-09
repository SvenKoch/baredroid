 #!/usr/bin/env python 

import os
import logging
import ConfigParser

from threading import Lock

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class ListApp(object):
    def __init__(self):
        self._list = []

    def createQueue(self, apps):
        self._list = apps

    def size(self):
        return len(self._list)

    def get(self):
        lock = Lock()
        lock.acquire()
        item = ''
        if not self.empty():
            try:
                item = self._list.pop()
            except:
                print 'List is empty'
        lock.release()
        return item


    def size(self):
        return len(self._list)

    def empty(self):
        if len(self._list) == 0:
            return True
        else:
            return False

def read_config(conf_file, clazz, field):
    """Read the config file passed as argument and 
    return the value stored in the given class.field"""
    c = ConfigParser.ConfigParser()
    c.read(conf_file)
    res = c.get(clazz, field)
    return res

def init_logger(conf_file, label):
    """Initialize logger."""

    log_folder = os.path.join(os.getcwd(), read_config(conf_file, 'Log', 'folder'))
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    log_info_file = os.path.join(log_folder,\
                         read_config(conf_file, 'Log', 'log'))
    log_error_file = os.path.join(log_folder,\
                         read_config(conf_file, 'Log', 'error'))

    if not os.path.exists(log_info_file):
        open(log_info_file, 'a').close()

    if not os.path.exists(log_error_file):
        open(log_error_file, 'a').close()

    logger = logging.getLogger(label)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(log_folder, log_info_file))
    fh.setLevel(logging.INFO)
    ch = logging.FileHandler(os.path.join(log_folder, log_error_file))
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
