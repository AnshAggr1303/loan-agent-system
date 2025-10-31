# ============================================================================
# IN-MEMORY SESSION MANAGER
# Path: backend/utils/session_manager.py
# ============================================================================

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

class SessionManager:
    """
    In-memory storage for chat sessions
    Stores conversation history and customer data
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.cleanup_interval = timedelta(minutes=30)
    
    def create_session(self) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "messages": [],
            "customer_data": {},
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now()
        return session
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history"""
        session = self.get_session(session_id)
        if session:
            session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_messages(self, session_id: str) -> List[Dict]:
        """Get all messages for session"""
        session = self.get_session(session_id)
        return session["messages"] if session else []
    
    def update_customer_data(self, session_id: str, data: Dict):
        """Update customer data for session"""
        session = self.get_session(session_id)
        if session:
            session["customer_data"].update(data)
    
    def get_customer_data(self, session_id: str) -> Dict:
        """Get customer data for session"""
        session = self.get_session(session_id)
        return session["customer_data"] if session else {}
    
    def clear_session(self, session_id: str):
        """Clear session from memory"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_inactive_sessions(self):
        """Remove sessions inactive for > 30 minutes"""
        now = datetime.now()
        to_remove = []
        
        for session_id, session in self.sessions.items():
            if now - session["last_activity"] > self.cleanup_interval:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return len(to_remove)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)

# Global session manager instance
session_manager = SessionManager()