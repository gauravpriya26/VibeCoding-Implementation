# Jenkins to GitHub Actions Automation Script

## 🎯 Purpose

This automation script converts Jenkins repositories to GitHub Actions workflows automatically. It analyzes your Jenkins pipeline configuration and generates equivalent GitHub Actions YAML files.

## 📋 What You Have

1. **`jenkins-to-gha-converter.py`** - Main conversion script (Python)
2. **`Convert-JenkinsToGHA.ps1`** - PowerShell version (Windows)
3. **`convert-jenkins-to-gha.bat`** - Batch file wrapper (Windows)
4. **`demo-converter.py`** - Interactive demo script

## 🚀 Quick Start

### Method 1: Interactive Demo (Easiest)
```bash
python demo-converter.py
```
This will guide you through the conversion process step by step.

### Method 2: Direct Command Line
```bash
python jenkins-to-gha-converter.py --input "./simple-java-maven-app" --output "./converted-project" --verbose
```

### Method 3: PowerShell (Windows)
```powershell
.\Convert-JenkinsToGHA.ps1 -InputPath ".\simple-java-maven-app" -OutputPath ".\converted-project" -Verbose
```

### Method 4: Batch File (Windows)
```batch
convert-jenkins-to-gha.bat ".\simple-java-maven-app" ".\converted-project"
```

## 📁 Example: Converting Your Java Maven Project

Your workspace has a sample project: `simple-java-maven-app`

**Input Structure (Jenkins):**
```
simple-java-maven-app/
├── Jenkinsfile                 # Jenkins pipeline
├── pom.xml                     # Maven configuration
├── jenkins/
│   ├── Jenkinsfile            # Additional Jenkins config
│   └── scripts/
│       └── deliver.sh         # Delivery script
└── src/
    ├── main/java/...          # Source code
    └── test/java/...          # Tests
```

**Output Structure (GitHub Actions):**
```
converted-project/
├── .github/
│   └── workflows/
│       ├── ci.yml             # Main CI/CD workflow
│       └── ci-jenkins.yml     # Additional workflow
├── pom.xml                    # Maven configuration (copied)
├── LICENSE.txt                # License (copied)
├── README.md                  # Documentation (copied)
└── src/                       # Source code (copied)
    ├── main/java/...
    └── test/java/...
```

## 🎯 What the Script Does

### 1. **Analyzes Jenkins Configuration**
- Finds all Jenkinsfiles in your repository
- Extracts stages (Build, Test, Deploy, etc.)
- Detects project type (Maven, Gradle, Node.js)
- Identifies working directories

### 2. **Generates GitHub Actions Workflows**
- **Build & Test Job**: Compiles, tests, and packages your application
- **Delivery Job**: Deploys to production (main branch only)
- **Security Scan Job**: Runs OWASP dependency checks
- **Matrix Strategy**: Tests against multiple Java versions (17, 21)

### 3. **Copies Source Code**
- Copies all source files and configurations
- Excludes Jenkins-specific files (Jenkinsfile, jenkins/ directory)
- Preserves directory structure

## 🔧 Customization Options

### Java Versions
```bash
python jenkins-to-gha-converter.py --input "./my-project" --output "./gha-project" --java-versions 8 11 17 21
```

### GitHub Runner
```bash
python jenkins-to-gha-converter.py --input "./my-project" --output "./gha-project" --runner windows-latest
```

### Verbose Output
```bash
python jenkins-to-gha-converter.py --input "./my-project" --output "./gha-project" --verbose
```

## 📊 Generated Workflow Features

### 1. **Multi-Version Testing**
```yaml
strategy:
  matrix:
    java-version: [17, 21]
```

### 2. **Caching**
```yaml
- name: Cache Maven dependencies
  uses: actions/cache@v4
  with:
    path: ~/.m2
    key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
```

### 3. **Test Reporting**
```yaml
- name: Generate test report
  uses: dorny/test-reporter@v1
  with:
    name: Maven Tests (JDK ${{ matrix.java-version }})
    path: target/surefire-reports/*.xml
    reporter: java-junit
```

### 4. **Security Scanning**
```yaml
- name: Run OWASP Dependency Check
  run: mvn org.owasp:dependency-check-maven:check
```

### 5. **Artifact Management**
```yaml
- name: Upload build artifacts
  uses: actions/upload-artifact@v4
  with:
    name: jar-artifact
    path: target/*.jar
```

## 📝 Step-by-Step Usage

### Step 1: Run the Conversion
```bash
# Using the interactive demo
python demo-converter.py

# Or directly
python jenkins-to-gha-converter.py --input "./simple-java-maven-app" --output "./my-gha-project" --verbose
```

### Step 2: Review Generated Files
```bash
# Check the generated workflows
cat ./my-gha-project/.github/workflows/ci.yml

# Review the project structure
ls -la ./my-gha-project/
```

### Step 3: Deploy to GitHub
```bash
# Copy to your GitHub repository
cp -r ./my-gha-project/* /path/to/your/github/repo/

# Or create a new repository
cd ./my-gha-project
git init
git add .
git commit -m "Convert from Jenkins to GitHub Actions"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### Step 4: Test the Workflow
1. Create a pull request or push to main branch
2. Check the "Actions" tab in your GitHub repository
3. Monitor the workflow execution

## 🎨 Supported Project Types

### ✅ **Fully Supported**
- **Maven Java Projects**: Complete conversion with all features
- **Multi-module Maven**: Handles complex project structures

### 🚧 **Partially Supported**
- **Gradle Projects**: Basic conversion
- **Node.js Projects**: Basic conversion

### 📅 **Planned**
- Docker-based projects
- Multi-language projects
- Custom Jenkins plugins

## 🛠️ Troubleshooting

### Common Issues

1. **"No Jenkinsfiles found"**
   - Ensure your input directory contains a `Jenkinsfile`
   - Check file naming (case-sensitive on Linux/macOS)

2. **Permission errors**
   ```bash
   chmod +x jenkins-to-gha-converter.py
   ```

3. **Python not found**
   - Install Python 3.7+
   - Use the PowerShell or batch versions instead

### Getting Help

1. Run with `--verbose` flag for detailed logging
2. Check the generated workflows for syntax
3. Review the Jenkins pipeline stages to ensure proper conversion

## 🎯 Example Output

When you run the converter on the sample project, you'll get:

```
2025-07-31 15:02:41,254 - INFO - Starting conversion from simple-java-maven-app to converted-project
2025-07-31 15:02:41,273 - INFO - Created workflows directory: converted-project\.github\workflows
2025-07-31 15:02:41,437 - INFO - Found 2 Jenkinsfile(s): ['simple-java-maven-app\Jenkinsfile', 'simple-java-maven-app\jenkins\Jenkinsfile']
2025-07-31 15:02:41,485 - INFO - Generated workflow: converted-project\.github\workflows\ci.yml
2025-07-31 15:02:41,537 - INFO - Generated workflow: converted-project\.github\workflows\ci-jenkins.yml
2025-07-31 15:02:41,924 - INFO - Conversion completed successfully!
✅ Conversion completed successfully!
📁 Output directory: ./converted-project
🔄 GitHub Actions workflows created in: ./converted-project/.github/workflows/
```

## 🚀 Ready to Convert?

Use any of these commands to start converting your Jenkins repositories:

```bash
# Interactive (recommended for first time)
python demo-converter.py

# Direct conversion
python jenkins-to-gha-converter.py --input "./your-jenkins-project" --output "./your-gha-project" --verbose

# PowerShell (Windows)
.\Convert-JenkinsToGHA.ps1 -InputPath ".\your-jenkins-project" -OutputPath ".\your-gha-project" -Verbose
```

The automation script will handle all the complex conversion logic for you! 🎉
