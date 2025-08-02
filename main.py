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
# ELEVENLABS CONVERSATION INITIATION WEBHOOK
# ============================================================================

@app.post("/api/chatbase/twilio-personalization")
async def elevenlabs_conversation_initiation(request: Request):
    """ElevenLabs conversation initiation webhook for caller identification"""
    try:
        webhook_data = await request.json()
        caller_phone = webhook_data.get("caller_id", "").replace("+1", "").replace("-", "").replace(" ", "")
        
        log.info(f"ElevenLabs conversation initiation - caller: {caller_phone}")
        
        # Look up caller in database
        try:
            user_info = await db_service.get_user_by_phone(caller_phone)
            if user_info:
                response_data = {
                    "caller_name": user_info.get("name", "Real Estate Agent"),
                    "caller_id": str(user_info.get("id", "")),
                    "caller_phone": caller_phone,
                    "agent_found": "true"
                }
                log.info(f"Caller identified: {response_data['caller_name']} (ID: {response_data['caller_id']})")
            else:
                response_data = {
                    "caller_name": "Real Estate Agent",
                    "caller_id": "unknown",
                    "caller_phone": caller_phone,
                    "agent_found": "false"
                }
                log.info(f"Caller not found in database: {caller_phone}")
                
        except Exception as e:
            log.error(f"Database lookup failed for {caller_phone}: {e}")
            response_data = {
                "caller_name": "Real Estate Agent",
                "caller_id": "unknown", 
                "caller_phone": caller_phone,
                "agent_found": "false"
            }
        
        return response_data
        
    except Exception as e:
        log.error(f"Conversation initiation webhook error: {e}")
        return {
            "caller_name": "Real Estate Agent",
            "caller_id": "unknown",
            "caller_phone": "unknown",
            "agent_found": "false"
        }

@app.get("/api/chatbase/query")
async def chatbase_query(agent_id: str, user_type: str, question: str):
    """
    ElevenLabs webhook endpoint for agent data queries
    This matches the format expected by the ElevenLabs agent configuration
    """
    try:
        log.info(f"Chatbase query - agent_id: {agent_id}, user_type: {user_type}, question: {question}")
        
        # Process the query through our existing text query logic
        # Look up user information
        user_info = await db_service.get_user_info(agent_id)
        if not user_info:
            return {
                "success": False,
                "message": "User not found",
                "response": "I couldn't find your information in the system."
            }
        
        # Generate SQL query from the natural language question
        sql_query = await ai_service.generate_sql_query(question, user_type, agent_id)
        if not sql_query:
            return {
                "success": False,
                "message": "Could not understand the question",
                "response": "I'm sorry, I couldn't understand your question. Could you try rephrasing it?"
            }
        
        # Execute the query
        query_result = await db_service.execute_query(sql_query, [agent_id])
        
        # Generate natural language response
        response_text = ai_service.generate_response(
            question,
            query_result,
            user_info.get("name", "Agent"),
            user_type
        )
        
        # Return in the format expected by ElevenLabs
        return {
            "success": True,
            "response": response_text,
            "data": query_result,
            "user": {
                "user_id": user_info.get("id"),
                "name": user_info.get("name"),
                "user_type": user_type
            }
        }
        
    except Exception as e:
        log.error(f"Chatbase query error: {e}")
        return {
            "success": False,
            "message": str(e),
            "response": "I'm experiencing technical difficulties. Please try again later."
        }

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
        
        # For now, use working TwiML with speech recognition
        # TODO: Set up ElevenLabs phone number registration for direct redirect
        greeting = f"Hi! I'm Jen, your AI assistant for real estate data. "
        if caller_name != "Real Estate Agent":
            greeting += f"Hello {caller_name}! "
        greeting += "I can help you with questions about your income, deals, and performance. What would you like to know?"
        
        twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather action="/twilio/process-speech" input="speech" method="POST" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Joanna-Neural">{greeting}</Say>
    </Gather>
    <Say>I didn't hear anything. Please call back when you're ready to ask a question.</Say>
</Response>'''
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        log.error(f"Twilio voice webhook error: {e}")
        
        # Fallback TwiML  
        fallback_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural">Sorry, I'm experiencing technical difficulties. Please try again later.</Say>
</Response>'''
        return PlainTextResponse(fallback_twiml, media_type="application/xml")

@app.post("/twilio/process-speech")
async def twilio_process_speech(request: Request):
    """Process speech input from Twilio Gather"""
    try:
        form_data = await request.form()
        speech_result = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid", "")
        from_number = form_data.get("From", "")
        
        log.info(f"Speech processing - CallSid: {call_sid}, From: {from_number}, Speech: {speech_result}")
        
        if not speech_result:
            # No speech detected
            twiml_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural">I didn't hear anything. Please call back when you're ready to ask a question.</Say>
</Response>'''
            return PlainTextResponse(twiml_response, media_type="application/xml")
        
        # Try to identify the user from their voice input or phone number
        user_id = None
        caller_name = "Real Estate Agent"
        
        # Check if user provided agent ID in speech
        if "agent id" in speech_result.lower() or "my id" in speech_result.lower():
            import re
            id_match = re.search(r'\b(\d{6})\b', speech_result)
            if id_match:
                user_id = id_match.group(1)
                log.info(f"Extracted user ID from speech: {user_id}")
        
        # If no ID in speech, try phone lookup
        if not user_id:
            try:
                user_info = await db_service.get_user_by_phone(from_number.replace("+1", "").replace("-", "").replace(" ", ""))
                if user_info:
                    user_id = str(user_info.get("id", ""))
                    caller_name = user_info.get("name", "Real Estate Agent")
            except:
                pass
        
        if not user_id:
            # Ask for agent ID
            twiml_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather action="/twilio/process-speech" input="speech" method="POST" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Joanna-Neural">I'd be happy to help! Please tell me your agent ID so I can access your data.</Say>
    </Gather>
    <Say>Please call back and provide your agent ID.</Say>
</Response>'''
            return PlainTextResponse(twiml_response, media_type="application/xml")
        
        # Process the business query
        try:
            result = await process_business_query(
                question=speech_result,
                user_id=user_id,
                user_type="agent",
                user_name=caller_name
            )
            
            response_text = result.get("response", "I'm sorry, I couldn't process your request.")
            
            # Return the response via voice
            twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural">{response_text}</Say>
    <Gather action="/twilio/process-speech" input="speech" method="POST" speechTimeout="auto" timeout="10">
        <Say voice="Polly.Joanna-Neural">Do you have any other questions?</Say>
    </Gather>
    <Say>Thank you for calling Jen AI Assistant. Have a great day!</Say>
</Response>'''
            
        except Exception as e:
            log.error(f"Query processing failed: {e}")
            twiml_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural">I'm sorry, I'm having trouble accessing the database right now. Please try again later.</Say>
</Response>'''
        
        return PlainTextResponse(twiml_response, media_type="application/xml")
        
    except Exception as e:
        log.error(f"Speech processing error: {e}")
        fallback_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna-Neural">Sorry, I'm having trouble processing your request. Please try again.</Say>
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

@app.post("/debug/test-user-types")
async def debug_test_user_types():
    """Debug endpoint to test specific user types with known IDs"""
    try:
        # Test users with known data
        test_users = [
            {"user_id": "129814", "expected_type": "agent", "description": "Agent test"},
            {"user_id": "11333", "expected_type": "managingbroker", "description": "Managing Broker test"},
            {"user_id": "121901", "expected_type": "admin", "description": "Admin test"}
        ]
        
        # First, let's check what UTYPE_IDs these users actually have
        utype_debug = []
        for test_user in test_users:
            try:
                utype_query = """
                SELECT 
                    u.USER_ID,
                    u.UTYPE_ID,
                    d.F_NAME + ' ' + d.L_NAME as full_name,
                    u.USTATUS
                FROM TBL_USER_CREATE u
                INNER JOIN TBL_USER_DETAILS d ON u.USER_ID = d.USER_ID
                WHERE u.USER_ID = %s
                """
                utype_result = await db_service.execute_query(utype_query, [test_user["user_id"]])
                if utype_result:
                    utype_debug.append({
                        "user_id": test_user["user_id"],
                        "expected_type": test_user["expected_type"],
                        "actual_utype_id": utype_result[0]["UTYPE_ID"],
                        "name": utype_result[0]["full_name"],
                        "status": utype_result[0]["USTATUS"]
                    })
            except Exception as e:
                utype_debug.append({
                    "user_id": test_user["user_id"],
                    "error": str(e)
                })
        
        results = []
        
        for test_user in test_users:
            user_id = test_user["user_id"]
            result = {"user_id": user_id, "description": test_user["description"]}
            
            try:
                # Test user lookup
                user_info = await db_service.get_user_info(user_id)
                if not user_info:
                    result["error"] = f"User {user_id} not found"
                    result["status"] = "failed"
                    results.append(result)
                    continue
                
                result["user_info"] = user_info
                result["actual_type"] = user_info.get("user_type", "unknown")
                
                # Test a simple query appropriate for each user type
                if user_info.get("user_type") == "agent":
                    question = "What is my total income this year?"
                elif user_info.get("user_type") in ["broker", "managingbroker"]:
                    question = "How many agents are in my team?"
                else:
                    question = "Show me system statistics"
                
                # Generate SQL query
                sql_query = await ai_service.generate_sql_query(
                    question=question,
                    user_type=user_info.get("user_type", "agent"),
                    user_id=user_id
                )
                
                if not sql_query:
                    result["error"] = "SQL generation failed"
                    result["status"] = "failed"
                    results.append(result)
                    continue
                
                result["sql_query"] = sql_query
                result["test_question"] = question
                
                # Execute query
                query_result = await db_service.execute_query(sql_query, [user_id])
                result["query_result"] = query_result
                result["data_count"] = len(query_result) if query_result else 0
                
                # Generate response
                response_text = ai_service.generate_response(
                    question=question,
                    data=query_result,
                    user_name=user_info.get("name", "User"),
                    user_type=user_info.get("user_type", "agent")
                )
                
                result["response"] = response_text
                result["status"] = "success"
                
            except Exception as e:
                result["error"] = str(e)
                result["status"] = "failed"
            
            results.append(result)
        
        # Summary
        success_count = sum(1 for r in results if r.get("status") == "success")
        
        return {
            "success": True,
            "utype_analysis": utype_debug,
            "test_results": results,
            "summary": {
                "total_tests": len(test_users),
                "successful": success_count,
                "failed": len(test_users) - success_count
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Debug test failed: {str(e)}",
            "exception_type": type(e).__name__
        }

@app.post("/debug/test-query")
async def debug_test_query():
    """Debug endpoint to test individual components"""
    try:
        # First, let's find what users actually exist
        try:
            sample_users_query = """
            SELECT TOP 5 
                u.USER_ID,
                d.F_NAME + ' ' + d.L_NAME as full_name,
                u.UTYPE_ID,
                CASE 
                    WHEN u.UTYPE_ID = 14 THEN 'agent'
                    WHEN u.UTYPE_ID IN (15, 16) THEN 'broker'
                    ELSE 'user'
                END as user_type
            FROM TBL_USER_CREATE u
            INNER JOIN TBL_USER_DETAILS d ON u.USER_ID = d.USER_ID
            WHERE u.USTATUS = 1
              AND u.UTYPE_ID = 14
            ORDER BY u.USER_ID
            """
            sample_users = await db_service.execute_query(sample_users_query)
            
            if not sample_users:
                return {"error": "No active agents found in database", "step": "user_discovery"}
            
            # Use the second available agent (skip company entity)
            first_agent = str(int(sample_users[1]["USER_ID"]))
            
        except Exception as e:
            return {"error": f"Failed to find sample users: {str(e)}", "step": "user_discovery"}
        
        # Test 1: Database user lookup - test the exact query from get_user_info
        try:
            test_query = """
            SELECT 
                u.USER_ID,
                d.F_NAME,
                d.L_NAME,
                d.F_NAME + ' ' + d.L_NAME as full_name,
                u.UTYPE_ID,
                CASE 
                    WHEN u.UTYPE_ID = 14 THEN 'agent'
                    WHEN u.UTYPE_ID IN (15, 16) THEN 'broker'
                    ELSE 'user'
                END as user_type,
                d.JOINED_DT,
                u.USTATUS
            FROM TBL_USER_CREATE u
            INNER JOIN TBL_USER_DETAILS d ON u.USER_ID = d.USER_ID
            WHERE u.USER_ID = %s
              AND u.USTATUS = 1
            """
            direct_result = await db_service.execute_query(test_query, [first_agent])
            
            if not direct_result:
                return {
                    "error": f"User {first_agent} not found in TBL_USER_DETAILS join", 
                    "step": "user_lookup_direct",
                    "available_users": sample_users,
                    "tested_user_id": first_agent
                }
            
        except Exception as e:
            return {
                "error": f"Direct query failed: {str(e)}", 
                "step": "user_lookup_direct_query",
                "tested_user_id": first_agent
            }
        
        user_info = await db_service.get_user_info(first_agent)
        if not user_info:
            return {"error": f"User {first_agent} not found via get_user_info", "step": "user_lookup", "available_users": sample_users, "direct_result": direct_result}
        
        # Test 2: AI service SQL generation
        question = "What is my total income this year?"
        sql_query = await ai_service.generate_sql_query(
            question=question,
            user_type="agent",
            user_id=first_agent
        )
        if not sql_query:
            return {"error": "SQL generation failed", "step": "sql_generation", "user_info": user_info}
        
        # Test 3: Database query execution
        try:
            query_result = await db_service.execute_query(sql_query, [first_agent])
        except Exception as e:
            return {
                "error": f"Database query failed: {str(e)}", 
                "step": "query_execution", 
                "sql": sql_query,
                "user_info": user_info
            }
        
        # Test 4: Response generation
        try:
            response_text = ai_service.generate_response(
                question=question,
                data=query_result,
                user_name=user_info["name"],
                user_type="agent"
            )
        except Exception as e:
            return {
                "error": f"Response generation failed: {str(e)}", 
                "step": "response_generation",
                "query_result": query_result,
                "user_info": user_info
            }
        
        # Success - return all data
        return {
            "success": True,
            "user_info": user_info,
            "sql_query": sql_query,
            "query_result": query_result,
            "response_text": response_text,
            "all_steps_passed": True
        }
        
    except Exception as e:
        return {
            "error": f"Debug test failed: {str(e)}", 
            "step": "unknown",
            "exception_type": type(e).__name__
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