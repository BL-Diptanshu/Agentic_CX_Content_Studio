"""
Unit tests for Image Content Generator - COMPLETE REWRITE  
Tests ImageGenerator class methods with mocked Replicate API
"""
import pytest
from unittest.mock import patch, MagicMock
from src.core.image_content_gen import ImageGenerator
import os


@pytest.fixture
def mock_replicate_response():
    """Mock Replicate API response"""
    return ["https://replicate.delivery/pbxt/mockimage123.webp"]


# All tests need to mock load_dotenv and set REPLICATE_API_TOKEN via monkeypatch
# to prevent the real .env file from interfering


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_experiment")
def test_image_generator_initialization(mock_mlflow, mock_load_env, monkeypatch):
    """Test ImageGenerator initializes correctly with API token"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    generator = ImageGenerator(model="black-forest-labs/flux-schnell")
    
    assert generator.model == "black-forest-labs/flux-schnell"
    assert generator.api_token == "test_replicate_token_456"


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_experiment")
def test_image_generator_missing_token(mock_mlflow, mock_load_env, monkeypatch):
    """Test ImageGenerator raises error when token is missing"""
    monkeypatch.delenv("REPLICATE_API_TOKEN", raising=False)
    
    with pytest.raises(ValueError, match="REPLICATE_API_TOKEN not found"):
        ImageGenerator()


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_tag")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_generate_image_success(
    mock_replicate_run, mock_set_exp, mock_start_run,
    mock_log_param, mock_log_metric, mock_set_tag, mock_load_env,
    mock_replicate_response, monkeypatch
):
    """Test successful image generation"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    # Setup mocks
    mock_replicate_run.return_value = mock_replicate_response
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = ImageGenerator()
    result = generator.generate(
        prompt="A professional marketing image",
        width=1024,
        height=1024
    )
    
    assert result == "https://replicate.delivery/pbxt/mockimage123.webp"
    assert mock_replicate_run.called
    assert mock_log_param.called
    assert mock_log_metric.called


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_tag")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_generate_image_with_seed(
    mock_replicate_run, mock_set_exp, mock_start_run,
    mock_log_param, mock_log_metric, mock_set_tag, mock_load_env,
    mock_replicate_response, monkeypatch
):
    """Test image generation with reproducible seed"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    mock_replicate_run.return_value = mock_replicate_response
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = ImageGenerator()
    result = generator.generate(
        prompt="Test image",
        seed=42
    )
    
    # Verify seed was passed
    call_args = mock_replicate_run.call_args
    assert call_args[1]["input"]["seed"] == 42


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.end_run")
@patch("mlflow.active_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_generate_image_api_error(mock_replicate_run, mock_set_exp, mock_active, mock_end, mock_load_env, monkeypatch):
    """Test error handling when Replicate API fails"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    mock_active.return_value = None  # No active run
    mock_replicate_run.side_effect = Exception("Replicate API Error")
    
    generator = ImageGenerator()
    
    with pytest.raises(Exception, match="Replicate API Error"):
        generator.generate(prompt="Test")


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_tag")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_generate_image_custom_dimensions(
    mock_replicate_run, mock_set_exp, mock_start_run,
    mock_log_param, mock_log_metric, mock_set_tag, mock_load_env,
    mock_replicate_response, monkeypatch
):
    """Test image generation with custom dimensions"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    mock_replicate_run.return_value = mock_replicate_response
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = ImageGenerator()
    result = generator.generate(
        prompt="Custom size image",
        width=512,
        height=768
    )
    
    # Verify dimensions were logged
    mock_log_param.assert_any_call("width", 512)
    mock_log_param.assert_any_call("height", 768)


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.end_run")
@patch("mlflow.active_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_generate_image_empty_response(mock_replicate_run, mock_set_exp, mock_active, mock_end, mock_load_env, monkeypatch):
    """Test handling of empty Replicate response"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    mock_active.return_value = None  # No active run
    mock_replicate_run.return_value = []
    
    generator = ImageGenerator()
    
    # Check if empty response raises an error
    with pytest.raises((ValueError, IndexError)):
        generator.generate(prompt="Test")


@patch("src.core.image_content_gen.load_dotenv")
@patch("mlflow.set_tag")
@patch("mlflow.log_metric")
@patch("mlflow.log_param")
@patch("mlflow.start_run")
@patch("mlflow.set_experiment")
@patch("replicate.run")
def test_mlflow_logging_complete(
    mock_replicate_run, mock_set_exp, mock_start_run,
    mock_log_param, mock_log_metric, mock_set_tag, mock_load_env,
    mock_replicate_response, monkeypatch
):
    """Test that all MLflow logging calls are made"""
    monkeypatch.setenv("REPLICATE_API_TOKEN", "test_replicate_token_456")
    
    mock_replicate_run.return_value = mock_replicate_response
    mock_run_context = MagicMock()
    mock_start_run.return_value.__enter__.return_value = mock_run_context
    
    generator = ImageGenerator(model="black-forest-labs/flux-dev")
    result = generator.generate(prompt="MLflow test", width=1024, height=1024)
    
    # Verify all logging occurred
    assert mock_log_param.call_count >= 3  # model, width, height
    assert mock_log_metric.call_count >= 1  # generation_time_ms
    assert mock_set_tag.call_count >= 1  # prompt or output_url
