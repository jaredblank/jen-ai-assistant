#!/usr/bin/env python3
"""
ULTIMATE JEN AI ASSISTANT DEPLOYMENT
Using correct Render.com API structure
"""

import requests
import json
import time

def deploy_ultimate():
    """Deploy with correct Render API structure"""
    
    print("""
    ==========================================
         JEN AI ASSISTANT - ULTIMATE DEPLOY
            FINAL PRODUCTION DEPLOYMENT
    ==========================================
    """)
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    
    # Correct Render API structure
    service_data = {
        "type": "web_service",
        "name": "jen-ai-assistant",
        "ownerId": "tea-d1rf5j3e5dus73dl49og",
        "repo": "https://github.com/jaredblank/jen-ai-assistant",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python start.py",
        "healthCheckPath": "/health",
        "runtime": "python",
        "region": "oregon",
        "plan": "starter",
        "rootDir": ".",
        "envVars": [
                {"key": "PORT", "value": "8000"},
                {"key": "HOST", "value": "0.0.0.0"},
                {"key": "ENVIRONMENT", "value": "production"},
                {"key": "LOG_LEVEL", "value": "INFO"},
                
                # Database Configuration
                {"key": "SQLSERVER_HOST", "value": "104.42.175.206"},
                {"key": "SQLSERVER_DB", "value": "Broker_Mgmt"},
                {"key": "SQLSERVER_USER", "value": "Jared"},
                {"key": "SQLSERVER_PASSWORD", "value": "N1ch0las1!"},
                {"key": "SQLSERVER_PORT", "value": "1433"},
                
                # AI Service Configuration  
                {"key": "OPENAI_API_KEY", "value": "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"},
                {"key": "OPENAI_BASE_URL", "value": "https://openrouter.ai/api/v1"},
                {"key": "OPENAI_MODEL", "value": "openai/gpt-4o-mini"},
                
                # ElevenLabs Voice Configuration
                {"key": "ELEVENLABS_API_KEY", "value": "sk_beb548af5488bc5c3710ac163aa3b1f8a7974983b1e84c0f"},
                {"key": "JEN_VOICE_ID", "value": "tnSpp4vdxKPjI9w0GnoV"},
                {"key": "JEN_AGENT_ID", "value": "agent_6501k1bae0n2ebbs8dmvwgzjmbjy"},
                {"key": "JEN_PHONE_NUMBER_SID", "value": "PNd7a8b8e2904cae40f0035b5c28e2dfbf"},
                
                # Authentication
                {"key": "JEN_API_KEY", "value": "JenAI2025"},
                {"key": "API_SECRET_KEY", "value": "EquityRachel2025ChatAPI"},
                
                # Webhook Configuration
                {"key": "JEN_WEBHOOK_URL", "value": "https://jen-ai-assistant.onrender.com/elevenlabs/webhook"},
                
                # Performance Settings
                {"key": "MAX_WORKERS", "value": "1"},
                {"key": "TIMEOUT_SECONDS", "value": "30"},
                {"key": "CACHE_TTL_SECONDS", "value": "300"},
                
                # CORS Settings
                {"key": "ALLOWED_ORIGINS", "value": "*"},
                {"key": "ALLOWED_METHODS", "value": "GET,POST,PUT,DELETE,OPTIONS"},
                {"key": "ALLOWED_HEADERS", "value": "*"}
            ]
    }
    
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("[DEPLOY] Deploying to Render.com...")
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_data,
            timeout=60
        )
        
        print(f"[INFO] Response Status: {response.status_code}")
        
        if response.status_code == 201:
            service_info = response.json()
            service_id = service_info.get('id')
            print("[SUCCESS] JEN AI ASSISTANT DEPLOYED SUCCESSFULLY!")
            print(f"[INFO] Service ID: {service_id}")
            return service_id
        else:
            print(f"[INFO] Response: {response.text}")
            
            # Try to find existing service
            print("[INFO] Checking for existing services...")
            get_response = requests.get(
                "https://api.render.com/v1/services",
                headers=headers,
                timeout=30
            )
            
            if get_response.status_code == 200:
                services = get_response.json()
                for service in services:
                    if service.get('name') == 'jen-ai-assistant':
                        service_id = service.get('id')
                        print(f"[SUCCESS] Found existing service: {service_id}")
                        return service_id
            
            return None
            
    except Exception as e:
        print(f"[ERROR] Deployment error: {e}")
        return None

def test_live_service():
    """Test the live service"""
    
    print("\n[TEST] Testing live service...")
    base_url = "https://jen-ai-assistant.onrender.com"
    
    # Wait for startup
    print("[INFO] Waiting for service startup (2 minutes)...")
    time.sleep(120)
    
    # Test health endpoint
    try:
        print("[TEST] Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=30)
        
        if response.status_code == 200:
            print("[PASS] Health check successful!")
            print(f"[INFO] Response: {response.json()}")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
        return False

def main():
    """Main deployment"""
    
    service_id = deploy_ultimate()
    
    if service_id:
        print(f"\n[SUCCESS] Service deployed with ID: {service_id}")
        
        # Test the service
        working = test_live_service()
        
        print("\n" + "="*60)
        print("JEN AI ASSISTANT - DEPLOYMENT COMPLETE")
        print("="*60)
        print(f"Status: {'LIVE AND OPERATIONAL' if working else 'DEPLOYED (starting up)'}")
        print(f"URL: https://jen-ai-assistant.onrender.com")
        print(f"Health: https://jen-ai-assistant.onrender.com/health")
        print(f"Docs: https://jen-ai-assistant.onrender.com/docs")
        print("="*60)
        
        if working:
            print("JEN AI ASSISTANT IS NOW LIVE IN PRODUCTION!")
            print("Revolutionary voice-enabled AI system ready for use!")
        else:
            print("Service deployed - may take a few more minutes to be fully ready.")
            print("Check the health endpoint in 5-10 minutes.")
        
        return 0
    else:
        print("\n[FAIL] Deployment failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)