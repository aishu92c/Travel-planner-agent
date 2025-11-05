"""Pytest configuration and fixtures.

Provides reusable fixtures for testing the LangGraph AWS application.

Fixtures:
- mock_settings: Override settings for tests
- mock_aws_client: Mocked boto3 clients
- mock_bedrock_client: Mocked Bedrock client
- mock_dynamodb: Mocked DynamoDB
- mock_s3: Mocked S3
- sample_documents: Test documents for RAG
- sample_chunks: Test chunks for RAG
- sample_agent_state: Test state for agents
- test_api_client: FastAPI TestClient
"""

import json
import os
import tempfile
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

# ============================================================================
# Settings Fixtures
# ============================================================================


@pytest.fixture
def mock_settings():
    """Mock settings for testing.

    Returns a settings object with test configuration that doesn't require
    real AWS credentials or services.

    Example:
        >>> def test_something(mock_settings):
        ...     assert mock_settings.aws.region == "us-east-1"
        ...     assert mock_settings.environment == "test"
    """
    from config.settings import Settings

    # Create test settings
    settings = Settings(
        environment="test",
        debug=True,
        app_name="LangGraph Test",
        aws={
            "region": "us-east-1",
            "bedrock": {
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            "bedrock_runtime_region": "us-east-1",
            "dynamodb": {
                "table_name": "test-checkpoints",
                "endpoint_url": None,
            },
            "s3": {
                "bucket_name": "test-bucket",
                "endpoint_url": None,
            },
            "secrets_manager_prefix": "test/",
        },
        api={
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 1,
            "reload": False,
            "cors_origins": ["*"],
            "secret_key": "test-secret-key-for-testing-only",
        },
        observability={
            "logging": {
                "level": "DEBUG",
                "format": "console",
                "file_path": None,
                "enable_cloudwatch": False,
            }
        },
    )

    return settings


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing.

    Example:
        >>> def test_with_env(mock_env):
        ...     assert os.getenv("ENVIRONMENT") == "test"
    """
    env_vars = {
        "ENVIRONMENT": "test",
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "test-access-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret-key",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


# ============================================================================
# AWS Client Fixtures (using moto)
# ============================================================================


@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Mock AWS credentials for moto.

    Example:
        >>> def test_with_credentials(mock_aws_credentials):
        ...     import boto3
        ...     # Will use mocked credentials
        ...     client = boto3.client("s3")
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client.

    Returns a MagicMock that simulates Bedrock Runtime client responses.

    Example:
        >>> def test_bedrock(mock_bedrock_client):
        ...     response = mock_bedrock_client.invoke_model(
        ...         modelId="claude-3",
        ...         body=json.dumps({"prompt": "Hello"})
        ...     )
        ...     assert "content" in json.loads(response["body"].read())
    """
    mock_client = MagicMock()

    # Mock successful response
    def mock_invoke_model(**kwargs):
        response_body = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "This is a test response."}],
            "model": "claude-3-5-sonnet-20241022",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
            },
        }

        # Create mock response with read() method
        mock_body = Mock()
        mock_body.read.return_value = json.dumps(response_body).encode()

        return {"body": mock_body, "ResponseMetadata": {"HTTPStatusCode": 200}}

    mock_client.invoke_model.side_effect = mock_invoke_model

    return mock_client


@pytest.fixture
def mock_dynamodb(mock_aws_credentials):
    """Mock DynamoDB using moto.

    Creates a test DynamoDB table for checkpoints.

    Example:
        >>> def test_dynamodb(mock_dynamodb):
        ...     table = mock_dynamodb
        ...     table.put_item(Item={"id": "test", "data": "value"})
        ...     response = table.get_item(Key={"id": "test"})
        ...     assert response["Item"]["data"] == "value"
    """
    from moto import mock_dynamodb

    with mock_dynamodb():
        import boto3

        # Create DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create test table
        table = dynamodb.create_table(
            TableName="test-checkpoints",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        yield table


@pytest.fixture
def mock_s3(mock_aws_credentials):
    """Mock S3 using moto.

    Creates a test S3 bucket.

    Example:
        >>> def test_s3(mock_s3):
        ...     bucket = mock_s3
        ...     bucket.put_object(Key="test.txt", Body=b"test data")
        ...     obj = bucket.Object("test.txt")
        ...     assert obj.get()["Body"].read() == b"test data"
    """
    from moto import mock_s3

    with mock_s3():
        import boto3

        # Create S3 resource
        s3 = boto3.resource("s3", region_name="us-east-1")

        # Create test bucket
        bucket = s3.create_bucket(Bucket="test-bucket")

        yield bucket


@pytest.fixture
def mock_secrets_manager(mock_aws_credentials):
    """Mock Secrets Manager using moto.

    Example:
        >>> def test_secrets(mock_secrets_manager):
        ...     client = mock_secrets_manager
        ...     client.create_secret(
        ...         Name="test-secret",
        ...         SecretString=json.dumps({"key": "value"})
        ...     )
        ...     response = client.get_secret_value(SecretId="test-secret")
        ...     assert json.loads(response["SecretString"])["key"] == "value"
    """
    from moto import mock_secretsmanager

    with mock_secretsmanager():
        import boto3

        client = boto3.client("secretsmanager", region_name="us-east-1")

        yield client


# ============================================================================
# Data Fixtures
# ============================================================================


@pytest.fixture
def sample_documents() -> list[dict[str, Any]]:
    """Sample documents for RAG testing.

    Returns a list of test documents with various content types.

    Example:
        >>> def test_rag(sample_documents):
        ...     assert len(sample_documents) == 3
        ...     assert sample_documents[0]["title"] == "Python Programming"
    """
    return [
        {
            "id": "doc_001",
            "title": "Python Programming",
            "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "source": "local_file",
            "metadata": {
                "author": "Test Author",
                "date": "2024-01-01",
                "category": "programming",
            },
            "tags": ["python", "programming", "tutorial"],
        },
        {
            "id": "doc_002",
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Common algorithms include linear regression, decision trees, and neural networks.",
            "source": "local_file",
            "metadata": {
                "author": "Test Author",
                "date": "2024-01-02",
                "category": "ml",
            },
            "tags": ["machine-learning", "ai", "algorithms"],
        },
        {
            "id": "doc_003",
            "title": "AWS Services Overview",
            "content": "Amazon Web Services (AWS) provides a comprehensive set of cloud computing services. Key services include EC2 for compute, S3 for storage, DynamoDB for databases, and Bedrock for generative AI.",
            "source": "local_file",
            "metadata": {
                "author": "Test Author",
                "date": "2024-01-03",
                "category": "cloud",
            },
            "tags": ["aws", "cloud", "services"],
        },
    ]


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Sample chunks for RAG testing.

    Returns a list of test chunks derived from documents.

    Example:
        >>> def test_chunks(sample_chunks):
        ...     assert len(sample_chunks) == 5
        ...     assert sample_chunks[0]["document_id"] == "doc_001"
    """
    return [
        {
            "id": "chunk_001",
            "document_id": "doc_001",
            "content": "Python is a high-level, interpreted programming language.",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 60,
            "embedding": [0.1] * 1536,  # Mock embedding vector
            "chunking_strategy": "sentence",
        },
        {
            "id": "chunk_002",
            "document_id": "doc_001",
            "content": "It supports multiple programming paradigms.",
            "chunk_index": 1,
            "start_char": 61,
            "end_char": 104,
            "embedding": [0.2] * 1536,
            "chunking_strategy": "sentence",
        },
        {
            "id": "chunk_003",
            "document_id": "doc_002",
            "content": "Machine learning is a subset of artificial intelligence.",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 56,
            "embedding": [0.3] * 1536,
            "chunking_strategy": "sentence",
        },
        {
            "id": "chunk_004",
            "document_id": "doc_002",
            "content": "Common algorithms include linear regression and decision trees.",
            "chunk_index": 1,
            "start_char": 57,
            "end_char": 119,
            "embedding": [0.4] * 1536,
            "chunking_strategy": "sentence",
        },
        {
            "id": "chunk_005",
            "document_id": "doc_003",
            "content": "Amazon Web Services (AWS) provides cloud computing services.",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 61,
            "embedding": [0.5] * 1536,
            "chunking_strategy": "sentence",
        },
    ]


@pytest.fixture
def sample_agent_state() -> dict[str, Any]:
    """Sample agent state for testing.

    Returns a test agent state with messages and context.

    Example:
        >>> def test_agent(sample_agent_state):
        ...     assert len(sample_agent_state["messages"]) == 2
        ...     assert sample_agent_state["context"]["user_id"] == "user_123"
    """
    return {
        "messages": [
            {
                "role": "user",
                "content": "What is Python?",
                "name": "user_123",
                "timestamp": datetime.now(UTC).isoformat(),
            },
            {
                "role": "assistant",
                "content": "Python is a high-level programming language.",
                "name": "assistant",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        ],
        "context": {
            "user_id": "user_123",
            "session_id": "session_456",
            "conversation_id": "conv_789",
        },
        "metadata": {
            "agent_id": "agent_001",
            "created_at": datetime.now(UTC).isoformat(),
        },
        "is_complete": False,
    }


@pytest.fixture
def sample_query_request() -> dict[str, Any]:
    """Sample API query request.

    Example:
        >>> def test_api(sample_query_request):
        ...     assert sample_query_request["query"] == "What is AI?"
    """
    return {
        "query": "What is AI?",
        "context": {"source": "web"},
        "user_id": "user_123",
        "session_id": "session_456",
        "stream": False,
        "max_tokens": 1000,
        "temperature": 0.7,
        "enable_rag": True,
        "enable_tools": False,
    }


@pytest.fixture
def sample_vector_search_results() -> list[dict[str, Any]]:
    """Sample vector search results for RAG testing.

    Example:
        >>> def test_rag(sample_vector_search_results):
        ...     assert len(sample_vector_search_results) == 3
        ...     assert sample_vector_search_results[0]["score"] == 0.95
    """
    return [
        {
            "chunk_id": "chunk_001",
            "document_id": "doc_001",
            "content": "Python is a high-level programming language.",
            "score": 0.95,
            "rank": 1,
            "metadata": {"source": "doc_001"},
        },
        {
            "chunk_id": "chunk_003",
            "document_id": "doc_002",
            "content": "Machine learning is a subset of AI.",
            "score": 0.85,
            "rank": 2,
            "metadata": {"source": "doc_002"},
        },
        {
            "chunk_id": "chunk_005",
            "document_id": "doc_003",
            "content": "AWS provides cloud computing services.",
            "score": 0.75,
            "rank": 3,
            "metadata": {"source": "doc_003"},
        },
    ]


# ============================================================================
# API Client Fixtures
# ============================================================================


@pytest.fixture
def test_api_client(mock_settings):
    """FastAPI test client.

    Creates a TestClient for testing API endpoints without starting a server.

    Example:
        >>> def test_health(test_api_client):
        ...     response = test_api_client.get("/health")
        ...     assert response.status_code == 200
    """
    try:
        # This would import your actual FastAPI app
        # For now, create a simple test app
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/health")
        def health():
            return {"status": "healthy"}

        @app.get("/")
        def root():
            return {"message": "LangGraph AWS API"}

        client = TestClient(app)
        return client
    except ImportError:
        pytest.skip("FastAPI not installed")


# ============================================================================
# Temporary File Fixtures
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Temporary directory for testing.

    Example:
        >>> def test_file_operations(temp_dir):
        ...     file_path = os.path.join(temp_dir, "test.txt")
        ...     with open(file_path, "w") as f:
        ...         f.write("test")
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Temporary file for testing.

    Example:
        >>> def test_file_read(temp_file):
        ...     with open(temp_file, "w") as f:
        ...         f.write("test content")
        ...     with open(temp_file) as f:
        ...         assert f.read() == "test content"
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ============================================================================
# Logging Fixtures
# ============================================================================


@pytest.fixture
def capture_logs():
    """Capture log messages for testing.

    Example:
        >>> def test_logging(capture_logs):
        ...     logger = logging.getLogger("test")
        ...     logger.info("Test message")
        ...     assert "Test message" in capture_logs.text
    """
    import logging
    from io import StringIO

    # Create string buffer
    log_buffer = StringIO()

    # Create handler
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(logging.DEBUG)

    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    yield log_buffer

    # Cleanup
    root_logger.removeHandler(handler)


# ============================================================================
# Metrics Fixtures
# ============================================================================


@pytest.fixture
def reset_metrics():
    """Reset metrics between tests.

    Example:
        >>> def test_metrics(reset_metrics):
        ...     metrics = get_metrics_collector()
        ...     metrics.increment_counter("test_counter")
        ...     # Metrics are reset after test
    """
    from prometheus_client import CollectorRegistry

    # Create new registry for test
    test_registry = CollectorRegistry()

    yield test_registry

    # Registry is garbage collected after test


# ============================================================================
# Mock Helper Functions
# ============================================================================


def create_mock_response(status_code: int = 200, body: dict[str, Any] = None) -> Mock:
    """Create a mock HTTP response.

    Args:
        status_code: HTTP status code
        body: Response body as dict

    Returns:
        Mock response object

    Example:
        >>> response = create_mock_response(200, {"message": "success"})
        >>> assert response.status_code == 200
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = body or {}
    mock_response.text = json.dumps(body or {})
    return mock_response


def create_mock_bedrock_response(text: str = "Test response") -> dict[str, Any]:
    """Create a mock Bedrock response.

    Args:
        text: Response text

    Returns:
        Mock Bedrock response dict

    Example:
        >>> response = create_mock_bedrock_response("Hello!")
        >>> assert response["content"][0]["text"] == "Hello!"
    """
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
    }
