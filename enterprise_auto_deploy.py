#!/usr/bin/env python3
"""
ENTERPRISE AUTO-DEPLOYMENT
Automated deployment to Render.com using all real credentials
"""

import requests
import json
import time
import subprocess
import os

def create_render_service_enterprise():
    """Create Render service with enterprise configuration"""
    
    print("""
    ==========================================
      ENTERPRISE AUTO-DEPLOYMENT STARTING
        DEPLOYING WITH ALL CREDENTIALS
    ==========================================
    """)
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    owner_id = "tea-d1rf5j3e5dus73dl49og"
    
    # Enterprise-grade service configuration
    service_config = {
        "type": "web_service",
        "name": "jen-ai-assistant",
        "ownerId": owner_id,
        "serviceDetails": {
            "repo": "https://github.com/jaredblank/jen-ai-assistant",
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "python start.py",
            "healthCheckPath": "/health",
            "publishPath": "",
            "envVars": [
                # Server Configuration
                {"key": "PORT", "value": "8000"},
                {"key": "HOST", "value": "0.0.0.0"},
                {"key": "ENVIRONMENT", "value": "production"},
                {"key": "LOG_LEVEL", "value": "INFO"},
                
                # LIVE PRODUCTION DATABASE
                {"key": "SQLSERVER_HOST", "value": "104.42.175.206"},
                {"key": "SQLSERVER_DB", "value": "Broker_Mgmt"},
                {"key": "SQLSERVER_USER", "value": "Jared"},
                {"key": "SQLSERVER_PASSWORD", "value": "N1ch0las1!"},
                {"key": "SQLSERVER_PORT", "value": "1433"},
                
                # LIVE AI SERVICE  
                {"key": "OPENAI_API_KEY", "value": "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"},
                {"key": "OPENAI_BASE_URL", "value": "https://openrouter.ai/api/v1"},
                {"key": "OPENAI_MODEL", "value": "openai/gpt-4o-mini"},
                
                # LIVE ELEVENLABS INTEGRATION
                {"key": "ELEVENLABS_API_KEY", "value": "sk_beb548af5488bc5c3710ac163aa3b1f8a7974983b1e84c0f"},
                {"key": "JEN_VOICE_ID", "value": "tnSpp4vdxKPjI9w0GnoV"},
                {"key": "JEN_AGENT_ID", "value": "agent_6501k1bae0n2ebbs8dmvwgzjmbjy"},
                {"key": "JEN_PHONE_NUMBER_SID", "value": "PNd7a8b8e2904cae40f0035b5c28e2dfbf"},
                
                # AUTHENTICATION
                {"key": "JEN_API_KEY", "value": "JenAI2025"},
                {"key": "API_SECRET_KEY", "value": "EquityRachel2025ChatAPI"},
                
                # PRODUCTION WEBHOOKS
                {"key": "JEN_WEBHOOK_URL", "value": "https://jen-ai-assistant.onrender.com/elevenlabs/webhook"},
                
                # ENTERPRISE PERFORMANCE
                {"key": "MAX_WORKERS", "value": "2"},  # Increased for enterprise
                {"key": "TIMEOUT_SECONDS", "value": "45"},  # Increased timeout
                {"key": "CACHE_TTL_SECONDS", "value": "600"},  # 10 minute cache
                
                # ENTERPRISE CORS
                {"key": "ALLOWED_ORIGINS", "value": "*"},
                {"key": "ALLOWED_METHODS", "value": "GET,POST,PUT,DELETE,OPTIONS"},
                {"key": "ALLOWED_HEADERS", "value": "*"}
            ],
            "region": "oregon",
            "plan": "starter",
            "runtime": "python"  # Fixed: should be "python" not "python3"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("[DEPLOY] Creating enterprise Render service...")
        print("[DEPLOY] Using all live production credentials...")
        
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_config,
            timeout=60
        )
        
        print(f"[INFO] Response status: {response.status_code}")
        
        if response.status_code == 201:
            service_data = response.json()
            service_id = service_data.get('id')
            
            print("[SUCCESS] ENTERPRISE SERVICE CREATED!")
            print(f"[INFO] Service ID: {service_id}")
            print(f"[INFO] Live URL: https://jen-ai-assistant.onrender.com")
            print(f"[INFO] Starting deployment process...")
            
            return service_id
        else:
            print(f"[INFO] Response: {response.text}")
            
            # Check if service already exists and get its ID
            if "already exists" in response.text.lower() or response.status_code == 422:
                print("[INFO] Service may already exist, checking...")
                
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
                            print(f"[FOUND] Existing service: {service_id}")
                            return service_id
            
            return None
        
    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
        return None

def wait_for_enterprise_deployment(service_id, timeout_minutes=15):
    """Wait for enterprise deployment with detailed monitoring"""
    
    print(f"\n[DEPLOY] Monitoring enterprise deployment...")
    print(f"[DEPLOY] Service ID: {service_id}")
    print(f"[DEPLOY] Timeout: {timeout_minutes} minutes")
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    
    headers = {
        "Authorization": f"Bearer {render_api_key}"
    }
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{service_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                service_data = response.json()
                service_details = service_data.get('serviceDetails', {})
                status = service_details.get('status', 'unknown')
                
                elapsed = int((time.time() - start_time) / 60)
                print(f"[DEPLOY] {elapsed}min - Status: {status}")
                
                if status == 'live':
                    print("[SUCCESS] ENTERPRISE DEPLOYMENT COMPLETE!")
                    print("[SUCCESS] System is LIVE and operational!")
                    return True
                elif status in ['failed', 'build_failed', 'deploy_failed']:
                    print(f"[FAIL] Deployment failed: {status}")
                    return False
                    
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"[WARNING] Status check error: {e}")
            time.sleep(30)
    
    print("[WARNING] Deployment monitoring timed out")
    print("[INFO] Service may still be deploying - check Render dashboard")
    return False

def validate_enterprise_system():
    """Validate enterprise system is fully operational"""
    
    print(f"\n" + "="*70)
    print("ENTERPRISE SYSTEM VALIDATION")
    print("="*70)
    
    base_url = "https://jen-ai-assistant.onrender.com"
    
    # Wait for system to fully initialize
    print("[VALIDATE] Waiting for system initialization...")
    time.sleep(60)
    
    validation_tests = [
        ("Health Check", f"{base_url}/health"),
        ("Database Connectivity", f"{base_url}/health/database"),
        ("AI Service", f"{base_url}/health/ai"),
        ("Voice Service", f"{base_url}/health/voice"),
        ("API Documentation", f"{base_url}/docs"),
        ("Analytics Dashboard", f"{base_url}/analytics/dashboard")
    ]
    
    passed = 0
    failed = 0
    
    for test_name, url in validation_tests:
        try:
            print(f"[VALIDATE] {test_name}...", end=" ")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print("PASS")
                passed += 1
            else:
                print(f"FAIL ({response.status_code})")
                failed += 1
        except Exception as e:
            print(f"ERROR ({str(e)[:30]}...)")
            failed += 1
    
    # Enterprise functional test
    try:
        print(f"[VALIDATE] Live Database Query...", end=" ")
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
            if 'response' in result and len(result['response']) > 10:
                print("PASS")
                print(f"         Sample: {result['response'][:60]}...")
                passed += 1
            else:
                print("FAIL (No response)")
                failed += 1
        else:
            print(f"FAIL ({response.status_code})")
            failed += 1
    except Exception as e:
        print(f"ERROR ({str(e)[:30]}...)")
        failed += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n[RESULTS] Validation: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    enterprise_ready = success_rate >= 80
    
    if enterprise_ready:
        print("[SUCCESS] SYSTEM IS ENTERPRISE-READY!")
    else:
        print("[WARNING] System needs optimization for enterprise use")
    
    return enterprise_ready

def main():
    """Main enterprise auto-deployment"""
    
    print("Starting enterprise auto-deployment...")
    
    # Step 1: Deploy service
    service_id = create_render_service_enterprise()
    
    if not service_id:
        print("[FAIL] Could not create or find service")
        return 1
    
    # Step 2: Monitor deployment
    deployment_success = wait_for_enterprise_deployment(service_id)
    
    # Step 3: Validate system
    system_ready = validate_enterprise_system()
    
    # Final report
    print(f"\n" + "="*80)
    print("ENTERPRISE DEPLOYMENT FINAL REPORT")
    print("="*80)
    
    print(f"Service ID: {service_id}")
    print(f"Deployment: {'SUCCESS' if deployment_success else 'IN PROGRESS'}")
    print(f"System Validation: {'PASSED' if system_ready else 'NEEDS ATTENTION'}")
    print(f"Enterprise Ready: {'YES' if system_ready else 'PARTIALLY'}")
    
    print(f"\nLIVE SYSTEM URLs:")
    print(f"Main: https://jen-ai-assistant.onrender.com")
    print(f"Health: https://jen-ai-assistant.onrender.com/health")
    print(f"Docs: https://jen-ai-assistant.onrender.com/docs")
    print(f"Dashboard: https://dashboard.render.com/web/{service_id}")
    
    if system_ready:
        print(f"\n[SUCCESS] JEN AI ASSISTANT IS LIVE AND ENTERPRISE-READY!")
        print(f"[SUCCESS] Revolutionary voice-enabled real estate AI system operational!")
    else:
        print(f"\n[INFO] System deployed but may need a few more minutes to be fully ready")
        print(f"[INFO] Monitor the dashboard and test endpoints in 5-10 minutes")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)