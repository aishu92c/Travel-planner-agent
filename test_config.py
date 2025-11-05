#!/usr/bin/env python3
"""Test configuration system.

Run this script to verify the configuration system is working correctly.

Usage:
    python test_config.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_settings():
    """Test basic settings loading."""
    print("=" * 70)
    print("Testing Basic Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ App Name: {settings.app_name}")
    print(f"✓ Version: {settings.version}")
    print(f"✓ Environment: {settings.environment}")
    print(f"✓ Debug: {settings.debug}")
    print()


def test_aws_settings():
    """Test AWS settings."""
    print("=" * 70)
    print("Testing AWS Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Region: {settings.aws.region}")
    print(f"✓ Bedrock Model: {settings.aws.bedrock_model_id}")
    print(f"✓ S3 Artifacts Bucket: {settings.aws.s3_bucket_artifacts}")
    print(f"✓ S3 Documents Bucket: {settings.aws.s3_bucket_documents}")
    print()


def test_api_settings():
    """Test API settings."""
    print("=" * 70)
    print("Testing API Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Host: {settings.api.host}")
    print(f"✓ Port: {settings.api.port}")
    print(f"✓ Workers: {settings.api.workers}")
    print(f"✓ CORS Origins: {settings.api.cors_origins}")
    print(
        f"✓ Rate Limit: {settings.api.rate_limit_requests} req/"
        f"{settings.api.rate_limit_window_seconds}s"
    )
    print()


def test_agent_settings():
    """Test agent settings."""
    print("=" * 70)
    print("Testing Agent Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Temperature: {settings.agent.temperature}")
    print(f"✓ Max Tokens: {settings.agent.max_tokens}")
    print(f"✓ Timeout: {settings.agent.timeout_seconds}s")
    print(f"✓ Max Retries: {settings.agent.max_retries}")
    print()


def test_database_settings():
    """Test database settings."""
    print("=" * 70)
    print("Testing Database Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Agents Table: {settings.database.agents_table}")
    print(f"✓ Checkpoints Table: {settings.database.checkpoints_table}")
    print(f"✓ Cache Table: {settings.database.cache_table}")
    print(f"✓ Billing Mode: {settings.database.billing_mode}")
    print()


def test_cache_settings():
    """Test cache settings."""
    print("=" * 70)
    print("Testing Cache Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Enabled: {settings.cache.enabled}")
    print(f"✓ Provider: {settings.cache.provider}")
    print(f"✓ Redis Host: {settings.cache.redis_host}:{settings.cache.redis_port}")
    print(f"✓ TTL: {settings.cache.ttl_seconds}s")
    print(f"✓ Semantic Cache: {settings.cache.semantic_cache_enabled}")
    print()


def test_vectordb_settings():
    """Test vector DB settings."""
    print("=" * 70)
    print("Testing Vector DB Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Provider: {settings.vectordb.provider}")
    print(f"✓ Embedding Model: {settings.vectordb.embedding_model}")
    print(f"✓ Embedding Dimension: {settings.vectordb.embedding_dimension}")
    print(f"✓ Top K: {settings.vectordb.top_k}")
    print(f"✓ Similarity Threshold: {settings.vectordb.similarity_threshold}")
    print()


def test_observability_settings():
    """Test observability settings."""
    print("=" * 70)
    print("Testing Observability Settings")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Tracing Enabled: {settings.observability.tracing_enabled}")
    print(f"✓ Metrics Enabled: {settings.observability.metrics_enabled}")
    print(f"✓ Log Level: {settings.observability.log_level}")
    print(f"✓ Log Format: {settings.observability.log_format}")
    print()


def test_feature_flags():
    """Test feature flags."""
    print("=" * 70)
    print("Testing Feature Flags")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ RAG: {settings.features.enable_rag}")
    print(f"✓ Caching: {settings.features.enable_caching}")
    print(f"✓ Streaming: {settings.features.enable_streaming}")
    print(f"✓ Multi-Agent: {settings.features.enable_multi_agent}")
    print(f"✓ Tool Calling: {settings.features.enable_tool_calling}")
    print()


def test_environment_helpers():
    """Test environment helper methods."""
    print("=" * 70)
    print("Testing Environment Helpers")
    print("=" * 70)

    from config import get_settings

    settings = get_settings()

    print(f"✓ Is Development: {settings.is_development()}")
    print(f"✓ Is Staging: {settings.is_staging()}")
    print(f"✓ Is Production: {settings.is_production()}")
    print()


def test_environment_configs():
    """Test environment-specific configurations."""
    print("=" * 70)
    print("Testing Environment-Specific Configs")
    print("=" * 70)

    from config.environments import (
        get_dev_settings,
        get_prod_settings,
        get_staging_settings,
    )

    # Development
    dev = get_dev_settings()
    print(f"✓ Development - Debug: {dev.debug}, " f"Log Level: {dev.observability.log_level}")

    # Staging
    staging = get_staging_settings()
    print(f"✓ Staging - Debug: {staging.debug}, " f"Workers: {staging.api.workers}")

    # Production
    prod = get_prod_settings()
    print(
        f"✓ Production - Debug: {prod.debug}, "
        f"Workers: {prod.api.workers}, "
        f"Sample Rate: {prod.observability.tracing_sample_rate}"
    )
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Configuration System Test" + " " * 28 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")

    tests = [
        test_basic_settings,
        test_aws_settings,
        test_api_settings,
        test_agent_settings,
        test_database_settings,
        test_cache_settings,
        test_vectordb_settings,
        test_observability_settings,
        test_feature_flags,
        test_environment_helpers,
        test_environment_configs,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            import traceback

            traceback.print_exc()
            return 1

    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print("\nConfiguration system is working correctly!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
