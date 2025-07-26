import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ChainConfig:
    name: str
    chain_id: int
    rpc_url: str
    block_time: int  # seconds
    api_key: str
    enabled: bool = True
    explorer_url: Optional[str] = None
    native_currency: str = "ETH"
    decimals: int = 18

class MultiChainConfig:
    def __init__(self):
        self.chains: Dict[int, ChainConfig] = {
            1: ChainConfig(
                name="Ethereum Mainnet",
                chain_id=1,
                rpc_url="https://eth-mainnet.g.alchemy.com/v2/",
                block_time=12,
                api_key=os.getenv("ALCHEMY_ETH_API_KEY", ""),
                explorer_url="https://etherscan.io",
                native_currency="ETH"
            ),
            137: ChainConfig(
                name="Polygon",
                chain_id=137,
                rpc_url="https://polygon-mainnet.g.alchemy.com/v2/",
                block_time=2,
                api_key=os.getenv("ALCHEMY_POLYGON_API_KEY", ""),
                explorer_url="https://polygonscan.com",
                native_currency="MATIC"
            ),
            56: ChainConfig(
                name="Binance Smart Chain",
                chain_id=56,
                rpc_url="https://bsc-dataseed.binance.org/",
                block_time=3,
                api_key="",  # BSC doesn't require API key
                explorer_url="https://bscscan.com",
                native_currency="BNB"
            ),
            42161: ChainConfig(
                name="Arbitrum One",
                chain_id=42161,
                rpc_url="https://arb-mainnet.g.alchemy.com/v2/",
                block_time=1,
                api_key=os.getenv("ALCHEMY_ARBITRUM_API_KEY", ""),
                explorer_url="https://arbiscan.io",
                native_currency="ETH"
            ),
            10: ChainConfig(
                name="Optimism",
                chain_id=10,
                rpc_url="https://opt-mainnet.g.alchemy.com/v2/",
                block_time=2,
                api_key=os.getenv("ALCHEMY_OPTIMISM_API_KEY", ""),
                explorer_url="https://optimistic.etherscan.io",
                native_currency="ETH"
            )
        }
    
    def get_chain(self, chain_id: int) -> Optional[ChainConfig]:
        """Get chain configuration by chain ID"""
        return self.chains.get(chain_id)
    
    def get_enabled_chains(self) -> Dict[int, ChainConfig]:
        """Get all enabled chains"""
        return {cid: config for cid, config in self.chains.items() if config.enabled}
    
    def get_chain_names(self) -> Dict[int, str]:
        """Get mapping of chain IDs to names"""
        return {cid: config.name for cid, config in self.chains.items()}
    
    def enable_chain(self, chain_id: int) -> bool:
        """Enable a specific chain"""
        if chain_id in self.chains:
            self.chains[chain_id].enabled = True
            return True
        return False
    
    def disable_chain(self, chain_id: int) -> bool:
        """Disable a specific chain"""
        if chain_id in self.chains:
            self.chains[chain_id].enabled = False
            return True
        return False
    
    def update_api_key(self, chain_id: int, api_key: str) -> bool:
        """Update API key for a specific chain"""
        if chain_id in self.chains:
            self.chains[chain_id].api_key = api_key
            return True
        return False
    
    def get_chain_status(self) -> Dict[str, Any]:
        """Get status of all chains"""
        status = {}
        for chain_id, config in self.chains.items():
            status[config.name] = {
                'chain_id': chain_id,
                'enabled': config.enabled,
                'has_api_key': bool(config.api_key),
                'block_time': config.block_time,
                'native_currency': config.native_currency
            }
        return status

# Global instance
multi_chain_config = MultiChainConfig() 