pipeline {
    agent any
    stages {
        stage("Checkout"){
            steps {
                echo 'checking for latest code '
                checkout scm //pulls the current branch 
            }
        }
        stage("Install Dependencies"){
            steps {
                echo 'installing dependencies ...'
                sh '''
                python -m venv venv && \
                source venv/bin/activate && \
                pip install -r services/data_process_service/requirements.txt && \
                pip install -r services/event_generator_service/requirements.txt && \
                pip install -r services/inference_service/requirements.txt'''


            }
        }
    }
}