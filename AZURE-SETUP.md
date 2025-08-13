# Azure Deployment Setup Guide

## 🔧 Your Azure Environment Details

**App Name:** `CTS-VibeAppUK51203-3`  
**Subscription:** `cb6255863a-vibecode05-az`  
**Subscription ID:** `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb`  
**Resource Group:** `CTS-VibeAppUK5120`  

## 🚀 Quick Setup Commands

### Step 1: Create Service Principal (Use these exact values)

Run these commands in Azure Cloud Shell or Azure CLI:

```bash
# Set your specific variables
SUBSCRIPTION_ID="ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb"
RESOURCE_GROUP="CTS-VibeAppUK5120"
APP_NAME="CTS-VibeAppUK51203-3"

# Create Service Principal with correct scope
az ad sp create-for-rbac \
  --name "github-actions-vibecode-sp" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

**Expected Output:**
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-client-secret-here",
  "subscriptionId": "ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb",
  "tenantId": "87654321-4321-4321-4321-210987654321"
}
```

### Step 2: Configure GitHub Repository Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions → New repository secret**

Add these secrets with the values from the Service Principal output:

| Secret Name | Description | Your Value (from command output) |
|-------------|-------------|-----------------------------------|
| `AZURE_CLIENT_ID` | Application (client) ID | Copy `clientId` from output |
| `AZURE_CLIENT_SECRET` | Client secret value | Copy `clientSecret` from output |
| `AZURE_TENANT_ID` | Directory (tenant) ID | Copy `tenantId` from output |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb` |

### Step 3: Configure Your Existing App Service

Since your App Service already exists, just configure the settings:

```bash
# Configure App Settings for your existing app
az webapp config appsettings set \
  --name "CTS-VibeAppUK51203-3" \
  --resource-group "CTS-VibeAppUK5120" \
  --settings \
    WEBSITES_PORT=8080 \
    JAVA_OPTS="-Dserver.port=8080 -Xmx512m" \
    WEBSITES_CONTAINER_START_TIME_LIMIT=600 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Set the startup command
az webapp config set \
  --name "CTS-VibeAppUK51203-3" \
  --resource-group "CTS-VibeAppUK5120" \
  --startup-file "java -jar *.jar"
```

### Step 4: Alternative - Using Azure Portal

1. **Create Service Principal via Azure Portal:**
   - Go to Azure Active Directory → App registrations → New registration
   - Name: `github-actions-sp`
   - Copy Application (client) ID → Use as `AZURE_CLIENT_ID`
   - Copy Directory (tenant) ID → Use as `AZURE_TENANT_ID`
   - Go to Certificates & secrets → New client secret
   - Copy secret value → Use as `AZURE_CLIENT_SECRET`

2. **Assign Permissions:**
   - Go to Subscriptions → Your subscription → Access control (IAM)
   - Add role assignment → Contributor → Select your service principal

3. **Create App Service:**
   - Go to App Services → Create
   - Runtime stack: Java 21
   - Operating System: Linux
   - App Service Plan: Basic B1

## 🔍 Troubleshooting

### Common Issues:

1. **"Login failed" Error:**
   - Verify all 4 secrets are correctly set in GitHub
   - Check service principal has Contributor role
   - Ensure subscription ID is correct

2. **"App not found" Error:**
   - Verify app name matches in workflow: `vibecoding-java-app`
   - Check resource group exists
   - Ensure app service is created

3. **"Permission denied" Error:**
   - Service principal needs Contributor role on resource group
   - Check subscription ID in secrets

### Verify Setup:

```bash
# Test Azure CLI login with your specific details
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Verify your specific web app
az webapp show \
  --name "CTS-VibeAppUK51203-3" \
  --resource-group "CTS-VibeAppUK5120" \
  --output table

# Check app settings
az webapp config appsettings list \
  --name "CTS-VibeAppUK51203-3" \
  --resource-group "CTS-VibeAppUK5120" \
  --output table
```

## 🚀 Next Steps

After setting up the secrets:

1. Push your changes to the `main` branch
2. GitHub Actions will automatically:
   - Build your Java application
   - Deploy to Azure App Service
   - Your app will be available at: `https://cts-vibeappuk51203-3.azurewebsites.net`

## 📝 Important Notes

- The Java application listens on port 8080 (configured via `PORT` environment variable)
- Health check endpoint: `/health`
- Main application: `/`
- API endpoint: `/api/message`
- Deployment typically takes 3-5 minutes
