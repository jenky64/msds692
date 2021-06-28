#!/bin/env python

import argparse
import docker
import sys
import shutil
from filecmp import cmp
from pathlib import Path, PurePath


docker_check_files = [('dockerfile.prev','dockerfile'),
                      ('testing-modules-list.prev','testing-modules-list.txt')]

def setup():
    """
    create and return docker client
    :return: docker client
    """
    return docker.from_env()


def build_image(client, wkspc_dir: str, tag: str) -> bool:
    """
    rebuild the docker container if required
    :param client:
    :param wkspc_dir: jenkins workpspace name
    :param tag: docker image tag
    :return: T/F
    """

    # first create the build directory
    build_dir: str = '/'.join(['/volumes', PurePath(wkspc_dir).name])

    # attempt to build the image
    # if it is successful return True
    # if it fails return False
    try:
        client.images.build(path=build_dir, 
                            tag=tag,
                            forcerm=True)
    except (docker.errors.BuildError, docker.errors.APIError):
        return False

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 
    parser.add_argument('-t','--tag') 

    args = parser.parse_args()

    client = setup()

    if args.dir and args.tag:
        wkspc_dir = args.dir
        tag = args.tag
        ret = build_image(client=client,
                          wkspc_dir=wkspc_dir,
                          tag=tag)

        if ret:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        pass

