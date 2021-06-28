pipeline {
    agent any

    environment {
        BASE_DIR='/jenkins'
        SCRIPT_DIR="${env.BASE_DIR}/scripts"
        VALID_IMAGE=0
        COMMIT_STATUS=1
        CHECKOUT_STATUS=1
        REVERT_STATUS=1
    }

    stages {
        stage("Configure") {
            steps {
                script {
                    echo "git branch: ${env.GIT_BRANCH}"
                    echo "git url: ${env.GIT_URL}"
                    echo "git commit: ${env.GIT_COMMIT}"
                    echo "git previous commit: ${env.GIT_PREVIOUS_COMMIT}"

                    JOB_DIR = JOB_NAME.replace('/','_')

                    echo "checking for repository branch volume directory..."
                    MKDIR = sh(returnStdout: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/configure.py -d ${env.WORKSPACE}").trim()
                    if (MKDIR == 'true') {
                        echo "repository branch volume directory ${JOB_DIR} successfully created."
                    } else {
                        echo "repository branch volume directory ${JOB_DIR} already exists."
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
                        echo "Docker image rebuild passed."
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
                        echo "tests passed. saving commit tag."
                        SAVE_COMMIT = sh(returnStatus: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/save_commit.py -c ${env.GIT_COMMIT} -d ${env.WORKSPACE}")
                        if (SAVE_COMMIT == 0) {
                            echo "commit tag save successful"
                        } else {
                            echo "commit tag save failed"
                        }
                    } else {
                        echo "tests failed. commit tag not saved. need to revert commit"
                    }
                }
            }
        }
        stage("RevertCommit") {
            when {
                expression {
                    RET != 0
                }
            }
            steps {
                script {
                    echo "reverting commit due to test failure..."
                    COMMIT = sh(returnStdout: true, script: "/usr/bin/python3 ${env.SCRIPT_DIR}/git/read_commit.py -d ${env.WORKSPACE}").trim()
                    if (COMMIT == 'false') {
                        echo "unable to read commit file. cannot revert commit. must be managed manually."
                    } else {
                       echo "commit = ${COMMIT}"
                    }
                    //REVERT_STATUS = sh(returnStatus: true, script: "git revert ${COMMIT} --no-edit")
                    REVERT_STATUS = sh(returnStatus: true, script: "git revert ${COMMIT}")
                    //COMMIT_STATUS = sh(returnStatus: true, script: "git commit -am 'reverting to clean state'")
                    //COMMIT_STATUS = 0
                    CHECKOUT_STATUS = sh(returnStatus: true, script: "git checkout -B ${env.GIT_BRANCH}")
                    echo "REVERT_STATUS = ${REVERT_STATUS}"
                    echo "CHECKOUT_status = ${CHECKOUT_STATUS}"
                }
            }
        }
       stage("PushAfterRevert") {
            environment {
                GIT_AUTH = credentials('cfa38db9-060f-4a7e-92c2-963b692a8ead')
            }
            when {
                expression {
                    CHECKOUT_STATUS == 0
                }
            }
            steps {
                script {
                    echo "testing push after revert"
                    echo "branch = ${env.GIT_BRANCH}"
                    echo "user = ${GIT_AUTH_USR}"
                    echo "password = ${GIT_AUTH_PSW}"
                    sh('''
                    git config --local credential.helper "!f() { echo username=\\$GIT_AUTH_USR; echo password=\\$GIT_AUTH_PSW; }; f"
                    git push origin HEAD:dev
                    ''')
                }
            }
        }
        stage("Notify") {
        }
    }
}