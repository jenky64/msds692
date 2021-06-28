#!/bin/env python

import argparse
import sys
from filecmp import cmp
from pathlib import Path, PurePath

# files that need to exist for the image to be validated
docker_check_files = [('dockerfile.prev', 'dockerfile'),
                      ('testing-modules-list.prev', 'testing-modules-list.txt')]


def validate_docker_image(wkspc_dir: str) -> bool:
    """

    :param wkspc_dir: jenkins workspace directory name
    :return: T/F
    """

    # get the branch directory name under /volumes
    vol_dir = '/'.join(['/volumes', PurePath(wkspc_dir).name])

    # iterate over files and compare the copy in
    # the workspace directory to the backup copy
    # in the branch volumes directory
    for file_names in docker_check_files:
        src_file = '/'.join([wkspc_dir, file_names[1]])
        chk_file = '/'.join([vol_dir, file_names[0]])

        # if the files does not exist return false
        try:
            val = cmp(src_file, chk_file)
        except OSError as e:
            val = False

        # the comparison will return 0 if they
        # are the same, otherwise 1
        # if we get even one that does not validate
        # we exit
        if not val:
            break

    if val:
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    if args.dir:
        wkspc_dir = args.dir
        ret = validate_docker_image(wkspc_dir=wkspc_dir)
        if ret:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)

