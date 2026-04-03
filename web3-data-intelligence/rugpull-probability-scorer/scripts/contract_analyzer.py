"""
Contract Analyzer - Analyzes smart contract security and detects malicious patterns
Uses GoPlus Security API, Honeypot.is API, and Etherscan API
"""

import os
import requests
from typing import Dict, Optional
from web3 import Web3
import time

class ContractAnalyzer:
    """Analyzes token smart contracts for security risks"""
    
    # API endpoints
    GOPLUS_API = "https://api.gopluslabs.io/api/v1"
    HONEYPOT_API = "https://api.honeypot.is/v2"
    
    # Block explorer APIs
    EXPLORER_APIS = {
        "ethereum": {
            "url": "https://api.etherscan.io/api",
            "key_env": "ETHERSCAN_API_KEY"
        },
        "bsc": {
            "url": "https://api.bscscan.com/api",
            "key_env": "BSCSCAN_API_KEY"
        },
        "polygon": {
            "url": "https://api.polygonscan.com/api",
            "key_env": "POLYGONSCAN_API_KEY"
        },
        "arbitrum": {
            "url": "https://api.arbiscan.io/api",
            "key_env": "ARBISCAN_API_KEY"
        },
        "base": {
            "url": "https://api.basescan.org/api",
            "key_env": "BASESCAN_API_KEY"
        }
    }
    
    # RPC endpoints
    RPC_URLS = {
        "ethereum": "https://eth.llamarpc.com",
        "bsc": "https://bsc-dataseed.binance.org",
        "polygon": "https://polygon-rpc.com",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "base": "https://mainnet.base.org"
    }
    
    # Chain IDs for GoPlus
    CHAIN_IDS = {
        "ethereum": "1",
        "bsc": "56",
        "polygon": "137",
        "arbitrum": "42161",
        "base": "8453"
    }
    
    def __init__(self):
        """Initialize contract analyzer"""
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def analyze_contract(self, token_address: str, chain: str = "ethereum") -> Dict:
        """
        Comprehensive contract security analysis
        
        Args:
            token_address: Token contract address
            chain: Blockchain network
            
        Returns:
            Contract analysis dictionary with security score
        """
        print(f"\n🔍 Analyzing contract: {token_address}")
        print(f"Chain: {chain}")
        
        # Validate address
        if not Web3.is_address(token_address):
            return {
                "success": False,
                "error": "Invalid contract address"
            }
        
        token_address = Web3.to_checksum_address(token_address)
        
        # Get GoPlus security analysis
        print("📊 Fetching GoPlus security data...")
        goplus_data = self._get_goplus_analysis(token_address, chain)
        
        # Check honeypot status
        print("🍯 Checking honeypot status...")
        honeypot_data = self._check_honeypot(token_address, chain)
        
        # Get contract verification status
        print("✅ Checking contract verification...")
        verification_data = self._check_verification(token_address, chain)
        
        # Calculate contract security score (max 30 points)
        score = self._calculate_contract_score(goplus_data, honeypot_data, verification_data)
        
        # Identify malicious functions
        malicious_functions = self._identify_malicious_functions(goplus_data)
        
        # Determine warnings and red flags
        warnings, red_flags = self._extract_warnings(goplus_data, honeypot_data, verification_data)
        
        print(f"✅ Contract analysis complete - Score: {score}/30")
        
        # Extract tax info safely
        sim_success = honeypot_data.get('simulationSuccess', {})
        if isinstance(sim_success, dict):
            buy_tax = sim_success.get('buyTax', 0)
            sell_tax = sim_success.get('sellTax', 0)
        else:
            buy_tax = 0
            sell_tax = 0
        
        return {
            "success": True,
            "token_address": token_address,
            "chain": chain,
            "security_score": score,
            "max_score": 30,
            "is_verified": verification_data.get('is_verified', False),
            "is_open_source": verification_data.get('is_open_source', False),
            "ownership_renounced": goplus_data.get('is_open_source') == '1' or goplus_data.get('owner_address') is None,
            "has_mint_function": goplus_data.get('is_mintable') == '1',
            "has_proxy": goplus_data.get('is_proxy') == '1',
            "has_blacklist": goplus_data.get('is_blacklisted') == '1',
            "hidden_fees": goplus_data.get('hidden_owner') == '1' or goplus_data.get('is_hidden_owner') == '1',
            "can_take_back_ownership": goplus_data.get('can_take_back_ownership') == '1',
            "transfer_pausable": goplus_data.get('transfer_pausable') == '1',
            "malicious_functions": malicious_functions,
            "is_honeypot": honeypot_data.get('isHoneypot', False),
            "honeypot_reason": honeypot_data.get('honeypotReason'),
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "warnings": warnings,
            "red_flags": red_flags,
            "goplus_result": goplus_data.get('is_open_source') if goplus_data else None
        }
    
    def check_honeypot(self, token_address: str, chain: str = "ethereum") -> Dict:
        """
        Quick honeypot check
        
        Returns:
            Honeypot status and trading taxes
        """
        token_address = Web3.to_checksum_address(token_address)
        honeypot_data = self._check_honeypot(token_address, chain)
        
        sim_success = honeypot_data.get('simulationSuccess', {})
        if isinstance(sim_success, dict):
            buy_tax = sim_success.get('buyTax', 0)
            sell_tax = sim_success.get('sellTax', 0)
        else:
            buy_tax = 0
            sell_tax = 0
        
        return {
            "is_honeypot": honeypot_data.get('isHoneypot', False),
            "can_buy": not honeypot_data.get('isHoneypot', False),
            "can_sell": not honeypot_data.get('isHoneypot', False),
            "buy_tax": buy_tax,
            "sell_tax": sell_tax,
            "honeypot_reason": honeypot_data.get('honeypotReason')
        }
    
    def _get_goplus_analysis(self, token_address: str, chain: str) -> Dict:
        """Get security analysis from GoPlus API"""
        try:
            chain_id = self.CHAIN_IDS.get(chain, "1")
            url = f"{self.GOPLUS_API}/token_security/{chain_id}"
            params = {"contract_addresses": token_address.lower()}
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 1 and data.get('result'):
                    token_data = data['result'].get(token_address.lower(), {})
                    if token_data:
                        print("✅ GoPlus data retrieved")
                        return token_data
            
            print("⚠️ GoPlus API returned no data")
            
        except Exception as e:
            print(f"⚠️ GoPlus API error: {str(e)}")
        
        return {}
    
    def _check_honeypot(self, token_address: str, chain: str) -> Dict:
        """Check honeypot status using Honeypot.is API"""
        try:
            # Honeypot.is uses different chain names
            chain_mapping = {
                "ethereum": "eth",
                "bsc": "bsc",
                "polygon": "polygon",
                "arbitrum": "arbitrum",
                "base": "base"
            }
            
            chain_name = chain_mapping.get(chain, "eth")
            url = f"{self.HONEYPOT_API}/IsHoneypot"
            params = {
                "address": token_address,
                "chainID": self.CHAIN_IDS.get(chain, "1")
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Honeypot check complete")
                return data
            else:
                print(f"⚠️ Honeypot API returned {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Honeypot API error: {str(e)}")
        
        # Return safe defaults if API fails
        return {
            "isHoneypot": False,
            "simulationSuccess": False
        }
    
    def _check_verification(self, token_address: str, chain: str) -> Dict:
        """Check if contract is verified on block explorer"""
        try:
            if chain not in self.EXPLORER_APIS:
                return {"is_verified": False, "is_open_source": False}
            
            api_config = self.EXPLORER_APIS[chain]
            api_key = os.getenv(api_config['key_env'])
            
            if not api_key:
                print(f"⚠️ No API key for {chain} - skipping verification check")
                return {"is_verified": False, "is_open_source": False}
            
            url = api_config['url']
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": token_address,
                "apikey": api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '1' and data.get('result'):
                    result = data['result'][0]
                    source_code = result.get('SourceCode', '')
                    
                    is_verified = bool(source_code)
                    is_open_source = len(source_code) > 100  # Has substantial code
                    
                    if is_verified:
                        print("✅ Contract is verified")
                    
                    return {
                        "is_verified": is_verified,
                        "is_open_source": is_open_source,
                        "contract_name": result.get('ContractName'),
                        "compiler_version": result.get('CompilerVersion')
                    }
            
        except Exception as e:
            print(f"⚠️ Verification check error: {str(e)}")
        
        return {"is_verified": False, "is_open_source": False}
    
    def _calculate_contract_score(self, goplus: Dict, honeypot: Dict, verification: Dict) -> int:
        """Calculate contract security score (0-30 points)"""
        score = 0
        
        # Verified contract (5 points)
        if verification.get('is_verified'):
            score += 5
        
        # No mint function (5 points)
        if goplus.get('is_mintable') == '0':
            score += 5
        elif goplus.get('is_mintable') != '1':  # Unknown/not found
            score += 3
        
        # Ownership renounced or no owner (5 points)
        if goplus.get('is_open_source') == '1' or not goplus.get('owner_address'):
            score += 5
        elif goplus.get('can_take_back_ownership') == '0':
            score += 3
        
        # No blacklist function (5 points)
        if goplus.get('is_blacklisted') == '0':
            score += 5
        elif goplus.get('is_blacklisted') != '1':
            score += 3
        
        # Not a proxy (5 points)
        if goplus.get('is_proxy') == '0':
            score += 5
        elif goplus.get('is_proxy') != '1':
            score += 3
        
        # No hidden fees/owner (5 points)
        if goplus.get('hidden_owner') == '0' and goplus.get('is_hidden_owner') == '0':
            score += 5
        elif not goplus.get('hidden_owner') and not goplus.get('is_hidden_owner'):
            score += 3
        
        # Not a honeypot (bonus from trading analysis, but affects contract score)
        if not honeypot.get('isHoneypot'):
            score = min(30, score + 2)
        
        return min(30, score)
    
    def _identify_malicious_functions(self, goplus: Dict) -> list:
        """Identify malicious or dangerous functions"""
        malicious = []
        
        if goplus.get('is_mintable') == '1':
            malicious.append("Mint function (can create unlimited tokens)")
        
        if goplus.get('is_blacklisted') == '1':
            malicious.append("Blacklist function (can block addresses)")
        
        if goplus.get('can_take_back_ownership') == '1':
            malicious.append("Can take back ownership")
        
        if goplus.get('transfer_pausable') == '1':
            malicious.append("Transfer pausable (can freeze trading)")
        
        if goplus.get('hidden_owner') == '1' or goplus.get('is_hidden_owner') == '1':
            malicious.append("Hidden owner detected")
        
        if goplus.get('selfdestruct') == '1':
            malicious.append("Self-destruct function")
        
        if goplus.get('external_call') == '1':
            malicious.append("External call (potential reentrancy)")
        
        return malicious
    
    def _extract_warnings(self, goplus: Dict, honeypot: Dict, verification: Dict) -> tuple:
        """Extract warnings and red flags"""
        warnings = []
        red_flags = []
        
        # Contract verification
        if not verification.get('is_verified'):
            red_flags.append("Contract not verified - cannot audit code")
        
        # Honeypot
        if honeypot.get('isHoneypot'):
            red_flags.append(f"HONEYPOT DETECTED: {honeypot.get('honeypotReason', 'Cannot sell')}")
        
        # High taxes
        sim_success = honeypot.get('simulationSuccess', {})
        if isinstance(sim_success, dict):
            buy_tax = sim_success.get('buyTax', 0)
            sell_tax = sim_success.get('sellTax', 0)
        else:
            buy_tax = 0
            sell_tax = 0
        
        if buy_tax > 10:
            warnings.append(f"High buy tax: {buy_tax}%")
        if sell_tax > 10:
            warnings.append(f"High sell tax: {sell_tax}%")
        if buy_tax > 25 or sell_tax > 25:
            red_flags.append(f"EXTREME TAX: Buy {buy_tax}% / Sell {sell_tax}%")
        
        # Mint function
        if goplus.get('is_mintable') == '1':
            red_flags.append("Can mint unlimited tokens")
        
        # Ownership issues
        if goplus.get('can_take_back_ownership') == '1':
            red_flags.append("Owner can take back control")
        
        if goplus.get('hidden_owner') == '1':
            red_flags.append("Hidden owner detected")
        
        # Blacklist
        if goplus.get('is_blacklisted') == '1':
            warnings.append("Contract has blacklist function")
        
        # Proxy
        if goplus.get('is_proxy') == '1':
            warnings.append("Proxy contract - implementation can be changed")
        
        # Transfer pausable
        if goplus.get('transfer_pausable') == '1':
            warnings.append("Trading can be paused by owner")
        
        # Self-destruct
        if goplus.get('selfdestruct') == '1':
            red_flags.append("Contract can self-destruct")
        
        # Trading cooldown
        if goplus.get('trading_cooldown') == '1':
            warnings.append("Trading cooldown enabled")
        
        return warnings, red_flags

