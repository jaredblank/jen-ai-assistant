#!/usr/bin/env python3
"""
Jen AI Assistant - Production Test Suite
Comprehensive testing including Twilio integration
"""

import os
import sys
import asyncio
import json
import requests
import logging
from typing import Dict, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("jen.production_test")

class ProductionTestSuite:
    """Production-ready test suite for Jen AI Assistant"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.results = {}
    
    def test_result(self, test_name: str, success: bool, message: str = ""):
        """Record test result"""
        if success:
            self.passed += 1
            status = "PASS"
            log.info(f"[PASS] {test_name}: {message}")
        else:
            self.failed += 1
            status = "FAIL"
            log.error(f"[FAIL] {test_name}: {message}")
        
        self.results[test_name] = {"status": status, "message": message}
    
    async def test_health_endpoints(self):
        """Test all health check endpoints"""
        try:
            # Main health check
            response = requests.get(f"{self.base_url}/health", timeout=10)
            main_healthy = response.status_code == 200
            self.test_result("Main Health Check", main_healthy, f"Status: {response.status_code}")
            
            # Database health
            response = requests.get(f"{self.base_url}/health/database", timeout=10)
            db_healthy = response.status_code == 200
            self.test_result("Database Health", db_healthy, f"Status: {response.status_code}")
            
            # AI service health
            response = requests.get(f"{self.base_url}/health/ai", timeout=10)
            ai_healthy = response.status_code == 200
            self.test_result("AI Service Health", ai_healthy, f"Status: {response.status_code}")
            
            # Voice service health
            response = requests.get(f"{self.base_url}/health/voice", timeout=10)
            voice_healthy = response.status_code == 200
            self.test_result("Voice Service Health", voice_healthy, f"Status: {response.status_code}")
            
            # Twilio health
            response = requests.get(f"{self.base_url}/health/twilio", timeout=10)
            twilio_healthy = response.status_code == 200
            if twilio_healthy:
                data = response.json()
                twilio_available = data.get('twilio_available', False)
                self.test_result("Twilio Health", twilio_available, f"Available: {twilio_available}")
            else:
                self.test_result("Twilio Health", False, f"Status: {response.status_code}")
        
        except Exception as e:
            self.test_result("Health Endpoints", False, str(e))
    
    async def test_api_endpoints(self):
        """Test API endpoints"""
        try:
            # Test text query endpoint
            query_data = {
                "question": "What is my total income this year?",
                "user_id": "121901"
            }
            
            response = requests.post(
                f"{self.base_url}/text/query",
                json=query_data,
                timeout=30
            )
            
            text_query_works = response.status_code == 200
            if text_query_works:
                data = response.json()
                has_response = 'response' in data and len(data['response']) > 0
                self.test_result("Text Query API", has_response, f"Response length: {len(data.get('response', ''))}")
            else:
                self.test_result("Text Query API", False, f"Status: {response.status_code}")
            
            # Test analytics dashboard
            response = requests.get(f"{self.base_url}/analytics/dashboard", timeout=10)
            analytics_works = response.status_code == 200
            self.test_result("Analytics Dashboard", analytics_works, f"Status: {response.status_code}")
            
        except Exception as e:
            self.test_result("API Endpoints", False, str(e))
    
    async def test_webhook_endpoints(self):
        """Test webhook endpoints"""
        try:
            # Test ElevenLabs webhook
            webhook_data = {
                "call_id": "test_call_production",
                "caller_number": "+15551234567",
                "status": "started"
            }
            
            response = requests.post(
                f"{self.base_url}/elevenlabs/webhook",
                json=webhook_data,
                timeout=30
            )
            
            elevenlabs_webhook_works = response.status_code == 200
            self.test_result("ElevenLabs Webhook", elevenlabs_webhook_works, f"Status: {response.status_code}")
            
            # Test Twilio voice webhook (simulate TwiML form data)
            twilio_voice_data = {
                "CallSid": "test_call_twilio_123",
                "From": "+15551234567",
                "To": "+15559876543",
                "CallStatus": "in-progress"
            }
            
            response = requests.post(
                f"{self.base_url}/twilio/voice",
                data=twilio_voice_data,  # Form data, not JSON
                timeout=30
            )
            
            twilio_voice_works = response.status_code == 200
            if twilio_voice_works:
                # Check if response is TwiML
                is_twiml = "xml" in response.headers.get("content-type", "").lower()
                self.test_result("Twilio Voice Webhook", is_twiml, f"Content-Type: {response.headers.get('content-type')}")
            else:
                self.test_result("Twilio Voice Webhook", False, f"Status: {response.status_code}")
            
            # Test Twilio SMS webhook
            twilio_sms_data = {
                "MessageSid": "test_sms_123",
                "From": "+15551234567",
                "To": "+15559876543",
                "Body": "Hello Jen, what is my total income?"
            }
            
            response = requests.post(
                f"{self.base_url}/twilio/sms",
                data=twilio_sms_data,
                timeout=30
            )
            
            twilio_sms_works = response.status_code == 200
            if twilio_sms_works:
                is_twiml = "xml" in response.headers.get("content-type", "").lower()
                self.test_result("Twilio SMS Webhook", is_twiml, f"Content-Type: {response.headers.get('content-type')}")
            else:
                self.test_result("Twilio SMS Webhook", False, f"Status: {response.status_code}")
            
        except Exception as e:
            self.test_result("Webhook Endpoints", False, str(e))
    
    async def test_speech_processing(self):
        """Test speech processing workflow"""
        try:
            # Simulate Twilio speech processing webhook
            speech_data = {
                "CallSid": "test_speech_call_123",
                "From": "+15551234567",
                "SpeechResult": "Hi, my name is Jared Blank and my agent ID is 121901. What is my total income this year?"
            }
            
            response = requests.post(
                f"{self.base_url}/twilio/process-speech",
                data=speech_data,
                timeout=45  # Longer timeout for AI processing
            )
            
            speech_processing_works = response.status_code == 200
            if speech_processing_works:
                is_twiml = "xml" in response.headers.get("content-type", "").lower()
                response_text = response.text
                # Check if response contains expected elements
                has_say = "<Say>" in response_text or "<say>" in response_text
                self.test_result("Speech Processing", has_say, f"TwiML generated with Say element")
            else:
                self.test_result("Speech Processing", False, f"Status: {response.status_code}")
            
        except Exception as e:
            self.test_result("Speech Processing", False, str(e))
    
    async def test_performance_endpoints(self):
        """Test performance and monitoring endpoints"""
        try:
            # Test call logs
            response = requests.get(f"{self.base_url}/twilio/call-logs", timeout=10)
            call_logs_work = response.status_code == 200
            self.test_result("Call Logs Endpoint", call_logs_work, f"Status: {response.status_code}")
            
            # Test message logs
            response = requests.get(f"{self.base_url}/twilio/message-logs", timeout=10)
            message_logs_work = response.status_code == 200
            self.test_result("Message Logs Endpoint", message_logs_work, f"Status: {response.status_code}")
            
        except Exception as e:
            self.test_result("Performance Endpoints", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        try:
            # Test invalid text query
            invalid_query = {
                "question": "",  # Empty question
                "user_id": "invalid_user"
            }
            
            response = requests.post(
                f"{self.base_url}/text/query",
                json=invalid_query,
                timeout=15
            )
            
            # Should handle gracefully (200 with error message or 400 status)
            handles_invalid = response.status_code in [200, 400]
            self.test_result("Invalid Query Handling", handles_invalid, f"Status: {response.status_code}")
            
            # Test invalid webhook data
            invalid_webhook = {}  # Empty webhook data
            
            response = requests.post(
                f"{self.base_url}/twilio/voice",
                data=invalid_webhook,
                timeout=15
            )
            
            # Should return valid TwiML even for invalid data
            webhook_error_handling = response.status_code == 200
            self.test_result("Webhook Error Handling", webhook_error_handling, f"Status: {response.status_code}")
            
        except Exception as e:
            self.test_result("Error Handling", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print("JEN AI ASSISTANT - PRODUCTION TEST RESULTS")
        print("="*70)
        print(f"Base URL: {self.base_url}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} [PASS]")
        print(f"Failed: {self.failed} [FAIL]")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*70)
        
        if self.failed > 0:
            print("\nFAILED TESTS:")
            for test_name, result in self.results.items():
                if result["status"] == "FAIL":
                    print(f"[FAIL] {test_name}: {result['message']}")
        
        print(f"\n{'PRODUCTION READY!' if self.failed == 0 else 'ISSUES DETECTED - CHECK FAILED TESTS'}")
        return self.failed == 0

async def main():
    """Main test function"""
    
    # Allow testing different environments
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    print(f"""
    ========================================
       JEN AI ASSISTANT PRODUCTION TEST
         Testing: {base_url}
    ========================================
    """)
    
    suite = ProductionTestSuite(base_url)
    
    # Run all test categories
    print("Testing health endpoints...")
    await suite.test_health_endpoints()
    
    print("Testing API endpoints...")
    await suite.test_api_endpoints()
    
    print("Testing webhook endpoints...")
    await suite.test_webhook_endpoints()
    
    print("Testing speech processing...")
    await suite.test_speech_processing()
    
    print("Testing performance endpoints...")
    await suite.test_performance_endpoints()
    
    print("Testing error handling...")
    await suite.test_error_handling()
    
    # Print summary
    all_passed = suite.print_summary()
    
    # Save results to file
    with open("production_test_results.json", "w") as f:
        json.dump({
            "base_url": base_url,
            "results": suite.results,
            "summary": {
                "total": suite.passed + suite.failed,
                "passed": suite.passed,
                "failed": suite.failed,
                "success_rate": (suite.passed / (suite.passed + suite.failed) * 100) if (suite.passed + suite.failed) > 0 else 0
            }
        }, f, indent=2)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)