"""
Semantic Search Agent - Orchestrates semantic search workflow
"""

from typing import List, Dict, Tuple
import clickhouse_connect
from src.skills.embedding_skill import EmbeddingSkill
from src.tools.vector_ops import cosine_similarity
import os

class SearchAgent:
    """Performs semantic search over ClickHouse data"""
    
    def __init__(self, provider: str = 'huggingface'):
        self.embedding_skill = EmbeddingSkill(provider=provider)
        self.client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=int(os.getenv('CLICKHOUSE_PORT', 9000))
        )
    
    def search(self, query: str, table: str, 
               content_column: str, embedding_column: str,
               limit: int = 10) -> List[Dict]:
        """
        Search for semantically similar documents
        
        Args:
            query: Search query text
            table: ClickHouse table name
            content_column: Column containing text content
            embedding_column: Column containing embeddings
            limit: Number of results to return
        
        Returns:
            List of results with content and similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_skill.generate(query)
        
        # Format embedding for ClickHouse
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Search query
        sql = f"""
        SELECT 
            {content_column} AS content,
            cosineDistance({embedding_column}, {embedding_str}) AS distance,
            1 - cosineDistance({embedding_column}, {embedding_str}) AS similarity
        FROM {table}
        WHERE length({embedding_column}) > 0
        ORDER BY distance ASC
        LIMIT {limit}
        """
        
        results = self.client.query(sql)
        
        return [
            {
                'content': row[0],
                'distance': row[1],
                'similarity': row[2]
            }
            for row in results.result_rows
        ]
    
    def search_with_expansion(self, query: str, table: str,
                             content_column: str, embedding_column: str,
                             limit: int = 10) -> List[Dict]:
        """
        Search with query expansion using LLM
        """
        from src.skills.llm_skill import LLMSkill
        
        llm = LLMSkill(provider='openai')
        
        # Expand query
        expansion_prompt = f"""
        Given this search query: "{query}"
        Generate 3 alternative phrasings that mean the same thing.
        Return only the alternatives, one per line.
        """
        
        alternatives = llm.generate(expansion_prompt).strip().split('\n')
        alternatives = [alt.strip('- ').strip() for alt in alternatives if alt.strip()]
        
        # Search with all variations
        all_results = []
        for q in [query] + alternatives[:3]:
            results = self.search(q, table, content_column, embedding_column, limit)
            all_results.extend(results)
        
        # Deduplicate and re-rank
        unique_results = {r['content']: r for r in all_results}.values()
        return sorted(unique_results, key=lambda x: x['similarity'], reverse=True)[:limit]
