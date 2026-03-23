"""
Analysis Agent - Multi-step text analysis workflows
"""

from typing import Dict, List, Optional
import clickhouse_connect
from src.skills.llm_skill import LLMSkill
from src.tools.prompt_templates import (
    sentiment_analysis,
    classify_text,
    summarize,
    extract_entities
)
import os

class AnalysisAgent:
    """Performs multi-step text analysis using LLMs"""
    
    def __init__(self, provider: str = 'openai'):
        self.llm_skill = LLMSkill(provider=provider)
        self.client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=int(os.getenv('CLICKHOUSE_PORT', 9000))
        )
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text
            
        Returns:
            Sentiment (positive/negative/neutral)
        """
        prompt = sentiment_analysis(text)
        result = self.llm_skill.generate(prompt, max_tokens=10, temperature=0)
        return result.strip().lower()
    
    def classify(self, text: str, categories: List[str]) -> str:
        """
        Classify text into categories
        
        Args:
            text: Input text
            categories: List of category options
            
        Returns:
            Selected category
        """
        prompt = classify_text(text, categories)
        result = self.llm_skill.generate(prompt, max_tokens=20, temperature=0)
        return result.strip()
    
    def summarize(self, text: str, num_sentences: int = 3) -> str:
        """
        Summarize text
        
        Args:
            text: Input text
            num_sentences: Number of sentences in summary
            
        Returns:
            Summary text
        """
        prompt = summarize(text, num_sentences)
        result = self.llm_skill.generate(prompt, max_tokens=200)
        return result.strip()
    
    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        prompt = extract_entities(text, f"top {num_keywords} keywords")
        result = self.llm_skill.generate(prompt, max_tokens=100, temperature=0)
        
        # Parse comma-separated list
        keywords = [k.strip() for k in result.split(',')]
        return keywords[:num_keywords]
    
    def full_analysis(self, text: str) -> Dict:
        """
        Perform comprehensive analysis
        
        Args:
            text: Input text
            
        Returns:
            Dict with sentiment, summary, keywords
        """
        return {
            'sentiment': self.analyze_sentiment(text),
            'summary': self.summarize(text, num_sentences=2),
            'keywords': self.extract_keywords(text, num_keywords=5),
            'length': len(text.split())
        }
    
    def batch_analyze(self, table: str, text_column: str, 
                     output_table: str) -> int:
        """
        Analyze all texts in a table
        
        Args:
            table: Source table name
            text_column: Column containing text
            output_table: Table to store results
            
        Returns:
            Number of rows analyzed
        """
        # Create output table
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {output_table} (
            id UInt64,
            text String,
            sentiment String,
            summary String,
            keywords Array(String),
            analyzed_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY id
        """
        self.client.command(create_sql)
        
        # Get texts to analyze
        select_sql = f"""
        SELECT rowNumberInAllBlocks() AS id, {text_column} AS text
        FROM {table}
        LIMIT 100
        """
        
        results = self.client.query(select_sql)
        
        # Analyze each text
        analyzed = []
        for row in results.result_rows:
            text_id, text = row
            
            try:
                analysis = self.full_analysis(text)
                analyzed.append({
                    'id': text_id,
                    'text': text,
                    'sentiment': analysis['sentiment'],
                    'summary': analysis['summary'],
                    'keywords': analysis['keywords']
                })
            except Exception as e:
                print(f"Error analyzing row {text_id}: {e}")
        
        # Insert results
        if analyzed:
            self.client.insert(output_table, analyzed)
        
        return len(analyzed)
