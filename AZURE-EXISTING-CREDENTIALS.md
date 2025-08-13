# Using Existing Azure App Service Extension Credentials

## 🔧 **Use Your Existing Azure Login from VS Code Extension**

Since you already have the Azure App Service extension configured in VS Code, we can use those existing credentials for GitHub Actions deployment.

## 🎯 **Method 1: Export Existing Azure CLI Credentials**

### Step 1: Check Your Current Azure Login

If you're already logged into Azure via VS Code extension, you can export the credentials:

1. **Open Terminal in VS Code** (Ctrl + `)
2. **Check if you're logged in:**
   ```bash
   az account show
   ```

3. **If logged in, get your current subscription details:**
   ```bash
   az account show --output table
   ```

### Step 2: Create Service Principal Using Your Current Login

```bash
# You're already authenticated, so just create the service principal
az ad sp create-for-rbac \
  --name "github-actions-vibecode-sp" \
  --role contributor \
  --scopes /subscriptions/ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb/resourceGroups/CTS-VibeAppUK5120 \
  --json-auth
```

## 🎯 **Method 2: Use Azure App Service Deployment Center**

### Step 1: Configure Deployment via Azure Portal

1. **Go to Azure Portal:** https://portal.azure.com
2. **Navigate to:** App Services → `CTS-VibeAppUK51203-3`
3. **Click:** `Deployment Center` (left sidebar)
4. **Select Source:** `GitHub`
5. **Authorize GitHub** if prompted
6. **Select:**
   - **Organization:** `gauravpriya26`
   - **Repository:** `VibeCoding-Implementation` 
   - **Branch:** `main`
7. **Build provider:** `GitHub Actions`
8. **Runtime stack:** `Java 21`
9. **Click:** `Save`

**✅ This will automatically:**
- Create the GitHub workflow file
- Generate and store Azure credentials as GitHub secrets
- Configure the deployment pipeline

### Step 2: Verify Auto-Generated Secrets

After saving, Azure will automatically create these GitHub secrets:
- `AZURE_CREDENTIALS` (or individual secrets)
- These will be visible in your GitHub repository secrets

## 🎯 **Method 3: Use Your Existing Azure Account in Terminal**

If you're already logged into Azure via VS Code:

### Step 1: Get Your Current Azure Context

```bash
# Check current login
az account show

# List available subscriptions  
az account list --output table

# Set correct subscription if needed
az account set --subscription "ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb"
```

### Step 2: Create Service Principal from Current Session

```bash
# Create service principal using your current authenticated session
az ad sp create-for-rbac \
  --name "github-actions-vibecode-sp" \
  --role contributor \
  --scopes /subscriptions/ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb/resourceGroups/CTS-VibeAppUK5120
```

### Step 3: Copy the Output to GitHub Secrets

The command will output:
```json
{
  "appId": "12345678-1234-5678-9012-123456789abc",
  "displayName": "github-actions-vibecode-sp", 
  "password": "your-secret-here",
  "tenant": "87654321-4321-4321-4321-210987654321"
}
```

**Map these to GitHub secrets:**
- `appId` → `AZURE_CLIENT_ID`
- `password` → `AZURE_CLIENT_SECRET`
- `tenant` → `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID` → `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb`

## 🚀 **Recommended Approach: Use Deployment Center**

**I recommend Method 2 (Deployment Center)** because:

✅ **Automatic Setup:** Azure configures everything for you  
✅ **No Manual Secrets:** Azure adds GitHub secrets automatically  
✅ **Uses Your Existing Login:** Leverages your current Azure authentication  
✅ **Zero Configuration:** Works out of the box  
✅ **Maintained by Azure:** Microsoft keeps it updated  

### Quick Deployment Center Steps:

1. **Azure Portal** → **App Services** → **`CTS-VibeAppUK51203-3`**
2. **Deployment Center** → **GitHub** → **Authorize**
3. **Select Repository:** `gauravpriya26/VibeCoding-Implementation`
4. **Branch:** `main` → **Runtime:** `Java 21` → **Save**
5. **Done!** Azure handles the rest automatically

## 🔍 **Verification**

After using any method:

1. **Check GitHub Secrets:**
   - Go to: `https://github.com/gauravpriya26/VibeCoding-Implementation/settings/secrets/actions`
   - Verify secrets are present

2. **Test Deployment:**
   - Push a change to `main` branch
   - Check GitHub Actions tab for successful deployment

3. **Access Your App:**
   - Visit: `https://cts-vibeappuk51203-3.azurewebsites.net`

## 📝 **Important Notes**

- **Method 2 (Deployment Center)** is the easiest and most reliable
- Your existing Azure login credentials will be used to create the deployment pipeline
- No need to manually copy/paste secrets with Deployment Center
- Azure automatically configures the GitHub workflow for Java 21

**Choose Method 2 for the simplest setup using your existing Azure credentials!** 🎯
