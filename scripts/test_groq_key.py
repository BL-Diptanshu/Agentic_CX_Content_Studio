"""Quick test to verify Groq API key validity"""
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key loaded: {api_key[:10]}...{api_key[-10:]}")
print(f"API Key length: {len(api_key)}")

try:
    client = Groq(api_key=api_key)
    print("\n✓ Groq client created successfully")
   
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'Hello World'"}],
        max_tokens=10
    )
    
    print(f"✓ API call successful!")
    print(f"Response: {completion.choices[0].message.content}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
