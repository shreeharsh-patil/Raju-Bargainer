import os
import sys
import time
import logging
from dotenv import load_dotenv

load_dotenv()
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agent import root_agent, app as adk_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fast_api_app")

_start_time = time.time()

app = FastAPI(title="Raju's Royal Artifacts - ADK Agent API")

# Configurable CORS origins (comma-separated in env, or default to *)
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
cors_origins = [o.strip() for o in cors_origins_env.split(",")] if cors_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "raju-agent",
        "uptime_seconds": round(time.time() - _start_time),
        "agent": runner.agent.name if hasattr(runner, 'agent') else "unknown",
    }


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
        err_upper = err_msg.upper()

        if any(kw in err_upper for kw in ("API_KEY", "AUTHENTICATION", "CREDENTIAL", "PERMISSION")):
            fallback = (
                "Arre my friend! Raju needs his GEMINI_API_KEY "
                "environment variable set to talk to the Gemini brain! "
                f"(Error: {err_msg})"
            )
        elif "RATE_LIMIT" in err_upper or "QUOTA" in err_upper:
            fallback = "Arre bhai! Too many customers at once! Raju needs a moment to catch his breath. Try again in a bit!"
        elif "TIMEOUT" in err_upper:
            fallback = "Arre bhai! The stars are aligning slowly today. Raju is thinking too hard — try asking something simpler!"
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


@app.post("/run_stream")
async def run_agent_stream(req: RunRequest):
    """Executes a turn with Raju agent using SSE streaming."""
    user_id = req.userId
    session_id = req.sessionId

    if not req.newMessage.parts or not req.newMessage.parts[0].text:
        raise HTTPException(status_code=400, detail="Missing message text in request")

    user_text = req.newMessage.parts[0].text
    logger.info(f"Stream agent request from user={user_id}: {user_text}")

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_text)]
    )

    async def event_generator():
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                text_chunk = ""
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                text_chunk += part.text
                elif hasattr(event, "text") and event.text:
                    text_chunk = event.text

                if text_chunk:
                    yield f"data: {json.dumps({'text': text_chunk})}\n\n"

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            err_msg = str(e)
            err_upper = err_msg.upper()
            if any(kw in err_upper for kw in ("API_KEY", "AUTHENTICATION", "CREDENTIAL", "PERMISSION")):
                fallback = f"Arre my friend! Raju needs his GEMINI_API_KEY set! (Error: {err_msg})"
            elif "RATE_LIMIT" in err_upper or "QUOTA" in err_upper:
                fallback = "Arre bhai! Too many customers! Try again in a bit!"
            else:
                fallback = f"Arre bhai! Something happened: {err_msg}"
            yield f"data: {json.dumps({'text': fallback})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
