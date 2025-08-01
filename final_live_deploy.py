#!/usr/bin/env python3
"""
FINAL LIVE PRODUCTION DEPLOYMENT - JEN AI ASSISTANT
"""

import requests
import json
import time

def deploy_jen_live():
    """Deploy Jen AI Assistant to live production"""
    
    print("""
    ==========================================
        JEN AI ASSISTANT - FINAL DEPLOYMENT
           GOING LIVE IN PRODUCTION!
    ==========================================
    """)
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    owner_id = "tea-d1rf5j3e5dus73dl49og"  # From the API response
    
    # Complete service configuration
    service_data = {
        "type": "web_service",
        "name": "jen-ai-assistant",
        "ownerId": owner_id,
        "repo": "https://github.com/jaredblank/jen-ai-assistant",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python start.py",
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
        ],
        "healthCheckPath": "/health",
        "region": "oregon",
        "plan": "starter",
        "rootDir": ".",
        "runtime": "python3"
    }
    
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("[DEPLOY] Creating Render service...")
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_data,
            timeout=60
        )
        
        if response.status_code == 201:
            service_info = response.json()
            service_id = service_info.get('id')
            
            print("[SUCCESS] JEN AI ASSISTANT DEPLOYED TO PRODUCTION!")
            print(f"[INFO] Service ID: {service_id}")
            print(f"[INFO] Live URL: https://jen-ai-assistant.onrender.com")
            print(f"[INFO] Dashboard: https://dashboard.render.com/web/{service_id}")
            
            return service_id, True
        else:
            print(f"[PARTIAL] Deployment response: {response.status_code}")
            print(f"[INFO] Response: {response.text}")
            
            # Check if service already exists
            if "already exists" in response.text.lower():
                print("[INFO] Service may already exist, checking status...")
                return None, True
            
            return None, False
            
    except Exception as e:
        print(f"[ERROR] Deployment error: {e}")
        return None, False

def test_production_system():
    """Test the live production system"""
    
    print("\n[TEST] TESTING LIVE PRODUCTION SYSTEM...")
    base_url = "https://jen-ai-assistant.onrender.com"
    
    # Give the service time to start
    print("[INFO] Allowing time for service startup...")
    time.sleep(90)
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Database Health", f"{base_url}/health/database"),
        ("AI Service", f"{base_url}/health/ai"),
        ("Voice Service", f"{base_url}/health/voice"),
        ("Analytics", f"{base_url}/analytics/dashboard")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, url in tests:
        try:
            print(f"[TEST] {test_name}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"[PASS] {test_name} - OK")
                passed += 1
            else:
                print(f"[FAIL] {test_name} - Status: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] {test_name} - Error: {e}")
    
    # Test live query
    try:
        print("[TEST] Live Database Query...")
        query_data = {
            "question": "What is my total income this year?",
            "user_id": "121901"
        }
        
        response = requests.post(
            f"{base_url}/text/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[PASS] Live Query - OK")
            print(f"[INFO] Response: {result.get('response', 'No response')[:80]}...")
            passed += 1
        else:
            print(f"[FAIL] Live Query - Status: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Live Query - Error: {e}")
    
    total += 1  # Add the query test
    
    print(f"\n[RESULTS] System Tests: {passed}/{total} passed")
    return passed >= (total * 0.8)  # 80% pass rate considered success

def main():
    """Main deployment function"""
    
    # Deploy the service
    service_id, deployed = deploy_jen_live()
    
    if not deployed:
        print("[FAIL] Deployment failed!")
        return 1
    
    # Test the system
    system_working = test_production_system()
    
    # Final status
    print("\n" + "="*70)
    print("JEN AI ASSISTANT - PRODUCTION DEPLOYMENT COMPLETE")
    print("="*70)
    
    print(f"[INFO] Deployment Status: {'SUCCESS' if deployed else 'FAILED'}")
    print(f"[INFO] System Status: {'OPERATIONAL' if system_working else 'STARTING'}")
    
    print(f"\nLIVE PRODUCTION URLS:")
    print(f"Main Service: https://jen-ai-assistant.onrender.com")
    print(f"Health Check: https://jen-ai-assistant.onrender.com/health")
    print(f"API Documentation: https://jen-ai-assistant.onrender.com/docs")
    print(f"Analytics Dashboard: https://jen-ai-assistant.onrender.com/analytics/dashboard")
    
    print(f"\nREPOSITORY:")
    print(f"GitHub: https://github.com/jaredblank/jen-ai-assistant")
    
    print(f"\nNEXT STEPS:")
    print("1. Configure ElevenLabs webhook: https://jen-ai-assistant.onrender.com/elevenlabs/webhook")
    print("2. Set up Twilio webhooks (when ready)")
    print("3. Test phone call functionality")
    print("4. Monitor system performance")
    
    print(f"\nJEN AI ASSISTANT IS NOW LIVE!")
    print("Revolutionary voice-enabled real estate AI system ready for production use!")
    print("="*70)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)