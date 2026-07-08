"""
Test all authentication and API connections
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded .env from: {env_path}")
else:
    load_dotenv(override=True)
    print("⚠️  .env file not found in project root")

print("\n" + "="*60)
print("🔍 CONNECTION TEST SUITE")
print("="*60 + "\n")

# Test 1: Check Environment Variables
print("📋 Test 1: Environment Variables")
print("-" * 60)

api_key = os.getenv("GOOGLE_API_KEY")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")

if api_key:
    print(f"✅ GOOGLE_API_KEY: Found ({api_key[:10]}...{api_key[-5:]})")
else:
    print("❌ GOOGLE_API_KEY: Missing")

if project_id:
    print(f"✅ GOOGLE_CLOUD_PROJECT: {project_id}")
else:
    print("❌ GOOGLE_CLOUD_PROJECT: Missing")

if location:
    print(f"✅ GOOGLE_CLOUD_LOCATION: {location}")
else:
    print("⚠️  GOOGLE_CLOUD_LOCATION: Missing (will use default)")

print()

# Test 2: Google Generative AI (API Key) - for LLMs
print("🤖 Test 2: Google Generative AI (LLMs with API Key)")
print("-" * 60)
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key,
        temperature=0
    )
    
    response = llm.invoke("Reply with only: OK")
    print(f"✅ Google Generative AI API: Connected!")
    print(f"   Response: {response.content}")
    print(f"   Model: gemini-2.0-flash-exp")
except Exception as e:
    print(f"❌ Google Generative AI API: Failed")
    print(f"   Error: {str(e)[:100]}")

print()

# Test 3: Vertex AI Embeddings (OAuth2)
print("📊 Test 3: Vertex AI Embeddings (OAuth2)")
print("-" * 60)
try:
    from langchain_google_vertexai import VertexAIEmbeddings
    
    embeddings = VertexAIEmbeddings(
        model_name="text-embedding-004",
        project=project_id,
        location=location or "us-central1"
    )
    
    # Test with a simple text
    test_text = ["Hello world"]
    result = embeddings.embed_documents(test_text)
    
    print(f"✅ Vertex AI Embeddings: Connected!")
    print(f"   Project: {project_id}")
    print(f"   Location: {location or 'us-central1'}")
    print(f"   Embedding dimension: {len(result[0])}")
except ImportError as e:
    print(f"❌ Vertex AI Embeddings: Module import failed")
    print(f"   Error: {str(e)}")
    print(f"   Fix: pip install langchain-google-vertexai")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Vertex AI Embeddings: Connection failed")
    
    if "403" in error_msg or "PERMISSION_DENIED" in error_msg:
        print(f"   Error: Permission Denied")
        print(f"   Reason: Your account lacks 'Vertex AI User' role")
        print(f"   Fix: See PERMISSION_FIX_GUIDE.md")
    elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
        print(f"   Error: Not authenticated")
        print(f"   Fix: Run 'gcloud auth application-default login'")
    else:
        print(f"   Error: {error_msg[:200]}")

print()

# Test 4: Alternative - HuggingFace Embeddings (Local, No Auth)
print("🤗 Test 4: HuggingFace Local Embeddings (Fallback)")
print("-" * 60)
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    print("   ⏳ Loading model (first time may download ~100MB)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Test with a simple text
    test_text = ["Hello world"]
    result = embeddings.embed_documents(test_text)
    
    print(f"✅ HuggingFace Embeddings: Working!")
    print(f"   Model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"   Embedding dimension: {len(result[0])}")
    print(f"   No authentication required ✨")
except Exception as e:
    print(f"❌ HuggingFace Embeddings: Failed")
    print(f"   Error: {str(e)[:200]}")

print()

# Test 5: Check Google Cloud Authentication
print("🔐 Test 5: Google Cloud Authentication Status")
print("-" * 60)
try:
    from google.auth import default
    from google.auth.exceptions import DefaultCredentialsError
    
    try:
        credentials, project = default()
        print(f"✅ Google Cloud Auth: Found!")
        print(f"   Auth type: {type(credentials).__name__}")
        if project:
            print(f"   Default project: {project}")
    except DefaultCredentialsError:
        print(f"❌ Google Cloud Auth: Not found")
        print(f"   Fix: Run 'gcloud auth application-default login'")
        print(f"   Or: Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
except ImportError:
    print(f"⚠️  google-auth package not installed")

print()

# Summary
print("="*60)
print("📊 SUMMARY")
print("="*60)
print("""
Current Configuration:
├─ LLMs (Gemini): Uses GOOGLE_API_KEY from .env
├─ Embeddings: Uses Vertex AI with OAuth2
└─ Fallback: HuggingFace local embeddings available

Recommendations:
1. If Vertex AI works: ✅ You're all set!
2. If Vertex AI fails (403): Switch to HuggingFace embeddings
3. If API key fails: Check your GOOGLE_API_KEY in .env
""")

print("="*60)
print("\nFor detailed fixes, see:")
print("  - AUTHENTICATION_GUIDE.md")
print("  - PERMISSION_FIX_GUIDE.md")
print("  - VERTEX_AI_SETUP.md")
print("="*60)
