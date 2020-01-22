# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

def get_commit():
    try:
        with open('commit_hash.txt') as f:
            return f.readline()
    except FileNotFoundError:
        return "no info"
