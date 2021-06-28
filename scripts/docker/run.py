#!/bin/env python

import argparse
import logging
import docker
import sys
import shutil
from filecmp import cmp
from pathlib import Path, PurePath


docker_check_files = [('dockerfile.prev','dockerfile'),
                      ('testing-modules-list.prev','testing-modules-list.txt')]

def setup():
    """
    setup and return the docker client
    :return: docker client
    """
    return docker.from_env()


def run_image(client, image: str, wkspc_dir: str) -> bool:
    """
    run the docker image
    :param client: docker client
    :param image: docker image name
    :param wkspc_dir: jenkins workspace directory name
    :return:  T/F
    """


    ret = True

    # verify the volume branch /volumes directory exists
    vol_dir = '/'.join(['/volumes', PurePath(wkspc_dir).name])
    if not Path(vol_dir).exists():
        return False

    # these are the filesystems that the image is
    # going to mount as volumes
    # wkspc_dir is the jenkins workspace directory
    # vol_dir is the branch directory under /volumes
    volumes = { wkspc_dir: {'bind': '/app', 'mode': 'rw'},
                vol_dir: {'bind': '/backup', 'mode': 'rw'}
              }

    # create unique name for the docker container
    # this will prevent name conflicts for branches
    # in different repositories that have the same name
    container_name = PurePath(wkspc_dir).name
    command='/app/runtests.py'

    try:
        client.containers.run(image=image,
                              command=command,
                              name=container_name,
                              volumes=volumes,
                              remove=True,
                              detach=False)
    except docker.errors.APIError:
        ret = False
    finally:
        pass

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 
    parser.add_argument('-i','--image') 

    args = parser.parse_args()

    client = setup()

    if args.dir and args.image:
        wkspc_dir = args.dir
        image = args.image
        ret = run_image(client, image=image, wkspc_dir=wkspc_dir)

        if ret:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)



