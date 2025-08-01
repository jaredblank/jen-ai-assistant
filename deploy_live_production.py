#!/usr/bin/env python3
"""
JEN AI ASSISTANT - ULTIMATE LIVE PRODUCTION DEPLOYMENT
Deploy to Render.com with ALL REAL CREDENTIALS for 100% PERFECT OPERATION!
"""

import requests
import json
import time
import os

def deploy_to_render_live():
    """Deploy Jen AI Assistant LIVE to Render.com with all real credentials"""
    
    print("""
    ==========================================
      JEN AI ASSISTANT LIVE DEPLOYMENT
        DEPLOYING TO PRODUCTION NOW!
    ==========================================
    """)
    
    render_api_key = "rnd_1q6pIHjPfAZOd8MmgrpN36mVqPbn"
    
    # Complete service configuration with ALL REAL CREDENTIALS
    service_data = {
        "type": "web_service",
        "name": "jen-ai-assistant",
        "repo": "https://github.com/jaredblank/jen-ai-assistant",
        "branch": "main",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python start.py",
        "envVars": [
            {"key": "PORT", "value": "8000"},
            {"key": "HOST", "value": "0.0.0.0"},
            {"key": "ENVIRONMENT", "value": "production"},
            {"key": "LOG_LEVEL", "value": "INFO"},
            
            # REAL DATABASE CONFIGURATION
            {"key": "SQLSERVER_HOST", "value": "104.42.175.206"},
            {"key": "SQLSERVER_DB", "value": "Broker_Mgmt"},
            {"key": "SQLSERVER_USER", "value": "Jared"},
            {"key": "SQLSERVER_PASSWORD", "value": "N1ch0las1!"},
            {"key": "SQLSERVER_PORT", "value": "1433"},
            
            # REAL AI SERVICE CONFIGURATION  
            {"key": "OPENAI_API_KEY", "value": "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"},
            {"key": "OPENAI_BASE_URL", "value": "https://openrouter.ai/api/v1"},
            {"key": "OPENAI_MODEL", "value": "openai/gpt-4o-mini"},
            
            # REAL ELEVENLABS VOICE CONFIGURATION
            {"key": "ELEVENLABS_API_KEY", "value": "sk_beb548af5488bc5c3710ac163aa3b1f8a7974983b1e84c0f"},
            {"key": "JEN_VOICE_ID", "value": "tnSpp4vdxKPjI9w0GnoV"},
            {"key": "JEN_AGENT_ID", "value": "agent_6501k1bae0n2ebbs8dmvwgzjmbjy"},
            {"key": "JEN_PHONE_NUMBER_SID", "value": "PNd7a8b8e2904cae40f0035b5c28e2dfbf"},
            
            # AUTHENTICATION
            {"key": "JEN_API_KEY", "value": "JenAI2025"},
            {"key": "API_SECRET_KEY", "value": "EquityRachel2025ChatAPI"},
            
            # WEBHOOK CONFIGURATION - LIVE PRODUCTION URL
            {"key": "JEN_WEBHOOK_URL", "value": "https://jen-ai-assistant.onrender.com/elevenlabs/webhook"},
            
            # PERFORMANCE SETTINGS
            {"key": "MAX_WORKERS", "value": "1"},
            {"key": "TIMEOUT_SECONDS", "value": "30"},
            {"key": "CACHE_TTL_SECONDS", "value": "300"},
            
            # CORS SETTINGS
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
    
    try:
        headers = {
            "Authorization": f"Bearer {render_api_key}",
            "Content-Type": "application/json"
        }
        
        print("🚀 DEPLOYING JEN AI ASSISTANT TO LIVE PRODUCTION...")
        print("📡 Connecting to Render.com API...")
        
        response = requests.post(
            "https://api.render.com/v1/services",
            headers=headers,
            json=service_data,
            timeout=30
        )
        
        if response.status_code == 201:
            service_info = response.json()
            service_id = service_info.get('id')
            
            print("✅ RENDER SERVICE CREATED SUCCESSFULLY!")
            print(f"🆔 Service ID: {service_id}")
            print(f"🌐 Live URL: https://jen-ai-assistant.onrender.com")
            print(f"📊 Dashboard: https://dashboard.render.com/web/{service_id}")
            
            return service_id
            
        elif response.status_code == 400:
            print("⚠️  Service might already exist, checking...")
            # Try to get existing service
            get_response = requests.get(
                "https://api.render.com/v1/services",
                headers=headers,
                timeout=10
            )
            
            if get_response.status_code == 200:
                services = get_response.json()
                for service in services:
                    if service.get('name') == 'jen-ai-assistant':
                        service_id = service.get('id')
                        print(f"✅ FOUND EXISTING SERVICE: {service_id}")
                        print(f"🌐 Live URL: https://jen-ai-assistant.onrender.com")
                        return service_id
            
            print(f"❌ Render deployment failed: {response.status_code}")
            print("Response:", response.text)
            return None
        else:
            print(f"❌ Render deployment failed: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except Exception as e:
        print(f"❌ Render API error: {e}")
        return None

def wait_for_deployment_live(service_id, timeout_minutes=15):
    """Wait for live deployment to complete"""
    print(f"⏳ Waiting for live deployment to complete (timeout: {timeout_minutes} minutes)...")
    
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
                status = service_data.get('serviceDetails', {}).get('status', 'unknown')
                
                print(f"📊 Deployment status: {status}")
                
                if status == 'live':
                    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
                    return True
                elif status in ['failed', 'build_failed']:
                    print(f"❌ Deployment failed with status: {status}")
                    return False
                    
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"⚠️  Status check error: {e}")
            time.sleep(30)
    
    print("⏰ Deployment timed out - but may still be in progress")
    return False

def test_live_system():
    """Test the live production system"""
    print("🧪 TESTING LIVE PRODUCTION SYSTEM...")
    
    base_url = "https://jen-ai-assistant.onrender.com"
    
    # Wait for service to be fully ready
    print("⏳ Waiting for service to be fully ready...")
    time.sleep(60)
    
    tests_passed = 0
    tests_total = 0
    
    try:
        # Test 1: Health Check
        tests_total += 1
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check PASSED!")
            print(f"   Status: {health_data}")
            tests_passed += 1
        else:
            print(f"❌ Health check FAILED: {response.status_code}")
        
        # Test 2: Database Health
        tests_total += 1
        print("🔍 Testing database connectivity...")
        response = requests.get(f"{base_url}/health/database", timeout=30)
        
        if response.status_code == 200:
            print("✅ Database health PASSED!")
            tests_passed += 1
        else:
            print(f"❌ Database health FAILED: {response.status_code}")
        
        # Test 3: AI Service
        tests_total += 1
        print("🔍 Testing AI service...")
        response = requests.get(f"{base_url}/health/ai", timeout=30)
        
        if response.status_code == 200:
            print("✅ AI service PASSED!")
            tests_passed += 1
        else:
            print(f"❌ AI service FAILED: {response.status_code}")
        
        # Test 4: Voice Service
        tests_total += 1
        print("🔍 Testing voice service...")
        response = requests.get(f"{base_url}/health/voice", timeout=30)
        
        if response.status_code == 200:
            print("✅ Voice service PASSED!")
            tests_passed += 1
        else:
            print(f"❌ Voice service FAILED: {response.status_code}")
        
        # Test 5: Live Query Test
        tests_total += 1
        print("🔍 Testing live database query...")
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
            print("✅ Live query test PASSED!")
            print(f"   Response: {result.get('response', 'No response')[:150]}...")
            tests_passed += 1
        else:
            print(f"❌ Live query test FAILED: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
        
        # Test 6: Analytics Dashboard
        tests_total += 1
        print("🔍 Testing analytics dashboard...")
        response = requests.get(f"{base_url}/analytics/dashboard", timeout=30)
        
        if response.status_code == 200:
            print("✅ Analytics dashboard PASSED!")
            tests_passed += 1
        else:
            print(f"❌ Analytics dashboard FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Live testing error: {e}")
    
    print(f"\n📊 LIVE SYSTEM TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    return tests_passed == tests_total

def configure_webhooks():
    """Display webhook configuration instructions"""
    print("\n🔗 WEBHOOK CONFIGURATION:")
    print("="*60)
    
    print("\n📞 ELEVENLABS CONFIGURATION:")
    print("1. Go to: https://elevenlabs.io/app/conversational-ai")
    print("2. Find agent: agent_6501k1bae0n2ebbs8dmvwgzjmbjy")
    print("3. Update webhook URL to:")
    print("   https://jen-ai-assistant.onrender.com/elevenlabs/webhook")
    
    print("\n📱 TWILIO CONFIGURATION (when ready):")
    print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
    print("2. Select your phone number")
    print("3. Set voice webhook to:")
    print("   https://jen-ai-assistant.onrender.com/twilio/voice")
    print("4. Set SMS webhook to:")
    print("   https://jen-ai-assistant.onrender.com/twilio/sms")

def main():
    """Ultimate live production deployment"""
    
    # Step 1: Deploy to Render
    service_id = deploy_to_render_live()
    if not service_id:
        print("❌ DEPLOYMENT FAILED!")
        return 1
    
    # Step 2: Wait for deployment
    print("\n" + "="*60)
    deployment_ready = wait_for_deployment_live(service_id)
    
    # Step 3: Test live system
    print("\n" + "="*60)
    system_working = test_live_system()
    
    # Step 4: Display webhook configuration
    configure_webhooks()
    
    # Final status
    print("\n" + "="*80)
    print("🎉 JEN AI ASSISTANT LIVE PRODUCTION DEPLOYMENT")
    print("="*80)
    
    if system_working:
        print("✅ DEPLOYMENT: SUCCESS")
        print("✅ SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ ALL TESTS: PASSED")
    else:
        print("⚠️  DEPLOYMENT: PARTIAL SUCCESS")
        print("⚠️  SYSTEM STATUS: NEEDS MONITORING")
    
    print(f"\n🌐 LIVE SYSTEM URLs:")
    print(f"   Main Service: https://jen-ai-assistant.onrender.com")
    print(f"   Health Check: https://jen-ai-assistant.onrender.com/health")
    print(f"   API Docs: https://jen-ai-assistant.onrender.com/docs")
    print(f"   Analytics: https://jen-ai-assistant.onrender.com/analytics/dashboard")
    print(f"   GitHub: https://github.com/jaredblank/jen-ai-assistant")
    
    print(f"\n🎤 READY FOR PRODUCTION USE!")
    print("   Real estate agents can now call and get instant AI-powered")
    print("   responses to business questions with live database data!")
    print("="*80)
    
    return 0 if system_working else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)