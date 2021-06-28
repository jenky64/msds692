#!/bin/env python

import shutil
import pwd
import sys
import pathlib

volumes_path = pathlib.Path('/volumes')
jenkins_path = pathlib.Path('/jenkins')


def make_paths() -> None:
    """
    create /volumes and /jenkins directories
    :return: None
    """
    if not jenkins_path.is_dir():
        jenkins_path.mkdir(parents=True)
        pathlib.Path('/jenkins/bin').mkdir(parents=True)

    if not volumes_path.is_dir():
        volumes_path.mkdir()


def copy_files() -> None:
    """
    copy the scripts directory to /jenkins
    :return: None
    """
    src = 'scripts'
    dest = '/jenkins/scripts'
    shutil.copytree(src, dest)


def set_ownership() -> None:
    """
    recursively set jenkins:jenkins ownership
    on /volumes and /jenkins
    :return: None
    """

    # make sure jenkins user exists and bail if not
    try:
        uid = pwd.getpwnam('/jenkins').pw_uid
    except Exception:
        print(f'user jenkins does not exist. cannot change directory/file ownership')
        sys.exit(1)
    else:
        shutil.chown('/volumes', user='jenkins', group='jenkins')
        shutil.chown('/jenkins', user='jenkins', group='jenkins')
        pth = pathlib.Path('/jenkins')
        for f in pth.glob('**/*'):
            shutil.chown(f, user='jenkins', group='jenkins')


if __name__ == '__main__':

    make_paths()
    copy_files()
    set_ownership()


