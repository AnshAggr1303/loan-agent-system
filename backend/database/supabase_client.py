# ============================================================================
# SUPABASE CLIENT - Python
# Path: backend/database/supabase_client.py
# ============================================================================

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Global Supabase client
_supabase_client = None

def get_supabase_client() -> Client:
    """
    Get or create Supabase client (singleton pattern)
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        _supabase_client = create_client(url, key)
        print("✅ Supabase client initialized")
    
    return _supabase_client

def get_service_client() -> Client:
    """
    Get Supabase client with service role key (for admin operations)
    """
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not url or not service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    
    return create_client(url, service_key)