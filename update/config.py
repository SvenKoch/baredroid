#!/usr/bin/env python

__author__ = "Simone Mutti"
__email__ = "simone.mutti@unibg.it"
__version__ = "0.0.1"

from os.path import join, abspath, dirname

"""Define static pointers to configuration files"""

modulePath = dirname(abspath(__file__))

configPath = join(modulePath, 'config')
configFile = join(configPath, 'config.cfg')

configPath = join(modulePath, 'config')
deviceInfoFile = join(configPath, 'devices.info')