"""
Whale Wallet Performance Tracker
Calculates wallet APY from on-chain transaction history and price data
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class WhalePerformanceTracker:
    """
    Tracks and calculates performance metrics for Ethereum wallets
    
    Features:
    - Fetches wallet transaction history (Etherscan API)
    - Gets current token prices (DexScreener API)
    - Calculates cost basis and current value
    - Computes APY over specified time periods
    - Identifies high-performing whale wallets (>100% APY)
    """
    
    def __init__(self, etherscan_api_key: Optional[str] = None):
        """
        Initialize the performance tracker
        
        Args:
            etherscan_api_key: Optional API key for Etherscan (free tier: 5 calls/sec)
        """
        self.etherscan_api_key = etherscan_api_key or "S61W6QK13ZPENIB91MKQ669MAZQS5WH552"
        self.etherscan_api = "https://api.etherscan.io/v2/api"
        self.dexscreener_api = "https://api.dexscreener.com"
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
        # Cache for token prices
        self.price_cache: Dict[str, Dict] = {}
        self.cache_expiry = 300  # 5 minutes
        
    def get_wallet_transactions(self, wallet_address: str, start_block: int = 0) -> List[Dict]:
        """
        Fetch ERC20 token transfer transactions for a wallet
        
        Args:
            wallet_address: Ethereum wallet address
            start_block: Starting block number (0 for all history)
            
        Returns:
            List of transaction dictionaries
        """
        try:
            params = {
                "chainid": 1,  # Ethereum mainnet
                "module": "account",
                "action": "tokentx",
                "address": wallet_address,
                "startblock": start_block,
                "endblock": 99999999,
                "page": 1,
                "offset": 1000,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            
            response = self.session.get(self.etherscan_api, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "1":
                return data.get("result", [])
            else:
                error_msg = data.get('message', 'Unknown error')
                result_msg = data.get('result', '')
                print(f"⚠️ Etherscan API error: {error_msg} - {result_msg}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching transactions: {e}")
            return []
    
    def get_token_price(self, token_address: str, chain: str = "ethereum") -> Optional[float]:
        """
        Get current token price in USD
        
        Args:
            token_address: Token contract address
            chain: Blockchain name (ethereum, bsc, arbitrum, etc.)
            
        Returns:
            Price in USD or None if not found
        """
        try:
            # Check cache first
            cache_key = f"{chain}:{token_address.lower()}"
            if cache_key in self.price_cache:
                cached = self.price_cache[cache_key]
                if time.time() - cached['timestamp'] < self.cache_expiry:
                    return cached['price']
            
            # Try DexScreener first (no API key needed)
            url = f"{self.dexscreener_api}/latest/dex/tokens/{token_address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                
                if pairs:
                    # Get price from pair with highest liquidity
                    sorted_pairs = sorted(
                        pairs,
                        key=lambda x: x.get("liquidity", {}).get("usd", 0),
                        reverse=True
                    )
                    price_usd = float(sorted_pairs[0].get("priceUsd", 0))
                    
                    # Cache the result
                    self.price_cache[cache_key] = {
                        'price': price_usd,
                        'timestamp': time.time()
                    }
                    return price_usd
            
            # Fallback: Try CoinGecko
            if token_address.lower() == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":  # WETH
                # Use ETH price for WETH
                url = f"{self.coingecko_api}/simple/price?ids=ethereum&vs_currencies=usd"
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    price = data.get("ethereum", {}).get("usd", 0)
                    self.price_cache[cache_key] = {'price': price, 'timestamp': time.time()}
                    return price
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error fetching price for {token_address}: {e}")
            return None
    
    def calculate_wallet_performance(
        self, 
        wallet_address: str,
        days_back: int = 30,
        min_value_usd: float = 1000
    ) -> Dict:
        """
        Calculate comprehensive wallet performance metrics
        
        Args:
            wallet_address: Wallet address to analyze
            days_back: How many days of history to analyze
            min_value_usd: Minimum position value to include in calculations
            
        Returns:
            Dictionary with performance metrics
        """
        print(f"\n📊 Analyzing wallet: {wallet_address[:10]}...")
        
        # Get transaction history
        transactions = self.get_wallet_transactions(wallet_address)
        
        if not transactions:
            return {
                "success": False,
                "error": "No transactions found or API error",
                "wallet": wallet_address
            }
        
        # Filter transactions by time window
        cutoff_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp())
        relevant_txs = [
            tx for tx in transactions 
            if int(tx.get("timeStamp", 0)) >= cutoff_timestamp
        ]
        
        print(f"   Found {len(relevant_txs)} transactions in last {days_back} days")
        
        # Build token positions
        positions = self._build_token_positions(relevant_txs, wallet_address)
        
        # Calculate current value and cost basis
        total_cost_basis = 0
        total_current_value = 0
        position_details = []
        
        for token_address, position in positions.items():
            balance = position['balance']
            
            if balance <= 0:
                continue  # Skip sold positions
            
            # Get current price
            current_price = self.get_token_price(token_address)
            
            if not current_price or current_price == 0:
                continue
            
            # Calculate values
            decimals = int(position.get('decimals', 18))
            balance_float = balance / (10 ** decimals)
            current_value_usd = balance_float * current_price
            
            # Skip small positions
            if current_value_usd < min_value_usd:
                continue
            
            # Calculate average cost basis
            avg_buy_price = position['cost_basis'] / position['total_bought'] if position['total_bought'] > 0 else current_price
            cost_basis_usd = balance_float * avg_buy_price
            
            total_cost_basis += cost_basis_usd
            total_current_value += current_value_usd
            
            position_details.append({
                "token": position['symbol'],
                "address": token_address,
                "balance": balance_float,
                "entry_price": avg_buy_price,
                "current_price": current_price,
                "cost_basis_usd": cost_basis_usd,
                "current_value_usd": current_value_usd,
                "profit_usd": current_value_usd - cost_basis_usd,
                "roi_percent": ((current_value_usd - cost_basis_usd) / cost_basis_usd * 100) if cost_basis_usd > 0 else 0
            })
        
        # Calculate overall metrics
        if total_cost_basis == 0:
            return {
                "success": False,
                "error": "No significant positions found",
                "wallet": wallet_address
            }
        
        total_profit = total_current_value - total_cost_basis
        roi_percent = (total_profit / total_cost_basis) * 100
        
        # Calculate APY (annualized)
        apy = (roi_percent / days_back) * 365
        
        # Determine whale status
        is_whale = apy >= 100 and total_current_value >= 10000
        
        return {
            "success": True,
            "wallet": wallet_address,
            "performance": {
                "days_analyzed": days_back,
                "total_cost_basis_usd": total_cost_basis,
                "total_current_value_usd": total_current_value,
                "total_profit_usd": total_profit,
                "roi_percent": roi_percent,
                "apy_percent": apy,
                "is_whale": is_whale,
                "whale_score": min(apy, 1000)  # Cap at 1000% for scoring
            },
            "positions": sorted(position_details, key=lambda x: x['current_value_usd'], reverse=True),
            "transactions_analyzed": len(relevant_txs),
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_token_positions(self, transactions: List[Dict], wallet_address: str) -> Dict:
        """
        Build token positions from transaction history
        
        Args:
            transactions: List of transaction dictionaries
            wallet_address: The wallet address being analyzed
            
        Returns:
            Dictionary mapping token addresses to position data
        """
        positions = defaultdict(lambda: {
            'balance': 0,
            'total_bought': 0,
            'total_sold': 0,
            'cost_basis': 0,
            'symbol': '',
            'decimals': 18
        })
        
        wallet_lower = wallet_address.lower()
        
        for tx in transactions:
            token_address = tx.get("contractAddress", "").lower()
            from_address = tx.get("from", "").lower()
            to_address = tx.get("to", "").lower()
            value = int(tx.get("value", 0))
            decimals = int(tx.get("tokenDecimal", 18))
            symbol = tx.get("tokenSymbol", "UNKNOWN")
            
            # Update position metadata
            positions[token_address]['symbol'] = symbol
            positions[token_address]['decimals'] = decimals
            
            # Determine if this is a buy or sell from wallet's perspective
            if to_address == wallet_lower:
                # Incoming = Buy
                positions[token_address]['balance'] += value
                positions[token_address]['total_bought'] += value
                
                # Approximate cost basis (would need DEX price at time of tx for accuracy)
                # For now, we'll use a simplified approach
                # In production, you'd want to fetch historical prices
                positions[token_address]['cost_basis'] += value
                
            elif from_address == wallet_lower:
                # Outgoing = Sell
                positions[token_address]['balance'] -= value
                positions[token_address]['total_sold'] += value
        
        return dict(positions)
    
    def identify_whale_wallets(
        self,
        wallet_addresses: List[str],
        min_apy: float = 100,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Screen multiple wallets to identify whales with high performance
        
        Args:
            wallet_addresses: List of wallet addresses to screen
            min_apy: Minimum APY threshold (default 100%)
            days_back: Time period for analysis
            
        Returns:
            List of whale wallet dictionaries sorted by APY
        """
        print(f"\n🐋 Screening {len(wallet_addresses)} wallets for whale performance...")
        
        whales = []
        
        for i, wallet in enumerate(wallet_addresses, 1):
            print(f"\n[{i}/{len(wallet_addresses)}] Analyzing {wallet[:10]}...")
            
            result = self.calculate_wallet_performance(wallet, days_back=days_back)
            
            if result.get("success"):
                performance = result.get("performance", {})
                if performance.get("apy_percent", 0) >= min_apy:
                    whales.append({
                        "wallet": wallet,
                        "apy": performance["apy_percent"],
                        "roi": performance["roi_percent"],
                        "current_value": performance["total_current_value_usd"],
                        "profit": performance["total_profit_usd"],
                        "positions": result.get("positions", [])
                    })
                    print(f"   ✅ WHALE FOUND! APY: {performance['apy_percent']:.1f}%")
                else:
                    print(f"   ⏭️ Skip (APY: {performance.get('apy_percent', 0):.1f}%)")
            else:
                print(f"   ❌ Error: {result.get('error')}")
            
            # Rate limiting
            time.sleep(0.3)  # Respect Etherscan free tier (5 calls/sec)
        
        # Sort by APY descending
        whales_sorted = sorted(whales, key=lambda x: x['apy'], reverse=True)
        
        print(f"\n🎯 Found {len(whales_sorted)} whale wallets with >{min_apy}% APY")
        
        return whales_sorted


if __name__ == "__main__":
    # Example usage
    tracker = WhalePerformanceTracker()
    
    # Example: Analyze a known whale wallet (Vitalik Buterin's public address)
    test_wallet = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Verified whale wallet
    
    result = tracker.calculate_wallet_performance(
        wallet_address=test_wallet,
        days_back=30,
        min_value_usd=100
    )
    
    if result.get("success"):
        perf = result["performance"]
        print(f"\n{'='*60}")
        print(f"WALLET PERFORMANCE ANALYSIS")
        print(f"{'='*60}")
        print(f"Wallet: {result['wallet']}")
        print(f"Period: {perf['days_analyzed']} days")
        print(f"\n💰 FINANCIAL METRICS:")
        print(f"  Cost Basis:    ${perf['total_cost_basis_usd']:,.2f}")
        print(f"  Current Value: ${perf['total_current_value_usd']:,.2f}")
        print(f"  Profit:        ${perf['total_profit_usd']:,.2f}")
        print(f"  ROI:           {perf['roi_percent']:.2f}%")
        print(f"  APY:           {perf['apy_percent']:.2f}%")
        print(f"\n🐋 WHALE STATUS: {'YES ✅' if perf['is_whale'] else 'NO ❌'}")
        
        if result.get("positions"):
            print(f"\n📈 TOP POSITIONS:")
            for pos in result["positions"][:5]:
                print(f"  {pos['token']}: ${pos['current_value_usd']:,.2f} "
                      f"({pos['roi_percent']:+.1f}%)")
