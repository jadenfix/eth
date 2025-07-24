#!/usr/bin/env python3
"""
Service Orchestrator - Start All Backend Services
Coordinates Ethereum ingestion, Graph API, Voice ops, and monitoring
"""
import os
import sys
import time
import signal
import subprocess
import threading
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServiceOrchestrator:
    def __init__(self):
        self.services = {}
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Received shutdown signal, stopping all services...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)
    
    def start_service(self, name, command, cwd=None):
        """Start a service process"""
        try:
            logger.info(f"🚀 Starting {name}...")
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd or os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.services[name] = process
            logger.info(f"✅ {name} started (PID: {process.pid})")
            return process
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return None
    
    def monitor_service(self, name, process):
        """Monitor service output"""
        while self.running and process.poll() is None:
            try:
                output = process.stdout.readline()
                if output:
                    logger.info(f"[{name}] {output.strip()}")
            except:
                break
    
    def stop_all_services(self):
        """Stop all running services"""
        for name, process in self.services.items():
            try:
                logger.info(f"🛑 Stopping {name}...")
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
    
    def check_service_health(self, name, url):
        """Check if service is healthy"""
        try:
            import requests
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {name} health check passed")
                return True
        except:
            pass
        logger.warning(f"⚠️ {name} health check failed")
        return False
    
    def run(self):
        """Start all services and monitor them"""
        logger.info("🚀 ETH HACKATHON - SERVICE ORCHESTRATOR")
        logger.info("=" * 60)
        
        # Test API connections first
        logger.info("🔍 Testing API connections...")
        self.test_api_connections()
        
        # Create BigQuery tables if needed
        logger.info("📊 Setting up BigQuery tables...")
        self.setup_bigquery()
        
        # Start core services
        logger.info("🎯 Starting backend services...")
        
        # 1. Graph API Service (port 4000)
        self.start_service(
            "Graph API",
            "python services/graph_api/graph_api_service.py",
            cwd="/Users/jadenfix/eth"
        )
        time.sleep(3)
        
        # 2. Voice Operations Service (port 5000)
        self.start_service(
            "Voice Ops",
            "python services/voiceops/voice_service_realtime.py",
            cwd="/Users/jadenfix/eth"
        )
        time.sleep(3)
        
        # 3. Ethereum Ingester (background)
        self.start_service(
            "ETH Ingester",
            "python services/ethereum_ingester/ethereum_ingester_realtime.py",
            cwd="/Users/jadenfix/eth"
        )
        time.sleep(3)
        
        # Health checks
        logger.info("🏥 Running health checks...")
        time.sleep(5)
        self.check_service_health("Graph API", "http://localhost:4000")
        self.check_service_health("Voice Ops", "http://localhost:5000")
        
        # Service status
        logger.info("📈 Service Status:")
        for name, process in self.services.items():
            status = "Running" if process.poll() is None else "Stopped"
            logger.info(f"  • {name}: {status}")
        
        logger.info("🎯 All services started! Press Ctrl+C to stop.")
        logger.info("=" * 60)
        logger.info("📍 Service Endpoints:")
        logger.info("  • Graph API: http://localhost:4000")
        logger.info("  • GraphQL: http://localhost:4000/docs")
        logger.info("  • WebSocket: ws://localhost:4000/subscriptions")
        logger.info("  • Voice Ops: http://localhost:5000")
        logger.info("  • Voice WebSocket: ws://localhost:5000/voice")
        logger.info("=" * 60)
        
        # Keep running and monitor
        try:
            while self.running:
                time.sleep(10)
                # Check if services are still running
                for name, process in list(self.services.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {name} has stopped unexpectedly")
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_services()
    
    def test_api_connections(self):
        """Test all external API connections"""
        import requests
        from google.cloud import bigquery
        from neo4j import GraphDatabase
        
        results = []
        
        # BigQuery
        try:
            client = bigquery.Client(project='ethhackathon')
            list(client.list_datasets())
            results.append("✅ BigQuery: Connected")
        except Exception as e:
            results.append(f"❌ BigQuery: {e}")
        
        # Neo4j
        try:
            driver = GraphDatabase.driver(
                os.getenv('NEO4J_URI'),
                auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
            )
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            results.append("✅ Neo4j: Connected")
        except Exception as e:
            results.append(f"❌ Neo4j: {e}")
        
        # Alchemy
        try:
            response = requests.post(
                f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                json={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1},
                timeout=5
            )
            if response.status_code == 200:
                block = int(response.json()['result'], 16)
                results.append(f"✅ Alchemy: Block {block}")
            else:
                results.append("❌ Alchemy: API Error")
        except Exception as e:
            results.append(f"❌ Alchemy: {e}")
        
        # ElevenLabs
        try:
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": os.getenv('ELEVENLABS_API_KEY')},
                timeout=5
            )
            if response.status_code == 200:
                voices = len(response.json().get('voices', []))
                results.append(f"✅ ElevenLabs: {voices} voices")
            else:
                results.append("❌ ElevenLabs: API Error")
        except Exception as e:
            results.append(f"❌ ElevenLabs: {e}")
        
        for result in results:
            logger.info(f"  {result}")
        
        working = sum(1 for r in results if '✅' in r)
        total = len(results)
        logger.info(f"📊 API Status: {working}/{total} ({working/total*100:.0f}%) operational")
    
    def setup_bigquery(self):
        """Ensure BigQuery tables exist"""
        try:
            from google.cloud import bigquery
            client = bigquery.Client(project='ethhackathon')
            
            # Raw events table schema
            schema = [
                bigquery.SchemaField("transaction_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("block_number", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("block_hash", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("from_address", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("to_address", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("value", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("gas_used", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("gas_price", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("raw_data", "STRING", mode="NULLABLE"),
            ]
            
            table_id = f"ethhackathon.onchain_data.raw_events"
            table = bigquery.Table(table_id, schema=schema)
            
            try:
                table = client.create_table(table)
                logger.info(f"✅ Created BigQuery table: {table.table_id}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"✅ BigQuery table already exists: raw_events")
                else:
                    logger.error(f"❌ BigQuery table creation failed: {e}")
                    
        except Exception as e:
            logger.error(f"❌ BigQuery setup failed: {e}")

if __name__ == "__main__":
    orchestrator = ServiceOrchestrator()
    orchestrator.run()
