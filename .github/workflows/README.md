# GitHub Actions Configuration

## Environment Variables
# Add these secrets in your GitHub repository settings:
# - SONAR_TOKEN (for SonarQube integration)
# - MAVEN_CENTRAL_TOKEN (for Maven Central deployment)
# - DOCKER_HUB_TOKEN (for Docker image publishing)

## Branch Protection Rules
# Configure these branch protection rules in GitHub:
# - Require status checks to pass before merging
# - Require branches to be up to date before merging
# - Require pull request reviews before merging
# - Dismiss stale reviews when new commits are pushed
# - Require review from code owners

## Workflow Features

### Caching Strategy
- Maven dependencies are cached using `actions/cache@v4`
- Cache key includes `pom.xml` hash for automatic invalidation
- Reduces build time and bandwidth usage

### Matrix Strategy
- Tests run on multiple Java versions (17, 21)
- Ensures compatibility across supported versions
- Only JDK 21 artifacts are uploaded to reduce storage

### Security Integration
- OWASP Dependency Check for vulnerability scanning
- Can be extended with SAST tools like CodeQL
- Security reports uploaded as artifacts

### Artifact Management
- Build artifacts retained for 30 days
- Release artifacts attached to GitHub releases
- Configurable artifact registry integration

## Customization Guide

### Adding New Jobs
1. Create new job in appropriate workflow file
2. Add `needs:` dependency if required
3. Configure appropriate triggers

### Environment-specific Deployments
```yaml
deploy-staging:
  needs: build-and-test
  runs-on: ubuntu-latest
  environment: staging
  if: github.ref == 'refs/heads/develop'
  # deployment steps
```

### Integration with External Tools
- SonarQube: Add sonar-scanner step
- Slack: Use slack-notifier action
- Jira: Use jira-integration action
