# Sybil & Insider Detector

Advanced on-chain detection system for identifying Sybil attacks, bot networks, and insider trading patterns using multi-heuristic analysis, machine learning clustering, and transaction graph algorithms.

## 🎯 Overview

This skill combines multiple detection techniques to expose hidden manipulation:

- **Sybil Attack Detection**: Identify bot networks and coordinated wallets
- **Insider Trading Detection**: Catch pre-launch accumulation and suspicious timing
- **Bot Behavior Analysis**: Profile automated trading patterns
- **Transaction Graph Analysis**: Detect funding patterns and coordination
- **ML Clustering**: K-Means and DBSCAN for behavioral grouping

## 🔧 Installation

### Prerequisites

- Python 3.9+
- Ethereum RPC endpoint (Infura, Alchemy, or local node)

### Install Dependencies

```bash
pip install web3 scikit-learn numpy networkx python-louvain
```

### Environment Setup

```bash
export RPC_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
```

## 📦 Modules

### 1. Address Clustering (`address_clustering.py`)

Groups related addresses using multiple heuristics:

- **Common Input Ownership**: Co-occurring inputs in transactions
- **Change Address Detection**: Identifies change outputs
- **Funding Pattern Analysis**: Groups by common funding source
- **Temporal Correlation**: Finds synchronized activity
- **ML Clustering**: K-Means and DBSCAN behavioral grouping

### 2. Graph Analyzer (`graph_analyzer.py`)

Transaction network analysis:

- **Graph Construction**: Directed weighted transaction graph
- **Community Detection**: Louvain and Label Propagation algorithms
- **Centrality Metrics**: PageRank, betweenness, degree
- **Pattern Detection**: Star and chain network patterns
- **Flow Analysis**: Money flow tracing

### 3. Behavior Profiler (`behavior_profiler.py`)

Detailed behavioral pattern analysis:

- **Temporal Patterns**: Activity timing regularity
- **Gas Behavior**: Price variance and optimization scoring
- **Value Distribution**: Transaction size patterns
- **Contract Interactions**: DEX, lending protocol categorization
- **Anomaly Detection**: Isolation Forest for outliers

### 4. Insider Detector (`insider_detector.py`)

Insider trading pattern detection:

- **Pre-Launch Accumulation**: Coordinated buying before launches
- **Pre-Announcement Activity**: Volume spikes before news
- **Coordinated Buying**: Synchronized purchases
- **Whale Tracking**: Large holder identification

### 5. Detection Engine (`detector_engine.py`)

Main orchestration combining all modules:

- **Unified Pipeline**: Coordinates all detection methods
- **Threat Scoring**: Multi-factor confidence calculation
- **Report Generation**: JSON and text export formats
- **Alert System**: Configurable thresholds

## 🚀 Usage

### Basic Usage

```python
from web3 import Web3
from detector_engine import DetectorEngine
import os

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))

# Initialize engine
engine = DetectorEngine(w3)

# Analyze addresses
addresses = ['0x123...', '0x456...', '0x789...']
transactions = [...]  # Your transaction data

report = engine.analyze_addresses(
    addresses,
    transactions,
    start_block=18000000,
    end_block=18100000
)

# Export report
print(engine.export_report(report, format='text'))
```

### Address Clustering

```python
from address_clustering import AddressClustering

clusterer = AddressClustering(w3)

# Extract features
features = [
    clusterer.extract_address_features(addr, start_block, end_block)
    for addr in addresses
]

# Cluster by behavior
clusters = clusterer.cluster_by_behavior(
    features,
    algorithm='kmeans',
    n_clusters=10
)

# Check for Sybil clusters
for cluster in clusters:
    if cluster.cluster_type == 'sybil':
        print(f"🚨 Sybil cluster detected!")
        print(f"   Confidence: {cluster.confidence:.2%}")
        print(f"   Addresses: {len(cluster.addresses)}")
```

### Transaction Graph Analysis

```python
from graph_analyzer import GraphAnalyzer

analyzer = GraphAnalyzer(w3)

# Build graph
graph = analyzer.build_transaction_graph(transactions)

# Detect communities
communities = analyzer.detect_communities(algorithm='louvain')

# Find star patterns (funding hubs)
stars = analyzer.detect_star_patterns(min_connections=10)

for network in stars:
    print(f"Hub: {network.hub_address}")
    print(f"Connected: {len(network.addresses)}")
```

### Behavior Profiling

```python
from behavior_profiler import BehaviorProfiler

profiler = BehaviorProfiler(w3)

# Profile address
profile = profiler.profile_address(address, transactions)

if profile.is_anomalous:
    print(f"⚠️ Anomalous behavior detected!")
    print(f"   Score: {profile.anomaly_score:.2f}")
    print(f"   Reasons: {profile.anomaly_reasons}")
```

### Insider Trading Detection

```python
from insider_detector import InsiderDetector

detector = InsiderDetector(w3)

# Detect pre-launch accumulation
event = detector.detect_pre_launch_accumulation(
    token_address='0xTokenAddress',
    launch_block=18000000,
    lookback_blocks=1000
)

if event:
    print(f"🚨 Insider trading detected!")
    print(f"   Type: {event.event_type}")
    print(f"   Confidence: {event.confidence:.2%}")
    print(f"   Addresses: {len(event.addresses)}")
```

## 📊 Detection Methods

### Sybil Detection Indicators

- Low transaction count variance across cluster
- Similar activity patterns (synchronized timing)
- Common funding source (bulk-funded wallets)
- Coordinated activities within time windows
- Identical gas price patterns

### Bot Detection Indicators

- High activity regularity (low timing variance)
- Consistent gas pricing (optimization score)
- Identical transaction values
- Extremely high transaction frequency
- Activity concentrated in specific hours

### Insider Trading Indicators

- Pre-launch accumulation patterns
- Volume spikes before announcements
- Coordinated buying within time windows
- Abnormal timing before major events
- Unusual accumulation by multiple addresses

## 🔬 Feature Engineering

8-dimensional feature vectors for ML clustering:

1. **Transaction Count**: Total transactions
2. **Value Sent/Received**: ETH amounts
3. **Unique Counterparties**: Distinct addresses
4. **Average Transaction Value**: Mean value
5. **Activity Span**: Duration in days
6. **Gas Price Variance**: Price volatility
7. **Contract Interactions**: Smart contract calls

## 🎯 Classification Logic

### Sybil Cluster
- Transaction count variance < 5
- Average transaction count > 10
- Similar activity patterns

### Suspicious Cluster
- Activity span std deviation < 1 day
- Coordinated timing patterns

### Normal Cluster
- High variance in features
- Diverse behavior patterns

### Confidence Scoring
Based on intra-cluster pairwise distances:
```
confidence = 1.0 - (avg_distance / 10.0)
```

## 📈 Performance

- **Address Analysis**: ~1-2 seconds per address
- **Graph Construction**: ~5-10 seconds for 10,000 transactions
- **Clustering**: ~2-5 seconds for 1000 addresses
- **Full Report**: ~30-60 seconds for comprehensive analysis

## 🛡️ Security Considerations

- Uses real blockchain data (no simulations)
- Requires archive node for historical analysis
- Rate limiting recommended for RPC endpoints
- Confidence thresholds configurable per use case

## 🔧 Configuration

Adjust detection thresholds in `DetectorEngine`:

```python
engine = DetectorEngine(
    w3,
    sybil_threshold=0.6,    # 60% confidence minimum
    insider_threshold=0.7,   # 70% confidence minimum
    bot_threshold=0.5        # 50% confidence minimum
)
```

## 📝 Report Formats

### JSON Export
```json
{
  "report_id": "report_20260219_120000",
  "summary": {
    "total_threats": 5,
    "critical_threats": 1,
    "high_threats": 2
  },
  "detections": {
    "sybil": [...],
    "insider": [...],
    "bot": [...]
  }
}
```

### Text Export
```
==================================================
SYBIL & INSIDER DETECTOR - ANALYSIS REPORT
==================================================
Report ID: report_20260219_120000
Generated: 2026-02-19 12:00:00

SUMMARY
--------------------------------------------------
Addresses Analyzed: 100
Threats Detected: 5
  Critical: 1
  High: 2
```

## 🤝 Contributing

This skill is part of the SpoonOS ecosystem. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🔗 References

- GraphSense: Bitcoin & Blockchain Analytics
- Ethereum Address Clustering Research
- K-Means Clustering for Behavioral Analysis
- NetworkX Graph Algorithms
- Scikit-learn Machine Learning

## 🆘 Support

For issues or questions:
- Check SKILL.md for detailed examples
- Review test outputs in PULL.md
- Open GitHub issue with reproduction steps
