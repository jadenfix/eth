# Infrastructure validation and cloud planning

The Terraform root is `infra/gcp`. Its tracked `neo4j_aura.tf` symlink includes
`infra/graph/neo4j_aura.tf`; the graph file is not a standalone Terraform module.
Aura is external; that file manages Google Secret Manager and optional Cloud SQL,
so it does not declare a separate Neo4j provider.

## Credential-free source gate

CI verifies the official Terraform 1.15.9 Linux archive against its pinned SHA256,
then runs the actual signed providers from the committed lock file:

```sh
terraform fmt -check -recursive infra
terraform -chdir=infra/gcp init -backend=false -input=false -lockfile=readonly
terraform -chdir=infra/gcp validate -no-color
```

These commands validate syntax, provider schema, and references. They do not
contact a configured GCP project, create infrastructure, certify a trained model,
or establish deployment readiness. Provider-download network access is required.

## Real cloud plan

The original cloud-plan job remains available when `GCP_SA_KEY` and
`GCP_PROJECT_ID` are present. Without them, CI explicitly records that the cloud
plan was not executed. A successful source gate is not a successful cloud plan.
Planning is non-interactive and no apply is performed.

Set these actual inputs before a real plan:

- `TF_VAR_project_id`: the authorized project ID.
- `TF_VAR_dlp_wrapped_key_base64`: actual KMS-encrypted DLP key material, base64
  encoded and encrypted with the actual DLP KMS key referenced by this module.
  That key must already exist (provisioned/imported) before wrapping the material.
  The former literal placeholder was removed.
- `TF_VAR_dev_postgres_password`: a unique password of at least 16 characters.
- `TF_VAR_dev_postgres_allowed_cidr`: an explicit client CIDR; unrestricted
  `0.0.0.0/0` and `::/0` are rejected.
- `TF_VAR_workbench_zone`: the VM's actual zone, default `us-central1-a`.

The workflow takes the first three sensitive inputs from `GCP_PROJECT_ID`,
`DLP_WRAPPED_KEY_BASE64`, and `DEV_POSTGRES_PASSWORD` secrets; the client CIDR from
repository variable `DEV_POSTGRES_ALLOWED_CIDR`. Missing or invalid inputs fail a
configured plan. Sensitive credentials also enter Terraform state, which needs a
protected backend before deployment. The current root has no remote backend.

## Model and training boundary

The Google 5.x provider does not implement the originally declared
`google_vertex_ai_model` or `google_vertex_ai_training_pipeline` resource types.
They were unsupported declarations, not working model provisioning. This module
creates the supported endpoint, feature-store and storage foundation. Model
training, upload and endpoint deployment belong to the actual Vertex SDK/API
workflow, with real training data, image, artifacts and credentials.

`vertex_model_resource` accepts an externally registered model resource. An
optional Dataflow batch job requires an actual caller-provided
`batch_prediction_template_gcs_path` and that model resource; the formerly
hardcoded unverified template is gone. With neither input, no batch job runs.
The `vertex_ml_integration` output explicitly reports that training and model
upload are not managed. No placeholder model, trained accuracy or serving
capability is claimed by Terraform validation.
