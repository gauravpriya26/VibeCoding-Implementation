# Azure Portal Setup Guide - No CLI Required!

## 🌐 **Complete Azure Portal Method**

Follow these steps to set up GitHub Actions deployment using only the Azure Portal.

## 🔧 Your Azure Environment Details

**App Name:** `CTS-VibeAppUK51203-3`  
**Subscription:** `cb6255863a-vibecode05-az`  
**Subscription ID:** `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb`  
**Resource Group:** `CTS-VibeAppUK5120`  

---

## 🚀 **Step 1: Create Service Principal via Azure Portal**

### 1.1 Register an Application

1. **Go to Azure Portal:** https://portal.azure.com
2. **Search for:** `Azure Active Directory` → Click it
3. **Click:** `App registrations` (left sidebar)
4. **Click:** `+ New registration`
5. **Fill in:**
   - **Name:** `github-actions-vibecode-sp`
   - **Supported account types:** `Accounts in this organizational directory only`
   - **Redirect URI:** Leave blank
6. **Click:** `Register`

### 1.2 Get Application IDs

After registration, you'll see the app overview page:

1. **Copy these values:**
   - **Application (client) ID:** `12345678-1234-5678-9012-123456789abc` 
     → **Save as:** `AZURE_CLIENT_ID`
   - **Directory (tenant) ID:** `87654321-4321-4321-4321-210987654321`
     → **Save as:** `AZURE_TENANT_ID`

### 1.3 Create Client Secret

1. **Click:** `Certificates & secrets` (left sidebar)
2. **Click:** `+ New client secret`
3. **Add description:** `GitHub Actions Secret`
4. **Set expires:** `24 months`
5. **Click:** `Add`
6. **⚠️ IMMEDIATELY COPY the "Value"** (not the Secret ID)
   → **Save as:** `AZURE_CLIENT_SECRET`
   
   **⚠️ WARNING:** You can only see this value once! Copy it now!

### 1.4 Assign Permissions to Resource Group

1. **Search for:** `Subscriptions` (in top search bar)
2. **Click:** Your subscription `cb6255863a-vibecode05-az`
3. **Click:** `Resource groups` (left sidebar)  
4. **Click:** `CTS-VibeAppUK5120`
5. **Click:** `Access control (IAM)` (left sidebar)
6. **Click:** `+ Add` → `Add role assignment`
7. **Select:**
   - **Role:** `Contributor`
   - **Assign access to:** `User, group, or service principal`
8. **Click:** `Next`
9. **Click:** `+ Select members`
10. **Search for:** `github-actions-vibecode-sp`
11. **Select it** and click `Select`
12. **Click:** `Review + assign`
13. **Click:** `Assign`

---

## 🔑 **Step 2: Add GitHub Repository Secrets**

### 2.1 Go to GitHub Repository

1. **Open:** https://github.com/gauravpriya26/VibeCoding-Implementation
2. **Click:** `Settings` (top menu bar)
3. **Click:** `Secrets and variables` → `Actions` (left sidebar)

### 2.2 Add the 4 Required Secrets

Click `New repository secret` for each of these:

| Secret Name | Value Source | Example Value |
|-------------|--------------|---------------|
| `AZURE_CLIENT_ID` | From Step 1.2 (Application ID) | `12345678-1234-5678-9012-123456789abc` |
| `AZURE_CLIENT_SECRET` | From Step 1.3 (Client secret value) | `abc123~DEF456_GHI789` |
| `AZURE_TENANT_ID` | From Step 1.2 (Directory ID) | `87654321-4321-4321-4321-210987654321` |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb` |

### 2.3 Verify Secrets

After adding all 4 secrets, you should see them listed (values will be hidden).

---

## ⚙️ **Step 3: Configure App Service Settings**

### 3.1 Navigate to Your App Service

1. **Search for:** `App Services` (in top search bar)
2. **Click:** `CTS-VibeAppUK51203-3`

### 3.2 Configure Application Settings

1. **Click:** `Configuration` (left sidebar)
2. **Click:** `+ New application setting` for each of these:

| Name | Value |
|------|-------|
| `WEBSITES_PORT` | `8080` |
| `JAVA_OPTS` | `-Dserver.port=8080 -Xmx512m` |
| `WEBSITES_CONTAINER_START_TIME_LIMIT` | `600` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. **Click:** `Save` at the top
4. **Click:** `Continue` when prompted

### 3.3 Set Startup Command

1. **Still in Configuration page**
2. **Click:** `General settings` tab
3. **In Startup Command field, enter:** `java -jar *.jar`
4. **Click:** `Save`

---

## 🧪 **Step 4: Test Your Setup**

### 4.1 Verify Service Principal Permissions

1. **Go to:** `Subscriptions` → `cb6255863a-vibecode05-az`
2. **Click:** `Access control (IAM)`
3. **Click:** `Role assignments` tab
4. **Search for:** `github-actions-vibecode-sp`
5. **Verify:** It shows `Contributor` role on `CTS-VibeAppUK5120`

### 4.2 Test GitHub Actions

1. **Push any change** to your `main` branch
2. **Go to:** GitHub → `Actions` tab
3. **Watch the workflow run**
4. **Azure Login step should succeed**

---

## 🚀 **Final Result**

After successful deployment, your app will be available at:
**https://cts-vibeappuk51203-3.azurewebsites.net**

### Test Endpoints:
- **Homepage:** `/`
- **Health Check:** `/health` 
- **API:** `/api/message`

---

## 🔍 **Troubleshooting**

### Common Issues:

1. **"Login failed" Error:**
   - Double-check all 4 GitHub secrets are correctly entered
   - Verify service principal has Contributor role on resource group
   - Make sure you copied the client secret value (not the ID)

2. **"Permission denied" Error:**
   - Service principal needs Contributor role on `CTS-VibeAppUK5120` resource group
   - Check role assignment in IAM

3. **"App not found" Error:**
   - Verify app name: `CTS-VibeAppUK51203-3`
   - Check resource group: `CTS-VibeAppUK5120`

### Quick Verification Checklist:

✅ Service principal created in Azure AD  
✅ Client secret generated and copied  
✅ Contributor role assigned to resource group  
✅ All 4 GitHub secrets added  
✅ App Service settings configured  
✅ Startup command set  

---

## 📋 **Summary of Values You Need**

| Purpose | Value |
|---------|-------|
| **GitHub Secret: AZURE_CLIENT_ID** | Application (client) ID from Azure AD |
| **GitHub Secret: AZURE_CLIENT_SECRET** | Client secret value (copy immediately!) |
| **GitHub Secret: AZURE_TENANT_ID** | Directory (tenant) ID from Azure AD |
| **GitHub Secret: AZURE_SUBSCRIPTION_ID** | `ba7f988a-1d5f-4d79-98a5-e7fce6ed86eb` |

**🎯 All steps are done through Azure Portal web interface - no command line required!**
