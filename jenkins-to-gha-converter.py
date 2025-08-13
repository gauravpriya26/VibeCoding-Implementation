#!/usr/bin/env python3
"""
Jenkins to GitHub Actions Converter
====================================

This script automatically converts Jenkins pipelines to GitHub Actions workflows.
It analyzes Jenkinsfiles and generates equivalent GitHub Actions YAML configurations.

Features:
- Converts Jenkins declarative pipelines to GHA workflows
- Handles Maven/Java projects
- Supports common Jenkins stages (Build, Test, Deploy)
- Generates security scanning workflows
- Creates appropriate caching strategies
- Handles matrix builds for multiple Java versions

Usage:
    python jenkins-to-gha-converter.py --input /path/to/jenkins/repo --output /path/to/gha/repo
"""

import os
import re
import json
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def dict_to_yaml(data, indent=0):
    """Convert dictionary to YAML format without external dependencies"""
    yaml_lines = []
    indent_str = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                yaml_lines.append(f"{indent_str}{key}:")
                yaml_lines.extend(dict_to_yaml(value, indent + 1))
            elif isinstance(value, list):
                yaml_lines.append(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        yaml_lines.append(f"{indent_str}- ")
                        # Add the dict items with proper indentation
                        item_lines = dict_to_yaml(item, indent + 1)
                        if item_lines:
                            # First line gets the "- " prefix, others get normal indent
                            yaml_lines[-1] += item_lines[0].strip()
                            yaml_lines.extend(item_lines[1:])
                    else:
                        yaml_lines.append(f"{indent_str}- {item}")
            elif isinstance(value, bool):
                yaml_lines.append(f"{indent_str}{key}: {str(value).lower()}")
            elif isinstance(value, str) and ('\n' in value):
                yaml_lines.append(f"{indent_str}{key}: |")
                for line in value.split('\n'):
                    yaml_lines.append(f"{indent_str}  {line}")
            else:
                yaml_lines.append(f"{indent_str}{key}: {value}")
    
    return yaml_lines

class JenkinsToGHAConverter:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.workflows_dir = self.output_path / '.github' / 'workflows'
        
        # Default configurations
        self.java_versions = ['17', '21']
        self.default_runner = 'ubuntu-latest'
    
    def convert(self):
        """Main conversion method"""
        logger.info(f"Starting conversion from {self.input_path} to {self.output_path}")
        
        # Create output directory structure
        self._setup_output_directory()
        
        # Find and analyze Jenkinsfiles
        jenkinsfiles = self._find_jenkinsfiles()
        
        if not jenkinsfiles:
            logger.warning("No Jenkinsfiles found in the input directory")
            return
        
        # Convert each Jenkinsfile
        for jenkinsfile in jenkinsfiles:
            self._convert_jenkinsfile(jenkinsfile)
        
        # Copy source code (excluding Jenkins-specific files)
        self._copy_source_code()
        
        logger.info("Conversion completed successfully!")
    
    def _setup_output_directory(self):
        """Create the output directory structure"""
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created workflows directory: {self.workflows_dir}")
    
    def _find_jenkinsfiles(self) -> List[Path]:
        """Find all Jenkinsfiles in the input directory"""
        jenkinsfiles = []
        
        # Common Jenkinsfile names
        jenkinsfile_names = ['Jenkinsfile', 'jenkinsfile', 'Jenkinsfile.groovy']
        
        for root, dirs, files in os.walk(self.input_path):
            # Skip .git directories
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            
            for file in files:
                if file in jenkinsfile_names:
                    jenkinsfiles.append(Path(root) / file)
        
        logger.info(f"Found {len(jenkinsfiles)} Jenkinsfile(s): {[str(jf) for jf in jenkinsfiles]}")
        return jenkinsfiles
    
    def _convert_jenkinsfile(self, jenkinsfile: Path):
        """Convert a single Jenkinsfile to GitHub Actions workflow"""
        logger.info(f"Converting {jenkinsfile}")
        
        try:
            with open(jenkinsfile, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Jenkins pipeline
            pipeline_info = self._parse_jenkinsfile(content, jenkinsfile)
            
            # Generate GitHub Actions workflow
            workflow = self._generate_gha_workflow(pipeline_info)
            
            # Determine workflow filename
            relative_path = jenkinsfile.relative_to(self.input_path)
            workflow_name = self._generate_workflow_name(relative_path)
            
            # Write workflow file
            workflow_file = self.workflows_dir / f"{workflow_name}.yml"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                yaml_content = dict_to_yaml(workflow)
                f.write('\n'.join(yaml_content) + '\n')
            
            logger.info(f"Generated workflow: {workflow_file}")
            
        except Exception as e:
            logger.error(f"Error converting {jenkinsfile}: {str(e)}")
    
    def _parse_jenkinsfile(self, content: str, jenkinsfile: Path) -> Dict:
        """Parse Jenkinsfile content and extract relevant information"""
        pipeline_info = {
            'stages': [],
            'tools': [],
            'triggers': [],
            'project_type': 'generic',
            'working_directory': None
        }
        
        # Detect project type
        project_dir = jenkinsfile.parent
        if (project_dir / 'pom.xml').exists():
            pipeline_info['project_type'] = 'maven'
            pipeline_info['working_directory'] = str(project_dir.relative_to(self.input_path))
        elif (project_dir / 'build.gradle').exists() or (project_dir / 'build.gradle.kts').exists():
            pipeline_info['project_type'] = 'gradle'
            pipeline_info['working_directory'] = str(project_dir.relative_to(self.input_path))
        elif (project_dir / 'package.json').exists():
            pipeline_info['project_type'] = 'node'
            pipeline_info['working_directory'] = str(project_dir.relative_to(self.input_path))
        
        # Extract stages
        stage_pattern = r'stage\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        stages = re.findall(stage_pattern, content, re.IGNORECASE)
        
        for stage in stages:
            stage_info = {
                'name': stage,
                'type': self._classify_stage(stage.lower()),
                'commands': self._extract_stage_commands(content, stage)
            }
            pipeline_info['stages'].append(stage_info)
        
        # Extract tools (Java version, etc.)
        if 'jdk' in content.lower() or 'java' in content.lower():
            pipeline_info['tools'].append('java')
        
        return pipeline_info
    
    def _classify_stage(self, stage_name: str) -> str:
        """Classify a stage based on its name"""
        build_keywords = ['build', 'compile', 'package']
        test_keywords = ['test', 'unit', 'integration']
        deploy_keywords = ['deploy', 'deliver', 'publish', 'release']
        security_keywords = ['security', 'scan', 'vulnerability', 'audit']
        
        if any(keyword in stage_name for keyword in build_keywords):
            return 'build'
        elif any(keyword in stage_name for keyword in test_keywords):
            return 'test'
        elif any(keyword in stage_name for keyword in deploy_keywords):
            return 'deliver'
        elif any(keyword in stage_name for keyword in security_keywords):
            return 'security'
        else:
            return 'build'  # Default to build
    
    def _extract_stage_commands(self, content: str, stage_name: str) -> List[str]:
        """Extract commands from a specific stage"""
        commands = []
        
        # Simple regex to find sh commands in the stage
        stage_pattern = rf'stage\s*\(\s*[\'"]({re.escape(stage_name)})[\'"]\s*\).*?\}}\s*\}}'
        stage_match = re.search(stage_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if stage_match:
            stage_content = stage_match.group(0)
            sh_pattern = r'sh\s+[\'"]([^\'"]+)[\'"]'
            commands = re.findall(sh_pattern, stage_content)
        
        return commands
    
    def _generate_workflow_name(self, relative_path: Path) -> str:
        """Generate a workflow filename based on the Jenkinsfile path"""
        if relative_path.parent.name and relative_path.parent.name != '.':
            return f"ci-{relative_path.parent.name.lower().replace(' ', '-')}"
        else:
            return "ci"
    
    def _generate_gha_workflow(self, pipeline_info: Dict) -> Dict:
        """Generate GitHub Actions workflow from pipeline info"""
        
        workflow = {
            'name': 'CI/CD Pipeline',
            'on': {
                'push': {
                    'branches': ['main', 'develop']
                },
                'pull_request': {
                    'branches': ['main']
                }
            },
            'jobs': {}
        }
        
        # Generate jobs based on stages
        if pipeline_info['project_type'] == 'maven':
            workflow['jobs'].update(self._generate_maven_jobs(pipeline_info))
        else:
            workflow['jobs'].update(self._generate_generic_jobs(pipeline_info))
        
        return workflow
    
    def _generate_maven_jobs(self, pipeline_info: Dict) -> Dict:
        """Generate Maven-specific jobs"""
        jobs = {}
        
        # Main build and test job
        jobs['build-and-test'] = {
            'runs-on': self.default_runner,
            'strategy': {
                'matrix': {
                    'java-version': self.java_versions
                }
            },
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v4'
                },
                {
                    'name': 'Set up JDK ${{ matrix.java-version }}',
                    'uses': 'actions/setup-java@v4',
                    'with': {
                        'java-version': '${{ matrix.java-version }}',
                        'distribution': 'temurin',
                        'cache': 'maven'
                    }
                },
                {
                    'name': 'Cache Maven dependencies',
                    'uses': 'actions/cache@v4',
                    'with': {
                        'path': '~/.m2',
                        'key': '${{ runner.os }}-m2-${{ hashFiles(\'**/pom.xml\') }}',
                        'restore-keys': '${{ runner.os }}-m2'
                    }
                }
            ]
        }
        
        # Add working directory if specified
        working_dir = pipeline_info.get('working_directory')
        if working_dir and working_dir != '.':
            working_directory = f"./{working_dir}"
        else:
            working_directory = None
        
        # Add Maven steps
        maven_steps = [
            {
                'name': 'Validate Maven project',
                'run': 'mvn validate'
            },
            {
                'name': 'Compile project',
                'run': 'mvn compile'
            },
            {
                'name': 'Run tests',
                'run': 'mvn test'
            },
            {
                'name': 'Generate test report',
                'uses': 'dorny/test-reporter@v1',
                'if': 'success() || failure()',
                'with': {
                    'name': 'Maven Tests (JDK ${{ matrix.java-version }})',
                    'path': f'{working_directory + "/" if working_directory else ""}target/surefire-reports/*.xml',
                    'reporter': 'java-junit',
                    'fail-on-error': True
                }
            },
            {
                'name': 'Build package',
                'run': 'mvn -B -DskipTests clean package'
            },
            {
                'name': 'Upload build artifacts',
                'uses': 'actions/upload-artifact@v4',
                'if': f'matrix.java-version == \'{self.java_versions[-1]}\'',
                'with': {
                    'name': 'jar-artifact',
                    'path': f'{working_directory + "/" if working_directory else ""}target/*.jar',
                    'retention-days': 30
                }
            }
        ]
        
        # Add working directory to steps that need it
        if working_directory:
            for step in maven_steps:
                if 'run' in step and step['run'].startswith('mvn'):
                    step['working-directory'] = working_directory
        
        jobs['build-and-test']['steps'].extend(maven_steps)
        
        # Add delivery job if deliver stage exists
        has_deliver_stage = any(stage['type'] == 'deliver' for stage in pipeline_info['stages'])
        if has_deliver_stage:
            jobs['deliver'] = self._create_maven_deliver_job(pipeline_info, working_directory)
        
        # Add security scan job
        jobs['security-scan'] = self._create_security_job(pipeline_info, working_directory)
        
        return jobs
    
    def _create_maven_deliver_job(self, pipeline_info: Dict, working_directory: Optional[str]) -> Dict:
        """Create Maven delivery job"""
        job = {
            'needs': 'build-and-test',
            'runs-on': self.default_runner,
            'if': 'github.ref == \'refs/heads/main\'',
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v4'
                },
                {
                    'name': f'Set up JDK {self.java_versions[-1]}',
                    'uses': 'actions/setup-java@v4',
                    'with': {
                        'java-version': self.java_versions[-1],
                        'distribution': 'temurin',
                        'cache': 'maven'
                    }
                },
                {
                    'name': 'Download build artifacts',
                    'uses': 'actions/download-artifact@v4',
                    'with': {
                        'name': 'jar-artifact',
                        'path': f'{working_directory + "/" if working_directory else ""}target/'
                    }
                },
                {
                    'name': 'Install to local repository',
                    'run': '''echo "Installing Maven-built Java application to local Maven repository"
mvn jar:jar install:install help:evaluate -Dexpression=project.name'''
                },
                {
                    'name': 'Extract project information',
                    'id': 'project-info',
                    'run': '''echo "Extracting project name and version"
NAME=$(mvn -q -DforceStdout help:evaluate -Dexpression=project.name)
VERSION=$(mvn -q -DforceStdout help:evaluate -Dexpression=project.version)
echo "PROJECT_NAME=$NAME" >> $GITHUB_OUTPUT
echo "PROJECT_VERSION=$VERSION" >> $GITHUB_OUTPUT
echo "Project: $NAME"
echo "Version: $VERSION"'''
                },
                {
                    'name': 'Run application',
                    'run': '''echo "Running the Java application"
java -jar target/${{ steps.project-info.outputs.PROJECT_NAME }}-${{ steps.project-info.outputs.PROJECT_VERSION }}.jar'''
                }
            ]
        }
        
        # Add working directory to steps that need it
        if working_directory:
            for step in job['steps']:
                if 'run' in step and ('mvn' in step['run'] or 'java -jar' in step['run']):
                    step['working-directory'] = working_directory
        
        return job
    
    def _create_security_job(self, pipeline_info: Dict, working_directory: Optional[str]) -> Dict:
        """Create security scanning job"""
        job = {
            'runs-on': self.default_runner,
            'needs': 'build-and-test',
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v4'
                },
                {
                    'name': f'Set up JDK {self.java_versions[-1]}',
                    'uses': 'actions/setup-java@v4',
                    'with': {
                        'java-version': self.java_versions[-1],
                        'distribution': 'temurin',
                        'cache': 'maven'
                    }
                },
                {
                    'name': 'Run OWASP Dependency Check',
                    'run': 'mvn org.owasp:dependency-check-maven:check',
                    'continue-on-error': True
                },
                {
                    'name': 'Upload OWASP Dependency Check results',
                    'uses': 'actions/upload-artifact@v4',
                    'if': 'always()',
                    'with': {
                        'name': 'owasp-dependency-check-report',
                        'path': f'{working_directory + "/" if working_directory else ""}target/dependency-check-report.html',
                        'retention-days': 30
                    }
                }
            ]
        }
        
        # Add working directory to Maven steps
        if working_directory:
            for step in job['steps']:
                if 'run' in step and 'mvn' in step['run']:
                    step['working-directory'] = working_directory
        
        return job
    
    def _generate_generic_jobs(self, pipeline_info: Dict) -> Dict:
        """Generate generic jobs for non-Maven projects"""
        jobs = {}
        
        jobs['build-and-test'] = {
            'runs-on': self.default_runner,
            'steps': [
                {
                    'name': 'Checkout code',
                    'uses': 'actions/checkout@v4'
                }
            ]
        }
        
        # Add steps based on detected stages
        for stage in pipeline_info['stages']:
            if stage['commands']:
                for command in stage['commands']:
                    jobs['build-and-test']['steps'].append({
                        'name': f'Run {stage["name"]}',
                        'run': command
                    })
        
        return jobs
    
    def _copy_source_code(self):
        """Copy source code excluding Jenkins-specific files"""
        exclude_patterns = [
            'Jenkinsfile*',
            'jenkins/',
            '.git/',
            '__pycache__/',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        ]
        
        logger.info("Copying source code to output directory...")
        
        for item in self.input_path.iterdir():
            if item.name.startswith('.git'):
                continue
                
            dest_path = self.output_path / item.name
            
            if item.is_file():
                # Skip Jenkins-related files
                if any(pattern.replace('*', '') in item.name for pattern in exclude_patterns if '*' not in pattern):
                    continue
                if any(item.name.startswith(pattern.replace('*', '')) for pattern in exclude_patterns if '*' in pattern):
                    continue
                
                # Copy file
                if not dest_path.exists():
                    shutil.copy2(item, dest_path)
                    logger.debug(f"Copied file: {item} -> {dest_path}")
            
            elif item.is_dir():
                # Skip Jenkins-related directories
                if any(pattern.replace('/', '') == item.name for pattern in exclude_patterns if '/' in pattern):
                    continue
                
                # Copy directory (excluding Jenkins files)
                if not dest_path.exists():
                    shutil.copytree(item, dest_path, ignore=shutil.ignore_patterns(*exclude_patterns))
                    logger.debug(f"Copied directory: {item} -> {dest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Jenkins pipelines to GitHub Actions workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jenkins-to-gha-converter.py --input ./jenkins-repo --output ./gha-repo
  python jenkins-to-gha-converter.py -i /path/to/jenkins/project -o /path/to/gha/project --java-versions 11 17 21
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input directory containing Jenkins project'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for GitHub Actions project'
    )
    
    parser.add_argument(
        '--java-versions',
        nargs='+',
        default=['17', '21'],
        help='Java versions to test against (default: 17 21)'
    )
    
    parser.add_argument(
        '--runner',
        default='ubuntu-latest',
        help='GitHub Actions runner (default: ubuntu-latest)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create converter instance
    converter = JenkinsToGHAConverter(args.input, args.output)
    converter.java_versions = args.java_versions
    converter.default_runner = args.runner
    
    try:
        converter.convert()
        print(f"✅ Conversion completed successfully!")
        print(f"📁 Output directory: {args.output}")
        print(f"🔄 GitHub Actions workflows created in: {args.output}/.github/workflows/")
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
