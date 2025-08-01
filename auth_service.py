"""
Authentication Service for Jen AI Assistant
Handles user identification and security
"""

import os
import logging
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from database_service import db_service

load_dotenv()
log = logging.getLogger("jen.auth")

class AuthService:
    """Authentication and user identification service"""
    
    def __init__(self):
        self.api_keys = {
            os.getenv("JEN_API_KEY", "JenAI2025"): "primary",
            os.getenv("API_SECRET_KEY", "EquityRachel2025ChatAPI"): "legacy"
        }
        
        # Known caller ID mappings (can be extended with database lookups)
        self.caller_mappings = {
            # Add known phone numbers -> user IDs here
            # "+15551234567": "121901"
        }
        
        log.info("AuthService initialized")
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key is valid"""
        return api_key in self.api_keys
    
    async def identify_user(self, caller_id: Optional[str] = None, transcript: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Identify user from caller ID or speech transcript"""
        
        # Try caller ID first
        if caller_id and caller_id in self.caller_mappings:
            user_id = self.caller_mappings[caller_id]
            user_info = await db_service.get_user_info(user_id)
            if user_info:
                log.info(f"User identified by caller ID: {user_info['name']}")
                return user_info
        
        # Try to extract identification from transcript
        if transcript:
            user_info = await self._identify_from_speech(transcript)
            if user_info:
                log.info(f"User identified from speech: {user_info['name']}")
                return user_info
        
        log.warning(f"Could not identify user - caller_id: {caller_id}, transcript: {transcript}")
        return None
    
    async def _identify_from_speech(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Extract user identification from speech transcript"""
        
        text = transcript.lower().strip()
        
        # Look for agent ID patterns
        agent_id_patterns = [
            r"my agent id is (\d+)",
            r"agent id (\d+)",
            r"id is (\d+)",
            r"i am agent (\d+)",
            r"this is agent (\d+)",
            r"agent number (\d+)",
            r"my id is (\d+)"
        ]
        
        for pattern in agent_id_patterns:
            match = re.search(pattern, text)
            if match:
                agent_id = match.group(1)
                user_info = await db_service.get_user_info(agent_id)
                if user_info:
                    return user_info
        
        # Look for name patterns
        name_patterns = [
            r"my name is ([a-zA-Z\s]+)",
            r"i am ([a-zA-Z\s]+)",
            r"this is ([a-zA-Z\s]+)",
            r"i'm ([a-zA-Z\s]+)",
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Remove common words that might be picked up
                name = re.sub(r'\b(calling|speaking|here)\b', '', name).strip()
                
                if len(name.split()) >= 2:  # At least first and last name
                    user_info = await db_service.find_user_by_name(name)
                    if user_info:
                        return user_info
        
        # Look for common greetings with names
        greeting_patterns = [
            r"hi\s+(?:this\s+is\s+|i'm\s+|i\s+am\s+)?([a-zA-Z\s]+)",
            r"hello\s+(?:this\s+is\s+|i'm\s+|i\s+am\s+)?([a-zA-Z\s]+)",
            r"hey\s+(?:this\s+is\s+|i'm\s+|i\s+am\s+)?([a-zA-Z\s]+)"
        ]
        
        for pattern in greeting_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\b(jen|calling|speaking|here|and)\b', '', name).strip()
                
                if len(name.split()) >= 2 and len(name) > 3:
                    user_info = await db_service.find_user_by_name(name)
                    if user_info:
                        return user_info
        
        return None
    
    def get_user_permissions(self, user_info: Dict[str, Any]) -> Dict[str, bool]:
        """Get user permissions based on user type"""
        
        user_type = user_info.get("user_type", "agent")
        
        if user_type == "broker":
            return {
                "can_view_own_data": True,
                "can_view_team_data": True,
                "can_view_branch_analytics": True,
                "can_manage_agents": True,
                "can_view_commission_reports": True
            }
        elif user_type == "agent":
            return {
                "can_view_own_data": True,
                "can_view_team_data": False,
                "can_view_branch_analytics": False,
                "can_manage_agents": False,
                "can_view_commission_reports": True
            }
        else:
            return {
                "can_view_own_data": True,
                "can_view_team_data": False,
                "can_view_branch_analytics": False,
                "can_manage_agents": False,
                "can_view_commission_reports": False
            }
    
    async def log_access_attempt(self, user_id: Optional[str], caller_id: Optional[str], 
                                transcript: Optional[str], success: bool):
        """Log access attempts for security monitoring"""
        
        log.info(f"Access attempt - User: {user_id}, Caller: {caller_id}, Success: {success}")
        
        # In production, you'd store this in a security log table
        # For now, just log it
        
    def is_authorized_for_query(self, user_info: Dict[str, Any], query_type: str) -> bool:
        """Check if user is authorized for specific query type"""
        
        permissions = self.get_user_permissions(user_info)
        
        # Define query type permissions
        query_permissions = {
            "own_income": "can_view_own_data",
            "own_deals": "can_view_own_data", 
            "team_performance": "can_view_team_data",
            "branch_analytics": "can_view_branch_analytics",
            "agent_management": "can_manage_agents"
        }
        
        required_permission = query_permissions.get(query_type, "can_view_own_data")
        return permissions.get(required_permission, False)

# Global instance
auth_service = AuthService()