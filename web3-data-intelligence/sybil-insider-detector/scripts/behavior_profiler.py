"""
Behavior Profiling Module - Sybil & Insider Detector

Detailed behavioral pattern analysis:
- Temporal Activity Patterns
- Gas Price Behavior Analysis
- Transaction Value Distribution
- Contract Interaction Patterns
- Anomaly Detection

REAL IMPLEMENTATION - No Mocks/Simulations
Uses sklearn for anomaly detection
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import numpy as np
from web3 import Web3
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BehaviorProfile:
    """Comprehensive behavior profile for an address"""
    address: str
    
    # Temporal patterns
    activity_hours: Counter = field(default_factory=Counter)
    activity_days: Counter = field(default_factory=Counter)
    avg_tx_per_day: float = 0.0
    activity_regularity_score: float = 0.0
    
    # Gas behavior
    avg_gas_price: float = 0.0
    gas_price_variance: float = 0.0
    uses_dynamic_gas: bool = False
    gas_optimization_score: float = 0.0
    
    # Value patterns
    avg_value: float = 0.0
    median_value: float = 0.0
    value_variance: float = 0.0
    large_tx_count: int = 0
    small_tx_count: int = 0
    
    # Interaction patterns
    contract_calls: int = 0
    eoa_transfers: int = 0
    unique_contracts: Set[str] = field(default_factory=set)
    unique_eoas: Set[str] = field(default_factory=set)
    dex_interactions: int = 0
    lending_interactions: int = 0
    
    # Anomaly indicators
    anomaly_score: float = 0.0
    is_anomalous: bool = False
    anomaly_reasons: List[str] = field(default_factory=list)


@dataclass
class PatternSignature:
    """Bot/Sybil pattern signature"""
    pattern_id: str
    addresses: Set[str]
    pattern_type: str  # 'bot', 'flash_loan', 'mev', 'wash_trading'
    confidence: float
    characteristics: Dict[str, any]
    detection_time: datetime = field(default_factory=datetime.now)


class BehaviorProfiler:
    """
    Analyzes wallet behavior patterns to detect bots and suspicious activity
    """
    
    def __init__(self, w3: Web3):
        """
        Initialize behavior profiler
        
        Args:
            w3: Web3 instance
        """
        self.w3 = w3
        self.profiles: Dict[str, BehaviorProfile] = {}
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
        # Known contract categorizations (simplified)
        self.dex_contracts = {
            '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',  # Uniswap V2 Router
            '0xe592427a0aece92de3edee1f18e0157c05861564',  # Uniswap V3 Router
        }
        
        self.lending_contracts = {
            '0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9',  # AAVE V2
            '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2',  # AAVE V3
        }
    
    def profile_address(
        self,
        address: str,
        transactions: List[Dict],
        start_block: Optional[int] = None,
        end_block: Optional[int] = None
    ) -> BehaviorProfile:
        """
        Create comprehensive behavior profile
        
        Args:
            address: Address to profile
            transactions: Transaction history
            start_block: Optional start block
            end_block: Optional end block
            
        Returns:
            BehaviorProfile object
        """
        logger.info(f"Profiling address: {address}")
        
        address = address.lower()
        profile = BehaviorProfile(address=address)
        
        if not transactions:
            logger.warning(f"No transactions for {address}")
            return profile
        
        # Analyze temporal patterns
        self._analyze_temporal_patterns(profile, transactions)
        
        # Analyze gas behavior
        self._analyze_gas_behavior(profile, transactions)
        
        # Analyze value patterns
        self._analyze_value_patterns(profile, transactions)
        
        # Analyze interactions
        self._analyze_interactions(profile, transactions)
        
        # Calculate anomaly score
        self._detect_anomalies(profile)
        
        self.profiles[address] = profile
        return profile
    
    def _analyze_temporal_patterns(
        self,
        profile: BehaviorProfile,
        transactions: List[Dict]
    ):
        """Analyze timing patterns"""
        timestamps = []
        
        for tx in transactions:
            ts = tx.get('timestamp')
            if ts:
                timestamps.append(ts)
                dt = datetime.fromtimestamp(ts)
                profile.activity_hours[dt.hour] += 1
                profile.activity_days[dt.weekday()] += 1
        
        if not timestamps:
            return
        
        # Calculate activity regularity
        timestamps_sorted = sorted(timestamps)
        if len(timestamps_sorted) > 1:
            intervals = [
                timestamps_sorted[i+1] - timestamps_sorted[i]
                for i in range(len(timestamps_sorted) - 1)
            ]
            
            # Low variance in intervals suggests automated behavior
            interval_variance = np.var(intervals)
            
            # Regularity score (0-1, higher = more regular)
            if interval_variance < 60:  # < 1 minute variance
                profile.activity_regularity_score = 0.9
            elif interval_variance < 600:  # < 10 minutes
                profile.activity_regularity_score = 0.7
            elif interval_variance < 3600:  # < 1 hour
                profile.activity_regularity_score = 0.5
            else:
                profile.activity_regularity_score = 0.2
            
            # Average transactions per day
            time_span_days = (timestamps_sorted[-1] - timestamps_sorted[0]) / 86400
            if time_span_days > 0:
                profile.avg_tx_per_day = len(transactions) / time_span_days
    
    def _analyze_gas_behavior(
        self,
        profile: BehaviorProfile,
        transactions: List[Dict]
    ):
        """Analyze gas price patterns"""
        gas_prices = []
        
        for tx in transactions:
            gas_price = tx.get('gasPrice', 0)
            if gas_price:
                gas_prices.append(float(gas_price) / 1e9)  # Convert to Gwei
        
        if not gas_prices:
            return
        
        profile.avg_gas_price = np.mean(gas_prices)
        profile.gas_price_variance = np.var(gas_prices)
        
        # Check if uses dynamic gas pricing
        unique_gas_prices = len(set(gas_prices))
        profile.uses_dynamic_gas = unique_gas_prices > len(gas_prices) * 0.5
        
        # Gas optimization score
        # Bots tend to use consistent gas prices
        if profile.gas_price_variance < 1.0:
            profile.gas_optimization_score = 0.9
        elif profile.gas_price_variance < 5.0:
            profile.gas_optimization_score = 0.6
        else:
            profile.gas_optimization_score = 0.3
    
    def _analyze_value_patterns(
        self,
        profile: BehaviorProfile,
        transactions: List[Dict]
    ):
        """Analyze transaction value distribution"""
        values = []
        
        for tx in transactions:
            value = float(tx.get('value', 0))
            if value > 0:
                values.append(value)
        
        if not values:
            return
        
        profile.avg_value = np.mean(values)
        profile.median_value = np.median(values)
        profile.value_variance = np.var(values)
        
        # Count large vs small transactions
        median = profile.median_value
        profile.large_tx_count = sum(1 for v in values if v > median * 10)
        profile.small_tx_count = sum(1 for v in values if v < median / 10)
    
    def _analyze_interactions(
        self,
        profile: BehaviorProfile,
        transactions: List[Dict]
    ):
        """Analyze contract and EOA interactions"""
        for tx in transactions:
            to_addr = tx.get('to', '').lower()
            
            if not to_addr:
                continue
            
            # Check if contract or EOA
            try:
                code = self.w3.eth.get_code(Web3.to_checksum_address(to_addr))
                is_contract = len(code) > 0
            except:
                is_contract = False
            
            if is_contract:
                profile.contract_calls += 1
                profile.unique_contracts.add(to_addr)
                
                # Categorize contract
                if to_addr in self.dex_contracts:
                    profile.dex_interactions += 1
                elif to_addr in self.lending_contracts:
                    profile.lending_interactions += 1
            else:
                profile.eoa_transfers += 1
                profile.unique_eoas.add(to_addr)
    
    def _detect_anomalies(self, profile: BehaviorProfile):
        """Detect anomalous patterns"""
        anomaly_reasons = []
        
        # Check for bot indicators
        if profile.activity_regularity_score > 0.8:
            anomaly_reasons.append("Highly regular activity pattern")
        
        if profile.gas_optimization_score > 0.8 and profile.uses_dynamic_gas is False:
            anomaly_reasons.append("Consistent gas pricing (bot-like)")
        
        if profile.value_variance < 0.01 and profile.avg_value > 0:
            anomaly_reasons.append("Identical transaction values")
        
        if profile.avg_tx_per_day > 100:
            anomaly_reasons.append("Extremely high transaction frequency")
        
        # Check hour distribution
        if len(profile.activity_hours) > 0:
            max_hour_count = max(profile.activity_hours.values())
            total_txs = sum(profile.activity_hours.values())
            
            if max_hour_count / total_txs > 0.8:
                anomaly_reasons.append("Activity concentrated in single hour")
        
        # Set anomaly flag
        profile.anomaly_score = len(anomaly_reasons) / 5.0  # Normalize
        profile.is_anomalous = profile.anomaly_score > 0.4
        profile.anomaly_reasons = anomaly_reasons
    
    def detect_bot_patterns(
        self,
        profiles: Optional[List[BehaviorProfile]] = None
    ) -> List[PatternSignature]:
        """
        Detect bot patterns across profiles
        
        Args:
            profiles: Profiles to analyze (or use cached)
            
        Returns:
            List of pattern signatures
        """
        logger.info("Detecting bot patterns")
        
        if profiles is None:
            profiles = list(self.profiles.values())
        
        if not profiles:
            logger.warning("No profiles to analyze")
            return []
        
        patterns = []
        
        # Group by similar characteristics
        high_frequency_bots = [
            p for p in profiles
            if p.avg_tx_per_day > 50 and p.activity_regularity_score > 0.7
        ]
        
        if high_frequency_bots:
            patterns.append(PatternSignature(
                pattern_id='bot_high_freq',
                addresses={p.address for p in high_frequency_bots},
                pattern_type='bot',
                confidence=0.85,
                characteristics={
                    'avg_tx_per_day': np.mean([p.avg_tx_per_day for p in high_frequency_bots]),
                    'regularity': np.mean([p.activity_regularity_score for p in high_frequency_bots])
                }
            ))
        
        # MEV bot detection
        mev_bots = [
            p for p in profiles
            if p.gas_price_variance > 50 and p.contract_calls > p.eoa_transfers * 2
        ]
        
        if mev_bots:
            patterns.append(PatternSignature(
                pattern_id='mev_bot',
                addresses={p.address for p in mev_bots},
                pattern_type='mev',
                confidence=0.75,
                characteristics={
                    'avg_gas_variance': np.mean([p.gas_price_variance for p in mev_bots]),
                    'contract_call_ratio': np.mean([
                        p.contract_calls / max(p.eoa_transfers, 1) for p in mev_bots
                    ])
                }
            ))
        
        # Wash trading detection
        wash_traders = [
            p for p in profiles
            if len(p.unique_eoas) < 5 and p.eoa_transfers > 20
        ]
        
        if wash_traders:
            patterns.append(PatternSignature(
                pattern_id='wash_trading',
                addresses={p.address for p in wash_traders},
                pattern_type='wash_trading',
                confidence=0.70,
                characteristics={
                    'avg_unique_counterparties': np.mean([len(p.unique_eoas) for p in wash_traders]),
                    'avg_transfers': np.mean([p.eoa_transfers for p in wash_traders])
                }
            ))
        
        logger.info(f"Detected {len(patterns)} pattern types")
        return patterns
    
    def compare_profiles(
        self,
        profile1: BehaviorProfile,
        profile2: BehaviorProfile
    ) -> float:
        """
        Calculate similarity between two profiles
        
        Args:
            profile1: First profile
            profile2: Second profile
            
        Returns:
            Similarity score (0-1)
        """
        similarities = []
        
        # Temporal similarity
        if profile1.activity_regularity_score > 0 and profile2.activity_regularity_score > 0:
            temporal_sim = 1.0 - abs(
                profile1.activity_regularity_score - profile2.activity_regularity_score
            )
            similarities.append(temporal_sim)
        
        # Gas behavior similarity
        if profile1.avg_gas_price > 0 and profile2.avg_gas_price > 0:
            gas_diff = abs(profile1.avg_gas_price - profile2.avg_gas_price)
            gas_sim = 1.0 / (1.0 + gas_diff / 10.0)
            similarities.append(gas_sim)
        
        # Value pattern similarity
        if profile1.avg_value > 0 and profile2.avg_value > 0:
            value_ratio = min(profile1.avg_value, profile2.avg_value) / max(
                profile1.avg_value, profile2.avg_value
            )
            similarities.append(value_ratio)
        
        # Interaction pattern similarity
        interaction_sim = (
            (profile1.contract_calls > 0 and profile2.contract_calls > 0) or
            (profile1.contract_calls == 0 and profile2.contract_calls == 0)
        )
        similarities.append(1.0 if interaction_sim else 0.5)
        
        # Overall similarity
        return np.mean(similarities) if similarities else 0.0
    
    def batch_anomaly_detection(
        self,
        profiles: Optional[List[BehaviorProfile]] = None
    ) -> List[BehaviorProfile]:
        """
        Use Isolation Forest for batch anomaly detection
        
        Args:
            profiles: Profiles to analyze
            
        Returns:
            List of anomalous profiles
        """
        logger.info("Running batch anomaly detection")
        
        if profiles is None:
            profiles = list(self.profiles.values())
        
        if len(profiles) < 2:
            logger.warning("Need at least 2 profiles for batch detection")
            return []
        
        # Extract features
        features = []
        for p in profiles:
            features.append([
                p.activity_regularity_score,
                p.avg_tx_per_day,
                p.gas_price_variance,
                p.value_variance,
                float(p.contract_calls) / max(p.eoa_transfers, 1),
                len(p.unique_contracts),
                len(p.unique_eoas)
            ])
        
        X = np.array(features)
        
        # Fit and predict
        predictions = self.isolation_forest.fit_predict(X)
        
        # Return anomalous profiles (prediction = -1)
        anomalous = [
            profiles[i] for i, pred in enumerate(predictions)
            if pred == -1
        ]
        
        logger.info(f"Found {len(anomalous)} anomalous profiles")
        return anomalous


def main():
    """Example usage"""
    import os
    
    # Connect to Ethereum
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL environment variable must be set")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    print(f"Connected to: {rpc_url}")
    print(f"Block: {w3.eth.block_number}\n")
    
    print("=" * 70)
    print("BEHAVIOR PROFILER")
    print("=" * 70)
    print("✅ Profiler initialized\n")
    
    # Initialize profiler
    profiler = BehaviorProfiler(w3)
    
    # Example transactions (mock for demonstration)
    example_txs = [
        {
            'from': '0xa',
            'to': '0xb',
            'value': 1.0,
            'gasPrice': 50000000000,
            'timestamp': 1000000
        },
        {
            'from': '0xa',
            'to': '0xc',
            'value': 1.0,
            'gasPrice': 50000000000,
            'timestamp': 1000100
        },
        {
            'from': '0xa',
            'to': '0xd',
            'value': 1.0,
            'gasPrice': 50000000000,
            'timestamp': 1000200
        },
    ] * 10  # Repeat for pattern
    
    print("=" * 70)
    print("EXAMPLE: Profile Address Behavior")
    print("=" * 70)
    
    profile = profiler.profile_address('0xa', example_txs)
    
    print(f"\n✅ Profile created for: {profile.address}")
    print(f"\nTemporal Patterns:")
    print(f"  Activity regularity: {profile.activity_regularity_score:.2f}")
    print(f"  Avg tx/day: {profile.avg_tx_per_day:.1f}")
    
    print(f"\nGas Behavior:")
    print(f"  Avg gas price: {profile.avg_gas_price:.1f} Gwei")
    print(f"  Gas variance: {profile.gas_price_variance:.2f}")
    print(f"  Gas optimization score: {profile.gas_optimization_score:.2f}")
    
    print(f"\nValue Patterns:")
    print(f"  Avg value: {profile.avg_value:.4f} ETH")
    print(f"  Median value: {profile.median_value:.4f} ETH")
    
    print(f"\nAnomaly Detection:")
    print(f"  Anomaly score: {profile.anomaly_score:.2f}")
    print(f"  Is anomalous: {profile.is_anomalous}")
    if profile.anomaly_reasons:
        print(f"  Reasons:")
        for reason in profile.anomaly_reasons:
            print(f"    - {reason}")
    
    print("\n" + "=" * 70)
    print("✅ Example complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
