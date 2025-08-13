pipeline {
	agent any
	stages {
		stage('Checkout') {
			steps { checkout scm }
		}
		stage('Build') {
			steps {
				bat 'mvn -B -DskipTests package'
			}
		}
		stage('Test') {
			steps {
				bat 'mvn -B test'
			}
		}
	}
	post {
		always {
			junit 'target/surefire-reports/*.xml'
		}
	}
} 