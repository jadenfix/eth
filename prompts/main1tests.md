Below is a v3 add-on E2E test suite that snaps onto the baseline tests I gave you for v2.
I list only new or changed flows—everything from v2 still runs—and flag which patch they cover.
Structure, naming, and folder layout mirror the earlier plan so you can drop these files straight into tests/e2e/ without rewriting CI.

⸻

0. Folder Overlay

tests/e2e/
├── graph_sync/               # Patch 1
│   ├── test_bq_to_neo4j.py
│   └── test_neo4j_to_bq.py
├── zk_attestation/           # Patch 2
│   ├── test_proof_generation.py
│   ├── test_solidity_verifier.py
│   └── test_signal_with_proof.py
├── gemini_explain/           # Patch 3
│   └── test_streaming_explanation.py
├── action_executor/          # Patch 4
│   ├── test_playbook_dispatch.py
│   ├── test_dry_run_guard.py
│   └── test_end_to_end_freeze_flow.py
├── voice_alerts/             # Patch 5
│   └── test_tts_websocket.py
└── cross_cutting/
    └── test_obs_demo_script.py


⸻

1. Patch 1 — Bidirectional Graph Sync

E2E-GS-01: BigQuery → Neo4j CDC Sync

Step	Trigger/Input	Expected Artifact	Validation
1	Insert/update a wallet label row in bq.curated.wallet_labels using fixture ID	Pub/Sub topic bq.cdc emits row event	Poll Pub/Sub; assert receipt
2	Dataflow neo4j_sync writes corresponding node/edge to AuraDB	AuraDB node exists within 90 s	Cypher query (MATCH (w:Wallet {id: …}))
3	CDC ack POSTs back to graph_api.py /edges/stream	ack_id present	REST response 200
KPI	End-to-end latency ≤ 90 s	Measure timestamps	assert <90

E2E-GS-02: Neo4j → BigQuery CDC Sync
	•	Reverse the flow: update a node property in Neo4j; expect BigQuery row patch.
	•	Verify optimistic locking (BQ row update_ts > prior value) to avoid lost update.

⸻

2. Patch 2 — ZK-Attested Signals

E2E-ZK-01: Proof Generation
	1.	Publish mock signal.json to Pub/Sub.
	2.	Cloud Function runs zk_attestation/prover/generate_proof.ts.
	3.	Artifact: proof.json in GCS bucket contains proof, publicSignals, signalHash.
	4.	Validate snarkJS groth16 verify returns true locally.

E2E-ZK-02: Solidity Verifier
	•	Deploy SignalVerifier.sol to local Hardhat chain in CI.
	•	Call verifySignal(proof, publicSignals); expect boolean true.
	•	Negative test: tamper bit in signalHash → expect false.

E2E-ZK-03: Full Signal Publication

Stage	What Happens	Assertion
Agent emits raw signal.json	Contains signal_id, no proofHash	OK
Proof pipeline runs	Adds proofHash to message on signals.verified topic	Non-empty
Front-end component ZkBadge fetches /verify → returns status: verified	UI shows green badge	Playwright screenshot compare


⸻

3. Patch 3 — Gemini 2-Pro “Explainability”

E2E-GM-01: Streaming Explanation API
	1.	Insert fixture signal_id into signal_explanations with NULL explanation.
	2.	Call /signals/{id}/explain REST → triggers ai_services/gemini_explain/inference.py.
	3.	Validate:
	•	First SSE chunk arrives ≤ 2 s (event: chunk).
	•	Stream ends with event: done.
	4.	BigQuery row now populated with explanation text.

⸻

4. Patch 4 — Autonomous Action Executor

E2E-AE-01: Playbook Dispatch
	•	Publish verified signal with action_required: freeze_position.
	•	dispatcher.py loads freeze_position.yaml playbook.
	•	Dry-run flag off ⇒ invokes mock ethers.js provider to send tx.
	•	Assert:
	•	Pub/Sub actions.executed topic contains tx hash.
	•	BigQuery table executed_actions row status SUCCESS.

E2E-AE-02: Dry-Run Guard
	•	Same as above but with dry_run: true header.
	•	Expect no on-chain call, status DRY_RUN_ONLY.

E2E-AE-03: End-to-End Freeze Flow
	1.	Whale Tracker emits ≥ $10 M transfer signal.
	2.	Proof verified (Patch 2).
	3.	Executor freezes address on mock chain.
	4.	Gemini explanation generated; UI side-panel shows “Position frozen automatically.”
	5.	Slack alert posts summary with tx hash and proof badge link.
	6.	KPIs: p95 latency pipeline ≤ 60 s.

⸻

5. Patch 5 — Voice & Alert Polish

E2E-VA-01: Browser TTS WebSocket
	•	Open dashboard page; JS connects to voiceops WebSocket.
	•	Server pushes TTS binary on signal arrival; browser AudioContext plays.
	•	Jest or Playwright intercept audio element events → assert ended fires.

E2E-VA-02: OBS Demo Script Integrity
	•	CI job loads docs/demo_script.obs.json, spins headless OBS container, and records 10 s.
	•	Verify video artifact exists and contains at least one audio track and two screen sources.

⸻

6. Cross-Patch Governance & Security Add-Ons

Test ID	What	Expected
E2E-GOV-03	ZK proof file never stored with PII pre-mask	Scan GCS bucket; filenames with pattern proof_*.json have zero fields matching DLP sensitive regex.
E2E-AUD-02	Action-executor on-chain tx logged in audit sink	Audit record includes signal_id, tx_hash, playbook, principal.
E2E-SEC-01	Bandit/gosec gate passes for new dirs (zk_attestation, action_executor)	CI fails if high-severity finding.


⸻

7. CI Layer Updates
	1.	Matrix job runs baseline v2 suite + new directories.
	2.	Use hardhat node --fork in a side-car for on-chain tests.
	3.	Cache circom+snarkJS build artifacts to keep runtime < 15 min.
	4.	OBS test runs only on nightly to avoid long builds.

⸻

8. Green-to-Blue Cut-over Criteria (v3)

Check	Pass Condition
❏ Graph sync lag 95th ≤ 90 s (E2E-GS-01/02)	
❏ ≥ 95 % of signals carry valid ZK proof (E2E-ZK-03)	
❏ Gemini explain endpoint p95 latency < 3 s, error < 1 %	
❏ Executor dry-run guard blocks Prod keys in CI (E2E-AE-02)	
❏ Voice WebSocket reliability > 99 % in 100 msg soak	


⸻

Need sample code, Playwright specs, or GitHub Actions YAML for any of these?

Just say the word and I’ll generate them.