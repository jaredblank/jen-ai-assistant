"""
Twilio Service for Jen AI Assistant
Advanced phone call handling and SMS capabilities
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

try:
    from twilio.rest import Client
    from twilio.twiml.voice_response import VoiceResponse, Gather
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

load_dotenv()
log = logging.getLogger("jen.twilio")

class TwilioService:
    """Advanced Twilio integration for phone calls and SMS"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.phone_number_sid = os.getenv("JEN_PHONE_NUMBER_SID", "")
        
        self.client = None
        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                log.info(f"TwilioService initialized - Phone: {self.phone_number}")
            except Exception as e:
                log.error(f"Failed to initialize Twilio client: {e}")
        else:
            log.warning("Twilio not available - missing credentials or library")
    
    def health_check(self) -> bool:
        """Check if Twilio service is healthy"""
        return self.client is not None
    
    def create_voice_response(self, message: str, gather_input: bool = False) -> str:
        """Create TwiML voice response"""
        try:
            response = VoiceResponse()
            
            if gather_input:
                # Gather speech input from caller
                gather = Gather(
                    input='speech',
                    timeout=10,
                    speech_timeout='auto',
                    action='/twilio/process-speech',
                    method='POST'
                )
                gather.say(message, voice='Polly.Joanna-Neural')
                response.append(gather)
                
                # Fallback if no input
                response.say("I didn't hear anything. Please call back when you're ready to ask a question.")
            else:
                # Simple message
                response.say(message, voice='Polly.Joanna-Neural')
            
            return str(response)
            
        except Exception as e:
            log.error(f"Failed to create voice response: {e}")
            # Fallback response
            fallback = VoiceResponse()
            fallback.say("Sorry, I'm experiencing technical difficulties. Please try again later.")
            return str(fallback)
    
    def create_sms_response(self, message: str) -> str:
        """Create TwiML SMS response"""
        try:
            response = MessagingResponse()
            response.message(message)
            return str(response)
            
        except Exception as e:
            log.error(f"Failed to create SMS response: {e}")
            # Fallback response
            fallback = MessagingResponse()
            fallback.message("Sorry, I'm experiencing technical difficulties. Please try again later.")
            return str(fallback)
    
    async def make_outbound_call(self, to_number: str, message: str) -> Optional[str]:
        """Make an outbound call with a message"""
        try:
            if not self.client:
                log.error("Twilio client not initialized")
                return None
            
            # Create TwiML for the message
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="Polly.Joanna-Neural">{message}</Say>
            </Response>"""
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                twiml=twiml
            )
            
            log.info(f"Outbound call initiated: {call.sid}")
            return call.sid
            
        except Exception as e:
            log.error(f"Failed to make outbound call: {e}")
            return None
    
    async def send_sms(self, to_number: str, message: str) -> Optional[str]:
        """Send SMS message"""
        try:
            if not self.client:
                log.error("Twilio client not initialized")
                return None
            
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            log.info(f"SMS sent: {message.sid}")
            return message.sid
            
        except Exception as e:
            log.error(f"Failed to send SMS: {e}")
            return None
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Twilio webhook"""
        try:
            log.info(f"Processing Twilio webhook: {webhook_data}")
            
            # Extract webhook type
            if 'MessageSid' in webhook_data:
                # SMS webhook
                return await self._handle_sms_webhook(webhook_data)
            elif 'CallSid' in webhook_data:
                # Voice webhook
                return await self._handle_voice_webhook(webhook_data)
            else:
                log.warning(f"Unknown webhook type: {webhook_data}")
                return {"status": "unknown_webhook_type"}
            
        except Exception as e:
            log.error(f"Webhook processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_sms_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SMS webhook"""
        try:
            from_number = webhook_data.get('From')
            message_body = webhook_data.get('Body', '').strip()
            message_sid = webhook_data.get('MessageSid')
            
            log.info(f"SMS from {from_number}: {message_body}")
            
            # Process the message through Jen AI
            # This would integrate with the main AI service
            response_message = f"Hi! I received your message: '{message_body}'. I'm Jen, your AI assistant. For detailed queries, please call me instead!"
            
            return {
                "status": "sms_processed",
                "message_sid": message_sid,
                "response": response_message,
                "twiml": self.create_sms_response(response_message)
            }
            
        except Exception as e:
            log.error(f"SMS webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_voice_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice call webhook"""
        try:
            call_sid = webhook_data.get('CallSid')
            from_number = webhook_data.get('From')
            call_status = webhook_data.get('CallStatus')
            speech_result = webhook_data.get('SpeechResult')
            
            log.info(f"Voice call from {from_number}, status: {call_status}")
            
            if call_status == 'in-progress' and not speech_result:
                # Initial call - ask for input
                greeting = """Hi! I'm Jen, your AI assistant for real estate data. 
                I can help you with questions about your income, deals, and performance. 
                What would you like to know?"""
                
                twiml = self.create_voice_response(greeting, gather_input=True)
                
                return {
                    "status": "call_started",
                    "call_sid": call_sid,
                    "twiml": twiml
                }
                
            elif speech_result:
                # Process speech input
                log.info(f"Speech detected: {speech_result}")
                
                # This would integrate with the main AI service
                response_message = f"I heard you ask: {speech_result}. Let me process that for you. This feature will be enhanced to provide real database results."
                
                twiml = self.create_voice_response(response_message, gather_input=False)
                
                return {
                    "status": "speech_processed",
                    "call_sid": call_sid,
                    "speech": speech_result,
                    "twiml": twiml
                }
            
            else:
                # Default handling
                default_message = "Thank you for calling Jen AI Assistant. Have a great day!"
                twiml = self.create_voice_response(default_message, gather_input=False)
                
                return {
                    "status": "call_handled",
                    "call_sid": call_sid,
                    "twiml": twiml
                }
            
        except Exception as e:
            log.error(f"Voice webhook handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_call_logs(self, limit: int = 50) -> list:
        """Get recent call logs"""
        try:
            if not self.client:
                return []
            
            calls = self.client.calls.list(limit=limit)
            
            call_logs = []
            for call in calls:
                call_logs.append({
                    "sid": call.sid,
                    "from": call.from_,
                    "to": call.to,
                    "status": call.status,
                    "direction": call.direction,
                    "duration": call.duration,
                    "start_time": call.start_time.isoformat() if call.start_time else None,
                    "end_time": call.end_time.isoformat() if call.end_time else None
                })
            
            return call_logs
            
        except Exception as e:
            log.error(f"Failed to get call logs: {e}")
            return []
    
    async def get_message_logs(self, limit: int = 50) -> list:
        """Get recent message logs"""
        try:
            if not self.client:
                return []
            
            messages = self.client.messages.list(limit=limit)
            
            message_logs = []
            for message in messages:
                message_logs.append({
                    "sid": message.sid,
                    "from": message.from_,
                    "to": message.to,
                    "body": message.body,
                    "status": message.status,
                    "direction": message.direction,
                    "date_created": message.date_created.isoformat() if message.date_created else None,
                    "date_sent": message.date_sent.isoformat() if message.date_sent else None
                })
            
            return message_logs
            
        except Exception as e:
            log.error(f"Failed to get message logs: {e}")
            return []

# Global instance
twilio_service = TwilioService()