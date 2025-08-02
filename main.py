#!/usr/bin/env python3
"""
Jen AI Assistant - The Ultimate Voice-Powered Real Estate AI

Complete system for voice-based real estate database queries.
Agents call Jen and get instant answers to any business question.
"""

import os
import logging
import json
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules
from database_service import DatabaseService
from ai_service import JenAI
from voice_service import VoiceProcessor
from auth_service import AuthService
from twilio_service import TwilioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Jen: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("jen.log")
    ]
)
log = logging.getLogger("jen")

# Initialize services
db_service = DatabaseService()
ai_service = JenAI()
voice_processor = VoiceProcessor()
auth_service = AuthService()
twilio_service = TwilioService()

# FastAPI app
app = FastAPI(
    title="Jen AI Assistant",
    description="The Ultimate Voice-Powered Real Estate AI Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class VoiceQueryRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    caller_id: Optional[str] = None
    session_id: Optional[str] = None

class TextQueryRequest(BaseModel):
    question: str
    user_id: str
    user_type: str = "agent"
    session_id: Optional[str] = None

class CallbackRequest(BaseModel):
    call_sid: str
    from_number: str
    speech_result: Optional[str] = None
    recording_url: Optional[str] = None

# Active WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

@app.get("/")
async def root():
    """Root endpoint - Jen's introduction"""
    return {
        "service": "Jen AI Assistant",
        "version": "1.0.0",
        "description": "The Ultimate Voice-Powered Real Estate AI Assistant",
        "status": "active",
        "capabilities": [
            "Voice-based queries via phone",
            "Natural language processing",
            "Real-time database access",
            "Instant business insights",
            "Multi-user support"
        ],
        "phone_number": os.getenv("JEN_PHONE_NUMBER", "Coming Soon"),
        "uptime": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Test database connection
        db_healthy = await db_service.health_check()
        
        # Test AI service
        ai_healthy = ai_service.health_check()
        
        # Test voice service
        voice_healthy = voice_processor.health_check()
        
        overall_health = db_healthy and ai_healthy and voice_healthy
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "ai_service": "healthy" if ai_healthy else "unhealthy",
                "voice_processor": "healthy" if voice_healthy else "unhealthy"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        log.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/voice/query")
async def voice_query(request: VoiceQueryRequest):
    """Process voice-based queries from phone calls"""
    try:
        log.info(f"Voice query from caller: {request.caller_id}")
        
        # Convert audio to text
        transcript = await voice_processor.speech_to_text(request.audio_data)
        log.info(f"Transcript: {transcript}")
        
        if not transcript:
            return {"error": "Could not understand audio"}
        
        # Identify user from caller ID or transcript
        user_info = await auth_service.identify_user(
            caller_id=request.caller_id,
            transcript=transcript
        )
        
        if not user_info:
            # Generate response asking for identification
            response_text = "Hi! I'm Jen, your AI assistant. Could you please tell me your agent ID or full name so I can help you?"
            audio_response = await voice_processor.text_to_speech(response_text)
            
            return {
                "success": False,
                "needs_identification": True,
                "text_response": response_text,
                "audio_response": audio_response,
                "session_id": request.session_id
            }
        
        # Process the business query
        result = await process_business_query(
            question=transcript,
            user_id=user_info["user_id"],
            user_type=user_info["user_type"],
            user_name=user_info.get("name", "")
        )
        
        # Convert response to speech
        audio_response = await voice_processor.text_to_speech(result["response"])
        
        # Broadcast to WebSocket connections
        await broadcast_query_result({
            "type": "voice_query",
            "user": user_info,
            "question": transcript,
            "response": result["response"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "transcript": transcript,
            "text_response": result["response"],
            "audio_response": audio_response,
            "data": result.get("data"),
            "session_id": request.session_id,
            "user": user_info
        }
        
    except Exception as e:
        log.error(f"Voice query error: {e}")
        error_response = "I'm sorry, I'm having trouble processing your request right now. Please try again."
        audio_response = await voice_processor.text_to_speech(error_response)
        
        return {
            "success": False,
            "error": str(e),
            "text_response": error_response,
            "audio_response": audio_response
        }

@app.post("/text/query")
async def text_query(request: TextQueryRequest):
    """Process text-based queries (for testing and web interface)"""
    try:
        log.info(f"Text query from user {request.user_id}: {request.question}")
        
        # Get user info
        user_info = await db_service.get_user_info(request.user_id)
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Process the business query
        result = await process_business_query(
            question=request.question,
            user_id=request.user_id,
            user_type=request.user_type,
            user_name=user_info.get("name", "")
        )
        
        # Broadcast to WebSocket connections
        await broadcast_query_result({
            "type": "text_query",
            "user": user_info,
            "question": request.question,
            "response": result["response"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "question": request.question,
            "response": result["response"],
            "data": result.get("data"),
            "user": user_info
        }
        
    except Exception as e:
        log.error(f"Text query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/elevenlabs/webhook")
async def elevenlabs_webhook(request: Request):
    """Webhook endpoint for ElevenLabs phone integration"""
    try:
        # Get the raw body for webhook verification
        body = await request.body()
        headers = dict(request.headers)
        
        log.info(f"ElevenLabs webhook received")
        
        # Parse the webhook data
        webhook_data = await request.json()
        
        # Process the phone call data
        result = await voice_processor.process_phone_webhook(webhook_data)
        
        return {"status": "success", "processed": True}
        
    except Exception as e:
        log.error(f"Webhook processing error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def process_business_query(question: str, user_id: str, user_type: str, user_name: str) -> Dict[str, Any]:
    """Process a business query and return response"""
    
    # Generate SQL query using AI
    sql_query = await ai_service.generate_sql_query(
        question=question,
        user_type=user_type,
        user_id=user_id
    )
    
    if not sql_query:
        return {
            "response": "I'm sorry, I couldn't understand your question. Could you try rephrasing it?",
            "data": None
        }
    
    # Execute the query
    query_result = await db_service.execute_query(sql_query, [user_id])
    
    # Generate natural language response
    response_text = ai_service.generate_response(
        question=question,
        data=query_result,
        user_name=user_name,
        user_type=user_type
    )
    
    return {
        "response": response_text,
        "data": query_result,
        "sql": sql_query
    }

async def broadcast_query_result(data: Dict[str, Any]):
    """Broadcast query results to all connected WebSocket clients"""
    if active_connections:
        message = json.dumps(data)
        for connection in active_connections.copy():
            try:
                await connection.send_text(message)
            except:
                active_connections.remove(connection)

@app.get("/analytics/dashboard")
async def analytics_dashboard():
    """Analytics dashboard data"""
    try:
        stats = await db_service.get_usage_analytics()
        return {
            "total_queries": stats.get("total_queries", 0),
            "active_users": stats.get("active_users", 0),
            "top_questions": stats.get("top_questions", []),
            "response_times": stats.get("avg_response_time", 0),
            "success_rate": stats.get("success_rate", 0)
        }
    except Exception as e:
        log.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TWILIO INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    """Handle incoming Twilio voice calls - redirect to ElevenLabs like Rachel"""
    try:
        form_data = await request.form()
        from_number = form_data.get("From", "")
        to_number = form_data.get("To", "")
        call_sid = form_data.get("CallSid", "")
        
        log.info(f"Twilio voice call from {from_number} to {to_number}, CallSid: {call_sid}")
        
        # Try to identify caller from database
        caller_name = "Real Estate Agent"  # Default
        caller_id = None
        
        try:
            # Simple phone number lookup
            user_info = await db_service.get_user_by_phone(from_number.replace("+1", "").replace("-", "").replace(" ", ""))
            if user_info:
                caller_name = user_info.get("name", "Real Estate Agent")
                caller_id = str(user_info.get("id", ""))
                log.info(f"Identified caller: {caller_name} (ID: {caller_id})")
        except Exception as e:
            log.warning(f"Could not identify caller {from_number}: {e}")
        
        # Create ElevenLabs redirect URL with caller context
        elevenlabs_url = f"https://api.us.elevenlabs.io/twilio/inbound_call?caller_name={caller_name.replace(' ', '+')}&caller_id={caller_id or 'unknown'}"
        
        # Return TwiML redirect to ElevenLabs (same pattern as Rachel)
        twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect method="POST">{elevenlabs_url}</Redirect>
</Response>'''
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        log.error(f"Twilio voice webhook error: {e}")
        
        # Fallback: redirect to ElevenLabs without caller identification  
        fallback_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect method="POST">https://api.us.elevenlabs.io/twilio/inbound_call</Redirect>
</Response>'''
        return PlainTextResponse(fallback_twiml, media_type="application/xml")

@app.post("/twilio/sms")
async def twilio_sms_webhook(request: Request):
    """Handle incoming Twilio SMS messages"""
    try:
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        log.info(f"Twilio SMS webhook: {webhook_data}")
        
        # Process through Twilio service
        result = await twilio_service.process_webhook(webhook_data)
        
        # Return TwiML response
        if 'twiml' in result:
            return PlainTextResponse(result['twiml'], media_type="application/xml")
        else:
            # Fallback TwiML
            return PlainTextResponse(
                twilio_service.create_sms_response("Sorry, I'm experiencing technical difficulties."),
                media_type="application/xml"
            )
        
    except Exception as e:
        log.error(f"Twilio SMS webhook error: {e}")
        fallback_twiml = twilio_service.create_sms_response("Sorry, I'm experiencing technical difficulties.")
        return PlainTextResponse(fallback_twiml, media_type="application/xml")

@app.post("/twilio/process-speech")
async def twilio_process_speech(request: Request):
    """Process speech input from Twilio Gather"""
    try:
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        caller_number = webhook_data.get('From')
        speech_result = webhook_data.get('SpeechResult', '').strip()
        call_sid = webhook_data.get('CallSid')
        
        log.info(f"Processing speech from {caller_number}: {speech_result}")
        
        if not speech_result:
            # No speech detected
            twiml = twilio_service.create_voice_response(
                "I didn't hear anything. Please try asking your question again.",
                gather_input=True
            )
            return PlainTextResponse(twiml, media_type="application/xml")
        
        # Identify the user
        user_info = await auth_service.identify_user(
            caller_id=caller_number,
            transcript=speech_result
        )
        
        if not user_info:
            # User not identified
            twiml = twilio_service.create_voice_response(
                "I couldn't identify you. Please say your name and agent ID, like 'Hi, this is John Smith, agent ID 121901'.",
                gather_input=True
            )
            return PlainTextResponse(twiml, media_type="application/xml")
        
        # Process the business query
        result = await process_business_query(
            question=speech_result,
            user_id=user_info['user_id'],
            user_type=user_info['user_type'],
            user_name=user_info['name']
        )
        
        # Create voice response
        response_text = result['response']
        
        # Add option to ask another question
        full_response = f"{response_text} Would you like to ask another question?"
        
        twiml = twilio_service.create_voice_response(full_response, gather_input=True)
        
        # Log the interaction
        await auth_service.log_access_attempt(
            user_id=user_info['user_id'],
            caller_id=caller_number,
            transcript=speech_result,
            success=True
        )
        
        return PlainTextResponse(twiml, media_type="application/xml")
        
    except Exception as e:
        log.error(f"Speech processing error: {e}")
        fallback_twiml = twilio_service.create_voice_response(
            "Sorry, I had trouble processing your request. Please try again.",
            gather_input=True
        )
        return PlainTextResponse(fallback_twiml, media_type="application/xml")

@app.get("/twilio/call-logs")
async def get_call_logs():
    """Get recent call logs"""
    try:
        logs = await twilio_service.get_call_logs(limit=100)
        return {"call_logs": logs}
    except Exception as e:
        log.error(f"Call logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/twilio/message-logs")
async def get_message_logs():
    """Get recent message logs"""
    try:
        logs = await twilio_service.get_message_logs(limit=100)
        return {"message_logs": logs}
    except Exception as e:
        log.error(f"Message logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/twilio/send-sms")
async def send_sms(request: Dict[str, str]):
    """Send SMS message"""
    try:
        to_number = request.get('to')
        message = request.get('message')
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing 'to' number or 'message'")
        
        message_sid = await twilio_service.send_sms(to_number, message)
        
        if message_sid:
            return {"status": "sent", "message_sid": message_sid}
        else:
            raise HTTPException(status_code=500, detail="Failed to send SMS")
            
    except Exception as e:
        log.error(f"Send SMS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/twilio")
async def twilio_health():
    """Check Twilio service health"""
    return {
        "twilio_available": twilio_service.health_check(),
        "phone_number": twilio_service.phone_number,
        "phone_number_sid": twilio_service.phone_number_sid
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    log.info(f"Starting Jen AI Assistant on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )