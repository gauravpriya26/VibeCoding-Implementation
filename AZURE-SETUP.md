# Azure Deployment Setup Guide

## 🔧 Required GitHub Secrets

To deploy your Java application to Azure App Service, you need to configure the following secrets in your GitHub repository:

### Step 1: Create Azure Service Principal

Run these commands in Azure Cloud Shell or Azure CLI:

```bash
# Set variables
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-resource-group-name"
APP_NAME="vibecoding-java-app"

# Create Service Principal
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

### Step 2: Configure GitHub Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AZURE_CLIENT_ID` | Application (client) ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_CLIENT_SECRET` | Client secret value | `your-client-secret-here` |
| `AZURE_TENANT_ID` | Directory (tenant) ID | `87654321-4321-4321-4321-210987654321` |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID | `abcdef12-3456-7890-abcd-ef1234567890` |

### Step 3: Create Azure App Service

```bash
# Create Resource Group (if not exists)
az group create --name $RESOURCE_GROUP --location "East US"

# Create App Service Plan
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_NAME}-plan" \
  --runtime "JAVA:21-java21"

# Configure App Settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    WEBSITES_PORT=8080 \
    JAVA_OPTS="-Dserver.port=8080 -Xmx512m" \
    WEBSITES_CONTAINER_START_TIME_LIMIT=600
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
# Test Azure CLI login
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# List your web apps
az webapp list --resource-group $RESOURCE_GROUP --output table
```

## 🚀 Next Steps

After setting up the secrets:

1. Push your changes to the `main` branch
2. GitHub Actions will automatically:
   - Build your Java application
   - Deploy to Azure App Service
   - Your app will be available at: `https://vibecoding-java-app.azurewebsites.net`

## 📝 Important Notes

- The Java application listens on port 8080 (configured via `PORT` environment variable)
- Health check endpoint: `/health`
- Main application: `/`
- API endpoint: `/api/message`
- Deployment typically takes 3-5 minutes
