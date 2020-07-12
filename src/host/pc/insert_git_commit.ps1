cp get_commit_hash.py __get_commit_hash___
cp get_commit_hash__.py get_commit_hash.py
$git_hash=git rev-parse HEAD
(Get-Content get_commit_hash.py).replace('REPLACE_WITH_GIT_HEX_HASH', $git_hash) | Set-Content get_commit_hash.py

