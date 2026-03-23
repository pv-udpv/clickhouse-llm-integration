"""
Q&A Agent - RAG-based question answering
"""

from typing import List, Dict, Optional, Tuple
import clickhouse_connect
from src.skills.embedding_skill import EmbeddingSkill
from src.skills.llm_skill import LLMSkill
from src.tools.prompt_templates import qa_with_context
import os

class QAAgent:
    """Question answering with retrieval-augmented generation (RAG)"""
    
    def __init__(self, 
                 embedding_provider: str = 'huggingface',
                 llm_provider: str = 'openai'):
        self.embedding_skill = EmbeddingSkill(provider=embedding_provider)
        self.llm_skill = LLMSkill(provider=llm_provider)
        self.client = clickhouse_connect.get_client(
            host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
            port=int(os.getenv('CLICKHOUSE_PORT', 9000))
        )
    
    def retrieve_context(self, 
                        question: str,
                        table: str,
                        content_column: str,
                        embedding_column: str,
                        top_k: int = 3) -> List[str]:
        """
        Retrieve relevant context for question
        
        Args:
            question: User question
            table: Knowledge base table
            content_column: Column with content
            embedding_column: Column with embeddings
            top_k: Number of contexts to retrieve
            
        Returns:
            List of relevant text chunks
        """
        # Generate question embedding
        question_emb = self.embedding_skill.generate(question)
        
        # Retrieve similar documents
        emb_str = '[' + ','.join(map(str, question_emb)) + ']'
        
        sql = f"""
        SELECT {content_column}
        FROM {table}
        WHERE length({embedding_column}) > 0
        ORDER BY cosineDistance({embedding_column}, {emb_str}) ASC
        LIMIT {top_k}
        """
        
        results = self.client.query(sql)
        return [row[0] for row in results.result_rows]
    
    def answer(self,
              question: str,
              table: str,
              content_column: str = 'content',
              embedding_column: str = 'embedding',
              top_k: int = 3) -> Dict:
        """
        Answer question using RAG
        
        Args:
            question: User question
            table: Knowledge base table
            content_column: Content column name
            embedding_column: Embedding column name
            top_k: Number of contexts to use
            
        Returns:
            Dict with answer and sources
        """
        # Retrieve relevant context
        contexts = self.retrieve_context(
            question, table, content_column, embedding_column, top_k
        )
        
        if not contexts:
            return {
                'answer': "I don't have enough information to answer this question.",
                'sources': [],
                'confidence': 'low'
            }
        
        # Combine contexts
        combined_context = "\n\n".join(contexts)
        
        # Generate answer
        prompt = qa_with_context(question, combined_context)
        answer = self.llm_skill.generate(prompt, max_tokens=300)
        
        return {
            'answer': answer.strip(),
            'sources': contexts,
            'num_sources': len(contexts),
            'confidence': 'high' if len(contexts) >= 2 else 'medium'
        }
    
    def conversational_qa(self,
                         question: str,
                         chat_history: Optional[List[Dict]] = None) -> str:
        """
        Answer question in conversational mode
        
        Args:
            question: User question
            chat_history: Previous conversation history
            
        Returns:
            Answer text
        """
        messages = chat_history or []
        messages.append({"role": "user", "content": question})
        
        answer = self.llm_skill.chat(messages, max_tokens=300)
        return answer
    
    def multi_hop_qa(self,
                     question: str,
                     table: str,
                     content_column: str = 'content',
                     embedding_column: str = 'embedding') -> Dict:
        """
        Answer complex multi-hop questions
        
        Args:
            question: Complex question requiring multiple steps
            table: Knowledge base table
            content_column: Content column
            embedding_column: Embedding column
            
        Returns:
            Dict with answer and reasoning steps
        """
        # Step 1: Break down question into sub-questions
        decompose_prompt = f"""
        Break down this complex question into 2-3 simpler sub-questions:
        
        Question: {question}
        
        Sub-questions (one per line):
        """
        
        sub_questions_text = self.llm_skill.generate(decompose_prompt, max_tokens=150)
        sub_questions = [q.strip() for q in sub_questions_text.split('\n') if q.strip()]
        
        # Step 2: Answer each sub-question
        sub_answers = []
        all_contexts = []
        
        for sub_q in sub_questions[:3]:  # Limit to 3 sub-questions
            result = self.answer(sub_q, table, content_column, embedding_column, top_k=2)
            sub_answers.append({
                'question': sub_q,
                'answer': result['answer']
            })
            all_contexts.extend(result['sources'])
        
        # Step 3: Synthesize final answer
        synthesis_prompt = f"""
        Based on the following information, answer this question: {question}
        
        Information:
        {chr(10).join(f"- {sa['answer']}" for sa in sub_answers)}
        
        Final Answer:
        """
        
        final_answer = self.llm_skill.generate(synthesis_prompt, max_tokens=400)
        
        return {
            'answer': final_answer.strip(),
            'reasoning_steps': sub_answers,
            'sources': list(set(all_contexts)),
            'approach': 'multi-hop'
        }
