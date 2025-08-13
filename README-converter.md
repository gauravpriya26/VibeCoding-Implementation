# Jenkins to GitHub Actions Converter

This repository contains automation scripts to convert Jenkins pipelines to GitHub Actions workflows. The tools analyze your Jenkins configuration and generate equivalent GitHub Actions YAML files.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Supported Project Types](#supported-project-types)
- [Generated Workflows](#generated-workflows)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

- **Automatic Conversion**: Converts Jenkins declarative pipelines to GitHub Actions
- **Multi-Language Support**: Handles Maven/Java, Gradle, Node.js projects
- **Security Integration**: Includes OWASP dependency scanning
- **Matrix Builds**: Supports testing against multiple Java versions
- **Artifact Management**: Handles build artifacts and test reports
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Multiple Tools**: Python script, PowerShell script, and batch file

## 📋 Prerequisites

### For Python Version:
- Python 3.7 or higher
- PyYAML library (`pip install pyyaml`)

### For PowerShell Version:
- PowerShell 5.1 or higher (Windows PowerShell or PowerShell Core)

### For Batch File:
- Windows operating system
- Either Python or PowerShell available

## 🚀 Installation

1. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd jenkins-to-gha-converter
   ```

2. **Install Python dependencies** (if using Python version):
   ```bash
   pip install pyyaml
   ```

3. **Make scripts executable** (Linux/macOS):
   ```bash
   chmod +x jenkins-to-gha-converter.py
   ```

## 💻 Usage

### Option 1: Using the Batch File (Windows - Easiest)

```batch
convert-jenkins-to-gha.bat
```

Or with parameters:
```batch
convert-jenkins-to-gha.bat "C:\path\to\jenkins\repo" "C:\path\to\output\repo"
```

### Option 2: Using Python Script

```bash
python jenkins-to-gha-converter.py --input /path/to/jenkins/repo --output /path/to/gha/repo
```

#### Python Script Options:
- `--input, -i`: Input directory containing Jenkins project (required)
- `--output, -o`: Output directory for GitHub Actions project (required)
- `--java-versions`: Java versions to test against (default: 17 21)
- `--runner`: GitHub Actions runner (default: ubuntu-latest)
- `--verbose, -v`: Enable verbose logging

#### Examples:
```bash
# Basic conversion
python jenkins-to-gha-converter.py -i ./jenkins-project -o ./gha-project

# With custom Java versions
python jenkins-to-gha-converter.py -i ./jenkins-project -o ./gha-project --java-versions 11 17 21

# With verbose output
python jenkins-to-gha-converter.py -i ./jenkins-project -o ./gha-project --verbose
```

### Option 3: Using PowerShell Script

```powershell
.\Convert-JenkinsToGHA.ps1 -InputPath "C:\path\to\jenkins\repo" -OutputPath "C:\path\to\gha\repo"
```

#### PowerShell Script Parameters:
- `-InputPath`: Input directory containing Jenkins project (required)
- `-OutputPath`: Output directory for GitHub Actions project (required)
- `-JavaVersions`: Java versions to test against (default: @("17", "21"))
- `-Runner`: GitHub Actions runner (default: "ubuntu-latest")
- `-Verbose`: Enable verbose logging

#### Examples:
```powershell
# Basic conversion
.\Convert-JenkinsToGHA.ps1 -InputPath ".\jenkins-project" -OutputPath ".\gha-project"

# With custom Java versions
.\Convert-JenkinsToGHA.ps1 -InputPath ".\jenkins-project" -OutputPath ".\gha-project" -JavaVersions @("11", "17", "21")

# With verbose output
.\Convert-JenkinsToGHA.ps1 -InputPath ".\jenkins-project" -OutputPath ".\gha-project" -Verbose
```

## 📁 Examples

### Converting the Sample Java Project

This repository includes a sample Java Maven project with Jenkins configuration. Here's how to convert it:

```bash
# Using Python
python jenkins-to-gha-converter.py --input ./simple-java-maven-app --output ./converted-project

# Using PowerShell
.\Convert-JenkinsToGHA.ps1 -InputPath ".\simple-java-maven-app" -OutputPath ".\converted-project"

# Using Batch File
convert-jenkins-to-gha.bat ".\simple-java-maven-app" ".\converted-project"
```

### Input Structure (Jenkins):
```
simple-java-maven-app/
├── Jenkinsfile
├── pom.xml
├── jenkins/
│   └── scripts/
│       └── deliver.sh
└── src/
    ├── main/java/...
    └── test/java/...
```

### Output Structure (GitHub Actions):
```
converted-project/
├── .github/
│   └── workflows/
│       └── ci-simple-java-maven-app.yml
├── pom.xml
└── src/
    ├── main/java/...
    └── test/java/...
```

## 🔍 Supported Project Types

### ✅ Fully Supported
- **Maven Java Projects**: Complete conversion with build, test, and delivery stages
- **Multi-module Maven Projects**: Handles complex project structures

### 🚧 Partially Supported
- **Gradle Projects**: Basic conversion (in development)
- **Node.js Projects**: Basic conversion (in development)

### 📝 Planned Support
- **Docker-based Projects**
- **Multi-language Projects**
- **Custom Jenkins Plugins**

## 🔄 Generated Workflows

The converter generates comprehensive GitHub Actions workflows with the following features:

### 1. **Build and Test Job** (`build-and-test`)
- Checkout code
- Set up Java (multiple versions via matrix)
- Cache Maven dependencies
- Validate, compile, and test the project
- Generate test reports
- Upload build artifacts

### 2. **Delivery Job** (`deliver`)
- Runs only on main branch
- Downloads build artifacts
- Installs to local Maven repository
- Extracts project information
- Runs the application

### 3. **Security Scan Job** (`security-scan`)
- OWASP dependency check
- Uploads security reports
- Runs in parallel with other jobs

### Sample Generated Workflow:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        java-version: [17, 21]
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Set up JDK ${{ matrix.java-version }}
      uses: actions/setup-java@v4
      with:
        java-version: ${{ matrix.java-version }}
        distribution: 'temurin'
        cache: maven
    # ... additional steps
```

## ⚙️ Customization

### Modifying Java Versions
```bash
# Python
python jenkins-to-gha-converter.py --java-versions 8 11 17 21

# PowerShell
.\Convert-JenkinsToGHA.ps1 -JavaVersions @("8", "11", "17", "21")
```

### Changing the Runner
```bash
# Python
python jenkins-to-gha-converter.py --runner windows-latest

# PowerShell
.\Convert-JenkinsToGHA.ps1 -Runner "windows-latest"
```

### Adding Custom Steps
After conversion, you can manually edit the generated workflows to add:
- Additional testing frameworks
- Code quality checks (SonarQube, CodeQL)
- Deployment steps
- Notification steps

## 🔧 Troubleshooting

### Common Issues

1. **"No Jenkinsfiles found"**
   - Ensure your input directory contains a `Jenkinsfile`
   - Check that the file is named correctly (case-sensitive on Linux/macOS)

2. **"Permission denied" (Linux/macOS)**
   ```bash
   chmod +x jenkins-to-gha-converter.py
   ```

3. **"PowerShell execution policy" (Windows)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Python import errors**
   ```bash
   pip install pyyaml
   ```

### Debugging

Enable verbose logging to see detailed conversion steps:
```bash
# Python
python jenkins-to-gha-converter.py --verbose

# PowerShell
.\Convert-JenkinsToGHA.ps1 -Verbose
```

### Manual Adjustments

After conversion, you may need to manually adjust:
- Environment variables
- Secrets and credentials
- Custom Jenkins plugins behavior
- Specific deployment configurations

## 📝 Post-Conversion Steps

1. **Review Generated Workflows**:
   - Check `.github/workflows/` directory
   - Verify job dependencies and conditions
   - Adjust runner types if needed

2. **Set Up Repository Secrets** (if needed):
   - Go to GitHub repository Settings > Secrets and variables > Actions
   - Add any required secrets (API keys, credentials, etc.)

3. **Test the Workflows**:
   - Commit and push to a branch
   - Create a pull request to trigger the workflow
   - Monitor the Actions tab for results

4. **Optimize Performance**:
   - Review caching strategies
   - Adjust parallel job execution
   - Consider runner specifications

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Use GitHub Issues to report bugs or request features
2. **Submit Pull Requests**: Fork the repository and submit PRs for improvements
3. **Add Support**: Help add support for more project types and Jenkins plugins
4. **Documentation**: Improve documentation and examples

### Development Setup
```bash
git clone <repository-url>
cd jenkins-to-gha-converter
pip install -r requirements.txt  # if requirements.txt exists
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- GitHub Actions documentation and community
- Jenkins community for pipeline patterns
- Contributors and testers

---

## 📞 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing [GitHub Issues](../../issues)
3. Create a new issue with detailed information about your problem
4. Include your Jenkins configuration and error messages

---

**Happy Converting! 🚀**
