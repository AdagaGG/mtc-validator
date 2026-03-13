"""
Test simple de Mistral API sin imagen
"""

import requests
import json

api_key = "kSh23thqlPbBtR1A0EKhm7qvmk8t32gr"

payload = {
    "model": "pixtral-12b-2409",
    "messages": [
        {
            "role": "user",
            "content": "Say hello in JSON format: {\"message\": \"hello\"}"
        }
    ]
}

print("Testing Mistral API with simple text...")

try:
    resp = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=10
    )
    
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"✓ API works! Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"❌ Error: {resp.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {e}")
