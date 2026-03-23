"""
MindsDB Skill - SQL-native ML operations
"""

from typing import Dict, List, Optional
import requests
import json
from datetime import datetime

class MindsDBSkill:
    """Interface for MindsDB operations"""
    
    def __init__(self, 
                 host: str = 'http://localhost:47334',
                 username: str = 'mindsdb',
                 password: str = ''):
        """
        Initialize MindsDB skill
        
        Args:
            host: MindsDB API endpoint
            username: MindsDB username
            password: MindsDB password
        """
        self.host = host.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (username, password) if password else None
    
    def execute_sql(self, query: str) -> Dict:
        """
        Execute SQL query in MindsDB
        
        Args:
            query: SQL query string
            
        Returns:
            Query results as dict
        """
        endpoint = f"{self.host}/api/sql/query"
        
        response = self.session.post(
            endpoint,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    def create_model(self,
                    model_name: str,
                    from_table: str,
                    predict_column: str,
                    engine: str = 'lightgbm',
                    order_by: Optional[str] = None,
                    group_by: Optional[str] = None,
                    window: Optional[int] = None,
                    horizon: Optional[int] = None,
                    **kwargs) -> Dict:
        """
        Create a ML model in MindsDB
        
        Args:
            model_name: Name for the model
            from_table: Source table (database.table)
            predict_column: Column to predict
            engine: ML engine (lightgbm, prophet, openai, etc)
            order_by: Column for ordering (time-series)
            group_by: Column for grouping
            window: Training window size
            horizon: Forecast horizon
            
        Returns:
            Model creation status
        """
        query = f"""
        CREATE MODEL {model_name}
        FROM {from_table}
        PREDICT {predict_column}
        """
        
        using_clauses = []
        if engine:
            using_clauses.append(f"engine = '{engine}'")
        
        for key, value in kwargs.items():
            if isinstance(value, str):
                using_clauses.append(f"{key} = '{value}'")
            else:
                using_clauses.append(f"{key} = {value}")
        
        if using_clauses:
            query += f"\nUSING {', '.join(using_clauses)}"
        
        if order_by:
            query += f"\nORDER BY {order_by}"
        
        if group_by:
            query += f"\nGROUP BY {group_by}"
        
        if window:
            query += f"\nWINDOW {window}"
        
        if horizon:
            query += f"\nHORIZON {horizon}"
        
        return self.execute_sql(query)
    
    def predict(self,
               model_name: str,
               from_table: Optional[str] = None,
               where: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict]:
        """
        Make predictions using a model
        
        Args:
            model_name: Name of the model
            from_table: Source table for input data
            where: WHERE clause conditions
            limit: Limit number of results
            
        Returns:
            List of predictions
        """
        if from_table:
            query = f"SELECT * FROM {model_name} JOIN {from_table}"
        else:
            query = f"SELECT * FROM {model_name}"
        
        if where:
            query += f" WHERE {where}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        result = self.execute_sql(query)
        return result.get('data', [])
    
    def list_models(self) -> List[Dict]:
        """
        List all models
        
        Returns:
            List of model information
        """
        result = self.execute_sql("SELECT * FROM models")
        return result.get('data', [])
    
    def get_model_status(self, model_name: str) -> Dict:
        """
        Get model training status
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model status information
        """
        result = self.execute_sql(
            f"SELECT * FROM models WHERE name = '{model_name}'"
        )
        
        data = result.get('data', [])
        return data[0] if data else {}
    
    def drop_model(self, model_name: str) -> Dict:
        """
        Delete a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Deletion status
        """
        return self.execute_sql(f"DROP MODEL {model_name}")
    
    def retrain_model(self, model_name: str) -> Dict:
        """
        Retrain an existing model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Retraining status
        """
        return self.execute_sql(f"RETRAIN {model_name}")
    
    def create_database_connection(self,
                                  db_name: str,
                                  engine: str,
                                  parameters: Dict) -> Dict:
        """
        Create database connection in MindsDB
        
        Args:
            db_name: Database connection name
            engine: Database engine (clickhouse, postgres, etc)
            parameters: Connection parameters
            
        Returns:
            Connection status
        """
        params_str = ', '.join(
            f'"{k}": "{v}"' for k, v in parameters.items()
        )
        
        query = f"""
        CREATE DATABASE {db_name}
        WITH ENGINE = '{engine}',
        PARAMETERS = {{{params_str}}}
        """
        
        return self.execute_sql(query)
    
    def create_llm_model(self,
                        model_name: str,
                        predict_column: str,
                        engine: str = 'openai',
                        model_type: str = 'gpt-4',
                        prompt_template: Optional[str] = None) -> Dict:
        """
        Create LLM-based model
        
        Args:
            model_name: Name for the model
            predict_column: Output column name
            engine: LLM engine (openai, anthropic, huggingface)
            model_type: Specific model (gpt-4, claude-3, etc)
            prompt_template: Template with {{variable}} placeholders
            
        Returns:
            Model creation status
        """
        using_params = [
            f"engine = '{engine}'",
            f"model_name = '{model_type}'"
        ]
        
        if prompt_template:
            # Escape single quotes in template
            escaped = prompt_template.replace("'", "''")
            using_params.append(f"prompt_template = '{escaped}'")
        
        query = f"""
        CREATE MODEL {model_name}
        PREDICT {predict_column}
        USING {', '.join(using_params)}
        """
        
        return self.execute_sql(query)
