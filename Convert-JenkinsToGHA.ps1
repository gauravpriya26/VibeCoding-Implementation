# Jenkins to GitHub Actions Converter - PowerShell Version
# =====================================================
# 
# This PowerShell script converts Jenkins pipelines to GitHub Actions workflows.
# It's designed to work well on Windows systems.
#
# Usage:
#   .\Convert-JenkinsToGHA.ps1 -InputPath "C:\path\to\jenkins\repo" -OutputPath "C:\path\to\gha\repo"

param(
    [Parameter(Mandatory=$true)]
    [string]$InputPath,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [string[]]$JavaVersions = @("17", "21"),
    
    [string]$Runner = "ubuntu-latest",
    
    [switch]$Verbose
)

# Set up logging
if ($Verbose) {
    $VerbosePreference = "Continue"
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Find-Jenkinsfiles {
    param([string]$Path)
    
    $jenkinsfileNames = @("Jenkinsfile", "jenkinsfile", "Jenkinsfile.groovy")
    $jenkinsfiles = @()
    
    Get-ChildItem -Path $Path -Recurse -File | Where-Object {
        $_.Name -in $jenkinsfileNames -and $_.DirectoryName -notlike "*\.git*"
    } | ForEach-Object {
        $jenkinsfiles += $_.FullName
    }
    
    return $jenkinsfiles
}

function Get-ProjectType {
    param([string]$ProjectDir)
    
    if (Test-Path (Join-Path $ProjectDir "pom.xml")) {
        return "maven"
    } elseif (Test-Path (Join-Path $ProjectDir "build.gradle")) {
        return "gradle"
    } elseif (Test-Path (Join-Path $ProjectDir "package.json")) {
        return "node"
    } else {
        return "generic"
    }
}

function Parse-Jenkinsfile {
    param([string]$FilePath)
    
    $content = Get-Content -Path $FilePath -Raw
    $projectDir = Split-Path -Parent $FilePath
    
    $pipelineInfo = @{
        stages = @()
        projectType = Get-ProjectType -ProjectDir $projectDir
        workingDirectory = $null
    }
    
    # Calculate relative working directory
    $relativePath = [System.IO.Path]::GetRelativePath($InputPath, $projectDir)
    if ($relativePath -ne ".") {
        $pipelineInfo.workingDirectory = $relativePath -replace "\\", "/"
    }
    
    # Extract stages using regex
    $stagePattern = "stage\s*\(\s*[`"']([^`"']+)[`"']\s*\)"
    $matches = [regex]::Matches($content, $stagePattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    foreach ($match in $matches) {
        $stageName = $match.Groups[1].Value
        $stageType = Get-StageType -StageName $stageName.ToLower()
        
        $pipelineInfo.stages += @{
            name = $stageName
            type = $stageType
        }
    }
    
    return $pipelineInfo
}

function Get-StageType {
    param([string]$StageName)
    
    $buildKeywords = @("build", "compile", "package")
    $testKeywords = @("test", "unit", "integration")
    $deployKeywords = @("deploy", "deliver", "publish", "release")
    $securityKeywords = @("security", "scan", "vulnerability", "audit")
    
    if ($buildKeywords | Where-Object { $StageName -like "*$_*" }) {
        return "build"
    } elseif ($testKeywords | Where-Object { $StageName -like "*$_*" }) {
        return "test"
    } elseif ($deployKeywords | Where-Object { $StageName -like "*$_*" }) {
        return "deliver"
    } elseif ($securityKeywords | Where-Object { $StageName -like "*$_*" }) {
        return "security"
    } else {
        return "build"
    }
}

function Create-MavenWorkflow {
    param([hashtable]$PipelineInfo)
    
    $workingDir = $PipelineInfo.workingDirectory
    $workingDirPath = if ($workingDir) { "./$workingDir" } else { $null }
    
    $workflow = @{
        name = "CI/CD Pipeline"
        on = @{
            push = @{
                branches = @("main", "develop")
            }
            pull_request = @{
                branches = @("main")
            }
        }
        jobs = @{
            "build-and-test" = @{
                "runs-on" = $Runner
                strategy = @{
                    matrix = @{
                        "java-version" = $JavaVersions
                    }
                }
                steps = @(
                    @{
                        name = "Checkout code"
                        uses = "actions/checkout@v4"
                    },
                    @{
                        name = "Set up JDK `${{ matrix.java-version }}"
                        uses = "actions/setup-java@v4"
                        with = @{
                            "java-version" = "`${{ matrix.java-version }}"
                            distribution = "temurin"
                            cache = "maven"
                        }
                    },
                    @{
                        name = "Cache Maven dependencies"
                        uses = "actions/cache@v4"
                        with = @{
                            path = "~/.m2"
                            key = "`${{ runner.os }}-m2-`${{ hashFiles('**/pom.xml') }}"
                            "restore-keys" = "`${{ runner.os }}-m2"
                        }
                    }
                )
            }
        }
    }
    
    # Add Maven build steps
    $mavenSteps = @(
        @{
            name = "Validate Maven project"
            run = "mvn validate"
        },
        @{
            name = "Compile project"
            run = "mvn compile"
        },
        @{
            name = "Run tests"
            run = "mvn test"
        },
        @{
            name = "Generate test report"
            uses = "dorny/test-reporter@v1"
            if = "success() || failure()"
            with = @{
                name = "Maven Tests (JDK `${{ matrix.java-version }})"
                path = if ($workingDirPath) { "$workingDirPath/target/surefire-reports/*.xml" } else { "target/surefire-reports/*.xml" }
                reporter = "java-junit"
                "fail-on-error" = $true
            }
        },
        @{
            name = "Build package"
            run = "mvn -B -DskipTests clean package"
        },
        @{
            name = "Upload build artifacts"
            uses = "actions/upload-artifact@v4"
            if = "matrix.java-version == '$($JavaVersions[-1])'"
            with = @{
                name = "jar-artifact"
                path = if ($workingDirPath) { "$workingDirPath/target/*.jar" } else { "target/*.jar" }
                "retention-days" = 30
            }
        }
    )
    
    # Add working directory to Maven steps
    if ($workingDirPath) {
        foreach ($step in $mavenSteps) {
            if ($step.ContainsKey("run") -and $step.run -like "mvn*") {
                $step."working-directory" = $workingDirPath
            }
        }
    }
    
    $workflow.jobs."build-and-test".steps += $mavenSteps
    
    # Add delivery job if needed
    $hasDeliverStage = $PipelineInfo.stages | Where-Object { $_.type -eq "deliver" }
    if ($hasDeliverStage) {
        $workflow.jobs.deliver = Create-DeliveryJob -WorkingDirPath $workingDirPath
    }
    
    # Add security scan job
    $workflow.jobs."security-scan" = Create-SecurityJob -WorkingDirPath $workingDirPath
    
    return $workflow
}

function Create-DeliveryJob {
    param([string]$WorkingDirPath)
    
    $job = @{
        needs = "build-and-test"
        "runs-on" = $Runner
        if = "github.ref == 'refs/heads/main'"
        steps = @(
            @{
                name = "Checkout code"
                uses = "actions/checkout@v4"
            },
            @{
                name = "Set up JDK $($JavaVersions[-1])"
                uses = "actions/setup-java@v4"
                with = @{
                    "java-version" = $JavaVersions[-1]
                    distribution = "temurin"
                    cache = "maven"
                }
            },
            @{
                name = "Download build artifacts"
                uses = "actions/download-artifact@v4"
                with = @{
                    name = "jar-artifact"
                    path = if ($WorkingDirPath) { "$WorkingDirPath/target/" } else { "target/" }
                }
            },
            @{
                name = "Install to local repository"
                run = @"
echo "Installing Maven-built Java application to local Maven repository"
mvn jar:jar install:install help:evaluate -Dexpression=project.name
"@
            },
            @{
                name = "Extract project information"
                id = "project-info"
                run = @"
echo "Extracting project name and version"
`$NAME = mvn -q -DforceStdout help:evaluate -Dexpression=project.name
`$VERSION = mvn -q -DforceStdout help:evaluate -Dexpression=project.version
echo "PROJECT_NAME=`$NAME" >> `$env:GITHUB_OUTPUT
echo "PROJECT_VERSION=`$VERSION" >> `$env:GITHUB_OUTPUT
echo "Project: `$NAME"
echo "Version: `$VERSION"
"@
            },
            @{
                name = "Run application"
                run = @"
echo "Running the Java application"
java -jar target/`${{ steps.project-info.outputs.PROJECT_NAME }}-`${{ steps.project-info.outputs.PROJECT_VERSION }}.jar
"@
            }
        )
    }
    
    # Add working directory to relevant steps
    if ($WorkingDirPath) {
        foreach ($step in $job.steps) {
            if ($step.ContainsKey("run") -and ($step.run -like "*mvn*" -or $step.run -like "*java -jar*")) {
                $step."working-directory" = $WorkingDirPath
            }
        }
    }
    
    return $job
}

function Create-SecurityJob {
    param([string]$WorkingDirPath)
    
    $job = @{
        "runs-on" = $Runner
        needs = "build-and-test"
        steps = @(
            @{
                name = "Checkout code"
                uses = "actions/checkout@v4"
            },
            @{
                name = "Set up JDK $($JavaVersions[-1])"
                uses = "actions/setup-java@v4"
                with = @{
                    "java-version" = $JavaVersions[-1]
                    distribution = "temurin"
                    cache = "maven"
                }
            },
            @{
                name = "Run OWASP Dependency Check"
                run = "mvn org.owasp:dependency-check-maven:check"
                "continue-on-error" = $true
            },
            @{
                name = "Upload OWASP Dependency Check results"
                uses = "actions/upload-artifact@v4"
                if = "always()"
                with = @{
                    name = "owasp-dependency-check-report"
                    path = if ($WorkingDirPath) { "$WorkingDirPath/target/dependency-check-report.html" } else { "target/dependency-check-report.html" }
                    "retention-days" = 30
                }
            }
        )
    }
    
    # Add working directory to Maven steps
    if ($WorkingDirPath) {
        foreach ($step in $job.steps) {
            if ($step.ContainsKey("run") -and $step.run -like "mvn*") {
                $step."working-directory" = $WorkingDirPath
            }
        }
    }
    
    return $job
}

function Convert-ToYaml {
    param([hashtable]$Object, [int]$Indent = 0)
    
    $yaml = ""
    $indentStr = "  " * $Indent
    
    foreach ($key in $Object.Keys) {
        $value = $Object[$key]
        
        if ($value -is [hashtable]) {
            $yaml += "$indentStr$key`:`n"
            $yaml += Convert-ToYaml -Object $value -Indent ($Indent + 1)
        } elseif ($value -is [array]) {
            $yaml += "$indentStr$key`:`n"
            foreach ($item in $value) {
                if ($item -is [hashtable]) {
                    $yaml += "$indentStr- `n"
                    $yaml += Convert-ToYaml -Object $item -Indent ($Indent + 1)
                } else {
                    $yaml += "$indentStr- $item`n"
                }
            }
        } elseif ($value -is [bool]) {
            $yaml += "$indentStr$key`: $($value.ToString().ToLower())`n"
        } elseif ($value -is [string] -and $value.Contains("`n")) {
            $yaml += "$indentStr$key`: |`n"
            $lines = $value -split "`n"
            foreach ($line in $lines) {
                $yaml += "$indentStr  $line`n"
            }
        } else {
            $yaml += "$indentStr$key`: $value`n"
        }
    }
    
    return $yaml
}

function Copy-SourceCode {
    param([string]$SourcePath, [string]$DestPath)
    
    $excludePatterns = @(
        "Jenkinsfile*",
        "jenkins",
        ".git",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "Thumbs.db"
    )
    
    Write-Log "Copying source code to output directory..."
    
    Get-ChildItem -Path $SourcePath -Recurse | Where-Object {
        $item = $_
        $shouldExclude = $false
        
        foreach ($pattern in $excludePatterns) {
            if ($pattern -like "*`**") {
                $cleanPattern = $pattern -replace "\*", ""
                if ($item.Name -like "*$cleanPattern*") {
                    $shouldExclude = $true
                    break
                }
            } elseif ($item.Name -eq $pattern -or $item.Name -like "$pattern*") {
                $shouldExclude = $true
                break
            }
        }
        
        -not $shouldExclude
    } | ForEach-Object {
        $relativePath = [System.IO.Path]::GetRelativePath($SourcePath, $_.FullName)
        $destFilePath = Join-Path $DestPath $relativePath
        $destDir = Split-Path -Parent $destFilePath
        
        if (-not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }
        
        if ($_.PSIsContainer) {
            if (-not (Test-Path $destFilePath)) {
                New-Item -Path $destFilePath -ItemType Directory -Force | Out-Null
            }
        } else {
            if (-not (Test-Path $destFilePath)) {
                Copy-Item -Path $_.FullName -Destination $destFilePath -Force
                Write-Verbose "Copied: $($_.FullName) -> $destFilePath"
            }
        }
    }
}

# Main execution
try {
    Write-Log "Starting Jenkins to GitHub Actions conversion"
    Write-Log "Input Path: $InputPath"
    Write-Log "Output Path: $OutputPath"
    
    # Validate input path
    if (-not (Test-Path $InputPath)) {
        throw "Input path does not exist: $InputPath"
    }
    
    # Create output directory
    if (-not (Test-Path $OutputPath)) {
        New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
    }
    
    $workflowsDir = Join-Path $OutputPath ".github\workflows"
    if (-not (Test-Path $workflowsDir)) {
        New-Item -Path $workflowsDir -ItemType Directory -Force | Out-Null
    }
    
    Write-Log "Created workflows directory: $workflowsDir"
    
    # Find Jenkinsfiles
    $jenkinsfiles = Find-Jenkinsfiles -Path $InputPath
    Write-Log "Found $($jenkinsfiles.Count) Jenkinsfile(s)"
    
    if ($jenkinsfiles.Count -eq 0) {
        Write-Log "No Jenkinsfiles found in the input directory" -Level "WARNING"
        return
    }
    
    # Convert each Jenkinsfile
    foreach ($jenkinsfile in $jenkinsfiles) {
        Write-Log "Converting: $jenkinsfile"
        
        try {
            $pipelineInfo = Parse-Jenkinsfile -FilePath $jenkinsfile
            
            # Generate workflow based on project type
            if ($pipelineInfo.projectType -eq "maven") {
                $workflow = Create-MavenWorkflow -PipelineInfo $pipelineInfo
            } else {
                Write-Log "Generic project type not fully implemented yet" -Level "WARNING"
                continue
            }
            
            # Generate workflow filename
            $relativePath = [System.IO.Path]::GetRelativePath($InputPath, $jenkinsfile)
            $projectName = Split-Path -Parent $relativePath | Split-Path -Leaf
            if ([string]::IsNullOrEmpty($projectName) -or $projectName -eq ".") {
                $workflowName = "ci"
            } else {
                $workflowName = "ci-$($projectName.ToLower() -replace ' ', '-')"
            }
            
            # Convert to YAML and save
            $yamlContent = Convert-ToYaml -Object $workflow
            $workflowFile = Join-Path $workflowsDir "$workflowName.yml"
            $yamlContent | Out-File -FilePath $workflowFile -Encoding UTF8
            
            Write-Log "Generated workflow: $workflowFile"
            
        } catch {
            Write-Log "Error converting $jenkinsfile`: $($_.Exception.Message)" -Level "ERROR"
        }
    }
    
    # Copy source code
    Copy-SourceCode -SourcePath $InputPath -DestPath $OutputPath
    
    Write-Log "✅ Conversion completed successfully!" -Level "SUCCESS"
    Write-Log "📁 Output directory: $OutputPath"
    Write-Log "🔄 GitHub Actions workflows created in: $workflowsDir"
    
} catch {
    Write-Log "❌ Conversion failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
