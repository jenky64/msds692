#!/bin/env python

from pathlib import Path, PurePath
import argparse
import shutil


save_files = ['dockerfile', 'noxfile.py', 'testing-modules-list.txt']


def check_directory(dir_name: str) -> str:
    """
    each branch of each repository gets a persistent
    directory under /volumes. The name format is :

    <repo_name>_<branch_name>

    So, if repository games has a branch named dev,
    the absolute path to the directory is:

    /volumes/games_dev

    this function checks if it exists and
    creates it if it does not

    :param dir_name: jenkins workspace directory name
    :return: string true or false
    """

    dst_dir = '/'.join(['/volumes', PurePath(dir_name).name])
    p = Path(dst_dir)
    if not p.is_dir():
        p.mkdir(parents=True)
        copy_files(src_dir = dir_name, dst_dir = dst_dir)
        print(f'true')
    else:
        print(f'false')

def copy_files(src_dir: str = None, dst_dir: str = None):
    """
    copy the files in save_files dict
    to the newly created /volumes directory.

    :param src_dir: source directory
    :param dst_dir: destination directory
    :return: None
    """
    for file_name in save_files:
        src_file_name = file_name
        dst_file_name = '.'.join([file_name.split('.')[0], 'prev'])
        src = '/'.join([src_dir, src_file_name]) 
        dst = '/'.join([dst_dir, dst_file_name]) 
        try:
            shutil.copy(src, dst)
        except shutil.Error:
            pass
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dir') 

    args = parser.parse_args()

    if args.dir:
        check_directory(args.dir)

