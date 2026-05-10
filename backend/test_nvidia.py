import os
from dotenv import load_dotenv
from openai import OpenAI

# 💡 PASTE YOUR NVIDIA API KEY HERE TO TEST IT
# Leave it empty ("") to load from the .env file automatically
HARDCODED_KEY = "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"

if HARDCODED_KEY:
    nvidia_api_key = HARDCODED_KEY
else:
    # Load the .env file
    load_dotenv()
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")

nvidia_base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
nvidia_model = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

print("========================================")
print("🔍 Testing NVIDIA API Key")
print("========================================\n")

if not nvidia_api_key or nvidia_api_key.startswith("nvapi-XXXX"):
    print("❌ ERROR: NVIDIA_API_KEY is not set correctly in your .env file.")
    print(f"Current value: {nvidia_api_key}")
    exit(1)

print(f"Key loaded: {nvidia_api_key[:10]}...{nvidia_api_key[-5:]}")
print(f"Model: {nvidia_model}\n")
print("Sending test request to NVIDIA...")

try:
    client = OpenAI(
        api_key=nvidia_api_key,
        base_url=nvidia_base_url,
    )
    
    response = client.chat.completions.create(
        model=nvidia_model,
        messages=[{"role": "user", "content": "Hello! Reply with 'NVIDIA API is working!' and nothing else."}],
        max_tokens=20
    )
    
    print("\n✅ SUCCESS! NVIDIA API is working perfectly.")
    print("Response from AI:", response.choices[0].message.content)
    
except Exception as e:
    print("\n❌ FAILED! Could not connect to NVIDIA API.")
    print(f"Error details: {e}")
    print("\nPossible reasons:")
    print("1. The API key is invalid or has a typo.")
    print("2. Your NVIDIA free credits have expired.")
    print("3. You copied the wrong key from the dashboard.")
