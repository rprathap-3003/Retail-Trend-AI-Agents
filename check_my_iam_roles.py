"""
Check Your IAM Roles Using Google Cloud Authentication
Works even if gcloud CLI is not installed
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

print("="*70)
print("🔍 CHECKING YOUR IAM ROLES")
print("="*70 + "\n")

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "sandbox-7940")

try:
    from google.auth import default
    from google.cloud import resourcemanager_v3
    
    # Get credentials
    print("📋 Getting authentication info...")
    credentials, project = default()
    
    print(f"✅ Authenticated!")
    print(f"   Credential Type: {type(credentials).__name__}")
    if project:
        print(f"   Default Project: {project}")
    print(f"   Using Project: {PROJECT_ID}")
    
    # Get user email if available
    if hasattr(credentials, 'service_account_email'):
        user_email = credentials.service_account_email
        print(f"   Service Account: {user_email}")
    elif hasattr(credentials, '_service_account_email'):
        user_email = credentials._service_account_email
        print(f"   Account: {user_email}")
    else:
        print(f"   Account: (User credentials)")
        user_email = None
    
    print("\n" + "-"*70)
    print("🔐 Attempting to fetch IAM policy...")
    print("-"*70 + "\n")
    
    try:
        # Try to get IAM policy
        client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        request = resourcemanager_v3.GetIamPolicyRequest(
            resource=f"projects/{PROJECT_ID}"
        )
        
        policy = client.get_iam_policy(request=request)
        
        print("✅ Successfully retrieved IAM policy!\n")
        print("📊 IAM Role Bindings:")
        print("="*70)
        
        found_roles = []
        vertex_ai_roles = []
        
        for binding in policy.bindings:
            # Check if you're in this binding
            if user_email and f"user:{user_email}" in binding.members:
                found_roles.append(binding.role)
                if "aiplatform" in binding.role.lower():
                    vertex_ai_roles.append(binding.role)
                print(f"✅ {binding.role}")
            elif not user_email and any("user:" in member for member in binding.members):
                # If we don't have email, show all user roles
                found_roles.append(binding.role)
                if "aiplatform" in binding.role.lower():
                    vertex_ai_roles.append(binding.role)
                print(f"   {binding.role}")
        
        print("="*70 + "\n")
        
        if vertex_ai_roles:
            print("🎉 VERTEX AI ROLES FOUND!")
            print("-"*70)
            for role in vertex_ai_roles:
                print(f"  ✅ {role}")
            print("\nYou should be able to use Vertex AI! 🚀")
        else:
            print("❌ NO VERTEX AI ROLES FOUND")
            print("-"*70)
            print("\nYou need one of these roles:")
            print("  • roles/aiplatform.user (Vertex AI User)")
            print("  • roles/aiplatform.admin (Vertex AI Administrator)")
            print("\nHow to get access:")
            print("  1. Ask your project admin")
            print("  2. Or check: https://console.cloud.google.com/iam-admin/iam?project=" + PROJECT_ID)
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  Could not retrieve IAM policy")
        print(f"   Error: {error_msg[:100]}")
        print("\n" + "-"*70)
        
        if "403" in error_msg or "Permission denied" in error_msg:
            print("❌ You don't have permission to view IAM policies")
            print("\nThis doesn't mean you don't have Vertex AI access!")
            print("It just means you can't view the IAM policy.")
        elif "404" in error_msg:
            print(f"❌ Project '{PROJECT_ID}' not found")
            print("   Check your GOOGLE_CLOUD_PROJECT in .env")
        
        print("\n📱 Check Your Roles via Web Console:")
        print("-"*70)
        print(f"1. Go to: https://console.cloud.google.com/iam-admin/iam?project={PROJECT_ID}")
        print("2. Find your email in the list")
        print("3. Check if you have 'Vertex AI User' role")
        print()

except ImportError as e:
    print("❌ Required packages not installed")
    print(f"   Missing: {str(e)}")
    print("\nInstall with:")
    print("   pip install google-cloud-resource-manager")
    print()

except Exception as e:
    print(f"❌ Authentication error: {str(e)}")
    print("\n💡 Fix:")
    print("   Run: gcloud auth application-default login")
    print()

print("="*70)
print("\n🎯 What You Need:")
print("-"*70)
print("Role: Vertex AI User (roles/aiplatform.user)")
print("\nWhat it allows:")
print("  • Use Vertex AI models (Gemini, embeddings)")
print("  • Access Vertex AI endpoints")
print("  • Required for your application to work")
print("\n" + "="*70)

print("\n📞 Next Steps:")
print("-"*70)
print("If you DON'T have Vertex AI roles:")
print("  → Ask your admin to grant 'Vertex AI User' role")
print("  → See: PERMISSION_FIX_GUIDE.md")
print("\nIf you DO have Vertex AI roles:")
print("  → Run: python test_vertex_ai.py")
print("  → Your app should work!")
print("\n" + "="*70)
