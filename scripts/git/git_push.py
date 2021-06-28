#!/bin/env python

import argparse
import logging
import os
import sys


def git_push(branch: str) -> bool:
    """
    push reverted changes to github
    :param branch: branch being pushed
    :return: T/F
    """

    push_cmd = f'git push origin {branch} >/dev/null 2>&1'

    try:
        execute_status = not os.system(push_cmd)
        logging.info("git push successful")
    except Exception as e:
        logging.error("git push failed: {e.message}")

    return execute_status

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b','--branch') 

    args = parser.parse_args()

    logging.basicConfig(filename='git.log',                                
                        format='%(asctime)s %(levelname)s:%(message)s',         
                        datefmt='%m/%d/%Y %I:%M:%S %p',                         
                        level=logging.DEBUG)

    if args.branch:
        branch = args.branch
        ret = git_push(branch=branch)

        if ret:
            logging.info("git push was successful")
            sys.exit(0)
        else:
            logging.error("git push failed. see logs for details.")
            sys.exit(1)
    else:
        sys.exit(1) 

