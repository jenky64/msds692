#!/bin/env python3

import glob
import logging
import os
import shutil
import sys
from filecmp import cmp
from pathlib import Path


reuse_envs = True
fail = False

app_dir: str = '.'
backup_dir: str = '/backup'

check_files: list = [('noxfile.prev', 'noxfile.py'),
                     ('modules-list.prev', 'modules-list.txt'),
                     ('testing-modules-list.prev', 'testing-modules-list.txt')]


def check_and_compare_files():
    logging.info('checking and comparing files...\n')
    for files in check_files:
        prev_file = Path('/'.join([backup_dir, files[0]]))
        cur_file = Path('/'.join([app_dir, files[1]]))
        logging.info(f'checking for {cur_file}.')
        if cur_file.exists():
            logging.info(f'file: {cur_file} found.')
        else:
            logging.error(f'file: {cur_file} does not exist. Cannot run tests.')
            logging.error(f'ensure file {cur_file} exists in repository.')
            fail = True

        logging.info(f'running file comparison on {cur_file} and {prev_file}.')
        try:
            if cmp(prev_file, cur_file):
                logging.info(f'file comparison on {cur_file} and {prev_file} successful.\n')
            else:
                logging.error(f'file comparison on {cur_file} and {prev_file} failed.')
                logging.error(f'this may be due to {prev_file} missing or a change to {cur_file}. Cannot reuse environments.\n')
                reuse_envs = False
        except OSError as error:
            logging.error(f'{error}')
            reuse_envs = False


def run(reuse_envs: bool = True):
    logging.info("running tests...")
    os.system('conda develop /app')
    if reuse_envs:
        ret = os.system('nox -R -s tests')
    else:
        ret = os.system('nox -s tests')

    logging.info(f'ret = {ret}')
    return ret


def post_run():
    logging.info("performing post run activities")
    logging.info("moving files to backup directory")

    check_files.append(('dockerfile.prev', 'dockerfile'))

    for files in check_files:
        backup_file = '/'.join([backup_dir, files[0]])
        cur_file = '/'.join([app_dir, files[1]])
        shutil.move(cur_file, backup_file)

    for f in glob.glob(r'/app/*.html'):
        dest_file = f.split('/')[-1]
        dest = '/'.join([backup_dir, dest_file])
        shutil.move(f, dest)


if __name__ == '__main__':

    logging.basicConfig(filename='runtests.log',
                        format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    logging.info(f'starting test runs\n')

    check_and_compare_files()
    if fail:
        logging.error(f'\nCANNOT RUN TESTS DUE TO ERROR!\n')
    else:
        ret = run(reuse_envs=reuse_envs)
        post_run()
        # this is kinda messy. shell returns 0 on success,
        # but in python 0 is false. Since the Jenkinsfile code
        # considers 0 to be a successful run, python false (fail)
        # needs to return shell success (0) and vice versa
        if ret:
            logging.error("tests failed or other error")
            sys.exit(1)
        else:
            logging.info("tests successful")
            sys.exit(0)
