"""Read-only Ethereum normalization, confirmed publishing and durable consumption.

Cloud clients are constructed only when used. Missing prices remain unavailable;
publication errors propagate so incomplete blocks are not treated as processed.
"""

import asyncio
import hashlib
import json
import os
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional
from web3 import Web3


def field(record, key, default=None):
    if isinstance(record, Mapping):
        return record.get(key, default)
    if hasattr(record, "__dict__") and key in vars(record):
        return vars(record)[key]
    value = getattr(record, key, default)
    return (
        value
        if value is None
        or isinstance(
            value, (str, bytes, int, float, dict, list, tuple, datetime, Decimal)
        )
        else default
    )


def quantity(value, default=0):
    if value is None:
        return default
    if isinstance(value, str):
        result = int(value, 16 if value.startswith("0x") else 10)
    elif isinstance(value, int) and not isinstance(value, bool):
        result = value
    else:
        raise ValueError("Ethereum quantity must be an integer or encoded integer")
    if result < 0:
        raise ValueError("Ethereum quantity cannot be negative")
    return result


def hash_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if callable(getattr(value, "hex", None)):
        result = value.hex()
        if isinstance(result, str):
            return result if result.startswith("0x") else "0x" + result
    raise ValueError("Transaction hash is required")


@dataclass
class ChainEvent:
    block_number: int
    transaction_hash: str
    log_index: Optional[int]
    contract_address: Optional[str]
    event_name: str
    event_data: dict
    timestamp: datetime
    chain_id: int

    def to_dict(self):
        return {
            **vars(self),
            "timestamp": self.timestamp.isoformat(),
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        }


class ValueCalculator:
    def __init__(self, price_provider=None):
        self.price_provider = price_provider

    def get_eth_price_usd(self):
        if self.price_provider is None:
            raise RuntimeError("No verified ETH/USD price source configured")
        price = Decimal(str(self.price_provider()))
        if not price.is_finite() or price <= 0:
            raise ValueError("Invalid ETH/USD price")
        return price

    def calculate_usd_value(self, value_eth):
        value = Decimal(str(value_eth))
        if not value.is_finite() or value < 0:
            raise ValueError("Invalid ETH amount")
        price = Decimal(str(self.get_eth_price_usd()))
        if not price.is_finite() or price <= 0:
            raise ValueError("Invalid ETH/USD price")
        return float(value * price)


class EventNormalizer:
    def __init__(self, chain_id=1, price_provider=None):
        self.chain_id = quantity(chain_id)
        self.calculator = ValueCalculator(price_provider) if price_provider else None

    def normalize_transaction(
        self, transaction, block_number, timestamp=None, receipt=None
    ):
        value = Decimal(quantity(field(transaction, "value", 0))) / Decimal(10**18)
        gas = quantity(
            field(transaction, "gasPrice", field(transaction, "effectiveGasPrice", 0))
        )
        source, target = field(transaction, "from"), field(transaction, "to")
        used = quantity(
            field(receipt or {}, "gasUsed", field(transaction, "gasUsed", 0))
        )
        now = (
            datetime.fromtimestamp(timestamp, timezone.utc)
            if isinstance(timestamp, (int, float))
            else datetime.now(timezone.utc)
        )
        return {
            "event_name": "TRANSACTION",
            "chain_id": self.chain_id,
            "block_number": quantity(block_number),
            "transaction_hash": hash_text(field(transaction, "hash")),
            "from_address": source,
            "to_address": target,
            "value_eth": float(value),
            "value_wei": str(quantity(field(transaction, "value", 0))),
            "gas_price_gwei": float(Decimal(gas) / Decimal(10**9)),
            "value_usd": (
                self.calculator.calculate_usd_value(value) if self.calculator else None
            ),
            "timestamp": now.isoformat(),
            "contract_address": target,
            "event_data": {
                "from": source,
                "to": target,
                "value": str(quantity(field(transaction, "value", 0))),
                "gas_price": str(gas),
                "gas_used": used,
                "status": quantity(field(receipt or {}, "status", 1)),
            },
        }


class MessagePublisher:
    def __init__(self, client=None, project=None):
        self.client = client
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")

    async def publish_event(self, topic, event):
        if not self.project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is required for publication")
        if self.client is None:
            from google.cloud import pubsub_v1

            self.client = pubsub_v1.PublisherClient()
        payload = event.to_dict() if isinstance(event, ChainEvent) else event
        future = self.client.publish(
            self.client.topic_path(self.project, topic),
            json.dumps(payload, allow_nan=False).encode(),
        )
        return await asyncio.to_thread(future.result, timeout=30)


class EthereumIngester:
    def __init__(self, web3=None, publisher=None, rpc_url=None):
        rpc = rpc_url or os.getenv("ETHEREUM_RPC_URL") or "http://127.0.0.1:8545"
        self.web3 = web3 if web3 is not None else Web3(Web3.HTTPProvider(rpc))
        self.publisher = publisher or MessagePublisher()
        self.normalizer = EventNormalizer()

    async def _process_block(self, block_number):
        block = await asyncio.to_thread(
            self.web3.eth.get_block, block_number, full_transactions=True
        )
        for transaction in field(block, "transactions", []):
            tx_hash = field(transaction, "hash")
            receipt = await asyncio.to_thread(
                self.web3.eth.get_transaction_receipt, tx_hash
            )
            await self._publish_event(
                self.normalizer.normalize_transaction(
                    transaction,
                    field(block, "number", block_number),
                    field(block, "timestamp"),
                    receipt,
                )
            )
            for i, log in enumerate(field(receipt, "logs", [])):
                await self._publish_event(
                    ChainEvent(
                        block_number,
                        hash_text(tx_hash),
                        i,
                        field(log, "address"),
                        "CONTRACT_EVENT",
                        {
                            "topics": [hash_text(x) for x in field(log, "topics", [])],
                            "data": field(log, "data"),
                            "removed": field(log, "removed", False),
                        },
                        datetime.fromtimestamp(field(block, "timestamp"), timezone.utc),
                        1,
                    )
                )

    async def _publish_event(self, event):
        return await self.publisher.publish_event("raw-chain-events", event)

    async def start_streaming(self):
        cursor = await asyncio.to_thread(lambda: self.web3.eth.block_number)
        while True:
            current = await asyncio.to_thread(lambda: self.web3.eth.block_number)
            for number in range(cursor + 1, current + 1):
                await self._process_block(number)
                cursor = number
            await asyncio.sleep(1)


class MessageProcessor:
    """Persist validated deliveries atomically before acknowledgement."""

    def __init__(self, database_path=None, handler=None):
        path = database_path or os.getenv("EVENT_DB_PATH", "./data/chain_events.sqlite")
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,payload TEXT NOT NULL)"
        )
        self.handler = handler
        self.lock = asyncio.Lock()

    async def process_message(self, message):
        async with self.lock:
            try:
                event = json.loads(message.data)
                if (
                    not isinstance(event, dict)
                    or not event.get("event_name")
                    or not isinstance(event.get("block_number"), int)
                ):
                    raise ValueError("Invalid chain event")
                encoded = json.dumps(event, sort_keys=True, allow_nan=False)
                identity = (
                    str(
                        event.get("transaction_hash")
                        or hashlib.sha256(encoded.encode()).hexdigest()
                    )
                    + ":"
                    + str(event.get("log_index", "transaction"))
                )
                if self.db.execute(
                    "SELECT 1 FROM events WHERE id=?", (identity,)
                ).fetchone():
                    message.ack()
                    return True
                if self.handler:
                    await self.handler(event)
                with self.db:
                    self.db.execute(
                        "INSERT INTO events VALUES(?,?) ON CONFLICT(id) DO NOTHING",
                        (identity, encoded),
                    )
                message.ack()
                return True
            except Exception:
                message.nack()
                return False

    def close(self):
        self.db.close()


async def main():
    await EthereumIngester().start_streaming()


if __name__ == "__main__":
    asyncio.run(main())
