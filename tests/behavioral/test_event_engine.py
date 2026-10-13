"""Offline regression tests: real computation/storage; explicit provider adapters."""

import json
import sqlite3
from unittest.mock import Mock, AsyncMock
import pytest
from services.ingestion.ethereum_ingester import (
    EventNormalizer,
    ValueCalculator,
    MessagePublisher,
    MessageProcessor,
    EthereumIngester,
)
from services.agents.mev_watch.agent import (
    SandwichDetector,
    GasPriceAnalyzer,
    MEVWatchAgent,
)
from services.entity_resolution.pipeline import (
    FeatureExtractor,
    ConfidenceScorer,
    EntityResolutionPipeline,
    VertexAIPipeline,
)
from services.ingestion.database_helper import BigQueryHelper


def transaction(**updates):
    return {
        "hash": "0x" + "1" * 64,
        "from": "0x" + "a" * 40,
        "to": "0x" + "b" * 40,
        "value": "0xde0b6b3a7640000",
        "gasPrice": "0x4a817c800",
        **updates,
    }


def test_quantities_price_availability_and_configured_decimal_conversion():
    record = EventNormalizer().normalize_transaction(transaction(), 18500000)
    assert record["value_eth"] == 1 and record["gas_price_gwei"] == 20
    assert record["value_usd"] is None
    priced = EventNormalizer(price_provider=lambda: "2000.25").normalize_transaction(
        transaction(), 18500000
    )
    assert priced["value_usd"] == 2000.25
    with pytest.raises(RuntimeError):
        ValueCalculator().calculate_usd_value(1)
    with pytest.raises(ValueError):
        EventNormalizer().normalize_transaction(transaction(value="-1"), 1)
    with pytest.raises(ValueError):
        ValueCalculator(lambda: "NaN").calculate_usd_value(1)


@pytest.mark.asyncio
async def test_publisher_confirmation_failure_propagates():
    client = Mock()
    client.publish.return_value.result.side_effect = RuntimeError(
        "provider publication failed"
    )
    publisher = MessagePublisher(client=client, project="fixture-project")
    with pytest.raises(RuntimeError, match="publication failed"):
        await publisher.publish_event("raw-chain-events", {"event_name": "TRANSACTION"})
    client.publish.return_value.result.assert_called_once_with(timeout=30)


@pytest.mark.asyncio
async def test_block_processing_propagates_publish_failure():
    rpc = Mock()
    rpc.eth.get_block.return_value = {
        "number": 1,
        "timestamp": 1700000000,
        "transactions": [transaction()],
    }
    rpc.eth.get_transaction_receipt.return_value = {
        "gasUsed": 21000,
        "status": 1,
        "logs": [],
    }
    publisher = Mock()
    publisher.publish_event = AsyncMock(side_effect=RuntimeError("broker down"))
    with pytest.raises(RuntimeError, match="broker down"):
        await EthereumIngester(web3=rpc, publisher=publisher)._process_block(1)


@pytest.mark.asyncio
async def test_message_storage_restart_dedup_and_failed_delivery(tmp_path):
    path = tmp_path / "events.sqlite"
    handler = AsyncMock()
    processor = MessageProcessor(str(path), handler)
    event = {
        "event_name": "TRANSACTION",
        "block_number": 1,
        "transaction_hash": "0xtest",
    }
    message = Mock(data=json.dumps(event).encode())
    assert await processor.process_message(message)
    assert await processor.process_message(message)
    handler.assert_awaited_once()
    assert message.ack.call_count == 2
    processor.close()
    restarted = MessageProcessor(str(path), handler)
    assert restarted.db.execute("SELECT count(*) FROM events").fetchone()[0] == 1
    malformed = Mock(data=b"{")
    assert not await restarted.process_message(malformed)
    malformed.nack.assert_called_once()
    malformed.ack.assert_not_called()
    restarted.close()


def test_sandwich_requires_victim_contract_order_and_distinct_hashes():
    attack = [
        transaction(hash="front", gasPrice=100),
        transaction(hash="victim", **{"from": "victim"}, gasPrice=50),
        transaction(hash="back", gasPrice=30),
    ]
    detector = SandwichDetector()
    assert detector.detect_sandwich_pattern(attack)
    assert not detector.detect_sandwich_pattern([attack[0], attack[2]])
    assert not detector.detect_sandwich_pattern(
        [{**tx, "from": "same"} for tx in attack]
    )
    assert not detector.detect_sandwich_pattern(
        [attack[0], {**attack[1], "to": "different"}, attack[2]]
    )
    assert not detector.detect_sandwich_pattern(list(reversed(attack)))
    assert not detector.detect_sandwich_pattern(
        [attack[0], attack[1], {**attack[2], "hash": "front"}]
    )
    assert not GasPriceAnalyzer().is_anomalous_gas_price(200, [20])


@pytest.mark.asyncio
async def test_whale_requires_real_valuation_and_heuristics_do_not_claim_attack():
    agent = MEVWatchAgent()
    agent._publish_signal = AsyncMock()
    await agent._detect_high_value_transfer(transaction(value_usd=None))
    agent._publish_signal.assert_not_awaited()
    await agent._analyze_transaction(transaction(gasPrice=200 * 10**9))
    signal = agent._publish_signal.call_args.args[0]
    assert signal.metadata["verified_attack"] is False
    assert "not a confirmed attack" in signal.description


def test_features_and_confidence_reject_invalid_input():
    with pytest.raises(ValueError):
        FeatureExtractor().extract_features({"transaction_count": -1})
    with pytest.raises(ValueError):
        ConfidenceScorer().calculate_confidence({"feature_similarity": 2})
    with pytest.raises(ValueError):
        FeatureExtractor().extract_features(
            {"first_seen": "2026-10-13", "last_seen": "2026-01-01"}
        )


@pytest.mark.asyncio
async def test_resolution_requires_observations_and_labels_candidates(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fixture-project")
    with pytest.raises(RuntimeError, match="explicitly authenticated"):
        await EntityResolutionPipeline().resolve_entities(["wallet-a"])
    updater = Mock()
    updater.update_entity_graph = AsyncMock()
    resolver = EntityResolutionPipeline(
        data_provider=lambda addresses: {
            a: {"transaction_count": 100, "total_volume_eth": 10} for a in addresses
        },
        graph_updater=updater,
    )
    result = await resolver.resolve_entities(["wallet-a", "wallet-b"])
    assert result["verified_identity"] is False and result["confidence"] <= 0.8
    updater.update_entity_graph.assert_awaited_once()


@pytest.mark.asyncio
async def test_unconfigured_vertex_and_bigquery_never_discover_credentials(monkeypatch):
    monkeypatch.delenv("VERTEX_PIPELINE_TEMPLATE", raising=False)
    with pytest.raises(RuntimeError, match="VERTEX_PIPELINE_TEMPLATE"):
        await VertexAIPipeline().run_entity_resolution_job({})
    helper = BigQueryHelper(project="fixture-project")
    with pytest.raises(RuntimeError, match="explicitly authenticated"):
        helper.query_recent_blocks()
