 #!/usr/bin/env python

class Device():
    """Class used to store:
    - general info about a device used by baredroid
    - the process used by the infrastructure to trigger the different states 
    (e.g., update, swap partitions) for a device"""
    
    def __init__(self, id, color, port, user):
        self._id = id
        self._color = color
        self._port = port
        self._process = None
        self._state = 'ready'
    

    def setDeviceId(self, deviceId):
        self_id = deviceId

    def getDeviceId(self):
        return self._id


    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color


    def getPort(self):
        return self._port

    def setPort(self, port):
        self._port = port


    def getState(self):
        return self._state

    def setState(self, state):
        self._state = state
