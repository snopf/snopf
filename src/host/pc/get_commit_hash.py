# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

import git

def get_commit_hash():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha
