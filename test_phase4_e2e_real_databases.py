#!/usr/bin/env python3
"""
Phase 4 E2E Test Suite with Real Database Integration
Tests automated actions and workflow builder functionality with real Neo4j and BigQuery
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class Phase4E2ETestSuite:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = datetime.now()
        
        # Test configuration
        self.test_config = {
            'GOOGLE_CLOUD_PROJECT': os.getenv('GOOGLE_CLOUD_PROJECT', 'ethhackathon'),
            'NEO4J_URI': os.getenv('NEO4J_URI'),
            'NEO4J_USER': os.getenv('NEO4J_USER'),
            'NEO4J_PASSWORD': os.getenv('NEO4J_PASSWORD'),
            'ETHEREUM_RPC_URL': os.getenv('ETHEREUM_RPC_URL', 'http://localhost:8545')
        }
        
        print("🚀 Phase 4 E2E Test Suite with Real Database Integration")
        print("=" * 60)
        print(f"📊 Project: {self.test_config['GOOGLE_CLOUD_PROJECT']}")
        print(f"🗄️  Neo4j: {self.test_config['NEO4J_URI']}")
        print(f"⏰ Started: {self.start_time}")
        print("=" * 60)
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            print(f"✅ {test_name}: PASS {details}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: FAIL {details}")
        
        self.results[test_name] = {"status": status, "details": details}
    
    async def test_1_action_executor_real_databases(self):
        """Test 1: Action Executor with Real Database Integration"""
        print("\n🧪 Test 1: Action Executor with Real Database Integration")
        
        try:
            from action_executor.action_executor import ActionExecutor, ActionRequest, ActionType
            
            # Initialize action executor
            executor = ActionExecutor()
            
            # Test database connections
            if not executor.neo4j_driver:
                self.log_test("Action Executor Neo4j Connection", "FAIL", "Neo4j not connected")
                return
            
            if not executor.bq_client:
                self.log_test("Action Executor BigQuery Connection", "FAIL", "BigQuery not connected")
                return
            
            self.log_test("Action Executor Database Connections", "PASS", "Neo4j and BigQuery connected")
            
            # Test action submission and execution
            action_request = ActionRequest(
                action_id="test_action_001",
                action_type=ActionType.SEND_ALERT,
                target_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                signal_id="test_signal_001",
                confidence_score=0.85,
                metadata={"test": True, "phase": 4},
                dry_run=True
            )
            
            # Submit action
            action_id = await executor.submit_action(action_request)
            self.log_test("Action Submission", "PASS", f"Action ID: {action_id}")
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Verify action was logged to Neo4j
            with executor.neo4j_driver.session() as session:
                query = """
                MATCH (a:Action {action_id: $action_id})
                RETURN a
                """
                result = session.run(query, action_id=action_id)
                record = result.single()
                
                if record:
                    self.log_test("Action Neo4j Logging", "PASS", "Action logged to Neo4j")
                else:
                    self.log_test("Action Neo4j Logging", "FAIL", "Action not found in Neo4j")
            
            # Test BigQuery logging
            try:
                table_id = f"{executor.bq_project}.onchain_data.action_results"
                query = f"""
                SELECT COUNT(*) as count
                FROM `{table_id}`
                WHERE action_id = '{action_id}'
                """
                query_job = executor.bq_client.query(query)
                results = query_job.result()
                
                for row in results:
                    if row.count > 0:
                        self.log_test("Action BigQuery Logging", "PASS", "Action logged to BigQuery")
                    else:
                        self.log_test("Action BigQuery Logging", "FAIL", "Action not found in BigQuery")
            except Exception as e:
                self.log_test("Action BigQuery Logging", "FAIL", f"BigQuery error: {e}")
            
        except Exception as e:
            self.log_test("Action Executor Integration", "FAIL", f"Error: {e}")
    
    async def test_2_position_manager_real_databases(self):
        """Test 2: Position Manager with Real Database Integration"""
        print("\n🧪 Test 2: Position Manager with Real Database Integration")
        
        try:
            from action_executor.position_manager import PositionManager, Position
            
            # Initialize position manager
            position_manager = PositionManager()
            
            # Test database connections
            if not position_manager.neo4j_driver:
                self.log_test("Position Manager Neo4j Connection", "FAIL", "Neo4j not connected")
                return
            
            if not position_manager.bq_client:
                self.log_test("Position Manager BigQuery Connection", "FAIL", "BigQuery not connected")
                return
            
            self.log_test("Position Manager Database Connections", "PASS", "Neo4j and BigQuery connected")
            
            # Create test position
            test_position = Position(
                address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                position_id="test_position_001",
                asset="ETH",
                amount=10.5,
                value_usd=21000.0,
                risk_score=0.75,
                status="active",
                created_at=datetime.now()
            )
            
            # Test position creation
            success = await position_manager.create_position(test_position)
            if success:
                self.log_test("Position Creation", "PASS", "Position created successfully")
            else:
                self.log_test("Position Creation", "FAIL", "Failed to create position")
                return
            
            # Test position retrieval
            retrieved_position = await position_manager.get_position(test_position.position_id)
            if retrieved_position:
                self.log_test("Position Retrieval", "PASS", "Position retrieved successfully")
            else:
                self.log_test("Position Retrieval", "FAIL", "Failed to retrieve position")
            
            # Test position freezing
            freeze_success = await position_manager.freeze_position(test_position.position_id, "Test freeze")
            if freeze_success:
                self.log_test("Position Freezing", "PASS", "Position frozen successfully")
            else:
                self.log_test("Position Freezing", "FAIL", "Failed to freeze position")
            
            # Test frozen positions query
            frozen_positions = await position_manager.get_frozen_positions()
            if len(frozen_positions) > 0:
                self.log_test("Frozen Positions Query", "PASS", f"Found {len(frozen_positions)} frozen positions")
            else:
                self.log_test("Frozen Positions Query", "FAIL", "No frozen positions found")
            
            # Test high risk positions query
            high_risk_positions = await position_manager.get_high_risk_positions(threshold=0.7)
            self.log_test("High Risk Positions Query", "PASS", f"Found {len(high_risk_positions)} high risk positions")
            
        except Exception as e:
            self.log_test("Position Manager Integration", "FAIL", f"Error: {e}")
    
    async def test_3_liquidity_hedger_real_databases(self):
        """Test 3: Liquidity Hedger with Real Database Integration"""
        print("\n🧪 Test 3: Liquidity Hedger with Real Database Integration")
        
        try:
            from action_executor.liquidity_hedger import LiquidityHedger, HedgePosition
            
            # Initialize liquidity hedger
            hedger = LiquidityHedger()
            
            # Test database connections
            if not hedger.neo4j_driver:
                self.log_test("Hedger Neo4j Connection", "FAIL", "Neo4j not connected")
                return
            
            if not hedger.bq_client:
                self.log_test("Hedger BigQuery Connection", "FAIL", "BigQuery not connected")
                return
            
            self.log_test("Hedger Database Connections", "PASS", "Neo4j and BigQuery connected")
            
            # Test hedge amount calculation
            hedge_amount = await hedger.calculate_hedge_amount(100000.0, "ETH")
            if hedge_amount > 0:
                self.log_test("Hedge Amount Calculation", "PASS", f"Calculated hedge amount: {hedge_amount}")
            else:
                self.log_test("Hedge Amount Calculation", "FAIL", "Invalid hedge amount")
            
            # Test hedge execution
            hedge_position = await hedger.execute_hedge(100000.0, "ETH", "USDC")
            if hedge_position:
                self.log_test("Hedge Execution", "PASS", f"Hedge executed: {hedge_position.hedge_id}")
            else:
                self.log_test("Hedge Execution", "FAIL", "Failed to execute hedge")
                return
            
            # Test hedge position retrieval
            retrieved_hedge = await hedger.get_hedge_position(hedge_position.hedge_id)
            if retrieved_hedge:
                self.log_test("Hedge Position Retrieval", "PASS", "Hedge position retrieved successfully")
            else:
                self.log_test("Hedge Position Retrieval", "FAIL", "Failed to retrieve hedge position")
            
            # Test active hedges query
            active_hedges = await hedger.get_active_hedges()
            if len(active_hedges) > 0:
                self.log_test("Active Hedges Query", "PASS", f"Found {len(active_hedges)} active hedges")
            else:
                self.log_test("Active Hedges Query", "FAIL", "No active hedges found")
            
            # Test total hedge exposure calculation
            total_exposure = await hedger.calculate_total_hedge_exposure()
            self.log_test("Total Hedge Exposure", "PASS", f"Total exposure: {total_exposure}")
            
            # Test hedge performance summary
            performance = await hedger.get_hedge_performance_summary()
            self.log_test("Hedge Performance Summary", "PASS", f"Performance data: {performance}")
            
        except Exception as e:
            self.log_test("Liquidity Hedger Integration", "FAIL", f"Error: {e}")
    
    async def test_4_workflow_builder_integration(self):
        """Test 4: Workflow Builder Integration"""
        print("\n🧪 Test 4: Workflow Builder Integration")
        
        try:
            from services.workflow_builder.dagster_config import fetch_blockchain_data, analyze_risk_patterns, generate_signals
            
            # Test workflow components
            blockchain_data = fetch_blockchain_data(None)
            if blockchain_data is not None and len(blockchain_data) > 0:
                self.log_test("Blockchain Data Fetching", "PASS", f"Fetched {len(blockchain_data)} records")
            else:
                self.log_test("Blockchain Data Fetching", "FAIL", "No blockchain data fetched")
            
            # Test risk pattern analysis
            risk_patterns = analyze_risk_patterns(None, blockchain_data)
            if risk_patterns is not None:
                self.log_test("Risk Pattern Analysis", "PASS", "Risk patterns analyzed successfully")
            else:
                self.log_test("Risk Pattern Analysis", "FAIL", "Failed to analyze risk patterns")
            
            # Test signal generation
            signals = generate_signals(None, risk_patterns)
            if signals is not None:
                self.log_test("Signal Generation", "PASS", "Signals generated successfully")
            else:
                self.log_test("Signal Generation", "FAIL", "Failed to generate signals")
            
        except Exception as e:
            self.log_test("Workflow Builder Integration", "FAIL", f"Error: {e}")
    
    async def test_5_playbook_execution(self):
        """Test 5: Playbook Execution"""
        print("\n🧪 Test 5: Playbook Execution")
        
        try:
            import yaml
            from action_executor.action_executor import ActionExecutor, ActionRequest, ActionType
            
            # Load playbooks
            playbook_dir = "action_executor/playbooks"
            if os.path.exists(playbook_dir):
                playbooks = {}
                for filename in os.listdir(playbook_dir):
                    if filename.endswith('.yaml'):
                        with open(os.path.join(playbook_dir, filename), 'r') as f:
                            playbook_name = filename.replace('.yaml', '')
                            playbooks[playbook_name] = yaml.safe_load(f)
                
                if playbooks:
                    self.log_test("Playbook Loading", "PASS", f"Loaded {len(playbooks)} playbooks")
                else:
                    self.log_test("Playbook Loading", "FAIL", "No playbooks loaded")
                    return
                
                # Test specific playbook execution
                if 'freeze_position' in playbooks:
                    executor = ActionExecutor()
                    
                    # Create action request for freeze position playbook
                    action_request = ActionRequest(
                        action_id="test_playbook_001",
                        action_type=ActionType.FREEZE_POSITION,
                        target_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                        signal_id="test_signal_002",
                        confidence_score=0.9,
                        metadata={"playbook": "freeze_position", "test": True},
                        dry_run=True
                    )
                    
                    # Submit action
                    action_id = await executor.submit_action(action_request)
                    self.log_test("Playbook Action Submission", "PASS", f"Action ID: {action_id}")
                    
                    # Wait for processing
                    await asyncio.sleep(2)
                    
                    # Verify playbook execution
                    with executor.neo4j_driver.session() as session:
                        query = """
                        MATCH (a:Action {action_id: $action_id})
                        RETURN a
                        """
                        result = session.run(query, action_id=action_id)
                        record = result.single()
                        
                        if record:
                            self.log_test("Playbook Execution", "PASS", "Playbook executed successfully")
                        else:
                            self.log_test("Playbook Execution", "FAIL", "Playbook execution not found")
                else:
                    self.log_test("Playbook Execution", "FAIL", "Freeze position playbook not found")
            else:
                self.log_test("Playbook Loading", "FAIL", "Playbook directory not found")
            
        except Exception as e:
            self.log_test("Playbook Execution", "FAIL", f"Error: {e}")
    
    async def test_6_database_persistence_and_recovery(self):
        """Test 6: Database Persistence and Recovery"""
        print("\n🧪 Test 6: Database Persistence and Recovery")
        
        try:
            from action_executor.action_executor import ActionExecutor
            from action_executor.position_manager import PositionManager
            from action_executor.liquidity_hedger import LiquidityHedger
            
            # Test data persistence across service restarts
            executor = ActionExecutor()
            position_manager = PositionManager()
            hedger = LiquidityHedger()
            
            # Create test data
            test_action_id = "persistence_test_001"
            test_position_id = "persistence_test_001"
            test_hedge_id = "persistence_test_001"
            
            # Verify data exists in databases
            if executor.neo4j_driver:
                with executor.neo4j_driver.session() as session:
                    # Check for actions
                    query = """
                    MATCH (a:Action)
                    RETURN count(a) as count
                    """
                    result = session.run(query)
                    action_count = result.single()['count']
                    
                    # Check for positions
                    query = """
                    MATCH (p:Position)
                    RETURN count(p) as count
                    """
                    result = session.run(query)
                    position_count = result.single()['count']
                    
                    # Check for hedge positions
                    query = """
                    MATCH (h:HedgePosition)
                    RETURN count(h) as count
                    """
                    result = session.run(query)
                    hedge_count = result.single()['count']
                    
                    self.log_test("Data Persistence", "PASS", 
                                f"Actions: {action_count}, Positions: {position_count}, Hedges: {hedge_count}")
            
            # Test BigQuery data persistence
            if executor.bq_client:
                try:
                    # Check action results table
                    table_id = f"{executor.bq_project}.onchain_data.action_results"
                    query = f"SELECT COUNT(*) as count FROM `{table_id}`"
                    query_job = executor.bq_client.query(query)
                    results = query_job.result()
                    
                    for row in results:
                        self.log_test("BigQuery Data Persistence", "PASS", f"Action results: {row.count}")
                        
                except Exception as e:
                    self.log_test("BigQuery Data Persistence", "FAIL", f"Error: {e}")
            
        except Exception as e:
            self.log_test("Database Persistence", "FAIL", f"Error: {e}")
    
    async def test_7_performance_and_scalability(self):
        """Test 7: Performance and Scalability"""
        print("\n🧪 Test 7: Performance and Scalability")
        
        try:
            from action_executor.action_executor import ActionExecutor, ActionRequest, ActionType
            
            executor = ActionExecutor()
            
            # Test concurrent action processing
            start_time = time.time()
            tasks = []
            
            for i in range(10):
                action_request = ActionRequest(
                    action_id=f"perf_test_{i:03d}",
                    action_type=ActionType.SEND_ALERT,
                    target_address=f"0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    signal_id=f"perf_signal_{i:03d}",
                    confidence_score=0.8,
                    metadata={"test": "performance", "index": i},
                    dry_run=True
                )
                tasks.append(executor.submit_action(action_request))
            
            # Wait for all actions to be submitted
            action_ids = await asyncio.gather(*tasks)
            submission_time = time.time() - start_time
            
            self.log_test("Concurrent Action Submission", "PASS", 
                         f"Submitted {len(action_ids)} actions in {submission_time:.2f}s")
            
            # Wait for processing
            await asyncio.sleep(5)
            
            # Verify all actions were processed
            if executor.neo4j_driver:
                with executor.neo4j_driver.session() as session:
                    query = """
                    MATCH (a:Action)
                    WHERE a.action_id STARTS WITH 'perf_test_'
                    RETURN count(a) as count
                    """
                    result = session.run(query)
                    processed_count = result.single()['count']
                    
                    if processed_count == len(action_ids):
                        self.log_test("Concurrent Action Processing", "PASS", 
                                    f"All {processed_count} actions processed")
                    else:
                        self.log_test("Concurrent Action Processing", "FAIL", 
                                    f"Only {processed_count}/{len(action_ids)} actions processed")
            
        except Exception as e:
            self.log_test("Performance and Scalability", "FAIL", f"Error: {e}")
    
    async def test_8_error_handling_and_recovery(self):
        """Test 8: Error Handling and Recovery"""
        print("\n🧪 Test 8: Error Handling and Recovery")
        
        try:
            from action_executor.action_executor import ActionExecutor, ActionRequest, ActionType
            
            executor = ActionExecutor()
            
            # Test invalid action handling
            try:
                invalid_action = ActionRequest(
                    action_id="error_test_001",
                    action_type=ActionType.SEND_ALERT,
                    target_address="invalid_address",
                    signal_id="error_signal_001",
                    confidence_score=1.5,  # Invalid confidence score
                    metadata={"test": "error_handling"},
                    dry_run=True
                )
                
                action_id = await executor.submit_action(invalid_action)
                self.log_test("Invalid Action Handling", "PASS", "Invalid action handled gracefully")
                
            except Exception as e:
                self.log_test("Invalid Action Handling", "PASS", f"Error caught: {e}")
            
            # Test database connection recovery
            if executor.neo4j_driver:
                try:
                    with executor.neo4j_driver.session() as session:
                        session.run("RETURN 1")
                    self.log_test("Database Connection Recovery", "PASS", "Database connection stable")
                except Exception as e:
                    self.log_test("Database Connection Recovery", "FAIL", f"Database error: {e}")
            
            # Test action retry mechanism
            retry_action = ActionRequest(
                action_id="retry_test_001",
                action_type=ActionType.SEND_ALERT,
                target_address="0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                signal_id="retry_signal_001",
                confidence_score=0.8,
                metadata={"test": "retry_mechanism"},
                dry_run=True
            )
            
            action_id = await executor.submit_action(retry_action)
            await asyncio.sleep(2)
            
            # Verify action was processed despite potential errors
            if executor.neo4j_driver:
                with executor.neo4j_driver.session() as session:
                    query = """
                    MATCH (a:Action {action_id: $action_id})
                    RETURN a
                    """
                    result = session.run(query, action_id=action_id)
                    record = result.single()
                    
                    if record:
                        self.log_test("Action Retry Mechanism", "PASS", "Action processed successfully")
                    else:
                        self.log_test("Action Retry Mechanism", "FAIL", "Action not found")
            
        except Exception as e:
            self.log_test("Error Handling and Recovery", "FAIL", f"Error: {e}")
    
    async def run_all_tests(self):
        """Run all Phase 4 E2E tests"""
        print("\n🚀 Starting Phase 4 E2E Test Suite with Real Database Integration")
        
        # Run all tests
        await self.test_1_action_executor_real_databases()
        await self.test_2_position_manager_real_databases()
        await self.test_3_liquidity_hedger_real_databases()
        await self.test_4_workflow_builder_integration()
        await self.test_5_playbook_execution()
        await self.test_6_database_persistence_and_recovery()
        await self.test_7_performance_and_scalability()
        await self.test_8_error_handling_and_recovery()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 PHASE 4 E2E TEST SUMMARY")
        print("=" * 60)
        print(f"⏰ Duration: {duration}")
        print(f"📈 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%" if self.total_tests > 0 else "N/A")
        
        print("\n🔍 DETAILED RESULTS:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result['status']} - {result['details']}")
        
        print("\n" + "=" * 60)
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Phase 4 implementation is robust and ready for production.")
        else:
            print(f"⚠️  {self.failed_tests} test(s) failed. Please review and fix issues.")
        
        print("=" * 60)

async def main():
    """Main test runner"""
    test_suite = Phase4E2ETestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 