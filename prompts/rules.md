no emojis,

1. Git & Branching
	1.	Branch per feature/bug: feature/<short-desc> or bugfix/<ticket#>-<desc>.
	2.	Pull Request Reviews: Every PR needs at least one approving review before merge.
	3.	Commit messages: Imperative, reference issue (e.g. “Add MEV-watch agent subscription (Closes #42)”).
	4.	Rebase, don’t merge: Keep main linear. Rebase feature branches onto latest main before merging.

2. Code Quality & Style
	5.	Language linting:
	•	Python: black + flake8 + mypy (≥95% type coverage)
	•	TypeScript: prettier + eslint + ts-strict
	6.	Single-responsibility modules: One class or function per file where it makes sense—keep services/ dirs flat.
	7.	DRY & explicit: Factor out repeated logic (e.g. JSON schema validation, BigQuery helpers) into shared utils in sdk/.

3. Testing & CI/CD
	8.	Test coverage: ≥80% overall; all new code comes with unit tests in tests/.
	9.	End-to-End smoke tests: A minimal “happy path” that exercises ingestion → Vertex AI → signal publish.
	10.	CI pipeline (GitHub Actions): On PR:
	•	Install deps
	•	Lint → type-check → run tests
	•	Build Docker images (no push)
	•	Validate Terraform plan (in infra/)

4. Infrastructure as Code
	11.	Terraform styling: terraform fmt + tflint on every change in infra/.
	12.	Module reuse: Encapsulate GCP patterns (Pub/Sub + Dataflow + BigQuery) as reusable Terraform modules.
	13.	Drift detection: Schedule nightly terraform plan in CI; alert on unexpected diffs.

5. API & Schema Governance
	14.	OpenAPI / gRPC proto specs:
	•	Keep api_gateway/proto/ as source-of-truth.
	•	Auto-generate clients into sdk/js/ and sdk/python/.
	15.	GraphQL schema: Document every type and field in services/ontology/graph_api.py; versioned migrations.
	16.	JSON schema validation: All “chain-event” objects must validate against a canonical schema before landing in BigQuery.

6. Security & Secret Management
	17.	No secrets in code: All creds via .env (dev) or GCP Secret Manager (prod).
	18.	Least privilege IAM: Service accounts scoped per-service (e.g. ingestion SA only BigQuery Data Editor + Pub/Sub Subscriber).
	19.	DLP enforcement: Column-level redaction policies defined in infra/dlp.tf.

7. Observability & Monitoring
	20.	Structured logging: JSON logs with severity, service, trace_id.
	21.	Metrics: Expose Prometheus endpoints in agents + ingestion, scrape via Cloud Monitoring.
	22.	Alerting:
	•	On Dataflow pipeline failures
	•	High anomaly-detector error rates
	•	Unexpected schema changes

8. Documentation & Collaboration
	23.	Docs in Markdown: Every service gets a README.md with purpose, env vars, local run steps.
	24.	Living architecture diagram: Update docs/system_architecture_v2.png whenever you add/remove a layer.
	25.	Sprint board: Track tasks in GitHub Projects or Trello; keep user stories aligned to hackathon days.