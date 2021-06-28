#!/bin/env python

import argparse
import logging
import sys
import shutil
from pathlib import Path, PurePath


def delete_commit(wkspc_dir) -> str:
    """
    the commit tag of the most recent commit
    whose tests passed is save in a file.
    this function deletes the file

    :param wkspc_dir: jenkins workspace directory
    :return:
    """

    vol_dir = '/'.join(['/volumes', PurePath(wkspc_dir).name])
    if not Path(vol_dir).exists():
        return False

    commit_path = Path('/'.join([vol_dir, 'commit.txt']))

    try:
        commit_path.unlink()
    except Exception:
        return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    if args.dir:
        wkspc_dir = args.dir
        ret = delete_commit(wkspc_dir=wkspc_dir)
        
        if ret:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)

