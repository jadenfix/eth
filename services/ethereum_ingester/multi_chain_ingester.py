import asyncio
import logging
from typing import Dict, List, Optional, Any
from web3 import Web3
from web3.exceptions import Web3Exception
import aiohttp
import json
from datetime import datetime, timedelta

from .config.chains import MultiChainConfig, ChainConfig
from .ethereum_ingester import EthereumIngester

logger = logging.getLogger(__name__)

class MultiChainIngester:
    def __init__(self):
        self.config = MultiChainConfig()
        self.ingesters: Dict[int, EthereumIngester] = {}
        self.web3_instances: Dict[int, Web3] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.setup_ingesters()
    
    def setup_ingesters(self):
        """Initialize ingesters for each enabled chain"""
        for chain_id, chain_config in self.config.get_enabled_chains().items():
            try:
                # Create Web3 instance
                if chain_config.api_key:
                    rpc_url = f"{chain_config.rpc_url}{chain_config.api_key}"
                else:
                    rpc_url = chain_config.rpc_url
                
                web3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # Test connection
                if web3.is_connected():
                    self.web3_instances[chain_id] = web3
                    self.ingesters[chain_id] = EthereumIngester(
                        web3=web3,
                        chain_id=chain_id,
                        chain_name=chain_config.name
                    )
                    logger.info(f"✅ Connected to {chain_config.name} (Chain ID: {chain_id})")
                else:
                    logger.warning(f"❌ Failed to connect to {chain_config.name} (Chain ID: {chain_id})")
                    
            except Exception as e:
                logger.error(f"Error setting up {chain_config.name}: {e}")
    
    async def start_session(self):
        """Start aiohttp session for API calls"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_latest_blocks(self) -> Dict[int, Dict[str, Any]]:
        """Get latest block from all chains"""
        results = {}
        
        for chain_id, ingester in self.ingesters.items():
            try:
                block = await ingester.get_latest_block()
                if block:
                    results[chain_id] = {
                        'chain_id': chain_id,
                        'chain_name': self.config.get_chain(chain_id).name,
                        'block_number': block['number'],
                        'block_hash': block['hash'],
                        'timestamp': block['timestamp'],
                        'transactions_count': len(block['transactions']),
                        'gas_used': block['gasUsed'],
                        'gas_limit': block['gasLimit'],
                        'base_fee_per_gas': block.get('baseFeePerGas', 0)
                    }
            except Exception as e:
                logger.error(f"Error getting block for chain {chain_id}: {e}")
                results[chain_id] = {
                    'chain_id': chain_id,
                    'chain_name': self.config.get_chain(chain_id).name,
                    'error': str(e)
                }
        
        return results
    
    async def get_chain_metrics(self) -> Dict[int, Dict[str, Any]]:
        """Get comprehensive metrics for all chains"""
        metrics = {}
        
        for chain_id, ingester in self.ingesters.items():
            try:
                chain_config = self.config.get_chain(chain_id)
                
                # Get latest block
                latest_block = await ingester.get_latest_block()
                
                # Get gas price
                gas_price = await ingester.get_gas_price()
                
                # Get network status
                network_status = await ingester.get_network_status()
                
                metrics[chain_id] = {
                    'chain_id': chain_id,
                    'chain_name': chain_config.name,
                    'native_currency': chain_config.native_currency,
                    'block_time': chain_config.block_time,
                    'latest_block': latest_block['number'] if latest_block else 0,
                    'gas_price_gwei': gas_price / 1e9 if gas_price else 0,
                    'gas_price_wei': gas_price if gas_price else 0,
                    'network_status': network_status,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error getting metrics for chain {chain_id}: {e}")
                metrics[chain_id] = {
                    'chain_id': chain_id,
                    'chain_name': self.config.get_chain(chain_id).name,
                    'error': str(e)
                }
        
        return metrics
    
    async def get_transaction_data(self, chain_id: int, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction data from a specific chain"""
        if chain_id not in self.ingesters:
            return None
        
        try:
            ingester = self.ingesters[chain_id]
            tx_data = await ingester.get_transaction(tx_hash)
            return tx_data
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash} from chain {chain_id}: {e}")
            return None
    
    async def get_block_data(self, chain_id: int, block_number: int) -> Optional[Dict[str, Any]]:
        """Get block data from a specific chain"""
        if chain_id not in self.ingesters:
            return None
        
        try:
            ingester = self.ingesters[chain_id]
            block_data = await ingester.get_block(block_number)
            return block_data
        except Exception as e:
            logger.error(f"Error getting block {block_number} from chain {chain_id}: {e}")
            return None
    
    async def get_address_balance(self, chain_id: int, address: str) -> Optional[Dict[str, Any]]:
        """Get address balance from a specific chain"""
        if chain_id not in self.ingesters:
            return None
        
        try:
            ingester = self.ingesters[chain_id]
            balance = await ingester.get_address_balance(address)
            return {
                'address': address,
                'chain_id': chain_id,
                'chain_name': self.config.get_chain(chain_id).name,
                'balance_wei': balance,
                'balance_eth': balance / 1e18 if balance else 0
            }
        except Exception as e:
            logger.error(f"Error getting balance for {address} on chain {chain_id}: {e}")
            return None
    
    async def get_aggregated_data(self) -> Dict[str, Any]:
        """Get aggregated data from all chains"""
        try:
            # Get latest blocks
            latest_blocks = await self.get_latest_blocks()
            
            # Get chain metrics
            chain_metrics = await self.get_chain_metrics()
            
            # Calculate aggregated metrics
            total_blocks = sum(
                block.get('block_number', 0) 
                for block in latest_blocks.values() 
                if 'error' not in block
            )
            
            total_transactions = sum(
                block.get('transactions_count', 0) 
                for block in latest_blocks.values() 
                if 'error' not in block
            )
            
            active_chains = len([b for b in latest_blocks.values() if 'error' not in b])
            
            return {
                'chains': latest_blocks,
                'metrics': chain_metrics,
                'summary': {
                    'total_blocks': total_blocks,
                    'total_transactions': total_transactions,
                    'active_chains': active_chains,
                    'total_chains': len(self.config.chains)
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting aggregated data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def start_all_ingesters(self):
        """Start ingestion for all enabled chains"""
        tasks = []
        for chain_id, ingester in self.ingesters.items():
            task = asyncio.create_task(ingester.start_ingestion())
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get status of all chains"""
        status = {}
        for chain_id, config in self.config.chains.items():
            is_connected = chain_id in self.web3_instances
            ingester_active = chain_id in self.ingesters
            
            status[config.name] = {
                'chain_id': chain_id,
                'enabled': config.enabled,
                'connected': is_connected,
                'ingester_active': ingester_active,
                'has_api_key': bool(config.api_key),
                'block_time': config.block_time,
                'native_currency': config.native_currency
            }
        
        return status

# Global instance
multi_chain_ingester = MultiChainIngester() 