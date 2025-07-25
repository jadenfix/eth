# Testing Services Integration Guide

This document provides comprehensive instructions for running E2E tests with real external services using your configured credentials.

## Overview

The test suite is organized into two main categories:

1. **Core Tests** (`tier0`, `tier1`) - Use mocks and local services
2. **Integration Tests** (`tier2`, `tier3`, `v3`) - Use real external services

## Environment Configuration

### Required Services

Your `.env` file contains credentials for the following services:

| Service | Status | Purpose |
|---------|--------|---------|
| **GCP** | ✅ Configured | BigQuery, Pub/Sub, Vertex AI |
| **Neo4j** | ✅ Configured | Graph database for ontology |
| **ElevenLabs** | ✅ Configured | Voice TTS/STT operations |
| **Slack** | ✅ Configured | Team notifications |
| **Stripe** | ✅ Configured | Billing and metering |
| **Dagster** | ✅ Configured | Workflow orchestration |
| **Blockchain APIs** | ✅ Configured | Alchemy, Infura, TheGraph |

### Environment Variables

All required environment variables are loaded from `/Users/jadenfix/eth/.env`:

```bash
# Google Cloud Platform
GOOGLE_CLOUD_PROJECT=ethhackathon
GOOGLE_APPLICATION_CREDENTIALS=.gcp_credentials.json

# BigQuery
BIGQUERY_DATASET=onchain_data
BIGQUERY_TABLE_RAW=raw_events
BIGQUERY_TABLE_CURATED=curated_events

# Neo4j
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Soccerginger20!

# ElevenLabs
ELEVENLABS_API_KEY=sk_41e0e2cbddf3197079d550fc0c9a90debe41ce1730609f80
ELEVENLABS_VOICE_ID=jqcCZkN6Knx8BJ5TBdYR

# Slack
SLACK_BOT_TOKEN=xoxb-9262480352880-9262647888928-A85ztNXRDAs0MRmhcujen8Ht
SLACK_APP_TOKEN=xapp-1-A097QE859A4-9241470962884-f4dfd218ba80c583a372e275fd1517a46a985c15be418115ad0e36acc6e49ef0
SLACK_SIGNING_SECRET=51342f50ee3d5193ee993853f1d0a192

# Stripe
STRIPE_SECRET_KEY=sk_test_51RSuZGP9ov6izJiujBWda1TMvXvTzzy0pdkD0IJHYZEthP1KFQbkHNFzljw5qEyhMTriu4m5ILbEukHTIxmIxArY00tpsdyk7L
STRIPE_WEBHOOK_SECRET=whsec_jTEubV1JlNKgUFW9xM2tWuygxqI2BcwO

# Dagster
DAGSTER_CLOUD_API_TOKEN=agent:eth:7d38d515427949b09a0f6c46dfb05543

# Blockchain APIs
ALCHEMY_API_KEY=Wol66FQUiZSrwlavHmn0OWL4U5fAOAGu
INFURA_PROJECT_ID=bb066d6f7fb2401e8c27a0c50699a0c1
INFURA_API_SECRET=u0FZ9vOgcOkeMxk5uPrOnCAaf+WW6DmDzItdm3OZ6WaCPkb9FCWyNw
THEGRAPH_API_KEY=46346b194efc554a0c3fc98c43964838
```

## Running Tests

### Quick Start

1. **Check Environment**:
   ```bash
   python test_runner_integration.py --check-env
   ```

2. **Run Integration Tests**:
   ```bash
   python test_runner_integration.py --mode integration --verbose
   ```

3. **Run Core Tests**:
   ```bash
   python test_runner_integration.py --mode core --verbose
   ```

4. **Run All Tests**:
   ```bash
   python test_runner_integration.py --mode all --verbose
   ```

### Manual Pytest Commands

**Integration Tests (Real Services)**:
```bash
# All integration tests
pytest -m integration -v --tb=short

# Specific test categories
pytest tests/e2e/tier2/ -m integration -v
pytest tests/e2e/tier3/ -m integration -v
pytest tests/e2e/graph_sync/ -m integration -v
pytest tests/e2e/zk_attestation/ -m integration -v
pytest tests/e2e/gemini_explain/ -m integration -v
pytest tests/e2e/action_executor/ -m integration -v
pytest tests/e2e/voice_alerts/ -m integration -v
```

**Core Tests (Mocks Only)**:
```bash
# All core tests
pytest -m "not integration" -v --tb=short

# Specific tiers
pytest tests/e2e/tier0/ -v
pytest tests/e2e/tier1/ -v
```

### Test Categories

#### Tier 0 (Smoke/Demo Blockers)
- **Location**: `tests/e2e/tier0/`
- **Purpose**: Basic functionality, UI loads, data visible
- **Services**: Mocks only
- **Run Time**: ~30 seconds

#### Tier 1 (Functional/Regression)
- **Location**: `tests/e2e/tier1/`
- **Purpose**: Core behaviors, data flow validation
- **Services**: Mocks + local Neo4j
- **Run Time**: ~2 minutes

#### Tier 2 (Governance/Compliance)
- **Location**: `tests/e2e/tier2/`
- **Purpose**: IAM, DLP, audit logs, real service integration
- **Services**: Real GCP, Neo4j, external APIs
- **Run Time**: ~5 minutes

#### Tier 3 (Resilience/Scale/Chaos)
- **Location**: `tests/e2e/tier3/`
- **Purpose**: Fault injection, performance, stress testing
- **Services**: Real services with load testing
- **Run Time**: ~10 minutes

#### V3 Add-on Tests
- **Location**: `tests/e2e/graph_sync/`, `tests/e2e/zk_attestation/`, etc.
- **Purpose**: New v3 features (CDC sync, ZK proofs, Gemini explain)
- **Services**: Real services
- **Run Time**: ~3 minutes

## Service-Specific Testing

### GCP Services

**BigQuery**:
- Tests: `tests/e2e/tier2/test_gcp_permissions_check.py`
- Validates: Dataset access, table creation, data insertion
- Note: May have permission restrictions

**Pub/Sub**:
- Tests: `tests/e2e/tier1/test_t1_a_realtime_ingestion.py`
- Validates: Topic creation, message publishing, subscription

**Vertex AI**:
- Tests: `tests/e2e/tier2/test_t2_b_v3_patches_integration.py`
- Validates: Model endpoint access, inference requests

### Neo4j Graph Database

**Connection**:
- Tests: `tests/e2e/tier0/test_t0_c_graph_queries.py`
- Validates: Database connectivity, CRUD operations

**Entity Resolution**:
- Tests: `tests/e2e/tier1/test_t1_b_bidirectional_sync.py`
- Validates: Entity creation, relationship management

### External APIs

**ElevenLabs Voice**:
- Tests: `tests/e2e/tier2/test_t2_b_v3_patches_integration.py`
- Validates: TTS generation, voice synthesis

**Slack Integration**:
- Tests: `tests/e2e/tier2/test_t2_a_real_service_integration.py`
- Validates: Bot authentication, message sending

**Stripe Billing**:
- Tests: `tests/e2e/tier2/test_t2_a_real_service_integration.py`
- Validates: API key validation, customer operations

**Blockchain APIs**:
- Tests: `tests/e2e/tier2/test_t2_a_real_service_integration.py`
- Validates: Alchemy, Infura, TheGraph connectivity

## Troubleshooting

### Common Issues

1. **Permission Denied (403)**:
   - **Cause**: GCP service account lacks permissions
   - **Solution**: Check IAM roles in GCP Console
   - **Workaround**: Tests will skip with warning

2. **Connection Refused**:
   - **Cause**: Local Neo4j not running
   - **Solution**: Start Neo4j: `docker-compose up neo4j`
   - **Workaround**: Tests will fail

3. **API Rate Limits**:
   - **Cause**: External API quotas exceeded
   - **Solution**: Wait for quota reset or upgrade plan
   - **Workaround**: Tests will skip with warning

4. **Missing Environment Variables**:
   - **Cause**: `.env` file not loaded
   - **Solution**: Check file path and format
   - **Workaround**: Tests will skip with clear message

### Debug Mode

Enable verbose output for detailed debugging:

```bash
# Verbose pytest
pytest -v -s --tb=long

# Verbose test runner
python test_runner_integration.py --verbose

# Check specific service
python test_runner_integration.py --check-env
```

### Mock Override

Force specific services to use mocks:

```bash
# Use mock for specific service
export USE_MOCK_GCP=1
export USE_MOCK_NEO4J=1
export USE_MOCK_ELEVENLABS=1

# Run tests
pytest -m integration -v
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  core-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Core Tests
        run: |
          python test_runner_integration.py --mode core

  integration-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Setup Environment
        run: |
          echo "${{ secrets.ENV_FILE }}" > .env
      - name: Run Integration Tests
        run: |
          python test_runner_integration.py --mode integration
```

### Environment Variables for CI

Store these in your CI/CD secrets:

```bash
# Required for integration tests
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account", ...}
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
ELEVENLABS_API_KEY=your-api-key
SLACK_BOT_TOKEN=your-slack-token
STRIPE_SECRET_KEY=your-stripe-key
```

## Performance Monitoring

### Test Execution Times

| Test Category | Average Time | Max Time |
|---------------|--------------|----------|
| Tier 0 | 30s | 60s |
| Tier 1 | 2m | 5m |
| Tier 2 | 5m | 10m |
| Tier 3 | 10m | 20m |
| V3 Add-ons | 3m | 8m |

### Resource Usage

- **Memory**: ~500MB per test process
- **CPU**: Moderate usage during API calls
- **Network**: Varies by external API usage
- **Storage**: Minimal (test data only)

## Best Practices

1. **Run Core Tests First**: Always run Tier 0/1 before integration tests
2. **Check Environment**: Use `--check-env` to validate configuration
3. **Use Verbose Mode**: Add `-v` for detailed output during debugging
4. **Monitor Costs**: Integration tests may incur API costs
5. **Clean Up**: Tests automatically clean up test data
6. **Parallel Execution**: Avoid running multiple integration test suites simultaneously

## Support

For issues with:
- **Test failures**: Check logs and environment configuration
- **Service access**: Verify credentials and permissions
- **Performance**: Monitor resource usage and API quotas
- **CI/CD**: Review GitHub Actions configuration

---

**Last Updated**: $(date)
**Test Suite Version**: v3.0.0
**Environment**: Production-ready with real service integration 