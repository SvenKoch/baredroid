#!/usr/bin/env python


class Pane(object):
    """used to store tmux pane information"""
    def __init__(self, session, window, pane):
        self._session = session
        self._window = window
        self._pane = pane

    def getPane():
        return self._pane

    def getWindow():
        return self._window

    def getSession():
        return self._session

    def sendCmd(command):
        self._pane.send_keys(command, enter=True)