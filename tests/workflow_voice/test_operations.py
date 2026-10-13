"""Execute real Dagster graphs against explicitly injected local data adapters."""

import io
import wave
from types import SimpleNamespace

import pandas as pd
import pytest
from dagster import ResourceDefinition

from services.workflow_builder.sample_signal import (
    build_custom_workflow,
    filter_data,
    detect_anomalies,
)
from services.voiceops.voice_service import (
    CommandProcessor,
    NotificationService,
    VoiceService,
    VoiceOpsService,
)


def test_actual_dagster_execution():
    frame = pd.DataFrame(
        [
            {"value_usd": 10, "event_type": "TRANSFER"},
            {"value_usd": 200, "event_type": "TRANSFER"},
            {"value_usd": 500, "event_type": "SWAP"},
        ]
    )

    class LocalResult:
        def to_dataframe(self):
            return frame.copy()

    class LocalQueryAdapter:
        def query(self, query, job_config=None):
            assert query == "SELECT fixture_rows"
            return LocalResult()

    config = {
        "name": "local_fixture_execution",
        "ops": {
            "fetch_blockchain_data": {
                "config": {"query": "SELECT fixture_rows", "parameters": {}}
            },
            "filter_data": {
                "config": {
                    "conditions": {
                        "event_type": {"operator": "eq", "value": "TRANSFER"}
                    }
                }
            },
            "detect_anomalies": {
                "config": {
                    "threshold": 100.0,
                    "comparison": "greater_than",
                    "metric": "value_usd",
                }
            },
        },
    }
    result = build_custom_workflow(config).execute_in_process(
        resources={
            "bigquery": ResourceDefinition.hardcoded_resource(LocalQueryAdapter()),
        }
    )
    assert result.success
    assert result.output_for_node("detect_anomalies")["value_usd"].tolist() == [200]


def test_bad_filter_and_missing_metric_are_rejected():
    frame = pd.DataFrame({"value_usd": [1, 2], "label": ["a.b", "axb"]})
    context = SimpleNamespace(
        op_config={"conditions": {"label": {"operator": "contains", "value": "a.b"}}}
    )
    assert filter_data(context, frame)["label"].tolist() == ["a.b"]
    context.op_config = {"conditions": {"absent": {"operator": "eq", "value": 1}}}
    with pytest.raises(ValueError, match="Unknown filter column"):
        filter_data(context, frame)
    context.op_config = {
        "metric": "absent",
        "threshold": 1,
        "comparison": "greater_than",
    }
    with pytest.raises(ValueError, match="Unknown anomaly metric"):
        detect_anomalies(context, frame)


def test_parse_preserves_checksum_and_unmute():
    processor = CommandProcessor()
    assert processor.parse_command("unmute alerts").intent == "unmute_alerts"
    address = "0x742d35Cc6639C0532fE9f484Bd8A0E22E1E7d6C1"
    assert (
        processor.parse_command("search address " + address).entities["address"]
        == address
    )
    assert (
        VoiceOpsService()
        .create_signal_alert(
            {"signal_type": "HIGH_VALUE_TRANSFER", "related_addresses": []}
        )
        .message
    )


@pytest.mark.asyncio
async def test_no_credentials_or_invalid_audio_is_not_success(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    service = VoiceService()
    assert service.recognizer is None and service.microphone is None
    with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
        await service.text_to_speech("hello")
    with pytest.raises(ValueError):
        await service.speech_to_text(b"not a WAV")
    monkeypatch.delenv("ALERT_WEBHOOK_URL", raising=False)
    with pytest.raises(ValueError, match="webhook"):
        await NotificationService().send_webhook_alert({"description": "fixture"})

def test_dagster_delivery_failure_is_not_a_successful_job(monkeypatch):
    monkeypatch.delenv('ALERT_WEBHOOK_URL', raising=False)
    class LocalResult:
        def to_dataframe(self):
            return pd.DataFrame({'value_usd': [200]})
    class LocalQueryAdapter:
        def query(self, query, job_config=None):
            return LocalResult()
    config = {'name': 'failed_delivery', 'ops': {
        'fetch_blockchain_data': {'config': {'query': 'SELECT fixture_rows', 'parameters': {}}},
        'detect_anomalies': {'config': {'threshold': 100.0, 'comparison': 'greater_than', 'metric': 'value_usd'}},
        'generate_signal': {'config': {'signal_type': 'FIXTURE', 'description': 'fixture anomaly', 'severity': 'LOW'}},
        'send_alert': {'config': {'channels': ['webhook']}},
    }}
    result = build_custom_workflow(config).execute_in_process(
        resources={
            'bigquery': ResourceDefinition.hardcoded_resource(LocalQueryAdapter()),
            'notification_service': ResourceDefinition.hardcoded_resource(NotificationService()),
        }, raise_on_error=False)
    assert result.success is False
    assert 'Configured notification delivery failed' in result.failure_data_for_node('send_alert').error.to_string()
