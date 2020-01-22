#!/usr/bin/env python3

# Copyright (c) 2018 Hajo Kortmann
# License: GNU GPL v2 (see License.txt)

# Firefox can't deal with ~/xyz paths

import json
import os

with open('dist/browser_extension/firefox/com.snopf.snopf.json') as f:
    data = json.load(f)
    
data['path'] = os.path.expanduser(data['path'])

with open('dist/browser_extension/firefox/com.snopf.snopf.json', 'w') as f:
    json.dump(data, f)
