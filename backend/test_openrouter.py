import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file (override existing terminal variables)
load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
openrouter_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

print("========================================")
print("🔍 Testing OpenRouter API Key")
print("========================================\n")

if not openrouter_api_key or openrouter_api_key.startswith("sk-or-v1-XXXX"):
    print("❌ ERROR: OPENROUTER_API_KEY is not set correctly in your .env file.")
    print(f"Current value: {openrouter_api_key}")
    exit(1)

print(f"Key loaded: {openrouter_api_key[:15]}...{openrouter_api_key[-5:]}")
print(f"Model: {openrouter_model}\n")
print("Sending test request to OpenRouter...")

try:
    client = OpenAI(
        api_key=openrouter_api_key,
        base_url=openrouter_base_url,
    )
    
    response = client.chat.completions.create(
        model=openrouter_model,
        messages=[{"role": "user", "content": "Hello! Reply with 'OpenRouter API is working!' and nothing else."}],
        max_tokens=20
    )
    
    print("\n✅ SUCCESS! OpenRouter API is working perfectly.")
    print("Response from AI:", response.choices[0].message.content)
    
except Exception as e:
    print("\n❌ FAILED! Could not connect to OpenRouter API.")
    print(f"Error details: {e}")
