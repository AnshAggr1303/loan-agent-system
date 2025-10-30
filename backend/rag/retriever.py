# ============================================================================
# KNOWLEDGE RETRIEVER - Semantic Search
# Path: backend/rag/retriever.py
# ============================================================================

from typing import List, Dict
from database.supabase_client import get_supabase_client
from rag.embeddings import GeminiEmbeddings

class KnowledgeRetriever:
    """
    Semantic search using Gemini embeddings + Supabase pgvector
    """
    
    def __init__(self):
        self.embedder = GeminiEmbeddings()
        self.supabase = get_supabase_client()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search: Find most relevant chunks
        """
        # Embed the query
        query_embedding = self.embedder.embed_query(query)
        
        try:
            # Search using pgvector cosine similarity
            result = self.supabase.rpc(
                "match_knowledge",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": top_k
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"❌ Retrieval error: {e}")
            return []
    
    def get_context(self, query: str, top_k: int = 5) -> str:
        """
        Get relevant context as formatted string
        """
        chunks = self.retrieve(query, top_k)
        
        if not chunks:
            return "No relevant information found in knowledge base."
        
        context = "\n\n".join([
            f"[Source {i+1}] (Similarity: {chunk.get('similarity', 0):.2f})\n{chunk['content']}"
            for i, chunk in enumerate(chunks)
        ])
        
        return context
    
    def search(self, query: str, top_k: int = 3) -> List[str]:
        """
        Simple search - returns just the content
        """
        chunks = self.retrieve(query, top_k)
        return [chunk['content'] for chunk in chunks]