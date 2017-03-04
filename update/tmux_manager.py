#!/usr/bin/env python

import tmuxp

def tmux_init(devices, session_name):
    
    #start server
    server = tmuxp.cli.Server()

    #find the session created by the init script
    session = server.find_where({ "session_name": session_name })

    #rename the first window
    session.list_windows()[0].rename_window('main')
    #session.list_windows()[0].split_window(attach=False)
    
    #create a window containing the main log
    winLog = session.new_window(attach=False, window_name='mainLog')
    winLog.split_window(attach=False)

    for id in devices:
        win = session.new_window(attach=False, window_name=str(id))
        win.split_window(attach=False)
        for p in win.list_panes():
            print p

    return session
