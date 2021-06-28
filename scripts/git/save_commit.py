#!/bin/env python

import argparse
import logging
import sys
import shutil
from pathlib import Path, PurePath


def save_commit(commit, wkspc_dir) -> bool:
    """
    save the commit tag to commit.txt
    :param commit: commit tag
    :param wkspc_dir: jenkins workspace directory
    :return: T/F
    """

    # confirm branch directory exists
    vol_dir = '/'.join(['/volumes', PurePath(wkspc_dir).name])
    if not Path(vol_dir).exists():
        return False

    # generate commit.txt file path
    commit_path = Path('/'.join([vol_dir, 'commit.txt']))

    # write value to file or bail
    try:
        commit_path.write_text(str(commit))
    except Exception as e:
        print(str(e))
        return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--commit') 
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    if args.dir and args.commit:
        wkspc_dir = args.dir
        commit = args.commit
        ret = save_commit(commit=commit, wkspc_dir=wkspc_dir)

        if ret:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)

