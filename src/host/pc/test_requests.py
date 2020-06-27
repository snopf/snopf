#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from requests import *

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *

def test_combine_standard_request():
    with open('../../test_data/test_build_request.json') as f:
        tests = json.load(f)
    
    for test in tests:
        expected = get_bytes_from_json(test['request'])
        master_key = get_bytes_from_json(test['master_key'])
        req = combine_standard_request(test['service'].encode(),
                                       test['account'].encode(),
                                       master_key, test['password_iteration'])
        assert expected == req
