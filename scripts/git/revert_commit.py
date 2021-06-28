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

    if commit != 'false':                                                       
        revert_cmd = f'git revert --no-commit {commit}..HEAD >/dev/null 2>&1'   
        commit_cmd = f'git commit -am "reverting to most recent clean state: tag -> {commit}." >/dev/null 2>&1'
        checkout_cmd = f'git checkout -B {branch} > /dev/null 2>&1'             
   
        # execute each call and bail if any fail                                
        try:                                                                    
            execute_status = not os.system(revert_cmd)                          
            logging.info("git revert successful")                               
        except Exception as e:                                                  
            logging.error("git revert failed: {e.message}")                     
   
        if execute_status:                                                      
            try:                                                                
                execute_state = not os.system(commit_cmd)                       
                logging.info("git commit successful")                           
            except Exception as e:                                              
                logging.error("git commit failed: {e.message}")                 
   
        if execute_status:                                                      
            try:                                                                
                execute_status = not os.system(checkout_cmd)                    
                logging.info("git checkout successful")                         
            except Exception as e:                                              
                logging.error("git checkout failed: {e.message}")               
   
        return execute_status                                                   
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

        if ret:
            logging.info("git revert process was successful")
            sys.exit(0)
        else:
            logging.error("git revert process failed. see logs for details.")
            sys.exit(1)
    else:
        sys.exit(1) 

