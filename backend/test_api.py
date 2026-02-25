print("=== Testing API Key Setup ===")
print()

# Test 1: Check if .env file exists
import os
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"1. Checking for .env file at: {env_path}")
print(f"   .env exists: {os.path.exists(env_path)}")
print()

# Test 2: Try loading environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("2. ✅ dotenv loaded successfully")
except Exception as e:
    print(f"2. ❌ Error loading dotenv: {e}")
print()

# Test 3: Check API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print(f"3. ✅ API Key found!")
    print(f"   First 20 chars: {api_key[:20]}...")
    print(f"   Length: {len(api_key)} characters")
else:
    print("3. ❌ API Key NOT found")
print()

# Test 4: Try importing anthropic
try:
    import anthropic
    print(f"4. ✅ Anthropic package loaded (v{anthropic.__version__})")
except Exception as e:
    print(f"4. ❌ Error importing anthropic: {e}")
print()

# Test 5: Try creating client
if api_key:
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("5. ✅ Anthropic client created successfully!")
    except Exception as e:
        print(f"5. ❌ Error creating client: {e}")
else:
    print("5. ⚠️ Skipped (no API key)")

print()
print("=== Debug Complete ===")