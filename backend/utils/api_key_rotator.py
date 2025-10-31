# ============================================================================
# API KEY ROTATOR - Round-Robin Key Selection
# Path: backend/utils/api_key_rotator.py
# ============================================================================

from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class APIKeyRotator:
    """
    Rotates through multiple API keys using round-robin
    """
    
    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("At least one API key is required")
        self.keys = [k for k in keys if k]  # Filter out empty keys
        if not self.keys:
            raise ValueError("No valid API keys provided")
        self.index = 0
    
    def get_key(self) -> str:
        """Get next key in rotation"""
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key
    
    def get_all_keys(self) -> List[str]:
        """Get all available keys"""
        return self.keys.copy()
    
    def get_count(self) -> int:
        """Get number of available keys"""
        return len(self.keys)

def load_groq_keys() -> APIKeyRotator:
    """Load Groq API keys from environment"""
    keys = []
    
    # Try to load up to 10 keys (GROQ_API_KEY_1, GROQ_API_KEY_2, etc.)
    for i in range(1, 11):
        key = os.getenv(f"GROQ_API_KEY_{i}")
        if key:
            keys.append(key)
    
    # Fallback to single key
    if not keys:
        single_key = os.getenv("GROQ_API_KEY")
        if single_key:
            keys.append(single_key)
    
    if not keys:
        raise ValueError("No Groq API keys found in environment")
    
    print(f"✅ Loaded {len(keys)} Groq API key(s)")
    return APIKeyRotator(keys)

# Global rotator instance
try:
    groq_key_rotator = load_groq_keys()
except Exception as e:
    print(f"⚠️  Warning: Could not load Groq keys - {e}")
    groq_key_rotator = None