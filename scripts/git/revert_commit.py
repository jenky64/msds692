#!/bin/env python

import argparse
import logging
import os
import sys
import shutil
from pathlib import Path, PurePath


def read_commit(wkspc_dir: str) -> str:
    """
    read and return commit value
    :param wkspc_dir: jenkins workspace directory
    :return: commit tag value
    """

    commit = 'false'

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
    finally:
        return commit


def revert_commit(branch: str, wkspc_dir: str) -> bool:
    """
    git revert to the provided commit value
    :param branch: branch name
    :param wkspc_dir: jenkins workspace directory
    :return: T/F
    """

    commit = read_commit(wkspc_dir)

    # perform the git operations to execute the rever
    # revert
    # checkout the brach
    # push the revert to github
    if commit is not 'false':
        revert_cmd = f'git revert {commit} --no-edit'
        checkout_cmd = f'git checkout -b {branch}'
        push_cmd = f'git push origin {branch}'

        os.system(revert_cmd)
        os.system(checkout_cmd)
        os.system(push_cmd)

    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b','--branch') 
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    logging.basicConfig(filename='git.log',                                
                        format='%(asctime)s %(levelname)s:%(message)s',         
                        datefmt='%m/%d/%Y %I:%M:%S %p',                         
                        level=logging.DEBUG)

    if args.dir and args.branch:
        wkspc_dir = args.dir
        branch = args.branch
        ret = revert_commit(branch=branch, wkspc_dir=wkspc_dir)

        if ret(0):
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        sys.exit(1) 

