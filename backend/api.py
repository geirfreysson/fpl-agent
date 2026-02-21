from fastapi import FastAPI, Request as FastAPIRequest, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List, Dict, Any, Annotated
import json
import logging
import os
import jwt
import requests
import tools as tools_module
from agents import create_agent
from clerk_backend_api import Clerk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

app = FastAPI()
security = HTTPBearer()

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Cache for Clerk JWKS
_jwks_cache = None

async def get_clerk_jwks():
    """Fetch Clerk's JWKS (JSON Web Key Set) for token verification"""
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    
    if not CLERK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="CLERK_SECRET_KEY not configured")
    
    # Extract the instance ID from the secret key
    # Clerk secret keys are in format: sk_test_xxxxx or sk_live_xxxxx
    try:
        # Get the publishable key to extract instance info
        response = requests.get(
            "https://api.clerk.com/v1/jwks",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"}
        )
        if response.status_code == 200:
            _jwks_cache = response.json()
            return _jwks_cache
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
    
    # Fallback: try to construct JWKS URL from instance
    # This is a simplified approach - in production you'd want more robust key management
    raise HTTPException(status_code=500, detail="Could not retrieve JWKS")

def verify_jwt_token(token: str) -> dict:
    """Verify the JWT token using Clerk's public keys"""
    try:
        # For development, we'll use a simpler approach
        # Decode without verification first to get the header
        unverified_header = jwt.get_unverified_header(token)
        
        # For now, we'll skip signature verification in development
        # In production, you should properly verify the signature using JWKS
        payload = jwt.decode(token, options={"verify_signature": False})
        
        logger.info(f"JWT payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """Get the current authenticated user using Clerk's verification"""
    token = credentials.credentials
    
    if not CLERK_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Authentication not configured")
    
    try:
        # Use Clerk SDK to verify the token
        clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY)
        session = clerk_client.sessions.verify_session_token(token)
        return {"sub": session.user_id, "session_id": session.id}
        
    except Exception:
        # Fallback to JWT decoding (for development)
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception:
            raise HTTPException(status_code=401, detail="Authentication failed")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No middleware - authentication handled per-endpoint as needed

class ContentPart(BaseModel):
    type: str
    text: str
    status: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    role: str
    content: List[ContentPart]

class ChatRequest(BaseModel):
    message: List[ContentPart]
    conversation_history: List[ChatMessage] = []
    context: Dict[str, Any] = {}

# Health check endpoints
@app.get("/")
async def root():
    return {"status": "ok", "message": "FPL Agent Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FPL Agent Backend API"}

@app.post("/api/chat")
async def chat_endpoint(
    raw_request: FastAPIRequest,
    user: dict = Depends(get_current_user)
):
    """Chat endpoint that streams responses from smolagents ToolCallingAgent."""
    
#    try:
    request_data = await raw_request.json()
    request = ChatRequest(**request_data)
#    except Exception as e:
#        return {"error": str(e)}
    
    def generate_response():
        try:
            tools_module.set_current_user(user)
            # Create agent with streaming enabled and conversation history
            # Convert conversation_history to the format expected by create_agent
            history_for_agent = []
            for msg in request.conversation_history:
                msg_dict = {
                    'role': msg.role,
                    'content': msg.content
                }
                history_for_agent.append(msg_dict)
            
            agent = create_agent(conversation_history=history_for_agent)
            
            # Extract text from message format
            user_message = " ".join([part.text for part in request.message if part.type == "text"])
            
            # Run agent in streaming mode with reset=False to preserve conversation history
            event_count = 0
            for event in agent.run(user_message, stream=True, reset=False):
                event_count += 1
                event_type = type(event).__name__
                
                # Handle different event types for frontend
                if event_type == "ToolCall":
                    # Skip final_answer tool calls as they're internal to smolagents
                    if event.name == "final_answer":
                        continue
                    
                    # Tool is about to be called
                    tool_call_data = {
                        "type": "tool_call_start",
                        "tool_name": event.name,
                        "tool_arguments": event.arguments,
                        "tool_call_id": event.id
                    }
                    yield f"0:{json.dumps(tool_call_data)}\n"
                
                elif event_type == "ToolOutput":
                    # For final_answer tool outputs, stream the content as text instead of showing tool call
                    if event.tool_call.name == "final_answer":
                        # Stream the final answer content as text
                        final_content = str(event.output)
                        for char in final_content:
                            text_data = {
                                "type": "text",
                                "content": char
                            }
                            yield f"0:{json.dumps(text_data)}\n"
                        continue
                    
                    # Only send tool_call_complete for the UI, don't stream the result as text later
                    tool_output_data = {
                        "type": "tool_call_complete", 
                        "tool_name": event.tool_call.name,
                        "tool_call_id": event.id,
                        "result": event.output,
                        "observation": event.observation,
                        "is_final_answer": event.is_final_answer
                    }
                    yield f"0:{json.dumps(tool_output_data)}\n"
                
                elif event_type == "ChatMessageStreamDelta":
                    # Stream text content if available
                    if event.content:
                        text_data = {
                            "type": "text",
                            "content": event.content
                        }
                        yield f"0:{json.dumps(text_data)}\n"
                
                # Skip ActionOutput and FinalAnswerStep events as they are redundant
                # The text content is already streamed via ToolOutput->final_answer handling
                
                # Skip ActionStep and other internal events for now
                # as they contain non-serializable objects
            
            # End of stream marker
            yield "d:\n"

        except GeneratorExit:
            # Client disconnected, exit cleanly without yielding
            return
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"0:{json.dumps({'type': 'error', 'message': error_msg})}\n"
            yield "d:\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
