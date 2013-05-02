#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
    start gevent wsgi web server
    ~~~~~~~~~~~~~~~~

    :copyright: 2012 by raptor.zh@gmail.com
"""
import sys
import os
from gevent import socket
from gevent import monkey
monkey.patch_all()
from gevent.wsgi import WSGIServer
import pwd

import logging

logger = logging.getLogger(__name__)

sys.stdout = sys.stderr

"""
#Usage:

application = app.wsgifunc()

# using socket
start_socket(application, sockpath, username)
# sockpath: /var/www/sockets/xxx.sock
# username: www-data

# using address and port
start_listen(application, addr, port)
# addr/port: ""/8080
"""

def start_socket(application, sockpath, username):
    pe = pwd.getpwnam(username)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove(sockpath)
    except OSError:
        pass
    sock.bind(sockpath)
    os.chown(sockpath, pe.pw_uid, pe.pw_gid)
    os.chmod(sockpath, 0770)
    sock.listen(256)
    WSGIServer(sock, application).serve_forever()

def start_listen(application, address, port):
    if type(port)!=type(int()):
        port = int(port)
    WSGIServer((address, port), application).serve_forever()

