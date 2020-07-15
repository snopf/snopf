#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from websocket_server import *

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *
from pytestqt import *
import json


def _test_msg(qtbot, msg, signal_name):
    server = SnopfWebsocketServer(None, 50000)
    ws = QWebSocket()
    with qtbot.waitSignal(ws.connected, timeout=6000) as blocker:
        ws.open(QUrl('ws://localhost:50000'))
    signal = getattr(server, signal_name)
    with qtbot.waitSignal(signal, timeout=6000) as blocker:
        ws.sendTextMessage(msg)
    ws.close()
    with qtbot.waitSignal(server.closed, timeout=6000) as blocker:
        server.close()
    
def test_cmd_get_accounts(qtbot):
    _test_msg(qtbot, json.dumps({'cmd': 'get-accounts'}), 'accountsRequest')
    
def test_cmd_get_device_available(qtbot):
    _test_msg(qtbot, json.dumps({'cmd': 'get-device-available'}), 'deviceAvailableRequest')
    
def test_cmd_password_request(qtbot):
    msg = json.dumps({'cmd': 'password-request', 
                      'data': {'service': 'test', 'account': 'test',
                               'add_new_entries': False}})
    _test_msg(qtbot, msg, 'passwordRequest')
