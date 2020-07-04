#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
QT Websocket server for connection to browser extensions
'''

import sys
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from PySide2.QtWebSockets import *
import json

import snopf_logging
logger = snopf_logging.get_logger('websocket-server')

class SnopfWebsocketError(Exception):
    pass

class SnopfWebsocketServer(QWebSocketServer):
    
    # Communication signals
    deviceAvailableRequest = Signal(QWebSocket)
    accountsRequest = Signal(QWebSocket)
    passwordRequest = Signal(str, str, bool)    
    
    def __init__(self, parent, port, whitelist=[]):
        # TODO whitelisting
        super().__init__('snopf-websocket-server', QWebSocketServer.SslMode.NonSecureMode , parent)
        
        # Websockets connected to us
        self.connections = []
        
        # Start server
        success = self.listen(QHostAddress.LocalHost, port=port)
        if not success:
            logger.error('Cannot start websocket server')
            err = self.errorString()
            logger.error(err)
            raise SnopfWebsocketError(err)
        
        logger.info('Running websocket server with name %s' % self.serverName())
        logger.info('Websocket server address: %s, port: %d' % (self.serverAddress(), self.serverPort()))
        
        self.newConnection.connect(self.addConnection)
        self.acceptError.connect(self.processAcceptError)
        self.serverError.connect(self.processServerError)
        
    def addConnection(self):
        logger.info('New websocket connection')
        websocket = self.nextPendingConnection()
        self.connections.append(websocket)
        logger.info('current list of websockets: %s' % str(self.connections))
        websocket.textMessageReceived.connect(lambda msg: self.textMessageReceived(websocket, msg))
        websocket.disconnected.connect(lambda: self.disconnected(websocket))
        websocket.error.connect(lambda: self.connError(websocket))
        
    def processAcceptError(self, socketError):
        logger.error('Websocket Accept Error %d' % socketError)
        err = self.errorString()
        logger.error(err)
        raise SnopfWebsocketError(err)
    
    def processServerError(self, closeCode):
        logger.error('Websocket Server Error %d' % closeCode)
        err = self.errorString()
        logger.error(err)
        raise SnopfWebsocketError(err)
    
    def disconnected(self, websocket):
        logger.info('Disconnected %s' % str(websocket))
        self.connections.pop(self.connections.index(websocket))
        logger.info('Current list of websockets: %s' % str(self.connections))
        
    def connError(self, websocket, socketError):
        logger.error('ws error %d' % socketError)
        err = websocket.errorString()
        logger.error(err)
        raise SnopfWebsocketError(err)
    
    def textMessageReceived(self, websocket, msg):
        logger.info('Text msg received from %s' % str(websocket))
        try:
            msg = json.loads(msg)
        except json.JSONDecodeError:
            logger.error('Could not read message from client')
            return
        if msg['cmd'] == 'get-accounts':
            logger.info('got get-accounts msg')
            self.accountsRequest.emit(websocket)
        elif msg['cmd'] == 'get-device-available':
            logger.info('got device-available msg')
            self.deviceAvailableRequest.emit(websocket)
        elif msg['cmd'] == 'password-request':
            # This is always the last command
            # and if we show an error message we get a segfault
            # here for some reason, so for now we force close the
            # connection after getting the request
            websocket.close()
            logger.info('got password-request')
            data = msg['data']
            self.passwordRequest.emit(data['service'], data['account'], data['add_new_entries'])
            
    def sendAccountsList(self, websocket, accounts):
        msg = {'cmd': 'new-accounts', 'data': accounts}
        websocket.sendTextMessage(json.dumps(msg))
        
    def sendDeviceAvailable(self, websocket, isAvailable):
        msg = {'cmd': 'device-available', 'data': {'device-available': isAvailable}}
        websocket.sendTextMessage(json.dumps(msg))       
    
