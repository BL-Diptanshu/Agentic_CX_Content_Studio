"""
Unit tests for Text Content Generator
Tests TextGenerator class methods with mocked Groq API
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from src.core.text_content_gen import TextGenerator, get_text_generator
import os


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response"""
    mock_message = MagicMock()
    mock_message.content = "Generated marketing copy for the campaign"
    
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 150
    
    return mock_response


@patch("src.core.text_content_gen.load_dotenv")  # Prevent loading real .env
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_text_generator_initialization(mock_groq_cls, mock_mlflow, mock_load_env, monkeypatch):
    """Test TextGenerator initializes correctly with API key"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    
    generator = TextGenerator(model_name="llama-3.1-8b-instant")
    
    assert generator.model_name == "llama-3.1-8b-instant"
    assert generator.client is not None
    mock_groq_cls.assert_called_once_with(api_key="test_groq_key_123")


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_text_generator_missing_api_key(mock_groq_cls, mock_mlflow, mock_load_env, monkeypatch):
    """Test TextGenerator raises error when API key is missing"""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
        TextGenerator()


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_generate_text_success(
    mock_groq_cls, mock_set_exp, mock_start_run, 
    mock_log_param, mock_log_metric, mock_load_env, mock_groq_response, monkeypatch
):
    """Test successful text generation"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    
    # Setup mock client
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_groq_response
    mock_groq_cls.return_value = mock_client
    
    # Mock MLflow context manager
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = TextGenerator()
    result = generator.generate_text(
        prompt="Create marketing copy",
        max_tokens=100,
        temperature=0.7
    )
    
    assert result == "Generated marketing copy for the campaign"
    assert mock_client.chat.completions.create.called
    assert mock_log_param.called
    assert mock_log_metric.called


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_generate_text_with_custom_params(
    mock_groq_cls, mock_set_exp, mock_start_run,
    mock_log_param, mock_log_metric, mock_load_env, mock_groq_response, monkeypatch
):
    """Test text generation with custom parameters"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_groq_response
    mock_groq_cls.return_value = mock_client
    
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = TextGenerator(model_name="llama-3.1-70b-versatile")
    result = generator.generate_text(
        prompt="Test prompt",
        max_tokens=200,
        temperature=0.9
    )
    
    # Verify custom parameters were used
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "llama-3.1-70b-versatile"
    assert call_args[1]["max_tokens"] == 200
    assert call_args[1]["temperature"] == 0.9


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.end_run")
@patch("mlflow.active_run")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_generate_text_api_error(mock_groq_cls, mock_set_exp, mock_active, mock_end, mock_load_env, monkeypatch):
    """Test error handling when Groq API fails"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    
    mock_active.return_value = None  # No active run
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_groq_cls.return_value = mock_client
    
    generator = TextGenerator()
    
    with pytest.raises(Exception, match="API Error"):
        generator.generate_text(prompt="Test")


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_get_text_generator_singleton(mock_groq_cls, mock_mlflow, mock_load_env, monkeypatch):
    """Test get_text_generator returns singleton instance"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    mock_client = MagicMock()
    mock_groq_cls.return_value = mock_client
    
    gen1 = get_text_generator()
    gen2 = get_text_generator()
    
    assert gen1 is gen2  # Should be same instance


@patch("src.core.text_content_gen.load_dotenv")
@patch("mlflow.end_run")
@patch("mlflow.active_run")
@patch("mlflow.set_experiment")
@patch("src.core.text_content_gen.Groq")
def test_generate_text_empty_response(mock_groq_cls, mock_set_exp, mock_active, mock_end, mock_load_env, monkeypatch):
    """Test handling of empty API response"""
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key_123")
    
    mock_active.return_value = None  # No active run
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = []
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_cls.return_value = mock_client
    
    generator = TextGenerator()
    
    with pytest.raises((IndexError, AttributeError)):
        generator.generate_text(prompt="Test")
