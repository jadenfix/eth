import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class MEVSignal:
    signal_id: str
    signal_type: str  # 'SANDWICH_ATTACK', 'FRONT_RUNNING', 'BACK_RUNNING', 'LIQUIDATION'
    confidence_score: float
    block_number: int
    timestamp: datetime
    target_transaction: Dict[str, Any]
    mev_transactions: List[Dict[str, Any]]
    profit_estimate: float
    gas_used: int
    addresses_involved: List[str]
    metadata: Dict[str, Any]

class MEVDetector:
    def __init__(self):
        self.recent_blocks = deque(maxlen=100)  # Keep last 100 blocks
        self.sandwich_patterns = defaultdict(list)
        self.liquidation_thresholds = {
            'aave': 0.8,  # 80% health factor
            'compound': 1.1,  # 110% collateral ratio
            'maker': 1.5  # 150% collateralization ratio
        }
        
    async def detect_sandwich_attack(self, block_transactions: List[Dict[str, Any]]) -> List[MEVSignal]:
        """Detect sandwich attacks in a block"""
        signals = []
        
        # Group transactions by target (victim transaction)
        potential_victims = []
        mev_candidates = []
        
        for tx in block_transactions:
            # Identify potential victim transactions (normal gas prices)
            if self._is_potential_victim(tx):
                potential_victims.append(tx)
            
            # Identify MEV transactions (high gas prices, specific patterns)
            if self._is_mev_candidate(tx):
                mev_candidates.append(tx)
        
        # Check for sandwich patterns
        for victim in potential_victims:
            sandwich = self._find_sandwich_pattern(victim, mev_candidates)
            if sandwich:
                signal = self._create_sandwich_signal(victim, sandwich)
                signals.append(signal)
        
        return signals
    
    def _is_potential_victim(self, tx: Dict[str, Any]) -> bool:
        """Identify potential victim transactions"""
        gas_price = tx.get('gasPrice', 0) / 1e9  # Convert to gwei
        
        # Normal gas prices (not MEV)
        if gas_price < 50:  # Less than 50 gwei
            return True
        
        # Check for DEX interactions (common victims)
        to_address = tx.get('to', '').lower()
        dex_addresses = {
            '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',  # Uniswap V2
            '0xe592427a0aece92de3edee1f18e0157c05861564',  # Uniswap V3
            '0x1111111254fb6c44bac0bed2854e76f90643097d',  # 1inch
        }
        
        if to_address in dex_addresses:
            return True
        
        return False
    
    def _is_mev_candidate(self, tx: Dict[str, Any]) -> bool:
        """Identify potential MEV transactions"""
        gas_price = tx.get('gasPrice', 0) / 1e9
        
        # High gas prices
        if gas_price > 200:  # More than 200 gwei
            return True
        
        # Check for known MEV bot patterns
        from_address = tx.get('from', '').lower()
        known_mev_bots = {
            '0x0000000000000000000000000000000000000000',  # Flashbots
            '0xdaFCE5670d3F67da9A3A44D6f3e82C7b8c5c3b3b',  # Example MEV bot
        }
        
        if from_address in known_mev_bots:
            return True
        
        # Check for flash loan patterns
        if self._has_flash_loan_pattern(tx):
            return True
        
        return False
    
    def _has_flash_loan_pattern(self, tx: Dict[str, Any]) -> bool:
        """Detect flash loan patterns in transaction"""
        input_data = tx.get('input', '')
        
        # Flash loan function signatures
        flash_loan_signatures = [
            '0x5cffe9de',  # Aave flash loan
            '0xb2a02ff1',  # Compound flash loan
            '0x1cff79cd',  # dYdX flash loan
        ]
        
        for signature in flash_loan_signatures:
            if input_data.startswith(signature):
                return True
        
        return False
    
    def _find_sandwich_pattern(self, victim: Dict[str, Any], mev_candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find sandwich attack pattern around victim transaction"""
        victim_gas_price = victim.get('gasPrice', 0)
        victim_position = self._get_transaction_position(victim)
        
        front_run = None
        back_run = None
        
        for mev_tx in mev_candidates:
            mev_gas_price = mev_tx.get('gasPrice', 0)
            mev_position = self._get_transaction_position(mev_tx)
            
            # Front run: higher gas price, earlier position
            if (mev_gas_price > victim_gas_price * 1.5 and 
                mev_position < victim_position):
                front_run = mev_tx
            
            # Back run: higher gas price, later position
            elif (mev_gas_price > victim_gas_price * 1.5 and 
                  mev_position > victim_position):
                back_run = mev_tx
        
        if front_run and back_run:
            return {
                'front_run': front_run,
                'victim': victim,
                'back_run': back_run
            }
        
        return None
    
    def _get_transaction_position(self, tx: Dict[str, Any]) -> int:
        """Get transaction position in block (simplified)"""
        # In a real implementation, this would use the actual transaction index
        return tx.get('transactionIndex', 0)
    
    def _create_sandwich_signal(self, victim: Dict[str, Any], sandwich: Dict[str, Any]) -> MEVSignal:
        """Create MEV signal for sandwich attack"""
        front_run = sandwich['front_run']
        back_run = sandwich['back_run']
        
        # Calculate profit estimate
        profit = self._estimate_sandwich_profit(victim, front_run, back_run)
        
        # Calculate confidence based on gas price differences
        confidence = min(
            (front_run['gasPrice'] / victim['gasPrice']) * 
            (back_run['gasPrice'] / victim['gasPrice']) / 10, 
            1.0
        )
        
        return MEVSignal(
            signal_id=f"sandwich_{victim['hash']}_{datetime.now().timestamp()}",
            signal_type='SANDWICH_ATTACK',
            confidence_score=confidence,
            block_number=victim.get('blockNumber', 0),
            timestamp=datetime.now(),
            target_transaction=victim,
            mev_transactions=[front_run, back_run],
            profit_estimate=profit,
            gas_used=front_run.get('gasUsed', 0) + back_run.get('gasUsed', 0),
            addresses_involved=[
                front_run.get('from', ''),
                victim.get('from', ''),
                back_run.get('from', '')
            ],
            metadata={
                'victim_gas_price': victim.get('gasPrice', 0),
                'front_run_gas_price': front_run.get('gasPrice', 0),
                'back_run_gas_price': back_run.get('gasPrice', 0),
                'gas_price_multiplier': front_run.get('gasPrice', 0) / victim.get('gasPrice', 1)
            }
        )
    
    def _estimate_sandwich_profit(self, victim: Dict[str, Any], front_run: Dict[str, Any], back_run: Dict[str, Any]) -> float:
        """Estimate profit from sandwich attack"""
        # Simplified profit estimation
        # In reality, this would analyze token transfers and price impact
        
        victim_value = victim.get('value', 0) / 1e18  # Convert from wei to ETH
        gas_cost = (front_run.get('gasUsed', 0) + back_run.get('gasUsed', 0)) * front_run.get('gasPrice', 0) / 1e18
        
        # Estimate profit as 0.1% of victim transaction value minus gas costs
        estimated_profit = victim_value * 0.001 - gas_cost
        
        return max(estimated_profit, 0)
    
    async def detect_liquidation_opportunities(self, block_transactions: List[Dict[str, Any]]) -> List[MEVSignal]:
        """Detect liquidation opportunities"""
        signals = []
        
        for tx in block_transactions:
            if self._is_liquidation_transaction(tx):
                signal = self._create_liquidation_signal(tx)
                signals.append(signal)
        
        return signals
    
    def _is_liquidation_transaction(self, tx: Dict[str, Any]) -> bool:
        """Identify liquidation transactions"""
        to_address = tx.get('to', '').lower()
        
        # Known liquidation contract addresses
        liquidation_contracts = {
            '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',  # Aave LendingPool
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B',  # Compound Comptroller
            '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B',  # Maker Vault
        }
        
        if to_address in liquidation_contracts:
            return True
        
        # Check for liquidation function calls
        input_data = tx.get('input', '')
        liquidation_signatures = [
            '0x2986c0e5',  # Aave liquidation
            '0xef693bed',  # Compound liquidation
        ]
        
        for signature in liquidation_signatures:
            if input_data.startswith(signature):
                return True
        
        return False
    
    def _create_liquidation_signal(self, tx: Dict[str, Any]) -> MEVSignal:
        """Create MEV signal for liquidation"""
        return MEVSignal(
            signal_id=f"liquidation_{tx['hash']}_{datetime.now().timestamp()}",
            signal_type='LIQUIDATION',
            confidence_score=0.9,
            block_number=tx.get('blockNumber', 0),
            timestamp=datetime.now(),
            target_transaction=tx,
            mev_transactions=[tx],
            profit_estimate=0.1,  # Estimated liquidation profit
            gas_used=tx.get('gasUsed', 0),
            addresses_involved=[tx.get('from', ''), tx.get('to', '')],
            metadata={
                'liquidation_type': 'debt_liquidation',
                'protocol': self._identify_protocol(tx.get('to', '')),
                'gas_price': tx.get('gasPrice', 0)
            }
        )
    
    def _identify_protocol(self, contract_address: str) -> str:
        """Identify the protocol from contract address"""
        protocol_addresses = {
            '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9': 'aave',
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B': 'compound',
            '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B': 'maker',
        }
        
        return protocol_addresses.get(contract_address.lower(), 'unknown') 