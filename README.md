# DevOps Migration Simulator

A simple Spring Boot web app with an H2 in-memory database and a tiny frontend to simulate migrating pipelines from Jenkins to GitHub Actions. Includes a `Jenkinsfile` (pre-migration) and a GitHub Actions workflow deploying to Azure Web App.

## Tech
- Spring Boot 3 (Java 17)
- Spring Web, Spring Data JPA, H2
- Static HTML/JS frontend (no framework)

## Run locally
```bash
mvn spring-boot:run
```
Visit `http://localhost:8080` for the UI.
H2 Console at `http://localhost:8080/h2-console` (JDBC URL: `jdbc:h2:mem:devopsdb`).

## API
- GET `/api/pipelines`
- POST `/api/pipelines` body: `{ "name": string, "source": "JENKINS" | "GITHUB_ACTIONS" }`
- POST `/api/pipelines/{id}/migrate`

## Pre-migration: Jenkins
- See `Jenkinsfile` for a simple build+test pipeline using Maven on Windows agents.

## Post-migration: GitHub Actions + Azure
Workflow: `.github/workflows/azure-webapp.yml`
- Builds and tests on `windows-latest` with JDK 17
- Publishes the JAR artifact
- Deploys to Azure Web App using publish profile

### Azure setup
1. Create an Azure Web App (Java 17 stack). Note the name, e.g. `my-java-webapp`.
2. In Azure Portal → Web App → Deployment Center → Get publish profile, copy XML.
3. In GitHub repo → Settings → Secrets and variables → Actions → New repository secret:
   - `AZURE_WEBAPP_NAME` = your web app name
   - `AZURE_WEBAPP_PUBLISH_PROFILE` = paste publish profile XML
4. Push to `main` to trigger build and deploy.

## Notes
- Uses in-memory H2; data resets on restart.
- The UI lets you create pipelines and migrate them (status flips to MIGRATED, source to GITHUB_ACTIONS). 