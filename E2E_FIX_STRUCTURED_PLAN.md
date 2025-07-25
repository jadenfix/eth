# E2E Test Fix - Structured Plan

## 🎯 **OVERALL OBJECTIVE**
Fix all E2E test errors systematically to achieve 100% pass rate across all test tiers.

## 📋 **PHASE 1: TIER 0 FIXES (Priority: CRITICAL)**

### 1.1 Fix Graph Path Query (Cypher Syntax)
**File**: `tests/e2e/tier0/test_t0_c_graph_queries.py`
**Error**: `neo4j.exceptions.CypherSyntaxError: Invalid input ':'`
**Root Cause**: Incorrect Cypher path syntax with relationship labels
**Fix**: Update path query to use proper Neo4j syntax

### 1.2 Fix Graph Aggregation Query (Duplicate Counting)
**File**: `tests/e2e/tier0/test_t0_c_graph_queries.py`
**Error**: `assert 1365 == 15` (overcounting)
**Root Cause**: Query returns duplicate relationships
**Fix**: Add DISTINCT to aggregation query

### 1.3 Fix Graph Export Format (Schema Mismatch)
**File**: `tests/e2e/tier0/test_t0_c_graph_queries.py`
**Error**: `AssertionError: Export should have 'edges' field`
**Root Cause**: Test expects 'edges' but helper returns 'relationships'
**Fix**: Update test assertion to match actual schema

### 1.4 Fix API Error Handling (Mock Response)
**File**: `tests/e2e/tier0/test_t0_d_ui_rendering.py`
**Error**: `AssertionError: Should return proper error code`
**Root Cause**: Mock client returns 200 instead of error codes
**Fix**: Update MockAsyncClient to return proper error codes

## 📋 **PHASE 2: TIER 1 FIXES (Priority: HIGH)**

### 2.1 Fix BigQuery Schema Issues
**Files**: Multiple Tier 1 test files
**Errors**: Missing fields in BigQuery schema
**Missing Fields**:
- `gas_price`
- `processing_timestamp`
- `latency_ms`
- `fixture_id`
- `first_seen`
- `send_attempt`
- `publish_timestamp`

**Fix**: Update BigQuery table creation in helper functions

### 2.2 Fix GCP Permission Handling
**Files**: Tier 1 test files
**Error**: `google.api_core.exceptions.PermissionDenied: 403`
**Root Cause**: Real GCP calls without proper mocking
**Fix**: Enhance GCP helper to handle permission errors gracefully

## 📋 **PHASE 3: COMPREHENSIVE TEST FIXES (Priority: MEDIUM)**

### 3.1 Fix Missing Dependencies
**Errors**: Missing modules
**Dependencies to Install**:
- `aioredis`
- `elevenlabs`
- Fix Dagster GCP resource imports

### 3.2 Fix Service Implementation Issues
**Issues**:
- Missing GraphQL types and resolvers
- Missing Vertex AI pipeline templates
- Missing audit sink classes
- Mock serialization issues

### 3.3 Fix Import Errors
**Files**: Multiple comprehensive test files
**Errors**: Cannot import various classes
**Fix**: Implement missing classes or fix import paths

## 📋 **PHASE 4: V3 ADD-ON TEST IMPLEMENTATION (Priority: HIGH)**

### 4.1 Create Test Directory Structure
```
tests/e2e/
├── graph_sync/
│   ├── test_bq_to_neo4j.py
│   └── test_neo4j_to_bq.py
├── zk_attestation/
│   ├── test_proof_generation.py
│   ├── test_solidity_verifier.py
│   └── test_signal_with_proof.py
├── gemini_explain/
│   └── test_streaming_explanation.py
├── action_executor/
│   ├── test_playbook_dispatch.py
│   ├── test_dry_run_guard.py
│   └── test_end_to_end_freeze_flow.py
├── voice_alerts/
│   └── test_tts_websocket.py
└── cross_cutting/
    └── test_obs_demo_script.py
```

### 4.2 Implement Each Test Category
- **Graph Sync**: Bidirectional data flow tests
- **ZK Attestation**: Proof generation and verification
- **Gemini Explain**: Streaming explanation tests
- **Action Executor**: Playbook execution tests
- **Voice Alerts**: TTS/STT integration tests

## 🔧 **EXECUTION ORDER**

### STEP 1: Install Missing Dependencies
```bash
pip install aioredis elevenlabs
```

### STEP 2: Fix Tier 0 Tests (4 files)
1. Fix `test_t0_c_graph_queries.py` (3 issues)
2. Fix `test_t0_d_ui_rendering.py` (1 issue)

### STEP 3: Fix Tier 1 Tests (2 files)
1. Fix BigQuery schema in `gcp.py` helper
2. Fix GCP permission handling

### STEP 4: Fix Comprehensive Tests (12 issues)
1. Fix import errors
2. Fix service implementation
3. Fix mock serialization

### STEP 5: Implement V3 Tests (8 files)
1. Create directory structure
2. Implement each test category

## 📊 **SUCCESS METRICS**

### Current Status
- Tier 0: 22/26 (85%)
- Tier 1: 1/10 (10%)
- Comprehensive: 14/26 (54%)
- V3 Tests: 0/0 (0%)

### Target Status
- Tier 0: 26/26 (100%)
- Tier 1: 10/10 (100%)
- Comprehensive: 26/26 (100%)
- V3 Tests: 8/8 (100%)

## ⏱️ **TIME ESTIMATES**

- **Phase 1**: 2-3 hours
- **Phase 2**: 2-3 hours
- **Phase 3**: 4-6 hours
- **Phase 4**: 8-12 hours
- **Total**: 16-24 hours

## 🚨 **RISK MITIGATION**

1. **Test each fix individually** before moving to next
2. **Keep backups** of working code
3. **Document each change** for rollback if needed
4. **Run tests frequently** to catch regressions

## 📝 **PROGRESS TRACKING**

- [x] Phase 1 Complete ✅ **TIER 0: 26/26 PASSING (100%)**
- [ ] Phase 2 Complete 🔄 **TIER 1: 4/10 PASSING (40%) - IN PROGRESS**
- [ ] Phase 3 Complete
- [ ] Phase 4 Complete
- [ ] All Tests Passing
- [ ] Documentation Updated

---

**NEXT ACTION**: Continue Phase 2 - Fix remaining Tier 1 Tests (GCP permissions, latency field type, Neo4j duplicates) 