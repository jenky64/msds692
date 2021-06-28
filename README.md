# Continuous Integration
## Intent and rationale
The intent of the Continuous Integration implementation is three-fold:

 1. To enforce code testing standards and requirements as github pushes will ultimately be unsuccessful unless code tests pass.
 2. To ensure a clean code state for all repository branches. Clean is defined as "all code tests have passed." It does not mean the code is error free. This state is ensured by running the code tests on each push to github and backing out the commit if one or more tests fail.
 3. To automate the testing workflow.


## Setup
The Continuous Integration is self-hosted on a dedicated Digital Ocean droplet. It uses Jenkins as the CI platform, Docker to containerize the test runs, and Python pytest and nox as the testing framework.
 1. **Digital Ocean droplet**
 The droplet runs on Ubuntu 20.04 and is minimally resourced with 1G ram and 1 CPU. sshd and Jenkins are the only services running. Both run on non-standard ports, 2021 and 8091, respectively. As other network services are not needed to meet the CI requirements, a firewall is enabled and rejects all traffic except for the above mentioned ports. Access is currently restricted to the project leads and the individual(s) managing the CI. 
 2. **Jenkins**
 Access  to the Jenkins web interface is via http://159.89.189.37:8091. The only currently configured user is the admin user.
3. **Docker**
The docker image is built on Debian buster and miniconda3. The python version is 3.8.5 and has the python modules listed in the file *testing-modules-list.txt* additionally installed. The current image tag is "l2lcommit:latest." It's sole purpose is to provide a generic python environment where the code tests will be run. It this respect, it is a generic build so as to be usable for all repositories and branches. This removes the need to provide separate images for each repository and/or branch. The only times the image should require a rebuild is when a new version of the miniconda3 image is released, when new versions of the additionally installed testing modules will be used, or when a move to python 3.9.x is made. 
4.  **pytest and nox**
    Python pytest and nox are used for the code testing framework. Nox is used due to its following features: 
    1. it can be configured to run tests on multiple Python versions and different module versions. This allows for testing code on new versions of repository/branch specific modules before upgrading the code. 
    2. it creates test specific virtual environments on demand. 
    3. it can re-use existing virtual environments, which will allow for quicker test runs and leaner resource usage.

## CI Testing workflow
The CI workflow is designed to fully automate the setup and execution of the testing requirements. It is built on a multibranch pipeline configuration that dynamically creates Jenkins jobs for all repository branches that contain a *Jenkinsfile*. Github repositories are required to have a github-webhook that ties the repository to the Jenkins installation. The workflow is managed by the *Jenkinsfile* in the repository. The *Jenkinsfile* itself is essentially a wrapper script that contains a sequence of calls to python scripts that are managed outside the repository.

 1. **execute a push to a configured github repository branch**  
 This will not apply to the main or master branch on the repository as merging with either of those branches will have a separate process. The current idea is that each repository will have a pre-main or pre-master branch that all other branches are initially merged into. After a successful merge has been confirmed, a subsequent merge to the main/master branch will be performed. This has implications for how git is configured on one's local machine and will be discussed below.
 2. **Jenkins pipeline job is triggered**  
 This is made possible through the repository github-webhook and is specific to the branch being pushed to.   
 3.  **pipeline stages**
	 1. *Configure*
	 This stage creates a branch specific volume directory if one does not already exist and initially populates it with the current version of the dockerfile. The current directory naming for branch specific volumes is */volumes/<repository_branch>* and is currently not managed by docker. For example, with a repository named cloud-point-test with branches named testconfig1 and testconfig2, the volume directory will look like:
	 
	    ```
	    l2l-regis-cicd:davidj / >  pwd
        /
        (base) l2l-regis-cicd:davidj / >  tree volumes
        volumes
        ├── cloud-point-test_testconfig1
        └── cloud-point-test_testconfig2
        ```
	 
	 2. *ValidateDockerImage*  
	      Checks if the docker images requires a rebuild. It does this by comparing the current version of the file in the volume directory with the one in the repository.
	
	 3. *DockerRebuild*    
	     Rebuilds the docker image if the configure stage has determined one is necessary.
	
	 4. *RunTests*  
	     This stage has a number of steps:
	       1. Confirms the tests can be run by verifying the existence of the following files in the repository: *noxfile.py*, *runtests.py*, *testing-modules-list.txt*, and *modules-list.txt*. If any of theses files is missing, the tests cannot be run. Except for *modules-list.txt* and possibly *noxfile.py*, the files will be the same across all repositories/branches.
	       2. Determines if the nox managed virtual environments can be reused. This is done by checking if the *noxfile* or the *module-list* files have changed since the previous branch push. The *module-list* files are used by nox to build the virtual environments. The *noxfile* determines how the tests are run and how it is configured can render the current nox managed environemnts environments invalid. If any of these files have changed, the current environment is flagged as invalid and it must be recreated. 
	       3. Run the tests with the current or recreated virtual environments.
	       4. Create backup copies of the *dockerfile*, the *noxfile*, and the *module-list* files. These will be used on the subsequent run to determine if any of the have itermittently changed.
		   5. Save the commit tag if the tests are successful. This is required for reverting the commit in subsequent runs if they fail.
	
	 5. *RevertCommit*  
	     Backout the commit pushed to the branch. This will occur only if one or more tests failed and will be skipped otherwise.

	 6. *PushAfterCommit*  
		 Push the reverted commit to github.
		
	 6. *Notify*  
	     Each nox run generates an html formatted results report. The current process is to email those files to the repository/branch owner. This has not been fully implemented at this time. Another possibility is to make a slack notification indicating the repository, branch, and success/failure status.

### Current workflow concerns and considerations
There are a few issues with the current workflow and how it is designed

 1. Currently, requiring the repositories to contain files that are not specifically required by the repository itself can be problematic. They can be accidentally modified or even removed, which can significantly affect the test runs. They also clutter the repository. This applies to the following files: *dockerfile*, *runtests.py*, and *testing-modules-list.txt*. While *testing-modules-list.txt* is used by nox to create the virtual environments, it contains no entries that are repository or branch specific. CI is designed in such a way as to ensure all branches are tested with the same modules. Modifying this file will violate that design. Due to nox restrictions, *runtests.py* needs to be in the same directory as the noxfile and tests directory, making it convenient to mimic that in the repository. However, it is not branch specific and is best managed a different way. 
 2. As currently written, the docker validation and rebuild stages are questionable because they are triggered by checking the *dockerfile* in the repository branch and a rebuild is performed if the file is modified between pushes.  Modifying the *dockerfile* at the repository level, by design, should never happen as it is managed by the CI manager, not the repository owners. The repository/branch owners have no reason to modify it. Because of this, this feature will need to be re-engineered to be managed outside the repositories.
 3. Process for making available and ensuring all repositories and branches receive updated *runtests.py* and *testing-modules-list.txt* files. Currently, no such process is in place.
 4. How merges with the main/master branch have not been implemented. One idea for how this can be done is discussed above. One issue of concern is how to address merges from branches that have different python module versions. This can possibly be addressed in a pre-main/pre-master merge. A process for determining the authoritative module version will have to be developed. This should not be a concern of CI.

## CI Code Layout
The CI design contains files that are required by the repositories and files that are managed separately.
 1. **Repository required files**
 The only file that is absolutely required by the repository is the *Jenkinsfile* as its existence is what triggers the Jenkins job. Other files required to exist in the repositories include: 
	 1. *dockerfile*: docker image definition file
	 2. *runtests.py*: python script that validates and executes the test runs and performs post-test cleanup.
	 3. *noxfile.py*: definition file for how nox builds and manages the virtual environments and invokes pytest. This can be modified by the repository and branch owners to accommodate branch specific testing requirements.
	 4. *testing-modules-list.txt*: the list of nox, pytest, and conda modules that are required to build the testing environments. This file is not repository specific and should not be modified with a repository.
	 5. *modules-list.txt*: the list of modules that are required by the code in the repository or branch. The content of this file may be specific to the branch and is managed by the repository/branch owner.
 2. **Non-repository managed files**
    As discussed above, Jenkins is essentially a wrapper script for a sequence of calls to python scripts. These scripts manage CI workflow from start to finish except for the notifications as that has yet to be fully implemented and Jenkins has built-in email and slack notification mechanisms. These can be accomplished with python scripts, so to be consistent with the rest of the design, this will be the first choice. 
    1. *current layout*
    
        ```
        (base) l2l-regis-cicd:davidj / >  pwd
        /
        (base) l2l-regis-cicd:davidj / >  tree jenkins
        jenkins
        ├── bin
        │   └── jenkins-cli.jar
        └── scripts
            ├── configure.py
            ├── docker
            │   ├── build.py
            │   ├── run.py
            │   └── validate.py
            |__ git
            |   |-- delete_commit.py 
            |   |-- read_commit.py 
            |   |-- revert_commit.py 
            |   |-- save_commit.py 
            └── runtests.py
    
    2. *files*
        1. *configure.py*: creates volume directory if necessary and populates it with the necessary files
        2. *runtests.py*: validates and executes the test runs and performs post-test cleanup.
        3. *docker/validate.py*: validates the docker image by checking if dockerfile has been modified
        4. *docker/build.py*: rebuilds the docker image
        5. *docker/run.py*: runs the docker image and executes the tests. 

## User Code Layout
The intent of the CI effort is to enforce code testing standards and requirements. Accordingly, the repository and branch code layout test format have been standardized and are expected to be reflected in each repository branch. Using pytest and nox provides some flexibility that will be discussed.
 1. **required files**  
  The required files are discussed in CI Code Layout section above. Except for *modules-list.txt*, which is repository and branch specific, all of the required files will be provided. A process for pushing out updated required files will be developed.

 2. **repository layout**  
	  The source and tests directories are assumed to be at the top level of the repository branch. There is some flexibility here as the underlying requirement is that the call to pytest from nox is able to find the tests. As long as pytest and nox can accomplish that, the source and tests directories may be configured in any way that makes sense for the repository branch. Because of how they are used in the CI workflow, the other required files necessarily must be at the top level of the repository branch. 
	  
	  ```
	  drwxr-xr-x 2 jenkins jenkins 4096 Jun 16 16:55 src
	  -rw-r--r-- 1 jenkins jenkins  236 Jun 16 16:55 dockerfile
	  -rw-r--r-- 1 jenkins jenkins 1033 Jun 16 17:51 Jenkinsfile
	  -rw-r--r-- 1 jenkins jenkins 1064 Jun 16 16:55 LICENSE
	  -rw-r--r-- 1 jenkins jenkins   28 Jun 16 16:55 modules-list.txt
	  -rw-r--r-- 1 jenkins jenkins  725 Jun 16 16:55 noxfile.py
	  -rw-r--r-- 1 jenkins jenkins   90 Jun 16 16:55 README.md
	  -rwxr-xr-x 1 jenkins jenkins 2025 Jun 16 16:55 runtests.py
	  -rw-r--r-- 1 jenkins jenkins  190 Jun 16 16:55 testing-modules-list.txt
	  drwxr-xr-x 2 jenkins jenkins 4096 Jun 16 16:55 tests
	  ```
	  
 3. **requirements, restrictions, and local configuration**  
     There are a few requirements and restrictions for the local code layout. By design, merging with the main/master branch is prohibited and pushing directly to the main/master branch is also prohibited. These restrictions are enforced by requiring pre-pull, pre-push, and pre-commit scripts in one's local cloned repository that will prevent such actions. These scripts are in the process of being developed. As discussed above, the current working idea is to create a pre-master or pre-main branch that is merged with first. After this merge has been validated and the subsequent tests have passed, a merge of this branch to the master branch will be automatically triggered.