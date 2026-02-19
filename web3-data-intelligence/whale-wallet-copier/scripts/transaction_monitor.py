"""
Whale Wallet Transaction Monitor
Real-time monitoring of whale wallet transactions and new token purchases
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict


class TransactionMonitor:
    """
    Monitors whale wallets for new token purchases in real-time
    
    Features:
    - Tracks recent transactions for specified wallets
    - Detects new token purchases (buy signals)
    - Filters out sells, transfers, and spam tokens
    - Provides actionable trade signals
    - Identifies token metadata (name, symbol, price, liquidity)
    """
    
    def __init__(self, etherscan_api_key: Optional[str] = None):
        """
        Initialize the transaction monitor
        
        Args:
            etherscan_api_key: Etherscan API key for transaction queries
        """
        self.etherscan_api_key = etherscan_api_key or "S61W6QK13ZPENIB91MKQ669MAZQS5WH552"
        self.etherscan_api = "https://api.etherscan.io/v2/api"
        self.dexscreener_api = "https://api.dexscreener.com"
        self.session = requests.Session()
        
        # Track last seen transactions to avoid duplicates
        self.last_seen_tx: Dict[str, str] = {}  # wallet -> last tx hash
        
        # Known tokens to filter spam
        self.known_stable_tokens = {
            "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
            "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",
            "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "WBTC"
        }
        
    def get_recent_transactions(
        self,
        wallet_address: str,
        minutes_back: int = 30
    ) -> List[Dict]:
        """
        Get recent token transactions for a wallet
        
        Args:
            wallet_address: Wallet address to monitor
            minutes_back: How many minutes of history to fetch
            
        Returns:
            List of recent transaction dictionaries
        """
        try:
            params = {
                "chainid": 1,  # Ethereum mainnet
                "module": "account",
                "action": "tokentx",
                "address": wallet_address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            
            response = self.session.get(self.etherscan_api, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "1":
                return []
            
            transactions = data.get("result", [])
            
            # Filter by time
            cutoff_timestamp = int((datetime.now() - timedelta(minutes=minutes_back)).timestamp())
            recent_txs = [
                tx for tx in transactions
                if int(tx.get("timeStamp", 0)) >= cutoff_timestamp
            ]
            
            return recent_txs
            
        except Exception as e:
            print(f"❌ Error fetching transactions for {wallet_address[:10]}: {e}")
            return []
    
    def detect_new_purchases(
        self,
        wallet_address: str,
        transactions: List[Dict]
    ) -> List[Dict]:
        """
        Detect new token purchases from transaction list
        
        Args:
            wallet_address: The wallet being monitored
            transactions: List of recent transactions
            
        Returns:
            List of purchase event dictionaries
        """
        purchases = []
        wallet_lower = wallet_address.lower()
        
        for tx in transactions:
            # Check if this is an incoming transaction (purchase)
            to_address = tx.get("to", "").lower()
            from_address = tx.get("from", "").lower()
            
            if to_address != wallet_lower:
                continue  # Not incoming to this wallet
            
            # Skip if it's from the wallet itself (internal transfer)
            if from_address == wallet_lower:
                continue
            
            # Extract token info
            token_address = tx.get("contractAddress", "").lower()
            token_symbol = tx.get("tokenSymbol", "UNKNOWN")
            token_name = tx.get("tokenName", "Unknown Token")
            value = int(tx.get("value", 0))
            decimals = int(tx.get("tokenDecimal", 18))
            tx_hash = tx.get("hash", "")
            timestamp = int(tx.get("timeStamp", 0))
            
            # Skip stablecoins and major tokens (not interesting for copy trading)
            if token_address in self.known_stable_tokens:
                continue
            
            # Skip very small amounts (likely spam)
            value_float = value / (10 ** decimals)
            if value_float < 0.01:  # Less than 0.01 tokens
                continue
            
            # Check if we've seen this transaction before
            last_tx = self.last_seen_tx.get(wallet_address, "")
            if tx_hash == last_tx:
                break  # Stop processing, we've reached previously seen transactions
            
            purchases.append({
                "wallet": wallet_address,
                "token_address": token_address,
                "token_symbol": token_symbol,
                "token_name": token_name,
                "amount": value_float,
                "decimals": decimals,
                "tx_hash": tx_hash,
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Update last seen transaction
        if transactions:
            self.last_seen_tx[wallet_address] = transactions[0].get("hash", "")
        
        return purchases
    
    def get_token_analysis(self, token_address: str) -> Optional[Dict]:
        """
        Get detailed token analysis (price, liquidity, safety metrics)
        
        Args:
            token_address: Token contract address
            
        Returns:
            Dictionary with token analysis or None
        """
        try:
            url = f"{self.dexscreener_api}/latest/dex/tokens/{token_address}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            pairs = data.get("pairs", [])
            
            if not pairs:
                return None
            
            # Get the pair with highest liquidity
            best_pair = max(pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0))
            
            liquidity_usd = best_pair.get("liquidity", {}).get("usd", 0)
            price_usd = float(best_pair.get("priceUsd", 0))
            price_change_5m = best_pair.get("priceChange", {}).get("m5", 0)
            price_change_1h = best_pair.get("priceChange", {}).get("h1", 0)
            price_change_24h = best_pair.get("priceChange", {}).get("h24", 0)
            volume_24h = best_pair.get("volume", {}).get("h24", 0)
            fdv = best_pair.get("fdv", 0)
            market_cap = best_pair.get("marketCap", 0)
            
            # Calculate safety score
            safety_score = self._calculate_token_safety(
                liquidity_usd, volume_24h, market_cap, price_change_24h
            )
            
            return {
                "token_address": token_address,
                "pair_address": best_pair.get("pairAddress", ""),
                "dex": best_pair.get("dexId", ""),
                "price_usd": price_usd,
                "liquidity_usd": liquidity_usd,
                "volume_24h": volume_24h,
                "market_cap": market_cap,
                "fdv": fdv,
                "price_change": {
                    "5m": price_change_5m,
                    "1h": price_change_1h,
                    "24h": price_change_24h
                },
                "safety_score": safety_score,
                "safety_rating": self._get_safety_rating(safety_score),
                "url": best_pair.get("url", "")
            }
            
        except Exception as e:
            print(f"⚠️ Error analyzing token {token_address[:10]}: {e}")
            return None
    
    def _calculate_token_safety(
        self,
        liquidity: float,
        volume_24h: float,
        market_cap: float,
        price_change_24h: float
    ) -> int:
        """
        Calculate a safety score (0-100) for a token
        
        Args:
            liquidity: Token liquidity in USD
            volume_24h: 24h trading volume
            market_cap: Market capitalization
            price_change_24h: 24h price change percentage
            
        Returns:
            Safety score (0-100)
        """
        score = 0
        
        # Liquidity score (0-40 points)
        if liquidity >= 1_000_000:
            score += 40
        elif liquidity >= 500_000:
            score += 35
        elif liquidity >= 100_000:
            score += 25
        elif liquidity >= 50_000:
            score += 15
        elif liquidity >= 10_000:
            score += 5
        
        # Volume score (0-25 points)
        if volume_24h >= 1_000_000:
            score += 25
        elif volume_24h >= 500_000:
            score += 20
        elif volume_24h >= 100_000:
            score += 15
        elif volume_24h >= 50_000:
            score += 10
        elif volume_24h >= 10_000:
            score += 5
        
        # Market cap score (0-20 points)
        if market_cap >= 10_000_000:
            score += 20
        elif market_cap >= 5_000_000:
            score += 15
        elif market_cap >= 1_000_000:
            score += 10
        elif market_cap >= 100_000:
            score += 5
        
        # Price stability score (0-15 points)
        abs_change = abs(price_change_24h) if price_change_24h else 0
        if abs_change < 10:
            score += 15
        elif abs_change < 25:
            score += 10
        elif abs_change < 50:
            score += 5
        
        return min(score, 100)
    
    def _get_safety_rating(self, score: int) -> str:
        """Convert safety score to rating"""
        if score >= 80:
            return "SAFE"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "RISKY"
        else:
            return "HIGH RISK"
    
    def monitor_whale_purchases(
        self,
        whale_wallets: List[str],
        check_interval: int = 60,
        duration_minutes: int = 30
    ) -> List[Dict]:
        """
        Monitor multiple whale wallets for new purchases
        
        Args:
            whale_wallets: List of whale wallet addresses to monitor
            check_interval: Seconds between checks (default 60)
            duration_minutes: How long to monitor (default 30 min)
            
        Returns:
            List of detected purchase signals
        """
        print(f"\n🔍 Monitoring {len(whale_wallets)} whale wallets...")
        print(f"   Check interval: {check_interval}s")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Press Ctrl+C to stop\n")
        
        all_signals = []
        checks_remaining = (duration_minutes * 60) // check_interval
        
        try:
            for check_num in range(checks_remaining):
                print(f"[Check {check_num + 1}/{checks_remaining}] {datetime.now().strftime('%H:%M:%S')}")
                
                for wallet in whale_wallets:
                    # Get recent transactions
                    txs = self.get_recent_transactions(wallet, minutes_back=check_interval // 60 + 5)
                    
                    # Detect purchases
                    purchases = self.detect_new_purchases(wallet, txs)
                    
                    for purchase in purchases:
                        # Analyze the token
                        token_analysis = self.get_token_analysis(purchase["token_address"])
                        
                        if token_analysis:
                            signal = {
                                **purchase,
                                "analysis": token_analysis,
                                "detected_at": datetime.now().isoformat()
                            }
                            all_signals.append(signal)
                            
                            # Print alert
                            self._print_purchase_alert(signal)
                    
                    time.sleep(0.3)  # Rate limiting
                
                if check_num < checks_remaining - 1:
                    time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
        
        return all_signals
    
    def _print_purchase_alert(self, signal: Dict):
        """Print a formatted purchase alert"""
        purchase = signal
        analysis = signal.get("analysis", {})
        
        print(f"\n{'='*70}")
        print(f"🐋 WHALE PURCHASE DETECTED!")
        print(f"{'='*70}")
        print(f"Time:      {purchase['datetime']}")
        print(f"Wallet:    {purchase['wallet'][:20]}...")
        print(f"Token:     {purchase['token_symbol']} ({purchase['token_name']})")
        print(f"Amount:    {purchase['amount']:,.4f} {purchase['token_symbol']}")
        print(f"Tx:        https://etherscan.io/tx/{purchase['tx_hash']}")
        
        if analysis:
            print(f"\n📊 TOKEN ANALYSIS:")
            print(f"   Price:     ${analysis.get('price_usd', 0):.8f}")
            print(f"   Liquidity: ${analysis.get('liquidity_usd', 0):,.0f}")
            print(f"   24h Vol:   ${analysis.get('volume_24h', 0):,.0f}")
            print(f"   Market Cap: ${analysis.get('market_cap', 0):,.0f}")
            print(f"   24h Change: {analysis.get('price_change', {}).get('24h', 0):,.1f}%")
            print(f"   Safety:    {analysis.get('safety_score', 0)}/100 ({analysis.get('safety_rating', 'UNKNOWN')})")
            print(f"   Chart:     {analysis.get('url', 'N/A')}")
        
        print(f"{'='*70}\n")


if __name__ == "__main__":
    # Example usage
    monitor = TransactionMonitor()
    
    # Example whale wallets (replace with real addresses)
    whale_wallets = [
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  # Example whale
        # Add more whale addresses here
    ]
    
    # Monitor for 10 minutes, checking every 30 seconds
    signals = monitor.monitor_whale_purchases(
        whale_wallets=whale_wallets,
        check_interval=30,
        duration_minutes=10
    )
    
    print(f"\n✅ Monitoring complete. Detected {len(signals)} purchase signals.")
