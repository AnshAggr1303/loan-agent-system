# ============================================================================
# MAIN SERVER - FastAPI with In-Memory Sessions
# Path: backend/main.py
# ============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global agent instance
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    global agent
    from agents.loan_agent import LoanAgent
    agent = LoanAgent()
    print("✅ Loan Agent initialized")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("👋 Shutting down...")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="QuickLoan AI Agent API",
    description="AI-powered loan application system with RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SessionClearRequest(BaseModel):
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "QuickLoan AI Agent API is running",
        "version": "1.0.0"
    }

@app.get("/api/tools")
async def get_tools():
    """Get list of available tools"""
    return {
        "tools": agent.get_tool_names() if agent else []
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with the AI agent
    Uses in-memory session storage for conversation history
    """
    try:
        start_time = datetime.now()
        
        # Process message through agent (agent handles session management)
        result = await agent.invoke(
            message=request.message,
            session_id=request.session_id
            # No need to pass conversation_history - agent gets it from memory
        )
        
        # Calculate response time
        end_time = datetime.now()
        response_time = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "success": True,
            "response": result.get("response"),
            "session_id": result.get("session_id"),
            "tools_used": result.get("tools_used", []),
            "response_time_ms": response_time
        }
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your request."
        }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details and message history from memory"""
    try:
        from utils.session_manager import session_manager
        
        session = session_manager.get_session(session_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": session.get("messages", []),
            "customer_data": session.get("customer_data", {}),
            "created_at": session.get("created_at").isoformat(),
            "last_activity": session.get("last_activity").isoformat()
        }
        
    except Exception as e:
        print(f"❌ Get session error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/session/clear")
async def clear_session(request: SessionClearRequest):
    """Clear a specific session from memory"""
    try:
        from utils.session_manager import session_manager
        
        session_manager.clear_session(request.session_id)
        
        return {
            "success": True,
            "message": f"Session {request.session_id} cleared"
        }
        
    except Exception as e:
        print(f"❌ Clear session error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/sessions/cleanup")
async def cleanup_inactive_sessions():
    """Cleanup sessions inactive for > 30 minutes"""
    try:
        from utils.session_manager import session_manager
        
        removed_count = session_manager.cleanup_inactive_sessions()
        
        return {
            "success": True,
            "removed_sessions": removed_count,
            "active_sessions": session_manager.get_active_sessions_count()
        }
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/sessions/stats")
async def session_stats():
    """Get session statistics"""
    try:
        from utils.session_manager import session_manager
        
        return {
            "success": True,
            "active_sessions": session_manager.get_active_sessions_count()
        }
        
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/embed-knowledge")
async def embed_knowledge():
    """
    ONE-TIME: Embed knowledge base into pgvector
    """
    try:
        from rag.embeddings import GeminiEmbeddings
        from database.supabase_client import get_supabase_client
        import uuid
        
        print("\n📄 Reading knowledge base...")
        
        # Read knowledge base
        with open("../knowledge_base.md", "r") as f:
            content = f.read()
        
        # Split into chunks (simple chunking by paragraphs)
        paragraphs = content.split("\n\n")
        chunks = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 50]
        
        print(f"✂️  Created {len(chunks)} chunks")
        
        # Initialize embedder
        embedder = GeminiEmbeddings()
        supabase = get_supabase_client()
        
        # Clear existing embeddings
        print("🗑️  Clearing old embeddings...")
        supabase.table("knowledge_base_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # Embed and store each chunk
        for i, chunk in enumerate(chunks):
            print(f"🔄 Embedding chunk {i+1}/{len(chunks)}")
            
            # Create embedding
            embedding = embedder.embed_text(chunk)
            
            # Store in database
            supabase.table("knowledge_base_embeddings").insert({
                "id": str(uuid.uuid4()),
                "content": chunk,
                "embedding": embedding,
                "metadata": {"chunk_index": i}
            }).execute()
        
        print("✅ Knowledge base embedded successfully!")
        
        return {
            "success": True,
            "chunks_embedded": len(chunks),
            "message": "Knowledge base embedded successfully"
        }
        
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🚀 Starting QuickLoan AI Agent API on {host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs\n")
    
    # Use import string for proper reload
    uvicorn.run(
        "main:app",  # Import string instead of app object
        host=host,
        port=port,
        reload=True,
        reload_dirs=["./"]
    )