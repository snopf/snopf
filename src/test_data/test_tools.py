#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

import json
import base64

TEST_SECRET = b'\x00' * 32

def get_bytes_from_json(data):
    # we store binary data as unicode(base64(data))
    return base64.decodebytes(data.encode())
