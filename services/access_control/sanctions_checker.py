import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class SanctionsResult:
    address: str
    is_sanctioned: bool
    sanctions_list: List[str]
    confidence_score: float
    last_checked: datetime
    metadata: Dict[str, Any]

class SanctionsChecker:
    def __init__(self):
        self.sanctions_cache = {}
        self.api_endpoints = {
            'chainalysis': 'https://api.chainalysis.com/api/risk/v2/entities/',
            'elliptic': 'https://api.elliptic.co/v2/risk/',
            'crystal': 'https://api.crystalblockchain.com/risk/'
        }
        self.api_keys = {
            'chainalysis': os.getenv('CHAINALYSIS_API_KEY'),
            'elliptic': os.getenv('ELLIPTIC_API_KEY'),
            'crystal': os.getenv('CRYSTAL_API_KEY')
        }
        
        # Known sanctioned addresses
        self.known_sanctioned = {
            '0x7F367cC41522cE07553e823bf3be79A889DEbe1B',  # Tornado Cash
            '0x722122dF12D4e14e13Ac3b6895a86e84145b6967',  # Tornado Cash
            '0xDD4c48C0B24039969fC16D1cdF626eaB821d3384',  # Tornado Cash
            '0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b',  # Tornado Cash
            '0x722122dF12D4e14e13Ac3b6895a86e84145b6967',  # Tornado Cash
        }
    
    async def check_address(self, address: str) -> SanctionsResult:
        """Check if an address is sanctioned"""
        # Check cache first
        if address in self.sanctions_cache:
            cached_result = self.sanctions_cache[address]
            if (datetime.now() - cached_result.last_checked).days < 1:
                return cached_result
        
        # Check known sanctioned addresses
        if address.lower() in self.known_sanctioned:
            result = SanctionsResult(
                address=address,
                is_sanctioned=True,
                sanctions_list=['OFAC', 'Tornado Cash'],
                confidence_score=1.0,
                last_checked=datetime.now(),
                metadata={'source': 'known_list'}
            )
            self.sanctions_cache[address] = result
            return result
        
        # Check external APIs
        sanctions_list = []
        confidence_scores = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Chainalysis check
            if self.api_keys['chainalysis']:
                tasks.append(self._check_chainalysis(session, address))
            
            # Elliptic check
            if self.api_keys['elliptic']:
                tasks.append(self._check_elliptic(session, address))
            
            # Crystal check
            if self.api_keys['crystal']:
                tasks.append(self._check_crystal(session, address))
            
            # Wait for all checks to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict) and result.get('sanctions'):
                        sanctions_list.extend(result['sanctions'])
                        confidence_scores.append(result.get('confidence', 0.5))
        
        # Determine final result
        is_sanctioned = len(sanctions_list) > 0
        confidence_score = np.mean(confidence_scores) if confidence_scores else 0.0
        
        result = SanctionsResult(
            address=address,
            is_sanctioned=is_sanctioned,
            sanctions_list=list(set(sanctions_list)),  # Remove duplicates
            confidence_score=confidence_score,
            last_checked=datetime.now(),
            metadata={'sources_checked': len(tasks)}
        )
        
        # Cache result
        self.sanctions_cache[address] = result
        
        return result
    
    async def _check_chainalysis(self, session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
        """Check address against Chainalysis API"""
        try:
            headers = {
                'Token': self.api_keys['chainalysis'],
                'Content-Type': 'application/json'
            }
            
            async with session.get(
                f"{self.api_endpoints['chainalysis']}{address}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'sanctions': data.get('sanctions', []),
                        'confidence': data.get('confidence', 0.5)
                    }
                else:
                    logger.warning(f"Chainalysis API error: {response.status}")
                    return {'sanctions': [], 'confidence': 0.0}
        except Exception as e:
            logger.error(f"Error checking Chainalysis: {e}")
            return {'sanctions': [], 'confidence': 0.0}
    
    async def _check_elliptic(self, session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
        """Check address against Elliptic API"""
        try:
            headers = {
                'Authorization': f"Bearer {self.api_keys['elliptic']}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                'address': address,
                'currency': 'ETH'
            }
            
            async with session.post(
                self.api_endpoints['elliptic'],
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'sanctions': data.get('sanctions', []),
                        'confidence': data.get('confidence', 0.5)
                    }
                else:
                    logger.warning(f"Elliptic API error: {response.status}")
                    return {'sanctions': [], 'confidence': 0.0}
        except Exception as e:
            logger.error(f"Error checking Elliptic: {e}")
            return {'sanctions': [], 'confidence': 0.0}
    
    async def _check_crystal(self, session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
        """Check address against Crystal API"""
        try:
            headers = {
                'X-API-KEY': self.api_keys['crystal'],
                'Content-Type': 'application/json'
            }
            
            async with session.get(
                f"{self.api_endpoints['crystal']}{address}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'sanctions': data.get('sanctions', []),
                        'confidence': data.get('confidence', 0.5)
                    }
                else:
                    logger.warning(f"Crystal API error: {response.status}")
                    return {'sanctions': [], 'confidence': 0.0}
        except Exception as e:
            logger.error(f"Error checking Crystal: {e}")
            return {'sanctions': [], 'confidence': 0.0}
    
    async def batch_check_addresses(self, addresses: List[str]) -> List[SanctionsResult]:
        """Check multiple addresses for sanctions"""
        tasks = [self.check_address(addr) for addr in addresses]
        return await asyncio.gather(*tasks)
    
    def get_sanctions_statistics(self) -> Dict[str, Any]:
        """Get sanctions checking statistics"""
        total_checks = len(self.sanctions_cache)
        sanctioned_count = sum(1 for result in self.sanctions_cache.values() if result.is_sanctioned)
        
        return {
            'total_addresses_checked': total_checks,
            'sanctioned_addresses': sanctioned_count,
            'sanction_rate': sanctioned_count / total_checks if total_checks > 0 else 0,
            'cache_hit_rate': len(self.sanctions_cache) / (len(self.sanctions_cache) + 1),  # Simplified
            'recent_checks': [
                {
                    'address': result.address,
                    'is_sanctioned': result.is_sanctioned,
                    'confidence': result.confidence_score,
                    'timestamp': result.last_checked.isoformat()
                }
                for result in list(self.sanctions_cache.values())[-10:]  # Last 10 checks
            ]
        }
    
    async def process_sample_addresses(self, addresses: List[str]) -> List[SanctionsResult]:
        """Process sample addresses for sanctions checking"""
        return await self.batch_check_addresses(addresses) 