#!/bin/env python

import argparse
import logging
import sys
import shutil
from pathlib import Path, PurePath


def read_commit(wkspc_dir) -> str:
    """
    read and return the value
    in the commit file
    :param wkspc_dir: jenkins workspace dicrectory
    :return: commit tag value
    """

    commit = 'false'

    # confirm branch directory exists
    vol_dir = '/'.join(['/volumes', PurePath(wkspc_dir).name])
    if not Path(vol_dir).exists():
        return commit

    commit_path = Path('/'.join([vol_dir, 'commit.txt']))

    # read commit value and return it.
    # or return 'false'
    try:
        commit = commit_path.read_text()
    except Exception:
        pass

    return commit


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    if args.dir:
        wkspc_dir = args.dir
        commit = read_commit(wkspc_dir=wkspc_dir)
        
        print(f'{commit}')
    else:
        print(f'false')

