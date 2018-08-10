# -*- coding:utf-8-*-

import os
from Adeployment.conf.conf import *

def get_playbook():
    playbook_path = os.environ.get('PLAYBOOK_PATH')
    if not playbook_path or playbook_path is None:
        playbook_path = FILE_PATH
    return playbook_path

