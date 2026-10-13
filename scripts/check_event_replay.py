"""Actual loopback JSON-RPC→Web3→normalization→SQLite→MEV replay.

RPC block/receipt are explicit local fixtures. No live chain, funded transaction,
price service, Pub/Sub, or calibrated attack/identity claim is involved.
"""

import asyncio
import json
import sqlite3
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from web3 import Web3
from services.ingestion.ethereum_ingester import EthereumIngester, MessageProcessor
from services.agents.mev_watch.agent import MEVWatchAgent

ZERO = "0x" + "0" * 64
TX = "0x" + "1" * 64
ADDRESS = "0x" + "a" * 40
TARGET = "0x" + "b" * 40


class FixtureRPC(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        method = data["method"]
        tx = {
            "hash": TX,
            "from": ADDRESS,
            "to": TARGET,
            "value": hex(10**18),
            "gasPrice": hex(200 * 10**9),
            "gas": hex(21000),
            "nonce": "0x0",
            "blockHash": ZERO,
            "blockNumber": "0x1",
            "transactionIndex": "0x0",
            "input": "0x",
        }
        if method == "eth_getBlockByNumber":
            result = {
                "number": "0x1",
                "hash": ZERO,
                "parentHash": ZERO,
                "timestamp": hex(1700000000),
                "transactions": [tx],
                "gasUsed": hex(21000),
                "gasLimit": hex(30000000),
                "difficulty": "0x0",
                "totalDifficulty": "0x0",
                "size": "0x100",
                "extraData": "0x",
                "nonce": "0x0000000000000000",
                "sha3Uncles": ZERO,
                "logsBloom": "0x" + "0" * 512,
                "miner": ADDRESS,
                "receiptsRoot": ZERO,
                "stateRoot": ZERO,
                "transactionsRoot": ZERO,
                "uncles": [],
            }
        elif method == "eth_getTransactionReceipt":
            result = {
                "transactionHash": TX,
                "transactionIndex": "0x0",
                "blockHash": ZERO,
                "blockNumber": "0x1",
                "from": ADDRESS,
                "to": TARGET,
                "cumulativeGasUsed": hex(21000),
                "gasUsed": hex(21000),
                "contractAddress": None,
                "logs": [],
                "logsBloom": "0x" + "0" * 512,
                "status": "0x1",
                "effectiveGasPrice": hex(200 * 10**9),
            }
        elif method == "eth_chainId":
            result = "0x1"
        else:
            result = None
        output = json.dumps(
            {"jsonrpc": "2.0", "id": data["id"], "result": result}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

    def log_message(self, *args):
        pass


class SQLitePublisher:
    """Explicit local replay sink; this is not a cloud Pub/Sub implementation."""

    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS replay(topic TEXT NOT NULL,id TEXT PRIMARY KEY,payload TEXT NOT NULL)"
        )

    async def publish_event(self, topic, event):
        payload = event.to_dict() if hasattr(event, "to_dict") else event
        identity = payload.get("signal_id") or payload["transaction_hash"]
        with self.db:
            self.db.execute(
                "INSERT INTO replay VALUES(?,?,?) ON CONFLICT(id) DO NOTHING",
                (topic, identity, json.dumps(payload)),
            )
        return identity

    def close(self):
        self.db.close()


async def verify(directory, port):
    path = str(Path(directory) / "replay.sqlite")
    publisher = SQLitePublisher(path)
    rpc = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{port}"))
    await EthereumIngester(web3=rpc, publisher=publisher)._process_block(1)
    event = json.loads(
        publisher.db.execute(
            "SELECT payload FROM replay WHERE topic='raw-chain-events'"
        ).fetchone()[0]
    )
    assert (
        event["value_eth"] == 1
        and event["gas_price_gwei"] == 200
        and event["value_usd"] is None
    )
    agent = MEVWatchAgent(publisher=publisher)
    processor = MessageProcessor(
        str(Path(directory) / "accepted.sqlite"), handler=agent._analyze_transaction
    )

    class Delivery:
        data = json.dumps(event).encode()
        acked = 0

        def ack(self):
            self.acked += 1

        def nack(self):
            raise AssertionError("Valid fixture delivery was rejected")

    delivery = Delivery()
    assert await processor.process_message(delivery)
    assert await processor.process_message(delivery)
    assert delivery.acked == 2
    processor.close()
    publisher.close()
    restarted = SQLitePublisher(path)
    rows = restarted.db.execute("SELECT topic,payload FROM replay").fetchall()
    assert len(rows) == 2
    signal = json.loads(
        next(payload for topic, payload in rows if topic == "ai-signals")
    )
    assert signal["metadata"]["verified_attack"] is False
    assert signal["signal_type"] == "FRONT_RUNNING"
    restarted.close()
    print(
        "PASS: real loopback JSON-RPC fixture → actual Web3 → normalization → SQLite durable delivery/dedup → MEV heuristic → restart persistence. No live provider or verified attack claim."
    )


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureRPC)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory() as directory:
            asyncio.run(verify(directory, server.server_port))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
