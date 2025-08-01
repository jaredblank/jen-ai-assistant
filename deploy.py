#!/usr/bin/env python3
"""
Jen AI Assistant - Production Deployment Script
Rock solid deployment for Render.com and local development
"""

import os
import sys
import json
import subprocess
import requests
import time
import asyncio
from datetime import datetime

def print_banner():
    """Display deployment banner"""
    print("""
    ==========================================
          JEN AI ASSISTANT DEPLOYMENT
         Rock Solid Production Setup
    ==========================================
    """)

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[FAIL] Python 3.8+ required")
        return False
    print("[PASS] Python version OK")
    
    # Check required files
    required_files = [
        'main.py', 'requirements.txt', '.env', 'start.py',
        'database_service.py', 'ai_service.py', 'voice_service.py', 
        'auth_service.py', 'twilio_service.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"[FAIL] Missing required file: {file}")
            return False
    print("[PASS] Required files present")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("[PASS] Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("[FAIL] Failed to install dependencies")
        return False

def run_tests():
    """Run comprehensive tests"""
    print("Running comprehensive tests...")
    try:
        result = subprocess.run([sys.executable, "test_jen.py"], 
                               capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("[PASS] All tests passed")
            return True
        else:
            print("[FAIL] Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("[FAIL] Tests timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Test execution failed: {e}")
        return False

def start_server(port=8001):
    """Start the server for testing"""
    print(f"Starting server on port {port}...")
    
    # Set environment variables
    os.environ["PORT"] = str(port)
    os.environ["HOST"] = "127.0.0.1"
    
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Test if server is running
        response = requests.get(f"http://127.0.0.1:{port}/health", timeout=10)
        if response.status_code == 200:
            print("[PASS] Server started successfully")
            return process
        else:
            print("[FAIL] Server health check failed")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"[FAIL] Failed to start server: {e}")
        return None

def run_production_tests(port=8001):
    """Run production tests against running server"""
    print("Running production tests...")
    
    # Set test environment
    os.environ["TEST_BASE_URL"] = f"http://127.0.0.1:{port}"
    
    try:
        result = subprocess.run([sys.executable, "test_production.py"], 
                               capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("[PASS] Production tests passed")
            return True
        else:
            print("[FAIL] Production tests failed")
            print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
            print("STDERR:", result.stderr[-1000:])
            return False
            
    except subprocess.TimeoutExpired:
        print("[FAIL] Production tests timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Production test execution failed: {e}")
        return False

def create_deployment_package():
    """Create deployment package for Render.com"""
    print("Creating deployment package...")
    
    # Create deployment info
    deployment_info = {
        "service_name": "jen-ai-assistant",
        "description": "The Ultimate Voice-Powered Real Estate AI Assistant",
        "runtime": "python3",
        "build_command": "pip install -r requirements.txt",
        "start_command": "python start.py",
        "health_check_path": "/health",
        "environment": "production",
        "created_at": datetime.now().isoformat(),
        "features": [
            "Voice-to-Database Integration",
            "ElevenLabs TTS Integration",
            "Twilio Phone System",
            "Natural Language Processing",
            "Real-time WebSocket Support",
            "Comprehensive Analytics"
        ],
        "endpoints": {
            "health": "/health",
            "text_query": "/text/query",
            "voice_query": "/voice/query",
            "elevenlabs_webhook": "/elevenlabs/webhook",
            "twilio_voice": "/twilio/voice",
            "twilio_sms": "/twilio/sms",
            "analytics": "/analytics/dashboard"
        }
    }
    
    with open("deployment_info.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print("[PASS] Deployment package created")
    return True

def generate_deployment_instructions():
    """Generate deployment instructions"""
    instructions = """
# Jen AI Assistant - Deployment Instructions

## Render.com Deployment

### 1. Create New Web Service
- Go to https://render.com/dashboard
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Use these settings:

### 2. Basic Settings
- **Name**: jen-ai-assistant
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start.py`
- **Instance Type**: Starter (can upgrade later)

### 3. Environment Variables
Set these in Render Dashboard:

```
# Database
SQLSERVER_HOST=YOUR_DB_HOST_HERE
SQLSERVER_DB=Broker_Mgmt
SQLSERVER_USER=Jared
SQLSERVER_PASSWORD=[from credentials.md]
SQLSERVER_PORT=1433

# AI Service
OPENAI_API_KEY=[OpenRouter key from credentials.md]
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini

# ElevenLabs
ELEVENLABS_API_KEY=[from credentials.md]
JEN_VOICE_ID=tnSpp4vdxKPjI9w0GnoV
JEN_AGENT_ID=agent_6501k1bae0n2ebbs8dmvwgzjmbjy

# Twilio (optional - add when available)
TWILIO_ACCOUNT_SID=[your Twilio account SID]
TWILIO_AUTH_TOKEN=[your Twilio auth token]
TWILIO_PHONE_NUMBER=[your Twilio phone number]

# Performance
PORT=8000
HOST=0.0.0.0
MAX_WORKERS=1
```

### 4. Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Test at: https://jen-ai.onrender.com

### 5. Configure Webhooks
After deployment:

**ElevenLabs:**
- Go to ElevenLabs dashboard
- Update webhook URL to: https://jen-ai.onrender.com/elevenlabs/webhook

**Twilio (when ready):**
- Go to Twilio Console
- Configure voice webhook: https://jen-ai.onrender.com/twilio/voice
- Configure SMS webhook: https://jen-ai.onrender.com/twilio/sms

## Testing Deployment

### Health Check
```bash
curl https://jen-ai.onrender.com/health
```

### Text Query Test
```bash
curl -X POST https://jen-ai.onrender.com/text/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is my total income this year?", "user_id": "121901"}'
```

### Voice Query Test
Call the configured phone number and ask: "What is my total income this year?"

## Monitoring

### Endpoints to Monitor
- `/health` - Overall system health
- `/health/database` - Database connectivity
- `/health/ai` - AI service status
- `/health/voice` - Voice service status
- `/analytics/dashboard` - Usage statistics

### Performance Metrics
- Response time < 2 seconds for cached queries
- Response time < 10 seconds for AI-generated queries  
- 99%+ uptime
- Error rate < 1%

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify SQL Server credentials
2. **AI Service**: Check OpenRouter API key and quotas
3. **Voice Service**: Verify ElevenLabs API key and voice ID
4. **Webhook Issues**: Check endpoint URLs and SSL certificates

### Logs
- View logs in Render dashboard
- Enable debug logging with LOG_LEVEL=DEBUG

## Support
- Documentation: See README.md and CLAUDE.md
- Test Suite: Run `python test_production.py`
- Health Checks: Monitor `/health` endpoints
"""
    
    with open("DEPLOYMENT.md", "w") as f:
        f.write(instructions)
    
    print("[PASS] Deployment instructions generated")
    return True

def main():
    """Main deployment function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("[FAIL] Prerequisites not met. Please fix issues and try again.")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("[FAIL] Failed to install dependencies.")
        return 1
    
    # Run tests
    if not run_tests():
        print("[FAIL] Tests failed. Please fix issues and try again.")
        return 1
    
    # Start server for production testing
    server_process = start_server(8001)
    if not server_process:
        print("[FAIL] Failed to start server for testing.")
        return 1
    
    try:
        # Run production tests
        production_tests_passed = run_production_tests(8001)
        
        # Stop server
        server_process.terminate()
        server_process.wait()
        
        if not production_tests_passed:
            print("[FAIL] Production tests failed.")
            return 1
        
        # Create deployment package
        if not create_deployment_package():
            print("[FAIL] Failed to create deployment package.")
            return 1
        
        # Generate deployment instructions
        if not generate_deployment_instructions():
            print("[FAIL] Failed to generate deployment instructions.")
            return 1
        
        print("\n" + "="*60)
        print("JEN AI ASSISTANT DEPLOYMENT READY!")
        print("="*60)
        print("[PASS] All tests passed")
        print("[PASS] Deployment package created")
        print("[PASS] Instructions generated")
        print("\nNext steps:")
        print("1. Push code to GitHub")
        print("2. Follow DEPLOYMENT.md instructions")
        print("3. Deploy to Render.com")
        print("4. Configure webhooks")
        print("5. Test production deployment")
        print("="*60)
        
        return 0
        
    finally:
        # Ensure server is stopped
        if server_process and server_process.poll() is None:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)