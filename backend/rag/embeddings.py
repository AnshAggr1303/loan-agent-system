# ============================================================================
# GEMINI EMBEDDINGS - Python
# Path: backend/rag/embeddings.py
# ============================================================================

import google.generativeai as genai
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiEmbeddings:
    """
    Wrapper for Google Gemini embeddings
    """
    
    def __init__(self):
        self.model = "models/text-embedding-004"
        self.dimensions = 768
    
    def embed_text(self, text: str) -> List[float]:
        """Embed single text"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return [0.0] * self.dimensions
    
    def embed_query(self, query: str) -> List[float]:
        """Embed query (different task type)"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"❌ Query embedding error: {e}")
            return [0.0] * self.dimensions
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts"""
        embeddings = []
        for i, text in enumerate(texts):
            print(f"Embedding {i+1}/{len(texts)}")
            emb = self.embed_text(text)
            embeddings.append(emb)
        return embeddings

# ============================================================================
# KNOWLEDGE BASE EMBEDDING
# ============================================================================

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    """
    # Split by sections (##)
    sections = text.split("##")
    
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # If section is small enough, keep as one chunk
        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            # Split large sections by words
            words = section.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                current_chunk.append(word)
                current_length += len(word) + 1
                
                if current_length >= chunk_size:
                    chunks.append(" ".join(current_chunk))
                    # Keep overlap
                    current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_length = sum(len(w) + 1 for w in current_chunk)
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
    
    return chunks

async def embed_knowledge_base():
    """
    One-time function to embed knowledge base
    Chunks the knowledge_base.md file and stores embeddings
    """
    from database.supabase_client import get_supabase_client
    import uuid
    
    print("📄 Reading knowledge base...")
    
    # Read knowledge base
    with open("../knowledge_base.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Chunk the content
    chunks = chunk_text(content, chunk_size=500, overlap=50)
    
    print(f"✂️  Created {len(chunks)} chunks")
    
    # Initialize embedder
    embedder = GeminiEmbeddings()
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    # Clear existing embeddings
    print("🗑️  Clearing old embeddings...")
    supabase.table("knowledge_base_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    # Embed each chunk
    for i, chunk in enumerate(chunks):
        print(f"🔄 Embedding chunk {i+1}/{len(chunks)}")
        
        # Create embedding
        embedding = embedder.embed_text(chunk)
        
        # Store in Supabase
        try:
            supabase.table("knowledge_base_embeddings").insert({
                "id": str(uuid.uuid4()),
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            }).execute()
        except Exception as e:
            print(f"❌ Error storing chunk {i}: {e}")
            continue
    
    print("✅ Knowledge base embedded successfully!")
    
    return {"total_chunks": len(chunks)}