#!/usr/bin/env python3
"""
Jen AI Assistant - Comprehensive Test Suite
Test all core functionality including voice, database, and AI integration
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("jen.test")

class JenTestSuite:
    """Comprehensive test suite for Jen AI Assistant"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = {}
    
    def test_result(self, test_name: str, success: bool, message: str = ""):
        """Record test result"""
        if success:
            self.passed += 1
            status = "PASS"
            log.info(f"[PASS] {test_name}: {status} {message}")
        else:
            self.failed += 1
            status = "FAIL"
            log.error(f"[FAIL] {test_name}: {status} {message}")
        
        self.results[test_name] = {"status": status, "message": message}
    
    async def test_database_connection(self):
        """Test database connectivity and basic queries"""
        try:
            from database_service import db_service
            
            # Test connection
            healthy = await db_service.health_check()
            self.test_result("Database Connection", healthy, "Health check passed")
            
            if healthy:
                # Test user lookup
                user_info = await db_service.get_user_info("121901")
                user_found = user_info is not None
                self.test_result("User Lookup", user_found, f"Found: {user_info.get('name', 'N/A') if user_info else 'None'}")
                
                # Test basic query
                results = await db_service.execute_query("SELECT COUNT(*) as total FROM TBL_USER_CREATE WHERE USTATUS = 1")
                query_success = len(results) > 0
                self.test_result("Basic Query", query_success, f"Active users: {results[0].get('total', 0) if results else 0}")
        
        except Exception as e:
            self.test_result("Database Connection", False, str(e))
    
    async def test_ai_service(self):
        """Test AI service functionality"""
        try:
            from ai_service import jen_ai
            
            # Test health check
            healthy = jen_ai.health_check()
            self.test_result("AI Service Health", healthy, "API key configured")
            
            if healthy:
                # Test SQL generation
                sql = await jen_ai.generate_sql_query("What is my total income this year?", "agent", "121901")
                sql_generated = sql is not None and len(sql.strip()) > 0
                self.test_result("SQL Generation", sql_generated, f"Generated: {len(sql) if sql else 0} chars")
                
                # Test cached queries
                cached_sql = jen_ai._get_cached_query("total income this year", "agent")
                cache_works = cached_sql is not None
                self.test_result("Query Caching", cache_works, "Cached query found")
                
                # Test response generation
                mock_data = [{"total_income": 125000.50}]
                response = jen_ai.generate_response("What is my total income?", mock_data, "John Smith", "agent")
                response_generated = len(response) > 0
                self.test_result("Response Generation", response_generated, f"Response: {len(response)} chars")
        
        except Exception as e:
            self.test_result("AI Service", False, str(e))
    
    async def test_voice_service(self):
        """Test voice processing capabilities"""
        try:
            from voice_service import voice_processor
            
            # Test health check
            healthy = voice_processor.health_check()
            self.test_result("Voice Service Health", healthy, "ElevenLabs API key configured")
            
            if healthy:
                # Test text-to-speech
                audio = await voice_processor.text_to_speech("Hello, this is a test of Jen's voice.")
                tts_works = audio is not None
                self.test_result("Text-to-Speech", tts_works, f"Audio generated: {len(audio) if audio else 0} chars")
                
                # Test webhook processing
                mock_webhook = {
                    "call_id": "test_call_123",
                    "caller_number": "+15551234567",
                    "status": "started"
                }
                webhook_result = await voice_processor.process_phone_webhook(mock_webhook)
                webhook_works = webhook_result.get("status") == "greeting_sent"
                self.test_result("Webhook Processing", webhook_works, f"Result: {webhook_result.get('status', 'unknown')}")
        
        except Exception as e:
            self.test_result("Voice Service", False, str(e))
    
    async def test_auth_service(self):
        """Test authentication and user identification"""
        try:
            from auth_service import auth_service
            
            # Test API key verification
            valid_key = auth_service.verify_api_key("JenAI2025")
            self.test_result("API Key Validation", valid_key, "Primary key valid")
            
            # Test user identification from speech
            test_transcript = "Hi, my name is John Smith and my agent id is 121901"
            user_info = await auth_service.identify_user(transcript=test_transcript)
            identification_works = user_info is not None
            self.test_result("Speech Identification", identification_works, f"Identified: {user_info.get('name', 'None') if user_info else 'None'}")
            
            # Test permission system
            if user_info:
                permissions = auth_service.get_user_permissions(user_info)
                permissions_work = isinstance(permissions, dict) and len(permissions) > 0
                self.test_result("Permission System", permissions_work, f"Permissions: {len(permissions)} rules")
        
        except Exception as e:
            self.test_result("Auth Service", False, str(e))
    
    async def test_integration_workflow(self):
        """Test complete integration workflow"""
        try:
            from database_service import db_service
            from ai_service import jen_ai
            from auth_service import auth_service
            
            # Simulate complete query workflow
            question = "What is my total income this year?"
            user_id = "121901"
            user_type = "agent"
            
            # Step 1: Generate SQL
            sql = await jen_ai.generate_sql_query(question, user_type, user_id)
            
            # Step 2: Execute query
            if sql:
                results = await db_service.execute_query(sql, [user_id])
                
                # Step 3: Generate response
                if results:
                    user_info = await db_service.get_user_info(user_id)
                    if user_info:
                        response = jen_ai.generate_response(question, results, user_info['name'], user_type)
                        workflow_success = len(response) > 0
                        self.test_result("Complete Workflow", workflow_success, f"Response: {response[:100]}...")
                        return
            
            self.test_result("Complete Workflow", False, "Workflow failed at some step")
        
        except Exception as e:
            self.test_result("Complete Workflow", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        try:
            from database_service import db_service
            from ai_service import jen_ai
            
            # Test invalid SQL
            try:
                await db_service.execute_query("SELECT * FROM non_existent_table")
                self.test_result("Error Handling - Invalid SQL", False, "Should have thrown exception")
            except:
                self.test_result("Error Handling - Invalid SQL", True, "Exception caught properly")
            
            # Test invalid user ID
            user_info = await db_service.get_user_info("999999")
            no_user_handled = user_info is None
            self.test_result("Error Handling - Invalid User", no_user_handled, "Returned None for invalid user")
            
            # Test empty question
            response = jen_ai.generate_response("", [], "Test User", "agent")
            empty_handled = len(response) > 0
            self.test_result("Error Handling - Empty Data", empty_handled, "Generated fallback response")
        
        except Exception as e:
            self.test_result("Error Handling", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("JEN AI ASSISTANT - TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} [PASS]")
        print(f"Failed: {self.failed} [FAIL]")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*60)
        
        if self.failed > 0:
            print("\nFAILED TESTS:")
            for test_name, result in self.results.items():
                if result["status"] == "FAIL":
                    print(f"[FAIL] {test_name}: {result['message']}")
        
        print(f"\n{'ALL TESTS PASSED!' if self.failed == 0 else 'SOME TESTS FAILED'}")
        return self.failed == 0

async def main():
    """Main test function"""
    print("""
    ==========================================
          JEN AI ASSISTANT TEST SUITE
            Comprehensive Testing
    ==========================================
    """)
    
    suite = JenTestSuite()
    
    # Run all test categories
    await suite.test_database_connection()
    await suite.test_ai_service()
    await suite.test_voice_service()
    await suite.test_auth_service()
    await suite.test_integration_workflow()
    await suite.test_error_handling()
    
    # Print summary
    all_passed = suite.print_summary()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(suite.results, f, indent=2)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)