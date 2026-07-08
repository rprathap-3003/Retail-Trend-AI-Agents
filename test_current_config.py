"""
Test Current Code Configuration
Tests the exact setup you're using right now in your application
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables the same way main.py does
current_file = Path(__file__).resolve()
env_path = current_file.parent / ".env"

if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded .env from: {env_path}")
else:
    load_dotenv(override=True)
    print("⚠️  .env file not found, using system environment")

print("\n" + "="*70)
print("🧪 CURRENT CODE CONFIGURATION TEST")
print("="*70 + "\n")

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ CRITICAL: GOOGLE_API_KEY not found!")
    print("   Your application will fail to start.")
    print("   Add GOOGLE_API_KEY to your .env file")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:15]}...{api_key[-10:]}\n")

# Test 1: LLMs - Same as generator.py, trend_agent.py, inventory_agent.py
print("="*70)
print("Test 1: LLM Services (generator, trend_agent, inventory_agent)")
print("="*70)
print("Configuration: ChatGoogleGenerativeAI with gemini-2.5-pro")
print("-"*70)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key
    )
    
    print("⏳ Testing LLM connection...")
    response = llm.invoke("Say only: Connection successful")
    
    print("✅ SUCCESS: LLM is working!")
    print(f"   Model: gemini-2.5-pro")
    print(f"   Response: {response.content}")
    llm_status = "✅ WORKING"
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ FAILED: LLM connection failed")
    print(f"   Error: {error_msg[:150]}")
    
    if "401" in error_msg or "UNAUTHENTICATED" in error_msg:
        print("\n   💡 FIX:")
        print("   - Your API key may be invalid or expired")
        print("   - Get a new key: https://aistudio.google.com/app/apikey")
        print("   - Update GOOGLE_API_KEY in .env file")
    elif "404" in error_msg or "not found" in error_msg.lower():
        print("\n   💡 FIX:")
        print("   - Model 'gemini-2.5-pro' may not be available")
        print("   - Try 'gemini-1.5-flash' or 'gemini-1.5-pro' instead")
    
    llm_status = "❌ FAILED"

print()

# Test 2: Embeddings - Same as vector_store.py
print("="*70)
print("Test 2: Embeddings (vector_store.py)")
print("="*70)
print("Configuration: GoogleGenerativeAIEmbeddings with text-embedding-004")
print("-"*70)

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=api_key
    )
    
    print("⏳ Testing embeddings with sample text...")
    test_texts = ["This is a test", "Hello world"]
    result = embeddings.embed_documents(test_texts)
    
    print("✅ SUCCESS: Embeddings are working!")
    print(f"   Model: text-embedding-004")
    print(f"   Embedding dimension: {len(result[0])}")
    print(f"   Test documents: {len(test_texts)}")
    embeddings_status = "✅ WORKING"
    
except Exception as e:
    error_msg = str(e)
    print(f"❌ FAILED: Embeddings connection failed")
    print(f"   Error: {error_msg[:150]}")
    
    if "401" in error_msg or "UNAUTHENTICATED" in error_msg:
        print("\n   💡 FIX:")
        print("   - API keys may not be supported for this embedding model")
        print("   - This is the error you saw earlier!")
        print("\n   SOLUTION OPTIONS:")
        print("   A) Switch to HuggingFace embeddings (no auth needed)")
        print("   B) Use Vertex AI with OAuth2 (needs permissions)")
    elif "403" in error_msg or "PERMISSION_DENIED" in error_msg:
        print("\n   💡 FIX:")
        print("   - You need 'Vertex AI User' role")
        print("   - See PERMISSION_FIX_GUIDE.md")
    
    embeddings_status = "❌ FAILED"

print()

# Test 3: Import all your modules
print("="*70)
print("Test 3: Application Module Imports")
print("="*70)
print("-"*70)

modules_to_test = [
    ("services.generator", "generator"),
    ("services.vector_store", "vector_store"),
    ("agents.trend_agent", "trend_agent"),
    ("agents.inventory_agent", "inventory_agent"),
]

import_errors = []
for module_name, obj_name in modules_to_test:
    try:
        # Add src to path if needed
        src_path = Path(__file__).parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        module = __import__(module_name, fromlist=[obj_name])
        obj = getattr(module, obj_name)
        print(f"✅ {module_name}.{obj_name}")
    except Exception as e:
        print(f"❌ {module_name}.{obj_name}: {str(e)[:50]}")
        import_errors.append(f"{module_name}.{obj_name}")

if import_errors:
    modules_status = f"⚠️ {len(import_errors)} ERRORS"
else:
    modules_status = "✅ ALL IMPORTED"

print()

# Summary
print("="*70)
print("📊 TEST SUMMARY")
print("="*70)

results = [
    ("LLM Services (Gemini)", llm_status),
    ("Embeddings (text-embedding-004)", embeddings_status),
    ("Module Imports", modules_status),
]

print()
for test_name, status in results:
    print(f"  {test_name:.<50} {status}")

print()
print("="*70)

# Final verdict
all_passed = all("✅" in status for _, status in results)

if all_passed:
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print()
    print("✅ Your application should work! Try running:")
    print("   python src\\main.py")
    print()
else:
    print("⚠️  SOME TESTS FAILED")
    print("="*70)
    print()
    
    if "❌" in embeddings_status:
        print("🔴 CRITICAL: Embeddings are not working")
        print()
        print("Your application will crash when initializing the vector store.")
        print()
        print("RECOMMENDED FIX:")
        print("  Switch to HuggingFace embeddings (tested and working)")
        print()
        print("  In src/services/vector_store.py, replace:")
        print("    from langchain_google_genai import GoogleGenerativeAIEmbeddings")
        print("  with:")
        print("    from langchain_community.embeddings import HuggingFaceEmbeddings")
        print()
        print("  And replace:")
        print("    self.text_embeddings = GoogleGenerativeAIEmbeddings(")
        print("        model=\"models/text-embedding-004\",")
        print("        google_api_key=os.getenv(\"GOOGLE_API_KEY\")")
        print("    )")
        print("  with:")
        print("    self.text_embeddings = HuggingFaceEmbeddings(")
        print("        model_name=\"sentence-transformers/all-MiniLM-L6-v2\",")
        print("        model_kwargs={'device': 'cpu'},")
        print("        encode_kwargs={'normalize_embeddings': True}")
        print("    )")
        print()
    
    if "❌" in llm_status:
        print("🟡 WARNING: LLMs are not working")
        print()
        print("Your application will crash when generating trends or analyzing inventory.")
        print()
        print("RECOMMENDED FIX:")
        print("  Get a new API key from: https://aistudio.google.com/app/apikey")
        print("  Update GOOGLE_API_KEY in .env file")
        print()

print("="*70)
print("\nFor detailed help, see:")
print("  - CONNECTION_TEST_RESULTS.md")
print("  - AUTHENTICATION_GUIDE.md")
print("  - PERMISSION_FIX_GUIDE.md")
print("="*70)
