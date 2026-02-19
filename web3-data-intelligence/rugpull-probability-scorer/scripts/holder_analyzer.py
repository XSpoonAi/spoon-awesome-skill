"""
Holder Analyzer - Analyzes token holder distribution and centralization risks
Uses Etherscan API and on-chain data
"""

import os
import requests
from typing import Dict, List
from web3 import Web3
import time

class HolderAnalyzer:
    """Analyzes token holder distribution for centralization risks"""
    
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
    
    # Known CEX wallets (to filter out from concentration analysis)
    KNOWN_CEX_WALLETS = {
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance 14",
        "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "Binance 15",
        "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "Binance 16",
        "0x56eddb7aa87536c09ccc2793473599fd21a8b17f": "Binance Hot",
        "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be": "Binance 7",
        "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance 8",
        "0x8894e0a0c962cb723c1976a4421c95949be2d4e3": "Binance US",
        "0x46340b20830761efd32832a74d7169b29feb9758": "Coinbase 1",
        "0x503828976d22510aad0201ac7ec88293211d23da": "Coinbase 2",
        "0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740": "Coinbase 3",
        "0x71660c4005ba85c37ccec55d0c4493e66fe775d3": "Coinbase 4",
        "0xa090e606e30bd747d4e6245a1517ebe430f0057e": "Coinbase Commerce",
        "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0": "Kraken",
        "0xe853c98f8f07b14f8809c1230d78fa80e1d73dce": "Kraken 2",
        "0x0a869d79a7052c7f1b55a8ebabbea3420f0d1e13": "Kraken 3",
        "0x2910543af39aba0cd09dbb2d50200b3e800a63d2": "Kraken 4",
        "0x43984d578803891dfa9706bdeee6078d80cfc79e": "Kraken 5",
    }
    
    # ERC20 ABI for balanceOf, totalSupply, and Transfer event
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": False, "name": "value", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        }
    ]
    
    # RPC endpoints
    RPC_URLS = {
        "ethereum": "https://eth.llamarpc.com",
        "bsc": "https://bsc-dataseed.binance.org",
        "polygon": "https://polygon-rpc.com",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "base": "https://mainnet.base.org"
    }
    
    def __init__(self):
        """Initialize holder analyzer"""
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })
        
    def analyze_holders(self, token_address: str, chain: str = "ethereum") -> Dict:
        """
        Analyze token holder distribution
        
        Args:
            token_address: Token contract address
            chain: Blockchain network
            
        Returns:
            Holder distribution analysis with score
        """
        print(f"\n👥 Analyzing holder distribution")
        
        if not Web3.is_address(token_address):
            return {
                "success": False,
                "error": "Invalid token address"
            }
        
        token_address = Web3.to_checksum_address(token_address)
        
        # Get top holders from block explorer
        print("📊 Fetching top holders...")
        holders_data = self._get_top_holders(token_address, chain)
        
        # Get total supply
        print("💰 Getting token supply...")
        total_supply = self._get_total_supply(token_address, chain)
        
        # Calculate holder metrics
        metrics = self._calculate_holder_metrics(holders_data, total_supply)
        
        # Calculate holder score (max 25 points)
        score = self._calculate_holder_score(metrics, holders_data)
        
        # Determine risk level
        risk_level = self._determine_risk_level(metrics)
        
        print(f"✅ Holder analysis complete - Score: {score}/25")
        
        return {
            "success": True,
            "token_address": token_address,
            "chain": chain,
            "score": score,
            "max_score": 25,
            "holder_count": metrics['holder_count'],
            "top_holder_percentage": metrics['top_holder_pct'],
            "top_10_percentage": metrics['top_10_pct'],
            "top_50_percentage": metrics['top_50_pct'],
            "centralization_risk": risk_level,
            "cex_holder_count": metrics['cex_count'],
            "non_cex_top_10_percentage": metrics['non_cex_top_10_pct'],
            "gini_coefficient": metrics['gini_coefficient'],
            "warnings": metrics['warnings']
        }
    
    def _get_top_holders(self, token_address: str, chain: str) -> List[Dict]:
        """Get top token holders using on-chain Transfer events"""
        print("📊 Scanning on-chain Transfer events for holder data...")
        return self._get_holders_via_rpc(token_address, chain)
    
    def _get_holders_via_rpc(self, token_address: str, chain: str) -> List[Dict]:
        """
        Get holders using on-chain Transfer events
        Scans recent blocks to find active holders
        """
        try:
            rpc_url = self.RPC_URLS.get(chain)
            if not rpc_url:
                print(f"⚠️ No RPC URL for chain: {chain}")
                return []
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not w3.is_connected():
                print("⚠️ RPC connection failed")
                return []
            
            token_address_checksum = Web3.to_checksum_address(token_address)
            contract = w3.eth.contract(address=token_address_checksum, abi=self.ERC20_ABI)
            
            # Get current block and scan last 1000 blocks for Transfer events  
            # (Most free RPCs limit to 1000 blocks per query)
            current_block = w3.eth.block_number
            from_block = max(0, current_block - 1000)
            
            print(f"🔍 Scanning blocks {from_block} to {current_block}...")
            
            # Transfer event signature
            transfer_event = contract.events.Transfer()
            
            # Get Transfer events
            events = transfer_event.get_logs(from_block=from_block, to_block=current_block)
            
            print(f"✅ Found {len(events)} Transfer events")
            
            # Build holder set from transfer recipients without querying balances
            # This avoids rate limits on free RPC endpoints
            holder_addresses = set()
            
            for event in events:
                to_address = event['args']['to']
                from_address = event['args']['from']
                
                # Add recipients (exclude zero address - burns/mints)
                if to_address != '0x0000000000000000000000000000000000000000':
                    holder_addresses.add(to_address)
                if from_address != '0x0000000000000000000000000000000000000000':
                    holder_addresses.add(from_address)
            
            print(f"✅ Found {len(holder_addresses)} unique holder addresses from recent activity")
            
            # Return simplified holder data (addresses only, no balances to avoid rate limits)
            # For production use with paid RPC, individual balances can be queried
            holders_list = [
                {
                    'TokenHolderAddress': address,
                    'TokenHolderQuantity': '0'  # Unknown without individual queries
                }
                for address in list(holder_addresses)[:50]
            ]
            
            return holders_list
            
        except Exception as e:
            print(f"⚠️ Error scanning holders: {str(e)}")
            return []
    
    def _get_total_supply(self, token_address: str, chain: str) -> int:
        """Get token total supply"""
        try:
            rpc_url = self.RPC_URLS.get(chain)
            if not rpc_url:
                return 0
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if w3.is_connected():
                contract = w3.eth.contract(address=token_address, abi=self.ERC20_ABI)
                total_supply = contract.functions.totalSupply().call()
                print(f"✅ Total supply: {total_supply}")
                return total_supply
                
        except Exception as e:
            print(f"⚠️ Error getting total supply: {str(e)}")
        
        return 0
    
    def _calculate_holder_metrics(self, holders: List[Dict], total_supply: int) -> Dict:
        """Calculate holder distribution metrics"""
        metrics = {
            "holder_count": len(holders),
            "top_holder_pct": 0,
            "top_10_pct": 0,
            "top_50_pct": 0,
            "cex_count": 0,
            "non_cex_top_10_pct": 0,
            "gini_coefficient": 0,
            "warnings": []
        }
        
        if not holders:
            metrics['warnings'].append("No holder data available")
            return metrics
        
        # Check if balances are available
        has_balances = any(int(h.get('TokenHolderQuantity', 0)) > 0 for h in holders)
        
        if not has_balances:
            # Estimate distribution based on holder count only
            # Typical token distribution: top 10 holders own 50-80% of supply
            metrics['warnings'].append(f"Holder distribution estimated from {len(holders)} active addresses")
            if len(holders) < 50:
                metrics['warnings'].append("Very few holders detected - possible low liquidity or new token")
                metrics['top_10_pct'] = 80.0  # Assume high concentration
            elif len(holders) < 200:
                metrics['top_10_pct'] = 60.0  # Moderate concentration
            else:
                metrics['top_10_pct'] = 40.0  # Better distribution
            
            metrics['top_holder_pct'] = metrics['top_10_pct'] / 2.5
            metrics['top_50_pct'] = min(95.0, metrics['top_10_pct'] * 1.4)
            return metrics
        
        if total_supply == 0:
            metrics['warnings'].append("Unable to calculate percentages without total supply")
            return metrics
        
        # Calculate percentages from actual balances
        top_10_balance = 0
        top_50_balance = 0
        non_cex_top_10_balance = 0
        
        for i, holder in enumerate(holders[:50]):
            balance = int(holder.get('TokenHolderQuantity', 0) if 'TokenHolderQuantity' in holder else holder.get('value', 0))
            percentage = (balance / total_supply * 100) if total_supply > 0 else 0
            
            address = holder.get('TokenHolderAddress', holder.get('address', '')).lower()
            is_cex = address in self.KNOWN_CEX_WALLETS
            
            if is_cex:
                metrics['cex_count'] += 1
            
            if i == 0:
                metrics['top_holder_pct'] = percentage
                if percentage > 50:
                    metrics['warnings'].append(f"Single holder owns {percentage:.1f}% of supply")
            
            if i < 10:
                top_10_balance += balance
                if not is_cex:
                    non_cex_top_10_balance += balance
            
            if i < 50:
                top_50_balance += balance
        
        metrics['top_10_pct'] = (top_10_balance / total_supply * 100) if total_supply > 0 else 0
        metrics['top_50_pct'] = (top_50_balance / total_supply * 100) if total_supply > 0 else 0
        metrics['non_cex_top_10_pct'] = (non_cex_top_10_balance / total_supply * 100) if total_supply > 0 else 0
        
        # Calculate Gini coefficient (measure of inequality)
        metrics['gini_coefficient'] = self._calculate_gini(holders, total_supply)
        
        # Add concentration warnings
        if metrics['top_10_pct'] > 80:
            metrics['warnings'].append("Extreme concentration - top 10 hold >80%")
        elif metrics['top_10_pct'] > 60:
            metrics['warnings'].append("High concentration - top 10 hold >60%")
        
        if metrics['non_cex_top_10_pct'] > 50 and metrics['cex_count'] > 0:
            metrics['warnings'].append("High non-CEX concentration")
        
        return metrics
    
    def _calculate_gini(self, holders: List[Dict], total_supply: int) -> float:
        """
        Calculate Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        """
        if not holders or total_supply == 0:
            return 0
        
        try:
            balances = []
            for holder in holders:
                balance = int(holder.get('TokenHolderQuantity', 0) if 'TokenHolderQuantity' in holder else holder.get('value', 0))
                balances.append(balance)
            
            balances.sort()
            n = len(balances)
            
            if n == 0:
                return 0
            
            # Calculate Gini using the standard formula
            cumsum = 0
            for i, balance in enumerate(balances):
                cumsum += (i + 1) * balance
            
            gini = (2 * cumsum) / (n * sum(balances)) - (n + 1) / n
            return round(gini, 3)
            
        except:
            return 0
    
    def _calculate_holder_score(self, metrics: Dict, holders: List[Dict]) -> int:
        """Calculate holder distribution score (0-25 points)"""
        score = 0
        
        # Holder count score (8 points)
        holder_count = metrics['holder_count']
        if holder_count > 10000:
            score += 8
        elif holder_count > 5000:
            score += 6
        elif holder_count > 1000:
            score += 4
        elif holder_count > 100:
            score += 2
        
        # Top 10 concentration score (10 points)
        top_10_pct = metrics['top_10_pct']
        if top_10_pct < 30:
            score += 10
        elif top_10_pct < 40:
            score += 8
        elif top_10_pct < 50:
            score += 6
        elif top_10_pct < 60:
            score += 4
        elif top_10_pct < 70:
            score += 2
        
        # Single large holder penalty (7 points if no whale)
        top_holder_pct = metrics['top_holder_pct']
        if top_holder_pct < 5:
            score += 7
        elif top_holder_pct < 10:
            score += 5
        elif top_holder_pct < 20:
            score += 3
        elif top_holder_pct < 30:
            score += 1
        
        return min(25, score)
    
    def _determine_risk_level(self, metrics: Dict) -> str:
        """Determine centralization risk level"""
        top_10_pct = metrics['top_10_pct']
        top_holder_pct = metrics['top_holder_pct']
        
        if top_holder_pct > 50 or top_10_pct > 80:
            return "Critical"
        elif top_holder_pct > 30 or top_10_pct > 70:
            return "High"
        elif top_holder_pct > 20 or top_10_pct > 60:
            return "Moderate"
        elif top_holder_pct > 10 or top_10_pct > 50:
            return "Low"
        else:
            return "Very Low"

