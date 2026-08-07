import os
import sys
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import root_agent, app as adk_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fast_api_app")

app = FastAPI(title="Raju's Royal Artifacts - ADK Agent API")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate InMemoryRunner for Raju agent with app_name="app" and auto_create_session=True
runner = InMemoryRunner(agent=root_agent, app_name="app")
runner.auto_create_session = True

class MessagePart(BaseModel):
    text: str

class NewMessage(BaseModel):
    role: Optional[str] = "user"
    parts: List[MessagePart]

class RunRequest(BaseModel):
    appName: Optional[str] = "app"
    userId: str
    sessionId: str
    newMessage: NewMessage

@app.get("/")
async def serve_index():
    """Serves the shopfront HTML interface."""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Raju's Royal Artifacts API! index.html not found."}

@app.post("/apps/app/users/{user_id}/sessions/{session_id}")
async def create_session(user_id: str, session_id: str):
    """Initializes a new session for the user."""
    try:
        sess = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        if not sess:
            await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id
            )
    except Exception:
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
    logger.info(f"Initialized session for user={user_id}, session={session_id}")
    return {
        "userId": user_id,
        "sessionId": session_id,
        "status": "initialized",
        "message": "Session created successfully"
    }

@app.post("/run")
async def run_agent(req: RunRequest):
    """Executes a turn with Raju agent."""
    user_id = req.userId
    session_id = req.sessionId
    app_name = req.appName or "app"
    
    # Extract user input text
    if not req.newMessage.parts or not req.newMessage.parts[0].text:
        raise HTTPException(status_code=400, detail="Missing message text in request")
        
    user_text = req.newMessage.parts[0].text
    logger.info(f"Run agent request from user={user_id}: {user_text}")

    # Build Content object for ADK
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_text)]
    )

    try:
        response_text = ""
        # Run agent asynchronously
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts") and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text
            elif hasattr(event, "text") and event.text:
                response_text += event.text
        
        if not response_text:
            response_text = "Arre bhai! Raju is thinking... Ask again, my friend!"

        logger.info(f"Raju response: {response_text}")

        return {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "content": {
                "role": "model",
                "parts": [{"text": response_text}]
            }
        }
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        err_msg = str(e)
        if "API_KEY" in err_msg.upper() or "AUTHENTICATION" in err_msg.upper() or "CREDENTIAL" in err_msg.upper():
            fallback = f"Arre my friend! Raju needs his GEMINI_API_KEY environment variable set to talk to the Gemini brain! (Error: {err_msg})"
        else:
            fallback = f"Arre bhai! Something unexpected happened in the bazaar: {err_msg}"
            
        return {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "content": {
                "role": "model",
                "parts": [{"text": fallback}]
            }
        }
