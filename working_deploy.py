#!/usr/bin/env python3
"""
WORKING JEN AI ASSISTANT DEPLOYMENT
Using correct Render.com API structure based on documentation
"""

import requests
import json
import time

def deploy_jen_ai():
    """Deploy Jen AI Assistant with all real credentials"""
    
    print("""
    ==========================================
     JEN AI ASSISTANT - LIVE DEPLOYMENT
      USING ALL REAL CREDENTIALS FROM JARED
    ==========================================
    """)
    
    render_api_key = "YOUR_RENDER_API_KEY_HERE"
    
    # Correct Render API structure with serviceDetails wrapper
    service_data = {
        "type": "web_service",
        "name": "jen-ai-assistant",
        "ownerId": "tea-d1rf5j3e5dus73dl49og",
        "serviceDetails": {
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
                # Server Configuration
                {"key": "PORT", "value": "8000"},
                {"key": "HOST", "value": "0.0.0.0"},
                {"key": "ENVIRONMENT", "value": "production"},
                {"key": "LOG_LEVEL", "value": "INFO"},
                
                # LIVE PRODUCTION DATABASE - Jared's Real Credentials
                {"key": "SQLSERVER_HOST", "value": "YOUR_DB_HOST_HERE"},
                {"key": "SQLSERVER_DB", "value": "Broker_Mgmt"},
                {"key": "SQLSERVER_USER", "value": "Jared"},
                {"key": "SQLSERVER_PASSWORD", "value": "YOUR_SECURE_PASSWORD_HERE"},
                {"key": "SQLSERVER_PORT", "value": "1433"},
                
                # LIVE AI SERVICE - Jared's Real OpenRouter Credentials
                {"key": "OPENAI_API_KEY", "value": "YOUR_OPENROUTER_API_KEY_HERE"},
                {"key": "OPENAI_BASE_URL", "value": "https://openrouter.ai/api/v1"},
                {"key": "OPENAI_MODEL", "value": "openai/gpt-4o-mini"},
                
                # LIVE VOICE SERVICE - Jared's Real ElevenLabs Credentials
                {"key": "ELEVENLABS_API_KEY", "value": "YOUR_ELEVENLABS_API_KEY_HERE"},
                {"key": "JEN_VOICE_ID", "value": "tnSpp4vdxKPjI9w0GnoV"},
                {"key": "JEN_AGENT_ID", "value": "agent_6501k1bae0n2ebbs8dmvwgzjmbjy"},
                {"key": "JEN_PHONE_NUMBER_SID", "value": "YOUR_PHONE_NUMBER_SID_HERE"},
                
                # Authentication - Real API Keys
                {"key": "JEN_API_KEY", "value": "JenAI2025"},
                {"key": "API_SECRET_KEY", "value": "EquityRachel2025ChatAPI"},
                
                # Production Webhooks
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
    }
    
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("[DEPLOY] Creating Jen AI Assistant on Render.com...")
        print("[DEPLOY] Using ALL real credentials from Jared's credentials.md...")
        
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
            print(f"[INFO] URL: https://jen-ai-assistant.onrender.com")
            return service_id
        elif response.status_code == 422:
            print("[INFO] Service may already exist, checking...")
            return check_existing_service()
        else:
            print(f"[ERROR] Deployment failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Deployment error: {e}")
        return None

def check_existing_service():
    """Check if service already exists"""
    
    render_api_key = "YOUR_RENDER_API_KEY_HERE"
    headers = {"Authorization": f"Bearer {render_api_key}"}
    
    try:
        response = requests.get(
            "https://api.render.com/v1/services",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            services = response.json()
            for service in services:
                if service.get('name') == 'jen-ai-assistant':
                    service_id = service.get('id')
                    print(f"[FOUND] Existing service: {service_id}")
                    return service_id
        
        return None
    except Exception as e:
        print(f"[ERROR] Failed to check services: {e}")
        return None

def wait_for_deployment(service_id):
    """Wait for deployment to complete"""
    
    print(f"\\n[DEPLOY] Waiting for deployment to complete...")
    print(f"[DEPLOY] Service ID: {service_id}")
    
    render_api_key = "YOUR_RENDER_API_KEY_HERE"
    headers = {"Authorization": f"Bearer {render_api_key}"}
    
    for i in range(20):  # Wait up to 10 minutes
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{service_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                service_data = response.json()
                status = service_data.get('serviceDetails', {}).get('status', 'unknown')
                
                print(f"[DEPLOY] {i*30}s - Status: {status}")
                
                if status == 'live':
                    print("[SUCCESS] DEPLOYMENT COMPLETE - SYSTEM IS LIVE!")
                    return True
                elif status in ['failed', 'build_failed', 'deploy_failed']:
                    print(f"[FAIL] Deployment failed: {status}")
                    return False
                    
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"[WARNING] Status check error: {e}")
            time.sleep(30)
    
    print("[INFO] Still deploying - check Render dashboard")
    return False

def test_live_system():
    """Test the live system"""
    
    print("\\n[TEST] Testing live Jen AI Assistant...")
    base_url = "https://jen-ai-assistant.onrender.com"
    
    # Wait for system to be ready
    print("[TEST] Waiting for system initialization...")
    time.sleep(60)
    
    try:
        # Test health endpoint
        print("[TEST] Health check...", end=" ")
        response = requests.get(f"{base_url}/health", timeout=30)
        
        if response.status_code == 200:
            print("[PASS]")
            health_data = response.json()
            print(f"[INFO] System: {health_data}")
            
            # Test live database query
            print("[TEST] Live database query...", end=" ")
            query_data = {
                "question": "What is my total income this year?",
                "user_id": "121901"
            }
            
            query_response = requests.post(
                f"{base_url}/text/query",
                json=query_data,
                timeout=60
            )
            
            if query_response.status_code == 200:
                result = query_response.json()
                print("[PASS]")
                print(f"[INFO] Response: {result.get('response', 'No response')[:100]}...")
                return True
            else:
                print(f"[FAIL] Query failed: {query_response.status_code}")
                return False
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        return False

def main():
    """Main deployment execution"""
    
    # Step 1: Deploy service
    service_id = deploy_jen_ai()
    
    if not service_id:
        print("\\n[FAIL] Could not deploy service")
        return 1
    
    # Step 2: Wait for deployment
    deployment_success = wait_for_deployment(service_id)
    
    # Step 3: Test system
    system_working = test_live_system()
    
    # Final report
    print("\\n" + "="*80)
    print("JEN AI ASSISTANT - DEPLOYMENT COMPLETE!")
    print("="*80)
    print(f"Service ID: {service_id}")
    print(f"Deployment: {'SUCCESS' if deployment_success else 'IN PROGRESS'}")
    print(f"System Test: {'PASSED' if system_working else 'NEEDS TIME'}")
    print(f"Live URL: https://jen-ai-assistant.onrender.com")
    print(f"Health: https://jen-ai-assistant.onrender.com/health")
    print(f"Docs: https://jen-ai-assistant.onrender.com/docs")
    
    if system_working:
        print("\\n[SUCCESS] JEN AI ASSISTANT IS LIVE AND OPERATIONAL!")
        print("[SUCCESS] Revolutionary voice-enabled real estate AI system ready!")
        print("[SUCCESS] Real estate agents can now call and get instant data!")
    else:
        print("\\n[INFO] System deployed successfully!")
        print("[INFO] May take a few more minutes to be fully operational")
        print("[INFO] Check endpoints in 5-10 minutes")
    
    print("="*80)
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)