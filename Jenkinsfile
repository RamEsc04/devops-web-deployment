pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'qa', 'prod'],
            description: 'Ambiente que se desea construir y desplegar'
        )
    }

    environment {
        PROJECT_NAME = 'devops-web-deployment'
    }

    stages {
        stage('Preparar variables') {
            steps {
                script {
                    switch (params.DEPLOY_ENV) {
                        case 'dev':
                            env.APP_VERSION = '1.0.0-dev'
                            env.NAMESPACE = 'web-dev'
                            break

                        case 'qa':
                            env.APP_VERSION = '1.0.0-rc'
                            env.NAMESPACE = 'web-qa'
                            break

                        case 'prod':
                            env.APP_VERSION = '1.0.0'
                            env.NAMESPACE = 'web-prod'
                            break

                        default:
                            error("Ambiente no válido: ${params.DEPLOY_ENV}")
                    }

                    env.IMAGE_NAME =
                        "${env.PROJECT_NAME}:${params.DEPLOY_ENV}"
                }

                echo "Ambiente: ${DEPLOY_ENV}"
                echo "Versión: ${APP_VERSION}"
                echo "Namespace: ${NAMESPACE}"
                echo "Imagen: ${IMAGE_NAME}"
            }
        }

        stage('Validar Shell') {
            steps {
                sh '''
                    bash -n app/app.sh
                    shellcheck app/app.sh
                '''
            }
        }

        stage('Generar aplicación') {
            steps {
                sh '''
                    APP_ENV="${DEPLOY_ENV}" \
                    APP_VERSION="${APP_VERSION}" \
                    ./app/app.sh

                    test -f app/output/index.html

                    grep -E "Ambiente|Versión" \
                        app/output/index.html
                '''
            }
        }

        stage('Validar Terraform') {
            steps {
                dir('terraform') {
                    sh '''
                        terraform fmt -check
                        terraform init -input=false
                        terraform validate
                    '''
                }
            }
        }

        stage('Validar Ansible') {
            steps {
                sh '''
                    ansible-inventory \
                        -i ansible/inventory.ini \
                        --list

                    ansible-playbook \
                        -i ansible/inventory.ini \
                        ansible/playbook.yml \
                        --syntax-check
                '''
            }
        }

        stage('Validar Kubernetes') {
            steps {
                sh '''
                    kubectl apply \
                        --dry-run=client \
                        -f "k8s/${DEPLOY_ENV}/"
                '''
            }
        }

        stage('Construir imagen Docker') {
            steps {
                sh '''
                    docker build \
                        -t "${IMAGE_NAME}" \
                        -f docker/Dockerfile .
                '''
            }
        }

        stage('Cargar imagen en Minikube') {
            steps {
                sh '''
                    minikube image load "${IMAGE_NAME}"

                    minikube image ls |
                        grep "${PROJECT_NAME}"
                '''
            }
        }

        stage('Desplegar en Kubernetes') {
            steps {
                sh '''
                    kubectl apply \
                        -f "k8s/${DEPLOY_ENV}/"

                    kubectl rollout status \
                        deployment/devops-web-deployment \
                        -n "${NAMESPACE}" \
                        --timeout=120s
                '''
            }
        }

        stage('Verificar despliegue') {
            steps {
                sh '''
                    kubectl get deployments \
                        -n "${NAMESPACE}"

                    kubectl get pods \
                        -n "${NAMESPACE}"

                    kubectl get services \
                        -n "${NAMESPACE}"
                '''
            }
        }
    }

    post {
        success {
            echo """
            Pipeline completado correctamente.

            Ambiente: ${params.DEPLOY_ENV}
            Versión: ${env.APP_VERSION}
            Namespace: ${env.NAMESPACE}
            Imagen: ${env.IMAGE_NAME}
            """
        }

        failure {
            echo """
            El pipeline falló.

            Revisa la etapa marcada en rojo en Jenkins.
            """
        }

        always {
            echo 'Ejecución del pipeline finalizada.'
        }
    }
}
