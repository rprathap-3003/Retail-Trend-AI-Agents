"""
Test Vertex AI Configuration
Verifies that all components are using Vertex AI with OAuth2
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded .env from: {env_path}\n")
else:
    load_dotenv(override=True)
    print("⚠️  .env file not found\n")

print("="*70)
print("🔵 VERTEX AI CONFIGURATION TEST")
print("="*70 + "\n")

# Check environment variables
project = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")

print("📋 Configuration Check:")
print("-"*70)
if project:
    print(f"✅ GOOGLE_CLOUD_PROJECT: {project}")
else:
    print("❌ GOOGLE_CLOUD_PROJECT: Missing!")
    print("   Add to .env: GOOGLE_CLOUD_PROJECT=sandbox-7940")
    sys.exit(1)

print(f"✅ GOOGLE_CLOUD_LOCATION: {location}")
print()

# Test 1: Google Cloud Authentication
print("="*70)
print("Test 1: Google Cloud Authentication (OAuth2)")
print("="*70)
print("-"*70)

try:
    from google.auth import default
    credentials, auth_project = default()
    
    print("✅ Google Cloud Auth: Found!")
    print(f"   Credential Type: {type(credentials).__name__}")
    if auth_project:
        print(f"   Authenticated Project: {auth_project}")
    print(f"   Using Project: {project}")
    auth_status = "✅ AUTHENTICATED"
except Exception as e:
    print(f"❌ Google Cloud Auth: Failed")
    print(f"   Error: {str(e)[:100]}")
    print("\n   💡 FIX:")
    print("   Run: gcloud auth application-default login")
    auth_status = "❌ FAILED"

print()

# Test 2: Vertex AI Embeddings
print("="*70)
print("Test 2: Vertex AI Embeddings")
print("="*70)
print("-"*70)

try:
    from langchain_google_vertexai import VertexAIEmbeddings
    
    print("⏳ Initializing Vertex AI embeddings...")
    embeddings = VertexAIEmbeddings(
        model_name="text-embedding-004",
        project=project,
        location=location
    )
    
    print("⏳ Testing with sample text...")
    result = embeddings.embed_documents(["Test embedding"])
    
    print("✅ Vertex AI Embeddings: Working!")
    print(f"   Model: text-embedding-004")
    print(f"   Project: {project}")
    print(f"   Location: {location}")
    print(f"   Embedding dimension: {len(result[0])}")
    embeddings_status = "✅ WORKING"
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ Vertex AI Embeddings: Failed")
    
    if "403" in error_msg or "PERMISSION_DENIED" in error_msg:
        print(f"   Error: Permission Denied")
        print(f"\n   💡 FIX:")
        print(f"   You need 'Vertex AI User' role on project: {project}")
        print(f"   Ask admin to run:")
        print(f"   gcloud projects add-iam-policy-binding {project} \\")
        print(f"     --member='user:YOUR_EMAIL@domain.com' \\")
        print(f"     --role='roles/aiplatform.user'")
    elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
        print(f"   Error: Not authenticated")
        print(f"\n   💡 FIX:")
        print(f"   Run: gcloud auth application-default login")
    else:
        print(f"   Error: {error_msg[:200]}")
    
    embeddings_status = "❌ FAILED"

print()

# Test 3: Vertex AI LLM
print("="*70)
print("Test 3: Vertex AI LLM (Gemini)")
print("="*70)
print("-"*70)

try:
    from langchain_google_vertexai import ChatVertexAI
    
    print("⏳ Initializing Vertex AI LLM...")
    llm = ChatVertexAI(
        model="gemini-2.5-pro",
        project=project,
        location=location
    )
    
    print("⏳ Testing with simple query...")
    response = llm.invoke("Reply with only: OK")
    
    print("✅ Vertex AI LLM: Working!")
    print(f"   Model: gemini-1.5-pro")
    print(f"   Project: {project}")
    print(f"   Location: {location}")
    print(f"   Response: {response.content}")
    llm_status = "✅ WORKING"
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ Vertex AI LLM: Failed")
    
    if "403" in error_msg or "PERMISSION_DENIED" in error_msg:
        print(f"   Error: Permission Denied")
        print(f"\n   💡 FIX:")
        print(f"   You need 'Vertex AI User' role on project: {project}")
    elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
        print(f"   Error: Not authenticated")
        print(f"\n   💡 FIX:")
        print(f"   Run: gcloud auth application-default login")
    else:
        print(f"   Error: {error_msg[:200]}")
    
    llm_status = "❌ FAILED"

print()

# Test 4: Import all modules
print("="*70)
print("Test 4: Application Module Imports")
print("="*70)
print("-"*70)

sys.path.insert(0, str(Path(__file__).parent / "src"))

modules = [
    ("services.generator", "generator"),
    ("services.vector_store", "vector_store"),
    ("agents.trend_agent", "trend_agent"),
    ("agents.inventory_agent", "inventory_agent"),
]

import_errors = []
for module_name, obj_name in modules:
    try:
        module = __import__(module_name, fromlist=[obj_name])
        getattr(module, obj_name)
        print(f"✅ {module_name}.{obj_name}")
    except Exception as e:
        print(f"❌ {module_name}.{obj_name}: {str(e)[:50]}")
        import_errors.append(module_name)

if import_errors:
    modules_status = f"⚠️ {len(import_errors)} ERRORS"
else:
    modules_status = "✅ ALL IMPORTED"

print()

# Summary
print("="*70)
print("📊 SUMMARY")
print("="*70)

results = [
    ("Google Cloud Auth (OAuth2)", auth_status),
    ("Vertex AI Embeddings", embeddings_status),
    ("Vertex AI LLM (Gemini)", llm_status),
    ("Module Imports", modules_status),
]

print()
for test_name, status in results:
    print(f"  {test_name:.<50} {status}")

print()
print("="*70)

all_passed = all("✅" in status for _, status in results)

if all_passed:
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print()
    print("✅ Your application is ready to run with Vertex AI!")
    print()
    print("Configuration:")
    print(f"  • Authentication: OAuth2 (Application Default Credentials)")
    print(f"  • Project: {project}")
    print(f"  • Location: {location}")
    print(f"  • Embeddings: text-embedding-004")
    print(f"  • LLM: gemini-1.5-pro")
    print()
    print("Run your application:")
    print("  python src\\main.py")
    print()
else:
    print("⚠️  SOME TESTS FAILED")
    print("="*70)
    print()
    
    if "❌" in auth_status:
        print("🔴 Authentication Required:")
        print("   Run: gcloud auth application-default login")
        print()
    
    if "❌" in embeddings_status or "❌" in llm_status:
        print("🔴 Permission Issue:")
        print("   You need 'Vertex AI User' role")
        print("   Ask your admin or see PERMISSION_FIX_GUIDE.md")
        print()

print("="*70)
