"""
Prompt Template Library for LLM UDFs
"""

from typing import Dict, List, Optional
from string import Template

class PromptTemplate:
    """Reusable prompt templates with variable substitution"""
    
    # Classification templates
    SENTIMENT_ANALYSIS = Template("""
Analyze the sentiment of the following text. Respond with ONLY one word: positive, negative, or neutral.

Text: $text

Sentiment:""")
    
    CATEGORY_CLASSIFICATION = Template("""
Classify the following text into one of these categories: $categories

Text: $text

Category:""")
    
    # Summarization templates
    SUMMARIZE_SHORT = Template("""
Summarize the following text in one sentence:

$text

Summary:""")
    
    SUMMARIZE_DETAILED = Template("""
Provide a detailed summary of the following text in $num_sentences sentences:

$text

Summary:""")
    
    # Extraction templates
    EXTRACT_ENTITIES = Template("""
Extract all $entity_type from the following text. Return as a comma-separated list.

Text: $text

$entity_type:""")
    
    EXTRACT_KEYWORDS = Template("""
Extract the top $num_keywords keywords from the following text.

Text: $text

Keywords:""")
    
    # Q&A templates
    QA_WITH_CONTEXT = Template("""
Answer the question based on the context provided. If the answer is not in the context, say "I don't know".

Context: $context

Question: $question

Answer:""")
    
    QA_CONVERSATIONAL = Template("""
You are a helpful assistant. Answer the following question:

$question

Answer:""")
    
    # Generation templates
    GENERATE_TITLE = Template("""
Generate a concise, engaging title for the following content:

$content

Title:""")
    
    GENERATE_DESCRIPTION = Template("""
Write a $length description for:

$content

Description:""")
    
    # SQL-specific templates
    TEXT_TO_SQL = Template("""
Convert the following natural language query into a SQL query for $table_name table.

Columns: $columns

Question: $question

SQL:""")
    
    EXPLAIN_SQL = Template("""
Explain what this SQL query does in plain English:

$sql_query

Explanation:""")
    
    # Data analysis templates
    ANALYZE_TREND = Template("""
Analyze the trend in this data and provide insights:

$data

Analysis:""")
    
    COMPARE_VALUES = Template("""
Compare the following values and explain the key differences:

Value A: $value_a
Value B: $value_b

Comparison:""")
    
    @classmethod
    def get_template(cls, name: str) -> Template:
        """Get template by name"""
        return getattr(cls, name.upper(), None)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List all available templates"""
        return [
            attr for attr in dir(cls)
            if not attr.startswith('_') and isinstance(getattr(cls, attr), Template)
        ]
    
    @classmethod
    def render(cls, template_name: str, **kwargs) -> str:
        """Render a template with variables"""
        template = cls.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        try:
            return template.substitute(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")


# Convenience functions for common use cases
def sentiment_analysis(text: str) -> str:
    """Generate sentiment analysis prompt"""
    return PromptTemplate.SENTIMENT_ANALYSIS.substitute(text=text)

def classify_text(text: str, categories: List[str]) -> str:
    """Generate classification prompt"""
    return PromptTemplate.CATEGORY_CLASSIFICATION.substitute(
        text=text,
        categories=", ".join(categories)
    )

def summarize(text: str, num_sentences: int = 3) -> str:
    """Generate summarization prompt"""
    if num_sentences == 1:
        return PromptTemplate.SUMMARIZE_SHORT.substitute(text=text)
    return PromptTemplate.SUMMARIZE_DETAILED.substitute(
        text=text,
        num_sentences=num_sentences
    )

def extract_entities(text: str, entity_type: str = "entities") -> str:
    """Generate entity extraction prompt"""
    return PromptTemplate.EXTRACT_ENTITIES.substitute(
        text=text,
        entity_type=entity_type
    )

def qa_with_context(question: str, context: str) -> str:
    """Generate Q&A prompt with context"""
    return PromptTemplate.QA_WITH_CONTEXT.substitute(
        question=question,
        context=context
    )

def text_to_sql(question: str, table_name: str, columns: List[str]) -> str:
    """Generate text-to-SQL prompt"""
    return PromptTemplate.TEXT_TO_SQL.substitute(
        question=question,
        table_name=table_name,
        columns=", ".join(columns)
    )
