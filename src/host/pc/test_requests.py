#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from requests import *

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *


def test_reduce_message_unicode_input():
    with open('../../test_data/test_vectors_reduced_messages.json') as f:
        tests = json.load(f)['tests']
    for test in tests:
        output = get_bytes_from_json(test[1])
        assert reduce_message(test[0]) == output
    
def test_reduce_message_bytes_input():
    with open('../../test_data/test_vectors_reduced_messages_bytes.json') as f:
        tests = json.load(f)['tests']
    for test in tests:
        msg = get_bytes_from_json(test[0])
        output = get_bytes_from_json(test[1])
        assert reduce_message(msg) == output
        
def test_combine_standard_request():
    with open('../../test_data/test_build_request.json') as f:
        tests = json.load(f)
    
    for test in tests:
        req = get_bytes_from_json(test['request'])
        assert req == combine_standard_request(test)
