"""
Whale Wallet Copier - Main Orchestrator
Complete workflow: Identify whales → Monitor purchases → Generate alerts
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from whale_performance_tracker import WhalePerformanceTracker
from transaction_monitor import TransactionMonitor


class WhaleWalletCopier:
    """
    Main orchestrator for the Whale Wallet Copier system
    
    Complete Workflow:
    1. Screen wallets to identify high-performers (>100% APY)
    2. Monitor identified whales for new token purchases
    3. Generate real-time alerts with token analysis
    4. Provide actionable trading signals
    
    Use Cases:
    - Copy trading top performing wallets
    - Early detection of promising tokens
    - Whale activity intelligence
    - Portfolio strategy insights
    """
    
    def __init__(self, etherscan_api_key: Optional[str] = None):
        """
        Initialize the Whale Wallet Copier
        
        Args:
            etherscan_api_key: Etherscan API key (optional, for higher rate limits)
        """
        self.performance_tracker = WhalePerformanceTracker(etherscan_api_key)
        self.transaction_monitor = TransactionMonitor(etherscan_api_key)
        self.etherscan_api_key = etherscan_api_key
        
        # Whale database
        self.known_whales: List[Dict] = []
        
    def discover_whales_from_list(
        self,
        wallet_addresses: List[str],
        min_apy: float = 100,
        days_back: int = 30,
        min_portfolio_value: float = 10000
    ) -> List[Dict]:
        """
        Screen a list of wallets to discover high-performing whales
        
        Args:
            wallet_addresses: List of wallet addresses to screen
            min_apy: Minimum APY threshold (default 100%)
            days_back: Analysis time period (default 30 days)
            min_portfolio_value: Minimum portfolio value in USD
            
        Returns:
            List of identified whale dictionaries
        """
        print(f"\n{'='*70}")
        print(f"WHALE DISCOVERY PHASE")
        print(f"{'='*70}")
        print(f"Screening: {len(wallet_addresses)} wallets")
        print(f"Criteria:  APY >{min_apy}%, Portfolio >${min_portfolio_value:,.0f}")
        print(f"Period:    Last {days_back} days")
        print(f"{'='*70}\n")
        
        whales = []
        
        for i, wallet in enumerate(wallet_addresses, 1):
            print(f"\n[{i}/{len(wallet_addresses)}] Analyzing {wallet}...")
            
            result = self.performance_tracker.calculate_wallet_performance(
                wallet_address=wallet,
                days_back=days_back,
                min_value_usd=1000
            )
            
            if result.get("success"):
                perf = result.get("performance", {})
                apy = perf.get("apy_percent", 0)
                current_value = perf.get("total_current_value_usd", 0)
                
                if apy >= min_apy and current_value >= min_portfolio_value:
                    whale_data = {
                        "wallet": wallet,
                        "apy": apy,
                        "roi": perf.get("roi_percent", 0),
                        "current_value_usd": current_value,
                        "profit_usd": perf.get("total_profit_usd", 0),
                        "positions": result.get("positions", []),
                        "discovered_at": datetime.now().isoformat(),
                        "days_analyzed": days_back
                    }
                    whales.append(whale_data)
                    
                    print(f"   ✅ WHALE IDENTIFIED!")
                    print(f"      APY: {apy:.1f}%")
                    print(f"      Value: ${current_value:,.0f}")
                    print(f"      Profit: ${perf.get('total_profit_usd', 0):,.0f}")
                else:
                    print(f"   ⏭️ Does not meet criteria (APY: {apy:.1f}%, Value: ${current_value:,.0f})")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            
            # Rate limiting
            time.sleep(0.3)
        
        # Sort by APY
        whales_sorted = sorted(whales, key=lambda x: x['apy'], reverse=True)
        
        # Update known whales
        self.known_whales = whales_sorted
        
        print(f"\n{'='*70}")
        print(f"✅ WHALE DISCOVERY COMPLETE")
        print(f"{'='*70}")
        print(f"Found: {len(whales_sorted)} qualifying whales")
        
        if whales_sorted:
            print(f"\nTop 5 Performers:")
            for i, whale in enumerate(whales_sorted[:5], 1):
                print(f"{i}. {whale['wallet'][:20]}... - APY: {whale['apy']:.1f}%")
        
        print(f"{'='*70}\n")
        
        return whales_sorted
    
    def start_monitoring(
        self,
        whale_wallets: Optional[List[str]] = None,
        check_interval: int = 60,
        duration_minutes: int = 1440,  # 24 hours default
        save_signals: bool = True
    ) -> List[Dict]:
        """
        Start monitoring whale wallets for new purchases
        
        Args:
            whale_wallets: List of whale addresses (uses known_whales if None)
            check_interval: Seconds between checks (default 60)
            duration_minutes: How long to monitor (default 24 hours)
            save_signals: Whether to save signals to file
            
        Returns:
            List of detected purchase signals
        """
        # Use provided wallets or known whales
        if whale_wallets is None:
            if not self.known_whales:
                print("❌ No whale wallets to monitor. Run discover_whales_from_list() first.")
                return []
            whale_wallets = [w['wallet'] for w in self.known_whales]
        
        print(f"\n{'='*70}")
        print(f"MONITORING PHASE")
        print(f"{'='*70}")
        print(f"Wallets:   {len(whale_wallets)} whales")
        print(f"Every:     {check_interval}s")
        print(f"Duration:  {duration_minutes} minutes")
        print(f"{'='*70}\n")
        
        # Start monitoring
        signals = self.transaction_monitor.monitor_whale_purchases(
            whale_wallets=whale_wallets,
            check_interval=check_interval,
            duration_minutes=duration_minutes
        )
        
        # Save signals to file
        if save_signals and signals:
            self.save_signals_to_file(signals)
        
        return signals
    
    def save_signals_to_file(self, signals: List[Dict], filename: Optional[str] = None):
        """
        Save trading signals to a JSON file
        
        Args:
            signals: List of signal dictionaries
            filename: Output filename (auto-generated if None)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"whale_signals_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(signals, f, indent=2)
            print(f"\n💾 Signals saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving signals: {e}")
    
    def save_whales_to_file(self, filename: str = "discovered_whales.json"):
        """
        Save discovered whales to a JSON file
        
        Args:
            filename: Output filename
        """
        if not self.known_whales:
            print("⚠️ No whales to save")
            return
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.known_whales, f, indent=2)
            print(f"\n💾 Whales saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Error saving whales: {e}")
    
    def load_whales_from_file(self, filename: str = "discovered_whales.json"):
        """
        Load previously discovered whales from file
        
        Args:
            filename: Input filename
        """
        try:
            with open(filename, 'r') as f:
                self.known_whales = json.load(f)
            print(f"\n📂 Loaded {len(self.known_whales)} whales from {filename}")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Error loading whales: {e}")
    
    def generate_report(self, signals: List[Dict]) -> str:
        """
        Generate a summary report of trading signals
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            Formatted report string
        """
        if not signals:
            return "No signals to report."
        
        # Group by token
        tokens = {}
        for signal in signals:
            token = signal.get("token_symbol", "UNKNOWN")
            if token not in tokens:
                tokens[token] = []
            tokens[token].append(signal)
        
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"WHALE TRADING SIGNALS REPORT")
        report.append(f"{'='*70}")
        report.append(f"Total Signals: {len(signals)}")
        report.append(f"Unique Tokens: {len(tokens)}")
        report.append(f"Period: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"{'='*70}\n")
        
        # Top tokens by whale interest
        token_counts = [(token, len(sigs)) for token, sigs in tokens.items()]
        token_counts.sort(key=lambda x: x[1], reverse=True)
        
        report.append("TOP TOKENS BY WHALE ACTIVITY:")
        report.append("-" * 70)
        for token, count in token_counts[:10]:
            example_signal = tokens[token][0]
            analysis = example_signal.get("analysis", {})
            price = analysis.get("price_usd", 0)
            safety = analysis.get("safety_rating", "UNKNOWN")
            
            report.append(f"\n{token}:")
            report.append(f"  Whale Purchases: {count}")
            report.append(f"  Current Price: ${price:.8f}")
            report.append(f"  Safety Rating: {safety}")
            report.append(f"  Address: {example_signal.get('token_address', 'N/A')}")
        
        report.append(f"\n{'='*70}\n")
        
        return "\n".join(report)
    
    def quick_start(
        self,
        sample_wallets: List[str],
        monitor_duration: int = 60
    ):
        """
        Quick start workflow: discover whales → monitor → report
        
        Args:
            sample_wallets: List of wallet addresses to screen
            monitor_duration: How long to monitor (minutes)
        """
        print(f"\n🚀 WHALE WALLET COPIER - QUICK START")
        print(f"{'='*70}\n")
        
        # Step 1: Discover whales
        print("Step 1/3: Discovering whales...")
        whales = self.discover_whales_from_list(
            wallet_addresses=sample_wallets,
            min_apy=100,
            days_back=30
        )
        
        if not whales:
            print("\n❌ No whales found meeting criteria. Try different wallets or lower thresholds.")
            return
        
        # Save whales
        self.save_whales_to_file()
        
        # Step 2: Monitor
        print(f"\nStep 2/3: Monitoring {len(whales)} whales for {monitor_duration} minutes...")
        signals = self.start_monitoring(
            check_interval=60,
            duration_minutes=monitor_duration,
            save_signals=True
        )
        
        # Step 3: Report
        print("\nStep 3/3: Generating report...")
        report = self.generate_report(signals)
        print(report)
        
        print(f"\n✅ Quick start complete!")
        print(f"   Whales discovered: {len(whales)}")
        print(f"   Signals detected: {len(signals)}")


if __name__ == "__main__":
    # Example usage - Full workflow
    copier = WhaleWalletCopier(etherscan_api_key="YourEtherscanAPIKey")
    
    # Example 1: Quick start with sample wallets
    sample_wallets = [
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  # Example wallet
        "0x220866B1A2219f40e72f5c628B65D54268cA3A9D",  # Example wallet 2
        # Add more wallets to screen
    ]
    
    # Run quick start (discover + monitor for 30 minutes)
    copier.quick_start(
        sample_wallets=sample_wallets,
        monitor_duration=30  # Monitor for 30 minutes
    )
    
    # Example 2: Manual workflow
    # Step 1: Discover whales
    # whales = copier.discover_whales_from_list(
    #     wallet_addresses=sample_wallets,
    #     min_apy=100,
    #     days_back=30
    # )
    #
    # # Step 2: Save whales to file
    # copier.save_whales_to_file("my_whales.json")
    #
    # # Step 3: Monitor specific whales
    # signals = copier.start_monitoring(
    #     whale_wallets=[w['wallet'] for w in whales[:5]],  # Monitor top 5
    #     check_interval=120,  # Every 2 minutes
    #     duration_minutes=60  # For 1 hour
    # )
    #
    # # Step 4: Generate report
    # report = copier.generate_report(signals)
    # print(report)
