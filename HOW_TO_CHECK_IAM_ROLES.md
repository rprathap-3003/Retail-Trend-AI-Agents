# 🔍 How to Check Your IAM Roles

## Quick Method: Use Google Cloud Console (Easiest!)

### Step 1: Open the IAM Page
Click this link or copy it to your browser:

```
https://console.cloud.google.com/iam-admin/iam?project=sandbox-7940
```

### Step 2: Find Your Account
- Look for your email address in the list
- It should be the same email you used to authenticate with gcloud

### Step 3: Check Your Roles
Look in the "Role" column next to your email. You need to see:

✅ **"Vertex AI User"** or
✅ **"Vertex AI Administrator"** or  
✅ **"Editor"** or
✅ **"Owner"**

---

## What Each Role Means:

| Role | Can Use Vertex AI? | Description |
|------|-------------------|-------------|
| **Vertex AI User** | ✅ YES | Perfect for your needs |
| **Vertex AI Administrator** | ✅ YES | Admin access to Vertex AI |
| **Editor** | ✅ YES | Can edit project resources |
| **Owner** | ✅ YES | Full project access |
| **Viewer** | ❌ NO | Read-only access |
| **Browser** | ❌ NO | Can browse only |

---

## Alternative: Use gcloud CLI

If you have gcloud installed, run this in PowerShell:

```powershell
# Get your email
$email = gcloud auth list --filter=status:ACTIVE --format="value(account)"
Write-Host "Your email: $email"

# Check your roles
gcloud projects get-iam-policy sandbox-7940 `
  --flatten="bindings[].members" `
  --format="table(bindings.role)" `
  --filter="bindings.members:$email"
```

---

## What You're Looking For:

Search the output for any of these:
- `roles/aiplatform.user` ✅
- `roles/aiplatform.admin` ✅
- `roles/editor` ✅
- `roles/owner` ✅

---

## If You DON'T Have These Roles:

### Option 1: Request from Admin
Send this message to your Google Cloud admin:

```
Hi,

I need access to Vertex AI for the retail_trend_ai project.

Project: sandbox-7940
My Email: [YOUR_EMAIL]
Role Needed: Vertex AI User (roles/aiplatform.user)

Instructions:
1. Go to: https://console.cloud.google.com/iam-admin/iam?project=sandbox-7940
2. Click "GRANT ACCESS"
3. Add principal: [YOUR_EMAIL]
4. Select role: "Vertex AI User"
5. Click "SAVE"

Or via command:
gcloud projects add-iam-policy-binding sandbox-7940 \
  --member='user:[YOUR_EMAIL]' \
  --role='roles/aiplatform.user'

Thank you!
```

### Option 2: Grant Yourself (If You're Admin)
```powershell
gcloud projects add-iam-policy-binding sandbox-7940 `
  --member='user:YOUR_EMAIL@domain.com' `
  --role='roles/aiplatform.user'
```

---

## After Getting Permissions:

1. **Wait 1-2 minutes** for IAM changes to propagate
2. **Test your setup:**
   ```powershell
   python test_vertex_ai.py
   ```
3. **Run your app:**
   ```powershell
   python src\main.py
   ```

---

## Quick Check: Do You Have Any Access?

Run this to see if you're authenticated:

```powershell
python -c "from google.auth import default; creds, project = default(); print(f'✅ Authenticated!\nProject: {project}')"
```

If this works, you're authenticated. You just need the right IAM role!

---

## Summary

1. ✅ **Check Console**: https://console.cloud.google.com/iam-admin/iam?project=sandbox-7940
2. 🔍 **Find your email** in the members list
3. 👀 **Look for** "Vertex AI User" role
4. ❌ **If missing** → Ask admin to add it
5. ✅ **If present** → Run `python test_vertex_ai.py`

---

**The web console is the easiest and most reliable way to check!** 🌐
