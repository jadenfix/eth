from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class NormalizedTransaction:
    tx_hash: str
    chain_id: int
    block_number: int
    from_address: str
    to_address: str
    value_wei: int
    value_eth: float
    gas_price_wei: int
    gas_price_gwei: float
    gas_used: int
    gas_limit: int
    status: bool
    timestamp: datetime
    contract_address: Optional[str] = None
    method_signature: Optional[str] = None
    input_data: Optional[str] = None
    logs: List[Dict] = None
    nonce: int = 0
    fee_wei: int = 0
    fee_eth: float = 0.0

class TransactionNormalizer:
    def __init__(self):
        self.eth_decimals = 18
        self.gwei_decimals = 9
        
    def normalize_transaction(
        self, 
        raw_tx: Dict[str, Any], 
        receipt: Dict[str, Any], 
        chain_id: int,
        block_timestamp: int
    ) -> NormalizedTransaction:
        """Normalize transaction data across different chains"""
        
        try:
            # Convert hex values to decimal
            value_wei = int(raw_tx.get('value', '0x0'), 16)
            gas_price_wei = int(raw_tx.get('gasPrice', '0x0'), 16)
            gas_used = int(receipt.get('gasUsed', '0x0'), 16)
            gas_limit = int(raw_tx.get('gas', '0x0'), 16)
            nonce = int(raw_tx.get('nonce', '0x0'), 16)
            
            # Convert to human-readable values
            value_eth = value_wei / (10 ** self.eth_decimals)
            gas_price_gwei = gas_price_wei / (10 ** self.gwei_decimals)
            
            # Calculate fees
            fee_wei = gas_used * gas_price_wei
            fee_eth = fee_wei / (10 ** self.eth_decimals)
            
            # Determine if it's a contract interaction
            contract_address = None
            method_signature = None
            input_data = None
            
            if raw_tx.get('input') and raw_tx['input'] != '0x':
                contract_address = raw_tx.get('to')
                input_data = raw_tx.get('input')
                method_signature = input_data[:10] if len(input_data) >= 10 else None
            
            return NormalizedTransaction(
                tx_hash=raw_tx.get('hash'),
                chain_id=chain_id,
                block_number=int(raw_tx.get('blockNumber', '0x0'), 16),
                from_address=raw_tx.get('from'),
                to_address=raw_tx.get('to'),
                value_wei=value_wei,
                value_eth=value_eth,
                gas_price_wei=gas_price_wei,
                gas_price_gwei=gas_price_gwei,
                gas_used=gas_used,
                gas_limit=gas_limit,
                status=receipt.get('status') == 1,
                timestamp=datetime.fromtimestamp(block_timestamp),
                contract_address=contract_address,
                method_signature=method_signature,
                input_data=input_data,
                logs=receipt.get('logs', []),
                nonce=nonce,
                fee_wei=fee_wei,
                fee_eth=fee_eth
            )
            
        except Exception as e:
            logger.error(f"Error normalizing transaction {raw_tx.get('hash', 'unknown')}: {e}")
            raise
    
    def normalize_block(
        self,
        raw_block: Dict[str, Any],
        chain_id: int
    ) -> Dict[str, Any]:
        """Normalize block data across different chains"""
        
        try:
            block_number = int(raw_block.get('number', '0x0'), 16)
            timestamp = int(raw_block.get('timestamp', '0x0'), 16)
            gas_used = int(raw_block.get('gasUsed', '0x0'), 16)
            gas_limit = int(raw_block.get('gasLimit', '0x0'), 16)
            
            return {
                'chain_id': chain_id,
                'block_number': block_number,
                'block_hash': raw_block.get('hash'),
                'parent_hash': raw_block.get('parentHash'),
                'timestamp': timestamp,
                'timestamp_iso': datetime.fromtimestamp(timestamp).isoformat(),
                'transactions_count': len(raw_block.get('transactions', [])),
                'gas_used': gas_used,
                'gas_limit': gas_limit,
                'gas_utilization': (gas_used / gas_limit * 100) if gas_limit > 0 else 0,
                'miner': raw_block.get('miner'),
                'difficulty': int(raw_block.get('difficulty', '0x0'), 16),
                'total_difficulty': int(raw_block.get('totalDifficulty', '0x0'), 16),
                'base_fee_per_gas': int(raw_block.get('baseFeePerGas', '0x0'), 16),
                'extra_data': raw_block.get('extraData'),
                'size': int(raw_block.get('size', '0x0'), 16)
            }
            
        except Exception as e:
            logger.error(f"Error normalizing block {raw_block.get('number', 'unknown')}: {e}")
            raise
    
    def normalize_log(
        self,
        raw_log: Dict[str, Any],
        chain_id: int,
        block_number: int,
        tx_hash: str
    ) -> Dict[str, Any]:
        """Normalize log data across different chains"""
        
        try:
            return {
                'chain_id': chain_id,
                'block_number': block_number,
                'transaction_hash': tx_hash,
                'log_index': int(raw_log.get('logIndex', '0x0'), 16),
                'address': raw_log.get('address'),
                'topics': raw_log.get('topics', []),
                'data': raw_log.get('data'),
                'removed': raw_log.get('removed', False)
            }
            
        except Exception as e:
            logger.error(f"Error normalizing log: {e}")
            raise
    
    def to_dict(self, normalized_tx: NormalizedTransaction) -> Dict[str, Any]:
        """Convert normalized transaction to dictionary"""
        return {
            'tx_hash': normalized_tx.tx_hash,
            'chain_id': normalized_tx.chain_id,
            'block_number': normalized_tx.block_number,
            'from_address': normalized_tx.from_address,
            'to_address': normalized_tx.to_address,
            'value_wei': normalized_tx.value_wei,
            'value_eth': normalized_tx.value_eth,
            'gas_price_wei': normalized_tx.gas_price_wei,
            'gas_price_gwei': normalized_tx.gas_price_gwei,
            'gas_used': normalized_tx.gas_used,
            'gas_limit': normalized_tx.gas_limit,
            'status': normalized_tx.status,
            'timestamp': normalized_tx.timestamp.isoformat(),
            'contract_address': normalized_tx.contract_address,
            'method_signature': normalized_tx.method_signature,
            'input_data': normalized_tx.input_data,
            'logs': normalized_tx.logs,
            'nonce': normalized_tx.nonce,
            'fee_wei': normalized_tx.fee_wei,
            'fee_eth': normalized_tx.fee_eth
        }
    
    def detect_transaction_type(self, normalized_tx: NormalizedTransaction) -> str:
        """Detect the type of transaction"""
        
        if normalized_tx.contract_address and normalized_tx.input_data:
            if normalized_tx.input_data.startswith('0xa9059cbb'):
                return 'token_transfer'
            elif normalized_tx.input_data.startswith('0x23b872dd'):
                return 'token_approval'
            elif normalized_tx.input_data.startswith('0x'):
                return 'contract_interaction'
            else:
                return 'unknown_contract'
        elif normalized_tx.value_wei > 0:
            return 'native_transfer'
        else:
            return 'contract_deployment'
    
    def extract_token_transfer_info(self, normalized_tx: NormalizedTransaction) -> Optional[Dict[str, Any]]:
        """Extract token transfer information from transaction"""
        
        if not normalized_tx.logs:
            return None
        
        # Look for Transfer event (0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef)
        transfer_topic = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
        
        for log in normalized_tx.logs:
            if log.get('topics') and log['topics'][0] == transfer_topic:
                return {
                    'token_address': log.get('address'),
                    'from_address': '0x' + log['topics'][1][-40:] if len(log['topics']) > 1 else None,
                    'to_address': '0x' + log['topics'][2][-40:] if len(log['topics']) > 2 else None,
                    'value': int(log.get('data', '0x0'), 16)
                }
        
        return None

# Global instance
transaction_normalizer = TransactionNormalizer() 