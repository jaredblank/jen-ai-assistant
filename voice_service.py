"""
Voice Service for Jen AI Assistant
Handles speech-to-text, text-to-speech, and phone integrations
"""

import os
import logging
import base64
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("jen.voice")

class VoiceProcessor:
    """Voice processing service for phone and audio integration"""
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.jen_voice_id = os.getenv("JEN_VOICE_ID", "tnSpp4vdxKPjI9w0GnoV")  # Hope voice ID
        self.phone_number_sid = os.getenv("JEN_PHONE_NUMBER_SID")
        
        # ElevenLabs API endpoints
        self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        
        log.info(f"VoiceProcessor initialized - Voice ID: {self.jen_voice_id}")
    
    def health_check(self) -> bool:
        """Check if voice service is healthy"""
        return bool(self.elevenlabs_api_key)
    
    async def speech_to_text(self, audio_data: str) -> Optional[str]:
        """Convert speech to text using ElevenLabs or Whisper"""
        try:
            # For now, this is a placeholder
            # In production, you'd use ElevenLabs speech recognition or OpenAI Whisper
            log.info("Processing speech-to-text conversion")
            
            # Placeholder implementation
            # You would decode the base64 audio and send to speech recognition service
            
            return "What is my total income this year?"  # Mock response for testing
            
        except Exception as e:
            log.error(f"Speech-to-text conversion failed: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech using ElevenLabs"""
        try:
            if not self.elevenlabs_api_key:
                log.error("ElevenLabs API key not configured")
                return None
            
            url = f"{self.elevenlabs_base_url}/text-to-speech/{self.jen_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Convert audio bytes to base64 for transmission
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                log.info(f"Text-to-speech successful for: {text[:50]}...")
                return audio_base64
            else:
                log.error(f"ElevenLabs TTS failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            log.error(f"Text-to-speech conversion failed: {e}")
            return None
    
    async def process_phone_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming phone webhook from ElevenLabs"""
        try:
            log.info(f"Processing phone webhook: {webhook_data}")
            
            # Extract relevant information from the webhook
            call_id = webhook_data.get("call_id")
            caller_number = webhook_data.get("caller_number")
            speech_result = webhook_data.get("speech_result")
            call_status = webhook_data.get("status")
            
            # Process based on call status
            if call_status == "started":
                # Call just started - send greeting
                return await self._handle_call_start(call_id, caller_number)
                
            elif call_status == "speech_detected":
                # User spoke something - process the speech
                return await self._handle_speech(call_id, caller_number, speech_result)
                
            elif call_status == "ended":
                # Call ended - cleanup
                return await self._handle_call_end(call_id)
            
            return {"status": "processed", "action": "none"}
            
        except Exception as e:
            log.error(f"Phone webhook processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_call_start(self, call_id: str, caller_number: str) -> Dict[str, Any]:
        """Handle the start of a phone call"""
        try:
            # Generate greeting message
            greeting = "Hi! I'm Jen, your AI assistant. I can help you with questions about your real estate business. What would you like to know?"
            
            # Convert to speech
            audio_response = await self.text_to_speech(greeting)
            
            if audio_response:
                # Send response back to ElevenLabs to play to caller
                await self._send_audio_response(call_id, audio_response)
            
            return {
                "status": "greeting_sent",
                "call_id": call_id,
                "caller": caller_number
            }
            
        except Exception as e:
            log.error(f"Call start handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_speech(self, call_id: str, caller_number: str, speech_text: str) -> Dict[str, Any]:
        """Handle detected speech from caller"""
        try:
            log.info(f"Processing speech from {caller_number}: {speech_text}")
            
            # This is where you'd integrate with the main query processing
            # For now, return a placeholder response
            
            response_text = f"I heard you say: {speech_text}. I'm processing your request now."
            
            # Convert to speech
            audio_response = await self.text_to_speech(response_text)
            
            if audio_response:
                await self._send_audio_response(call_id, audio_response)
            
            return {
                "status": "speech_processed",
                "call_id": call_id,
                "transcript": speech_text,
                "response": response_text
            }
            
        except Exception as e:
            log.error(f"Speech handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_call_end(self, call_id: str) -> Dict[str, Any]:
        """Handle the end of a phone call"""
        try:
            log.info(f"Call ended: {call_id}")
            
            # Cleanup any resources, log the call, etc.
            
            return {
                "status": "call_ended",
                "call_id": call_id
            }
            
        except Exception as e:
            log.error(f"Call end handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_audio_response(self, call_id: str, audio_base64: str) -> bool:
        """Send audio response back to ElevenLabs phone system"""
        try:
            # This would send the audio back to ElevenLabs to play to the caller
            # Implementation depends on ElevenLabs phone API
            
            log.info(f"Sending audio response for call {call_id}")
            
            # Placeholder - actual implementation would use ElevenLabs phone API
            
            return True
            
        except Exception as e:
            log.error(f"Failed to send audio response: {e}")
            return False
    
    async def create_phone_agent(self, agent_config: Dict[str, Any]) -> Optional[str]:
        """Create a new phone agent in ElevenLabs"""
        try:
            if not self.elevenlabs_api_key:
                log.error("ElevenLabs API key not configured")
                return None
            
            url = f"{self.elevenlabs_base_url}/conversational-ai/agents"
            
            headers = {
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Default configuration for Jen
            default_config = {
                "name": "Jen AI Assistant",
                "voice_id": self.jen_voice_id,
                "system_prompt": """You are Jen, a helpful AI assistant for real estate professionals. 
                You help agents and brokers with questions about their business data, income, deals, and performance. 
                You are friendly, professional, and always ready to help with business insights.""",
                "first_message": "Hi! I'm Jen, your AI assistant. I can help you with questions about your real estate business. What would you like to know?",
                "language": "en",
                "max_duration_seconds": 600,
                "webhook_url": os.getenv("JEN_WEBHOOK_URL", "https://jen-ai.onrender.com/elevenlabs/webhook")
            }
            
            # Merge with provided config
            config = {**default_config, **agent_config}
            
            response = requests.post(url, json=config, headers=headers, timeout=30)
            
            if response.status_code == 201:
                result = response.json()
                agent_id = result.get("agent_id")
                log.info(f"Created phone agent: {agent_id}")
                return agent_id
            else:
                log.error(f"Failed to create phone agent: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            log.error(f"Phone agent creation failed: {e}")
            return None

# Global instance
voice_processor = VoiceProcessor()