pipeline {
    agent any

    environment {
        BASE_DIR='/jenkins'
        SCRIPT_DIR="${env.BASE_DIR}/scripts"
        VALID_IMAGE=0
        COMMIT_STATUS=1
        CHECKOUT_STATUS=1
        REVERT_STATUS=1
        COMMIT_TAG=""
    }

    stages {
        stage("Configure") {
            steps {
                script {
                    echo "git branch: ${env.GIT_BRANCH}"
                    echo "git url: ${env.GIT_URL}"
                    echo "git commit: ${env.GIT_COMMIT}"
                    JOB_DIR = JOB_NAME.replace('/','_')

                    echo "checking for repository branch volume directory..."
                    MKDIR = sh(returnStdout: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/configure.py -d ${env.WORKSPACE}").trim()
                    if (MKDIR == 'true') {
                        echo "repository branch volume directory /volumes/${JOB_DIR} successfully created."
                    } else {
                        echo "repository branch volume directory /volumes/${JOB_DIR} already exists."
                    }
                }
            }
        }
        stage("ValidateDockerImage") {
            steps {
                script {
                    echo "validating docker image..."
                    VALID_IMAGE = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/docker/validate.py -d ${env.WORKSPACE}")
                    if (VALID_IMAGE == 0) {
                        echo "Docker image validation passed."
                    } else {
                        echo "Docker image validation failed. Rebuild required."
                    }
                }
            }
        }
        stage("DockerRebuild") {
            when {
                expression {
                    VALID_IMAGE == 1
                }
            }
            steps {
                script {
                    echo "Rebuilding docker image..."
                    BUILD = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/docker/build.py -d ${env.WORKSPACE} -t l2lcommit:latest")
                    echo "build_image = ${BUILD_IMAGE}"
                    if (BUILD_IMAGE == 'true') {
                        echo "Docker image rebuild completed successfully."
                    } else {
                        echo "Docker image rebuild failed.."
                    }
                }
            }
        }
        stage("RunTests") {
            steps {
                script {
                    echo "running tests"
                    RET = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/docker/run.py -d ${env.WORKSPACE} -i l2lcommit:latest")
                    echo "ret = ${RET}"
                    if (RET == 0) {
                        echo "tests passed successfully. saving commit tag ${env.GIT_COMMIT}."
                        SAVE_COMMIT = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/save_commit.py -c ${env.GIT_COMMIT} -d ${env.WORKSPACE}")
                        if (SAVE_COMMIT == 0) {
                            echo "commit tag saved successfully"
                        } else {
                            echo "commit tag save failed. manual intervention required"
                        }
                    } else {
                        echo "tests failed. commit tag not saved. need to revert commit"
                    }
                }
            }
        }
        stage("CommitRevert") {
            when {
                expression {
                    RET != 0
                }
            }
            steps {
                script {
                    COMMIT_TAG = sh(returnStdout: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/read_commit.py -d ${env.WORKSPACE}").trim()
                    echo "reverting commits from ${COMMIT_TAG} forward due to test failure..."
                    REVERT_STATUS = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/revert_commit.py -b ${env.GIT_BRANCH} -d ${env.WORKSPACE}")
                    echo "REVERT_STATUS = ${REVERT_STATUS}"
                }
            }
        }
       stage("PushAfterRevert") {
            environment {
                GIT_AUTH = credentials('cfa38db9-060f-4a7e-92c2-963b692a8ead')
            }
            when {
                expression {
                    REVERT_STATUS == 0
                }
            }
            steps {
                script {
                    echo "branch = ${env.GIT_BRANCH}"
                    sh('''
                    git config --local credential.helper "!f() { echo username=\\$GIT_AUTH_USR; echo password=\\$GIT_AUTH_PSW; }; f"
                    ''')
                    GIT_STATUS = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/git_push.py -b ${env.GIT_BRANCH}")
                    echo "GIT_STATUS = ${GIT_STATUS}"
                    if (GIT_STATUS == 0) {
                        COMMIT =
                        echo "git push after revert completed successfully"
                    }
                }
            }
       }
       stage("CleanUp") {
           steps {
               script {
                   echo "this is the cleanup stage"
               }
           }
       }
       stage("Notify") {
           steps {
               script {
                   echo "this is the notify stage"
               }
           }
       }

    }
}