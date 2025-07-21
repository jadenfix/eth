# Onchain Command Center

A Palantir-grade blockchain intelligence platform for real-time data fusion, AI-powered analysis, and institutional-grade compliance.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Identity & Access → Ingestion → Semantic Fusion → Intelligence     │
│  Cloud IAM + DLP  → Dataflow   → Ontology + ER   → Agent Mesh       │
│                    → BigQuery  → Neo4j Graph    → Vertex AI         │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

1. **Prerequisites**
   ```bash
   # Install dependencies
   npm install
   pip install -r requirements.txt
   
   # Setup GCP credentials
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Environment Setup**
   ```bash
   cp .env.sample .env
   # Edit .env with your credentials
   ```

3. **Infrastructure Deployment**
   ```bash
   cd infra/gcp
   terraform init
   terraform plan
   terraform apply
   ```

4. **Local Development**
   ```bash
   ./scripts/local_dev_env.sh
   ```

## Services

- **Ingestion**: Real-time blockchain data via Alchemy/Infura
- **Ontology**: GraphQL API with Neo4j semantic layer  
- **Entity Resolution**: Vertex AI-powered identity matching
- **Agent Mesh**: MEV, whale tracking, sanctions monitoring
- **Risk AI**: Anomaly detection, fraud analysis
- **VoiceOps**: ElevenLabs TTS/STT integration
- **Dashboard**: Next.js real-time war room

## Development

See individual service READMEs for detailed setup instructions.

## License

MIT