from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Import our modules (will create next)
from agents.loan_agent import LoanAgent
from rag.embeddings import embed_knowledge_base
from database.supabase_client import get_supabase_client

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="QuickLoan AI Agent API",
    description="Agentic loan application system with RAG",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
loan_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global loan_agent
    loan_agent = LoanAgent()
    print("✅ Loan Agent initialized")

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    tools_used: List[str]
    response_time_ms: int

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "message": "QuickLoan AI Agent API is running",
        "version": "1.0.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - AI agent decides what to do
    """
    try:
        import time
        start_time = time.time()
        
        # Invoke agent
        result = await loan_agent.invoke(
            message=request.message,
            session_id=request.session_id,
            conversation_history=request.conversation_history
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        return ChatResponse(
            success=True,
            response=result["response"],
            session_id=result["session_id"],
            tools_used=result["tools_used"],
            response_time_ms=response_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/embed-knowledge")
async def embed_knowledge():
    """
    One-time endpoint to embed knowledge base
    Creates embeddings and stores in pgvector
    """
    try:
        result = await embed_knowledge_base()
        return {
            "success": True,
            "chunks_embedded": result["total_chunks"],
            "message": "Knowledge base embedded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get conversation history"""
    try:
        supabase = get_supabase_client()
        
        # Get session
        session_response = supabase.table("conversation_sessions").select("*").eq("id", session_id).single().execute()
        
        # Get messages
        messages_response = supabase.table("conversation_messages").select("*").eq("session_id", session_id).order("created_at").execute()
        
        return {
            "success": True,
            "session": session_response.data,
            "messages": messages_response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": loan_agent.get_tool_names() if loan_agent else []
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )