"""Read-only evidence-based MEV heuristics; patterns are not verified attacks."""

import asyncio
import hashlib
import json
from collections import deque
from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone
from decimal import Decimal
from statistics import median
from services.ingestion.ethereum_ingester import MessagePublisher, field, quantity


@dataclass
class MEVSignal:
    signal_id: str
    agent_name: str = "mev_watch"
    signal_type: str = ""
    confidence_score: float = 0.0
    related_addresses: list = dc_field(default_factory=list)
    related_transactions: list = dc_field(default_factory=list)
    description: str = ""
    severity: str = "LOW"
    metadata: dict = dc_field(default_factory=dict)
    timestamp: datetime = dc_field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("confidence_score must be between0 and1")
        return {**vars(self), "timestamp": self.timestamp.isoformat()}


class GasPriceAnalyzer:
    def is_anomalous_gas_price(self, current, history):
        prices = [Decimal(str(v)) for v in history]
        value = Decimal(str(current))
        if (
            not value.is_finite()
            or value < 0
            or any(not x.is_finite() or x < 0 for x in prices)
        ):
            raise ValueError("Gas prices must be finite and nonnegative")
        if len(prices) < 3:
            return False
        center = median(prices)
        deviation = median(abs(x - center) for x in prices)
        return value > max(center * 3, center + 6 * max(deviation, Decimal("1")))


def transaction_view(tx):
    data = field(tx, "event_data", {}) or {}
    price = field(tx, "gasPrice", data.get("gas_price"))
    if price is None:
        price = int(Decimal(str(field(tx, "gas_price_gwei", 0))) * Decimal(10**9))
    return {
        "hash": field(tx, "hash", field(tx, "transaction_hash")),
        "from": field(tx, "from", field(tx, "from_address", data.get("from"))),
        "to": field(tx, "to", field(tx, "to_address", data.get("to"))),
        "gasPrice": quantity(price),
    }


class SandwichDetector:
    def find_patterns(self, transactions):
        txs = [transaction_view(tx) for tx in transactions]
        results = []
        for i, first in enumerate(txs):
            if not first["from"] or not first["to"] or not first["hash"]:
                continue
            for j in range(i + 1, len(txs) - 1):
                middle = txs[j]
                if (
                    not middle["from"]
                    or middle["from"] == first["from"]
                    or middle["to"] != first["to"]
                    or not middle["hash"]
                ):
                    continue
                for last in txs[j + 1 :]:
                    if (
                        last["from"] == first["from"]
                        and last["to"] == first["to"]
                        and last["hash"]
                        and len({first["hash"], middle["hash"], last["hash"]}) == 3
                        and first["gasPrice"] > middle["gasPrice"] >= last["gasPrice"]
                    ):
                        results.append([first, middle, last])
        return results

    def detect_sandwich_pattern(self, transactions):
        return bool(self.find_patterns(transactions))


class MEVWatchAgent:
    def __init__(
        self, publisher=None, gas_threshold_gwei=100, whale_threshold_usd=100000
    ):
        self.publisher = publisher or MessagePublisher()
        self.recent_transactions = {}
        self.gas_history = deque(maxlen=200)
        self.gas_threshold_gwei = Decimal(str(gas_threshold_gwei))
        self.whale_threshold_usd = Decimal(str(whale_threshold_usd))
        self.detector = SandwichDetector()

    def _generate_signal_id(self, identifier, signal_type):
        return hashlib.sha256(f"{identifier}:{signal_type}".encode()).hexdigest()

    async def _publish_signal(self, signal):
        return await self.publisher.publish_event("ai-signals", signal.to_dict())

    async def _analyze_transaction(self, tx):
        view = transaction_view(tx)
        block = field(tx, "block_number")
        if block is not None:
            recent = self.recent_transactions.setdefault(quantity(block), [])
            if not any(transaction_view(x)["hash"] == view["hash"] for x in recent):
                recent.append(tx)
            for old in list(self.recent_transactions):
                if old < block - 10:
                    del self.recent_transactions[old]
            await self._detect_sandwich_attack(tx, block)
        gwei = Decimal(view["gasPrice"]) / Decimal(10**9)
        if gwei >= self.gas_threshold_gwei:
            await self._publish_signal(
                MEVSignal(
                    self._generate_signal_id(view["hash"], "gas"),
                    signal_type="FRONT_RUNNING",
                    confidence_score=0.55,
                    related_addresses=[x for x in [view["from"], view["to"]] if x],
                    related_transactions=[view["hash"]],
                    description="High-gas transaction: investigate potential front-running; not a confirmed attack",
                    severity="MEDIUM",
                    metadata={
                        "evidence": "configured_gas_threshold",
                        "gas_price_gwei": float(gwei),
                        "verified_attack": False,
                        "heuristic_score": True,
                    },
                )
            )
        self.gas_history.append(gwei)
        await self._detect_high_value_transfer(tx)

    async def _detect_sandwich_attack(self, tx, block_number):
        view = transaction_view(tx)
        for pattern in self.detector.find_patterns(
            self.recent_transactions.get(block_number, [])
        ):
            if view["hash"] not in [x["hash"] for x in pattern]:
                continue
            await self._publish_signal(
                MEVSignal(
                    self._generate_signal_id(
                        ":".join(x["hash"] for x in pattern), "sandwich"
                    ),
                    signal_type="SANDWICH_ATTACK",
                    confidence_score=0.7,
                    related_addresses=list(dict.fromkeys(x["from"] for x in pattern)),
                    related_transactions=[x["hash"] for x in pattern],
                    description="Ordered attacker/victim/attacker transaction pattern; requires swap-trace confirmation",
                    severity="HIGH",
                    metadata={
                        "block_number": block_number,
                        "verified_attack": False,
                        "heuristic_score": True,
                    },
                )
            )

    async def _detect_high_value_transfer(self, tx):
        usd = field(tx, "value_usd")
        if usd is None:
            return
        amount = Decimal(str(usd))
        if not amount.is_finite() or amount < 0:
            raise ValueError("Invalid USD value")
        if amount >= self.whale_threshold_usd:
            view = transaction_view(tx)
            await self._publish_signal(
                MEVSignal(
                    self._generate_signal_id(view["hash"], "whale"),
                    signal_type="HIGH_VALUE_TRANSFER",
                    confidence_score=0.8,
                    related_addresses=[x for x in [view["from"], view["to"]] if x],
                    related_transactions=[view["hash"]],
                    description="High-value transfer based on supplied USD valuation",
                    severity="HIGH",
                    metadata={
                        "value_usd": float(amount),
                        "valuation_source": "input_record",
                        "verified_attack": False,
                    },
                )
            )

    async def start_monitoring(self):
        import os
        from google.cloud import pubsub_v1

        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is required")
        loop = asyncio.get_running_loop()
        subscriber = pubsub_v1.SubscriberClient()

        def callback(message):
            async def process():
                try:
                    await self._analyze_transaction(json.loads(message.data))
                    message.ack()
                except Exception:
                    message.nack()

            asyncio.run_coroutine_threadsafe(process(), loop)

        future = subscriber.subscribe(
            subscriber.subscription_path(project, "agents-raw-events-sub"),
            callback=callback,
        )
        try:
            await asyncio.to_thread(future.result)
        finally:
            future.cancel()
            subscriber.close()


async def main():
    await MEVWatchAgent().start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
