import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mistral_api():
    """Test Mistral AI API key with a simple request."""
    
    api_key = os.getenv("MISTRAL_API_KEY")
    endpoint = "https://api.mistral.ai/v1/chat/completions"
    
    print(f"Testing Mistral AI API...")
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    print(f"Endpoint: {endpoint}")
    
    if not api_key:
        print("❌ ERROR: MISTRAL_API_KEY not found in environment variables")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'API test successful' if you can read this."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print("\n🔄 Making API request...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']['content']
            print(f"✅ SUCCESS: {message}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    test_mistral_api()
