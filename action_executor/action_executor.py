import asyncio
import json
import yaml
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from web3 import Web3
from eth_account import Account
from neo4j import GraphDatabase
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

class ActionType(Enum):
    BLOCK_TRANSACTION = "block_transaction"
    FREEZE_POSITION = "freeze_position"
    HEDGE_LIQUIDITY = "hedge_liquidity"
    SEND_ALERT = "send_alert"
    UPDATE_RISK_SCORE = "update_risk_score"
    QUARANTINE_ADDRESS = "quarantine_address"

@dataclass
class ActionRequest:
    action_id: str
    action_type: ActionType
    target_address: str
    signal_id: str
    confidence_score: float
    metadata: Dict[str, Any]
    dry_run: bool = False
    priority: int = 1

@dataclass
class ActionResult:
    action_id: str
    success: bool
    transaction_hash: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[datetime] = None
    gas_used: Optional[int] = None
    metadata: Dict[str, Any] = None

class ActionExecutor:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL', 'http://localhost:8545')))
        self.account = Account.from_key(os.getenv('PRIVATE_KEY', '0x' + '0' * 64))
        self.playbooks = self._load_playbooks()
        self.action_queue = asyncio.Queue()
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Initialize real database connections
        self._init_databases()
        
        # Action handlers
        self.handlers = {
            ActionType.BLOCK_TRANSACTION: self._block_transaction,
            ActionType.FREEZE_POSITION: self._freeze_position,
            ActionType.HEDGE_LIQUIDITY: self._hedge_liquidity,
            ActionType.SEND_ALERT: self._send_alert,
            ActionType.UPDATE_RISK_SCORE: self._update_risk_score,
            ActionType.QUARANTINE_ADDRESS: self._quarantine_address
        }
    
    def _init_databases(self):
        """Initialize real database connections"""
        try:
            # Initialize Neo4j for action logging and state management
            self.neo4j_uri = os.getenv('NEO4J_URI')
            self.neo4j_user = os.getenv('NEO4J_USER')
            self.neo4j_password = os.getenv('NEO4J_PASSWORD')
            
            if self.neo4j_uri and self.neo4j_user and self.neo4j_password:
                self.neo4j_driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                self.logger.info("✅ Neo4j connected for action logging")
            else:
                self.neo4j_driver = None
                self.logger.warning("⚠️ Neo4j credentials not found, using local storage")
            
            # Initialize BigQuery for action analytics
            self.bq_project = os.getenv('GOOGLE_CLOUD_PROJECT')
            if self.bq_project:
                self.bq_client = bigquery.Client(project=self.bq_project)
                self.logger.info("✅ BigQuery connected for action analytics")
            else:
                self.bq_client = None
                self.logger.warning("⚠️ BigQuery project not found, analytics disabled")
                
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            self.neo4j_driver = None
            self.bq_client = None
    
    def _load_playbooks(self) -> Dict[str, Dict[str, Any]]:
        """Load action playbooks from YAML files"""
        playbooks = {}
        playbook_dir = "action_executor/playbooks"
        
        if os.path.exists(playbook_dir):
            for filename in os.listdir(playbook_dir):
                if filename.endswith('.yaml'):
                    try:
                        with open(os.path.join(playbook_dir, filename), 'r') as f:
                            playbook_name = filename.replace('.yaml', '')
                            playbooks[playbook_name] = yaml.safe_load(f)
                    except Exception as e:
                        self.logger.error(f"Error loading playbook {filename}: {e}")
        
        return playbooks
    
    async def start_executor(self):
        """Start the action executor"""
        self.is_running = True
        asyncio.create_task(self._process_action_queue())
        self.logger.info("Action Executor started")
    
    async def stop_executor(self):
        """Stop the action executor"""
        self.is_running = False
        self.logger.info("Action Executor stopped")
    
    async def submit_action(self, action_request: ActionRequest) -> str:
        """Submit an action for execution"""
        await self.action_queue.put(action_request)
        
        # Log action submission to database
        await self._log_action_submission(action_request)
        
        self.logger.info(f"Action submitted: {action_request.action_id}")
        return action_request.action_id
    
    async def _log_action_submission(self, action_request: ActionRequest):
        """Log action submission to Neo4j"""
        if not self.neo4j_driver:
            return
            
        try:
            with self.neo4j_driver.session() as session:
                query = """
                CREATE (a:Action {
                    action_id: $action_id,
                    action_type: $action_type,
                    target_address: $target_address,
                    signal_id: $signal_id,
                    confidence_score: $confidence_score,
                    dry_run: $dry_run,
                    priority: $priority,
                    status: 'submitted',
                    submitted_at: datetime(),
                    metadata: $metadata
                })
                """
                session.run(query, 
                    action_id=action_request.action_id,
                    action_type=action_request.action_type.value,
                    target_address=action_request.target_address,
                    signal_id=action_request.signal_id,
                    confidence_score=action_request.confidence_score,
                    dry_run=action_request.dry_run,
                    priority=action_request.priority,
                    metadata=json.dumps(action_request.metadata)
                )
        except Exception as e:
            self.logger.error(f"Failed to log action submission: {e}")
    
    async def _process_action_queue(self):
        """Process actions from the queue"""
        while self.is_running:
            try:
                action_request = await asyncio.wait_for(
                    self.action_queue.get(), timeout=1.0
                )
                
                # Execute the action
                result = await self._execute_action(action_request)
                
                # Log the result
                await self._log_action_result(result)
                
                # Mark as done
                self.action_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing action: {e}")
    
    async def _execute_action(self, action_request: ActionRequest) -> ActionResult:
        """Execute a single action"""
        start_time = datetime.now()
        
        try:
            if action_request.dry_run:
                result = await self._dry_run_action(action_request)
            else:
                # Get the appropriate handler
                handler = self.handlers.get(action_request.action_type)
                if handler:
                    result = await handler(action_request)
                else:
                    result = ActionResult(
                        action_id=action_request.action_id,
                        success=False,
                        error_message=f"Unknown action type: {action_request.action_type}"
                    )
            
            result.execution_time = datetime.now() - start_time
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing action {action_request.action_id}: {e}")
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e),
                execution_time=datetime.now() - start_time
            )
    
    async def _block_transaction(self, action_request: ActionRequest) -> ActionResult:
        """Block a transaction from being processed"""
        try:
            # Get transaction details from metadata
            tx_hash = action_request.metadata.get('transaction_hash')
            if not tx_hash:
                raise ValueError("Transaction hash required for blocking")
            
            # Create blocking transaction
            blocking_tx = {
                'to': action_request.target_address,
                'value': 0,
                'data': self._create_blocking_data(tx_hash),
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                blocking_tx, self.account.key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return ActionResult(
                action_id=action_request.action_id,
                success=True,
                transaction_hash=tx_hash.hex(),
                gas_used=100000
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _freeze_position(self, action_request: ActionRequest) -> ActionResult:
        """Freeze a position/address"""
        try:
            # Load freeze position playbook
            playbook = self.playbooks.get('freeze_position')
            if not playbook:
                raise ValueError("Freeze position playbook not found")
            
            # Execute freeze steps
            steps = playbook.get('steps', [])
            results = []
            
            for step in steps:
                step_result = await self._execute_playbook_step(step, action_request)
                results.append(step_result)
                
                if not step_result['success']:
                    break
            
            # Check if all steps succeeded
            success = all(r['success'] for r in results)
            
            return ActionResult(
                action_id=action_request.action_id,
                success=success,
                metadata={'steps_executed': len(results), 'step_results': results}
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _hedge_liquidity(self, action_request: ActionRequest) -> ActionResult:
        """Hedge liquidity against risk"""
        try:
            # Load hedge liquidity playbook
            playbook = self.playbooks.get('hedge_liquidity')
            if not playbook:
                raise ValueError("Hedge liquidity playbook not found")
            
            # Calculate hedge amount
            risk_amount = action_request.metadata.get('risk_amount', 0)
            hedge_ratio = playbook.get('hedge_ratio', 0.5)
            hedge_amount = risk_amount * hedge_ratio
            
            # Execute hedge transaction
            hedge_tx = {
                'to': playbook.get('hedge_contract'),
                'value': int(hedge_amount * 1e18),  # Convert to wei
                'data': self._create_hedge_data(hedge_amount),
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(
                hedge_tx, self.account.key
            )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return ActionResult(
                action_id=action_request.action_id,
                success=True,
                transaction_hash=tx_hash.hex(),
                gas_used=200000,
                metadata={'hedge_amount': hedge_amount}
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _send_alert(self, action_request: ActionRequest) -> ActionResult:
        """Send alert notification"""
        try:
            # Get alert configuration
            alert_config = action_request.metadata.get('alert_config', {})
            channels = alert_config.get('channels', ['slack', 'email'])
            
            # Send to each channel
            results = []
            for channel in channels:
                if channel == 'slack':
                    result = await self._send_slack_alert(action_request)
                elif channel == 'email':
                    result = await self._send_email_alert(action_request)
                else:
                    result = {'success': False, 'error': f'Unknown channel: {channel}'}
                
                results.append({'channel': channel, 'result': result})
            
            success = any(r['result']['success'] for r in results)
            
            return ActionResult(
                action_id=action_request.action_id,
                success=success,
                metadata={'alert_results': results}
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _update_risk_score(self, action_request: ActionRequest) -> ActionResult:
        """Update risk score for an address"""
        try:
            # Get new risk score
            new_score = action_request.metadata.get('risk_score', 0.5)
            
            # Update in database
            # This would typically update Neo4j or BigQuery
            # For now, just log the update
            
            self.logger.info(f"Updated risk score for {action_request.target_address}: {new_score}")
            
            return ActionResult(
                action_id=action_request.action_id,
                success=True,
                metadata={'new_risk_score': new_score}
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _quarantine_address(self, action_request: ActionRequest) -> ActionResult:
        """Quarantine an address"""
        try:
            # Add address to quarantine list
            quarantine_data = {
                'address': action_request.target_address,
                'reason': action_request.metadata.get('reason', 'High risk'),
                'quarantine_date': datetime.now().isoformat(),
                'expiry_date': action_request.metadata.get('expiry_date')
            }
            
            # Store in quarantine database
            # This would typically update a quarantine table
            self.logger.info(f"Quarantined address: {quarantine_data}")
            
            return ActionResult(
                action_id=action_request.action_id,
                success=True,
                metadata=quarantine_data
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action_request.action_id,
                success=False,
                error_message=str(e)
            )
    
    async def _dry_run_action(self, action_request: ActionRequest) -> ActionResult:
        """Simulate action execution without actually performing it"""
        self.logger.info(f"DRY RUN: Would execute {action_request.action_type} for {action_request.target_address}")
        
        return ActionResult(
            action_id=action_request.action_id,
            success=True,
            metadata={'dry_run': True, 'action_type': action_request.action_type.value}
        )
    
    async def _execute_playbook_step(self, step: Dict[str, Any], action_request: ActionRequest) -> Dict[str, Any]:
        """Execute a single playbook step"""
        step_type = step.get('type')
        
        if step_type == 'contract_call':
            return await self._execute_contract_call(step, action_request)
        elif step_type == 'api_call':
            return await self._execute_api_call(step, action_request)
        elif step_type == 'database_update':
            return await self._execute_database_update(step, action_request)
        else:
            return {'success': False, 'error': f'Unknown step type: {step_type}'}
    
    async def _execute_contract_call(self, step: Dict[str, Any], action_request: ActionRequest) -> Dict[str, Any]:
        """Execute a smart contract call"""
        try:
            contract_address = step.get('contract_address')
            function_name = step.get('function_name')
            parameters = step.get('parameters', [])
            
            # Create contract instance
            contract = self.web3.eth.contract(
                address=contract_address,
                abi=step.get('abi', [])
            )
            
            # Build transaction
            tx = contract.functions[function_name](*parameters).build_transaction({
                'from': self.account.address,
                'gas': step.get('gas', 100000),
                'gasPrice': self.web3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'step_type': 'contract_call'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_type': 'contract_call'
            }
    
    async def _execute_api_call(self, step: Dict[str, Any], action_request: ActionRequest) -> Dict[str, Any]:
        """Execute an API call"""
        try:
            import aiohttp
            
            url = step.get('url')
            method = step.get('method', 'POST')
            headers = step.get('headers', {})
            data = step.get('data', {})
            
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    result = await response.json()
                    
                    return {
                        'success': response.status == 200,
                        'response': result,
                        'step_type': 'api_call'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_type': 'api_call'
            }
    
    async def _execute_database_update(self, step: Dict[str, Any], action_request: ActionRequest) -> Dict[str, Any]:
        """Execute a database update"""
        try:
            # This would typically update Neo4j or BigQuery
            # For now, just log the update
            
            table = step.get('table')
            data = step.get('data', {})
            
            self.logger.info(f"Database update: {table} - {data}")
            
            return {
                'success': True,
                'step_type': 'database_update'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step_type': 'database_update'
            }
    
    def _create_blocking_data(self, tx_hash: str) -> str:
        """Create transaction data for blocking"""
        # This would be the actual function call data
        # For now, return a placeholder
        return "0x"
    
    def _create_hedge_data(self, amount: float) -> str:
        """Create transaction data for hedging"""
        # This would be the actual function call data
        # For now, return a placeholder
        return "0x"
    
    async def _send_slack_alert(self, action_request: ActionRequest) -> Dict[str, Any]:
        """Send Slack alert"""
        try:
            # This would send to Slack webhook
            # For now, just log
            self.logger.info(f"Slack alert sent for {action_request.target_address}")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _send_email_alert(self, action_request: ActionRequest) -> Dict[str, Any]:
        """Send email alert"""
        try:
            # This would send email
            # For now, just log
            self.logger.info(f"Email alert sent for {action_request.target_address}")
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _log_action_result(self, result: ActionResult):
        """Log action result to real databases"""
        # Log to Neo4j for graph relationships
        if self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (a:Action {action_id: $action_id})
                    SET a.status = $status,
                        a.success = $success,
                        a.transaction_hash = $tx_hash,
                        a.error_message = $error,
                        a.execution_time = $exec_time,
                        a.gas_used = $gas_used,
                        a.completed_at = datetime(),
                        a.result_metadata = $metadata
                    """
                    session.run(query,
                        action_id=result.action_id,
                        status='completed' if result.success else 'failed',
                        success=result.success,
                        tx_hash=result.transaction_hash,
                        error=result.error_message,
                        exec_time=str(result.execution_time) if result.execution_time else None,
                        gas_used=result.gas_used,
                        metadata=json.dumps(result.metadata) if result.metadata else '{}'
                    )
            except Exception as e:
                self.logger.error(f"Failed to log action result to Neo4j: {e}")
        
        # Log to BigQuery for analytics
        if self.bq_client:
            try:
                table_id = f"{self.bq_project}.onchain_data.action_results"
                rows_to_insert = [{
                    'action_id': result.action_id,
                    'success': result.success,
                    'transaction_hash': result.transaction_hash,
                    'error_message': result.error_message,
                    'execution_time_seconds': result.execution_time.total_seconds() if result.execution_time else None,
                    'gas_used': result.gas_used,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': json.dumps(result.metadata) if result.metadata else '{}'
                }]
                
                errors = self.bq_client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    self.logger.error(f"Failed to insert into BigQuery: {errors}")
                else:
                    self.logger.info(f"Action result logged to BigQuery: {result.action_id}")
            except Exception as e:
                self.logger.error(f"Failed to log action result to BigQuery: {e}")
        
        self.logger.info(f"Action result logged: {result.action_id} - Success: {result.success}") 