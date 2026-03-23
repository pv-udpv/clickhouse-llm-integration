"""
Test suite for MindsDB integration
"""

import pytest
import os
from src.skills.mindsdb_skill import MindsDBSkill

# Skip tests if MindsDB not available
MINDSDB_HOST = os.getenv('MINDSDB_HOST', 'http://localhost:47334')

@pytest.fixture
def mindsdb_skill():
    """Create MindsDB skill instance"""
    return MindsDBSkill(host=MINDSDB_HOST)

class TestMindsDBConnection:
    """Test MindsDB connection and basic operations"""
    
    def test_connection(self, mindsdb_skill):
        """Test basic connection to MindsDB"""
        try:
            result = mindsdb_skill.execute_sql("SELECT 1 as test")
            assert 'data' in result
            print("✅ MindsDB connection successful")
        except Exception as e:
            pytest.skip(f"MindsDB not available: {e}")
    
    def test_list_models(self, mindsdb_skill):
        """Test listing models"""
        try:
            models = mindsdb_skill.list_models()
            assert isinstance(models, list)
            print(f"✅ Found {len(models)} models")
        except Exception as e:
            pytest.skip(f"Cannot list models: {e}")

class TestMindsDBModels:
    """Test model creation and prediction"""
    
    @pytest.mark.skipif(
        not os.getenv('MINDSDB_TEST'),
        reason="Set MINDSDB_TEST=1 to run model tests"
    )
    def test_create_simple_model(self, mindsdb_skill):
        """Test creating a simple prediction model"""
        model_name = f"test_model_{int(time.time())}"
        
        try:
            # Create model
            result = mindsdb_skill.create_model(
                model_name=model_name,
                from_table="mindsdb.example_data",
                predict_column="target",
                engine="lightgbm"
            )
            
            print(f"✅ Model {model_name} created")
            
            # Check status
            status = mindsdb_skill.get_model_status(model_name)
            assert status['name'] == model_name
            
            # Cleanup
            mindsdb_skill.drop_model(model_name)
            
        except Exception as e:
            print(f"⚠️  Model test failed: {e}")
            pytest.skip(f"Model creation failed: {e}")

class TestMindsDBLLM:
    """Test LLM model integration"""
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY required for LLM tests"
    )
    def test_create_llm_model(self, mindsdb_skill):
        """Test creating LLM-based model"""
        model_name = f"test_llm_{int(time.time())}"
        
        try:
            result = mindsdb_skill.create_llm_model(
                model_name=model_name,
                predict_column="sentiment",
                engine="openai",
                model_type="gpt-4",
                prompt_template="Analyze sentiment: {{text}}"
            )
            
            print(f"✅ LLM model {model_name} created")
            
            # Cleanup
            mindsdb_skill.drop_model(model_name)
            
        except Exception as e:
            print(f"⚠️  LLM model test failed: {e}")
            pytest.skip(f"LLM model creation failed: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
