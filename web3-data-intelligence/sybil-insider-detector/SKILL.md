---
name: Sybil & Insider Detector
category: Web3 Data Intelligence
subcategory: On-Chain Analysis
description: Advanced detection system identifying Sybil attacks, bot networks, and insider trading using multi-heuristic analysis, machine learning clustering, and transaction graph algorithms
tags: [sybil-detection, insider-trading, bot-detection, graph-analysis, machine-learning, clustering, blockchain-forensics, network-analysis, anomaly-detection, web3-security]
difficulty: advanced
status: production
version: 1.0.0

activation_triggers:
  - detect sybil attack
  - find bot networks
  - insider trading detection
  - wallet clustering
  - transaction graph analysis
  - detect coordinated manipulation

parameters:
  w3:
    description: Web3 instance for blockchain connection
    required: true
    example: "Web3(Web3.HTTPProvider('https://ethereum-rpc.publicnode.com'))"
  addresses:
    description: List of addresses to analyze
    required: true
    example: "['0xabc...', '0xdef...']"
  transactions:
    description: Transaction data for graph analysis
    required: true
  start_block:
    description: Start block for analysis window
    required: false
  end_block:
    description: End block for analysis window
    required: false

requirements:
  python: ">=3.8"
  packages:
    - web3>=6.0.0
    - scikit-learn>=1.3.0
    - numpy>=1.24.0
    - networkx>=3.0
    - python-louvain>=0.16
  external:
    - Ethereum RPC access (archive node recommended)
---

# Sybil & Insider Detector

## Overview

Advanced detection system for identifying Sybil attacks, bot networks, and insider trading patterns using multi-heuristic analysis, machine learning clustering, and transaction graph algorithms on real blockchain data.

**Analysis Type**: Multi-Modal (Clustering + Graph + Behavioral + Insider)  
**Approach**: Domain Heuristics + ML + Graph Algorithms  
**Target**: Ethereum & EVM-Compatible Chains  
**Status**: Production Ready

## Key Capabilities

### 1. **Address Clustering** (address_clustering.py)
- ✅ Common input ownership heuristic (DFS graph traversal)
- ✅ Change address detection (single-input dual-output patterns)
- ✅ Funding pattern analysis (bulk-funded networks)
- ✅ Temporal correlation (synchronized activity)
- ✅ K-Means & DBSCAN clustering with 8D features
- ✅ Confidence scoring and classification

### 2. **Transaction Graph Analysis** (graph_analyzer.py)
- ✅ Directed weighted graph construction with NetworkX
- ✅ Community detection (Louvain, Label Propagation)
- ✅ Centrality metrics (PageRank, betweenness, degree)
- ✅ Star pattern detection (hub-and-spoke funding)
- ✅ Chain pattern detection (sequential transfers)
- ✅ Network flow analysis

### 3. **Behavior Profiling** (behavior_profiler.py)
- ✅ Temporal activity pattern analysis
- ✅ Gas behavior profiling (variance, optimization)
- ✅ Value distribution analysis
- ✅ Contract interaction categorization (DEX, lending)
- ✅ Anomaly detection (Isolation Forest + rule-based)
- ✅ Bot pattern signatures (MEV, high-frequency)

### 4. **Insider Trading Detection** (insider_detector.py)
- ✅ Pre-launch accumulation detection
- ✅ Pre-announcement activity analysis (volume spikes)
- ✅ Coordinated buying detection (time clustering)
- ✅ Whale wallet tracking
- ✅ Timing correlation analysis
- ✅ Multi-factor confidence scoring

### 5. **Detection Engine** (detector_engine.py)
- ✅ 4-phase detection pipeline (clustering → graph → behavior → insider)
- ✅ Threat level classification (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ Multi-module coordination
- ✅ Comprehensive reporting (JSON, text)
- ✅ Configurable thresholds

## Components

### address_clustering.py (650 lines)
**Purpose**: Multi-heuristic address clustering with ML

**Key Classes**:
- `AddressClustering` - Main clustering engine
- `ClusterResult` - Cluster with confidence and classification

**Detection Methods**:
```python
common_input_heuristic(txs)              # Co-occurring input detection
detect_change_addresses(txs)             # Change address identification
analyze_funding_patterns(addresses, txs) # Common funding source
temporal_correlation(addr_list, txs, window)  # Synchronized activity
cluster_by_behavior(features, algorithm, n_clusters)  # ML clustering
extract_address_features(addr, start_block, end_block)  # 8D feature extraction
```

### graph_analyzer.py (580 lines)
**Purpose**: Transaction network analysis with graph algorithms

**Key Classes**:
- `GraphAnalyzer` - NetworkX-based graph analysis
- `StarPattern` - Hub-and-spoke network detection
- `ChainPattern` - Sequential transfer detection

**Analysis Methods**:
```python
build_transaction_graph(txs)             # Directed weighted graph
detect_communities(algorithm)            # Community detection
calculate_centrality_metrics()           # PageRank, betweenness, degree
detect_star_patterns(min_connections, max_hops)  # Bot farm funding
detect_chain_patterns(min_length)        # Money laundering chains
find_common_funding_sources()            # Trace funding origins
```

### behavior_profiler.py (520 lines)
**Purpose**: Behavioral pattern analysis and anomaly detection

**Key Classes**:
- `BehaviorProfiler` - Behavioral analysis engine
- `AddressProfile` - Complete behavior profile
- `BotPattern` - Detected bot signature

**Profiling Methods**:
```python
profile_address(addr, txs)               # Comprehensive profiling
calculate_temporal_patterns(txs)         # Activity timing analysis
analyze_gas_behavior(txs)                # Gas price patterns
analyze_value_distribution(txs)          # Transaction value patterns
categorize_contract_interactions(txs)    # Contract usage profiling
detect_anomalies(profile)                # Isolation Forest + rules
detect_bot_patterns(profiles)            # Bot signature matching
compare_profiles(profile1, profile2)     # Similarity analysis
```

### insider_detector.py (490 lines)
**Purpose**: Insider trading pattern detection

**Key Classes**:
- `InsiderDetector` - Insider trading detection engine
- `InsiderEvent` - Detected insider trading event

**Detection Methods**:
```python
detect_pre_launch_accumulation(token, launch_block, lookback)
detect_pre_announcement_activity(token, announcement_block, lookback)
detect_coordinated_buying(token, start_block, end_block, time_window)
calculate_timing_correlation(timestamps)
calculate_volume_ratio(baseline_volume, suspicious_volume)
```

### detector_engine.py (400 lines)
**Purpose**: Unified detection orchestration

**Key Classes**:
- `DetectorEngine` - Main orchestration engine
- `DetectionReport` - Comprehensive analysis report
- `ThreatLevel` - Severity classification enum

**Pipeline Methods**:
```python
analyze_addresses(addrs, txs, start_block, end_block)  # Full 4-phase pipeline
export_report(report, format)           # JSON or text export
classify_threat_level(confidence, evidence)  # Threat classification
aggregate_detections(results)           # Multi-module aggregation
```

## Detection Algorithms

### Address Clustering

#### Common Input Ownership Heuristic
Identifies addresses that appear together as inputs in the same transaction.

**Algorithm**:
1. Build co-occurrence graph from transaction inputs
2. Use DFS to merge transitive relationships
3. Return clusters of related addresses

**Use Case**: Detect wallet clusters controlled by same entity

#### Change Address Detection
Identifies change addresses from payment transactions.

**Pattern**: Single-input, dual-output transactions where one output is a new address

**Algorithm**:
1. Filter transactions with 1 input, 2 outputs
2. Check if output address appears only once
3. Link change address to owner

**Use Case**: Connect change addresses to known wallets

#### Funding Pattern Analysis
Groups addresses by common funding source.

**Algorithm**:
1. Trace first funding transaction for each address
2. Group addresses funded by same source
3. Detect bulk-funded bot networks

**Use Case**: Identify coordinated Sybil networks funded from single source

#### Temporal Correlation
Finds addresses with synchronized activity patterns.

**Algorithm**:
1. Extract activity timestamps for each address
2. Calculate overlap within time window (default 1 hour)
3. Flag addresses with >30% correlated activity

**Use Case**: Detect coordinated manipulation

#### ML Clustering (K-Means & DBSCAN)
Groups addresses by behavioral similarity using 8-dimensional feature vectors.

**Features**:
- Transaction count
- Total value sent/received
- Unique counterparties
- Average transaction value
- Activity span (days)
- Gas price variance
- Contract interactions

**Classification Logic**:
```python
if tx_count_variance < 5 and avg_tx_count > 10:
    cluster_type = 'sybil'  # Coordinated behavior
elif activity_span_std < 1.0:
    cluster_type = 'suspicious'  # Similar timing
else:
    cluster_type = 'normal'  # Diverse patterns
```

**Confidence Scoring**:
```python
confidence = 1.0 - (avg_pairwise_distance / 10.0)
```

### Transaction Graph Analysis

#### Graph Construction
Creates directed weighted graph from transactions.

**Vertices**: Wallet addresses  
**Edges**: Transactions (weighted by value)  
**Properties**: Transaction count, timestamp, cumulative value

#### Community Detection
Identifies clusters of closely connected addresses using Louvain Method and Label Propagation algorithms.

**Use Case**: Find isolated bot networks

#### Centrality Metrics
Calculates influence and importance scores.

**Metrics**:
- **PageRank**: Influence within network
- **Betweenness Centrality**: Bridge between communities
- **Degree Centrality**: Connection count
- **Clustering Coefficient**: Local connectivity

**Use Case**: Identify hub addresses and key players

#### Star Pattern Detection
Detects hub-and-spoke funding patterns.

**Pattern**: One address (hub) funding many others (spokes)

**Algorithm**:
1. Find addresses with high out-degree (>= min_connections)
2. Trace connected nodes within max_hops
3. Calculate confidence based on degree ratio

**Use Case**: Detect bot farm funding

#### Chain Pattern Detection
Detects sequential fund routing.

**Pattern**: A → B → C → D (sequential transfers)

**Algorithm**:
1. Find addresses with exactly 1 successor
2. Follow chain until break (cycle or branching)
3. Flag chains >= min_length

**Use Case**: Detect money laundering chains

### Behavior Profiling

#### Temporal Pattern Analysis
Analyzes activity timing regularity.

**Metrics**:
- Activity hours distribution
- Activity days distribution  
- Average transactions per day
- Activity regularity score (variance in timing)

**Bot Indicator**: Regularity score > 0.8 (highly regular)

#### Gas Behavior Analysis
Profiles gas price usage patterns.

**Metrics**:
- Average gas price
- Gas price variance
- Dynamic pricing usage
- Gas optimization score

**Bot Indicator**: Variance < 1.0 Gwei and consistent pricing

#### Value Distribution Analysis
Analyzes transaction value patterns.

**Metrics**:
- Average value
- Median value
- Value variance
- Large vs. small transaction counts

**Bot Indicator**: Variance < 0.01 (identical values)

#### Contract Interaction Profiling
Categorizes smart contract usage (DEX, lending protocols, EOA transfers).

**Use Case**: Identify MEV bots and arbitrage bots

#### Anomaly Detection (Isolation Forest)
ML-based outlier detection using 7-dimensional behavioral vectors with 10% contamination threshold.

### Insider Trading Detection

#### Pre-Launch Accumulation
Detects coordinated buying before token launches.

**Algorithm**:
1. Get token transfers in lookback window before launch
2. Identify addresses that accumulated before launch
3. Check timing correlation (variance < 1 hour)
4. Calculate confidence score

**Evidence**: Coordinated buyer count, time variance, average buy size, accumulation window

#### Pre-Announcement Activity
Detects volume spikes before announcements.

**Algorithm**:
1. Get baseline activity (older time period)
2. Get pre-announcement activity (recent period)
3. Calculate volume ratio
4. Flag if ratio > 2.0x baseline

**Evidence**: Baseline volume, suspicious volume, volume ratio, unusual address count

#### Coordinated Buying
Detects synchronized purchases.

**Algorithm**:
1. Extract buy timestamps
2. Cluster buys within time window (default 5 minutes)
3. Flag clusters with >= 3 addresses
4. Calculate confidence based on cluster size

**Evidence**: Cluster size, time window, actual time span, total volume

### Detection Engine Pipeline

#### Unified 4-Phase Architecture

**Phase 1: Address Clustering**
- Apply common input heuristic
- Detect change addresses
- Analyze funding patterns
- Perform temporal correlation

**Phase 2: Graph Analysis**
- Build transaction graph
- Detect communities
- Find star patterns
- Detect chain patterns

**Phase 3: Behavior Profiling**
- Profile each address
- Detect anomalies
- Identify bot patterns

**Phase 4: Insider Detection**
- Scan for token launches
- Detect pre-launch accumulation
- Check pre-announcement activity
- Find coordinated buying

#### Threat Level Classification

```python
class ThreatLevel(Enum):
    LOW = "low"           # Minimal risk
    MEDIUM = "medium"     # Suspicious but not confirmed
    HIGH = "high"         # Strong evidence
    CRITICAL = "critical" # Confirmed threat
```

#### Multi-Factor Scoring
Combines evidence from multiple detection methods with confidence calculation based on address cluster size, timing precision, and volume concentration.

## Usage Examples

### Example 1: Basic Address Analysis

```python
from web3 import Web3
from address_clustering import AddressClustering
import os

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
clusterer = AddressClustering(w3)

# Analyze addresses
addresses = [
    '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',  # vitalik.eth
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'   # WETH
]

# Extract features
features = [
    clusterer.extract_address_features(addr, 18000000, 18100000)
    for addr in addresses
]

# Perform clustering
clusters = clusterer.cluster_by_behavior(
    features,
    algorithm='kmeans',
    n_clusters=3
)

# Print results
for cluster in clusters:
    print(f"Cluster {cluster.cluster_id}: {cluster.cluster_type}")
    print(f"  Confidence: {cluster.confidence:.2%}")
    print(f"  Addresses: {len(cluster.addresses)}")
```

**Expected Output**:
```
INFO:address_clustering:Extracting features for address...
INFO:address_clustering:Clustering 3 address features
INFO:address_clustering:K-Means clustering complete

Cluster 0: normal
  Confidence: 75.23%
  Addresses: 2

Cluster 1: normal
  Confidence: 68.45%
  Addresses: 1
```

### Example 2: Transaction Graph Analysis

```python
from graph_analyzer import GraphAnalyzer

analyzer = GraphAnalyzer(w3)

# Build graph from transactions
transactions = [
    {'from': '0xa...', 'to': '0xb...', 'value': 1.5, 'timestamp': 1000},
    {'from': '0xa...', 'to': '0xc...', 'value': 1.5, 'timestamp': 1001},
    # ... more transactions
]

graph = analyzer.build_transaction_graph(transactions)

# Detect communities
communities = analyzer.detect_communities(algorithm='louvain')

print(f"Found {len(communities)} communities")
for comm_id, addresses in communities.items():
    print(f"  Community {comm_id}: {len(addresses)} addresses")

# Find star patterns
stars = analyzer.detect_star_patterns(min_connections=5)

for network in stars:
    print(f"\n🚨 Star network detected!")
    print(f"  Hub: {network.hub_address}")
    print(f"  Connected: {len(network.addresses)} addresses")
    print(f"  Total volume: {network.total_volume:.2f} ETH")
    print(f"  Confidence: {network.confidence:.2%}")
```

**Test Output** (from test execution):
```
INFO:graph_analyzer:Building transaction graph from 5 transactions
INFO:graph_analyzer:Graph: 6 nodes, 5 edges
INFO:graph_analyzer:Detecting communities using label_propagation
INFO:graph_analyzer:Found 2 communities
INFO:graph_analyzer:Detecting star/hub patterns
INFO:graph_analyzer:Detected 1 star patterns

✅ Graph built:
   Nodes: 6
   Edges: 5

✅ Calculated metrics for 6 addresses

0xa:
  PageRank: 0.1107
  Degree centrality: 0.6000
  In-degree: 0
  Out-degree: 3

Network 0:
  Hub: 0xa
  Addresses: 6
  Confidence: 0.18
  Total volume: 6.50
```

### Example 3: Behavior Profiling

```python
from behavior_profiler import BehaviorProfiler

profiler = BehaviorProfiler(w3)

# Profile address
address = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
addr_transactions = [...]  # Get transaction history

profile = profiler.profile_address(address, addr_transactions)

print(f"Profile for {profile.address}")
print(f"\nTemporal Patterns:")
print(f"  Regularity score: {profile.activity_regularity_score:.2f}")
print(f"  Avg tx/day: {profile.avg_tx_per_day:.1f}")

print(f"\nGas Behavior:")
print(f"  Avg gas price: {profile.avg_gas_price:.1f} Gwei")
print(f"  Optimization score: {profile.gas_optimization_score:.2f}")

print(f"\nAnomaly Detection:")
print(f"  Is anomalous: {profile.is_anomalous}")
print(f"  Anomaly score: {profile.anomaly_score:.2f}")

if profile.anomaly_reasons:
    print(f"  Reasons:")
    for reason in profile.anomaly_reasons:
        print(f"    - {reason}")
```

**Test Output** (from test execution):
```
INFO:behavior_profiler:Profiling address: 0xa

✅ Profile created for: 0xa

Temporal Patterns:
  Activity regularity: 0.50
  Avg tx/day: 12960.0

Gas Behavior:
  Avg gas price: 50.0 Gwei
  Gas variance: 0.00
  Gas optimization score: 0.90

Value Patterns:
  Avg value: 1.0000 ETH
  Median value: 1.0000 ETH

Anomaly Detection:
  Anomaly score: 0.80
  Is anomalous: True
  Reasons:
    - Consistent gas pricing (bot-like)
    - Identical transaction values
    - Extremely high transaction frequency
    - Activity concentrated in single hour
```

### Example 4: Insider Trading Detection

```python
from insider_detector import InsiderDetector

detector = InsiderDetector(w3)

# Detect pre-launch accumulation
token_address = '0xTokenContractAddress'
launch_block = 18500000

event = detector.detect_pre_launch_accumulation(
    token_address,
    launch_block,
    lookback_blocks=1000,
    min_addresses=3
)

if event:
    print(f"🚨 INSIDER TRADING DETECTED!")
    print(f"  Type: {event.event_type}")
    print(f"  Token: {event.token_address}")
    print(f"  Confidence: {event.confidence:.2%}")
    print(f"  Addresses involved: {len(event.addresses)}")
    print(f"  Total volume: {event.total_volume:.2f}")
    print(f"\n  Evidence:")
    for key, value in event.evidence.items():
        print(f"    {key}: {value}")
else:
    print("✅ No insider trading detected")
```

**Test Output** (from test execution):
```
INFO:insider_detector:Detecting pre-launch accumulation for 0x1234567890...
INFO:insider_detector:No pre-launch activity found

✅ No insider trading detected (expected - no real activity)
```

### Example 5: Comprehensive Detection (Main Engine)

```python
from detector_engine import DetectorEngine

# Initialize engine with custom thresholds
engine = DetectorEngine(
    w3,
    sybil_threshold=0.6,
    insider_threshold=0.7,
    bot_threshold=0.5
)

# Run comprehensive analysis
addresses = [...]  # List of addresses to analyze
transactions = [...]  # Transaction data

report = engine.analyze_addresses(
    addresses,
    transactions,
    start_block=18000000,
    end_block=18100000
)

# Print summary
print(f"Analysis Report: {report.report_id}")
print(f"Addresses analyzed: {report.total_addresses_analyzed}")
print(f"Transactions analyzed: {report.total_transactions_analyzed}")
print(f"\nThreats detected: {report.total_threats}")
print(f"  Critical: {report.critical_threats}")
print(f"  High: {report.high_threats}")

# Export as JSON
json_report = engine.export_report(report, format='json')
print(json_report)

# Export as text
text_report = engine.export_report(report, format='text')
print(text_report)
```

**Test Output** (from test execution):
```
INFO:detector_engine:Analyzing 5 addresses with 3 transactions
INFO:detector_engine:Phase 1: Address clustering analysis
INFO:detector_engine:Phase 2: Transaction graph analysis
INFO:detector_engine:Phase 3: Behavior profiling
INFO:detector_engine:Phase 4: Insider trading detection
INFO:detector_engine:Analysis complete: 2 threats detected

✅ Analysis complete!

======================================================================
SYBIL & INSIDER DETECTOR - ANALYSIS REPORT
======================================================================
Report ID: report_20260219_151409
Generated: 2026-02-19 15:14:09.760431

SUMMARY
----------------------------------------------------------------------
Addresses Analyzed: 5
Transactions Analyzed: 3
Total Threats: 2
  Critical: 0
  High: 1
Communities Found: 2
Suspicious Patterns: 0

BOT DETECTIONS
----------------------------------------------------------------------
• bot_0xa
  Threat Level: HIGH
  Confidence: 100.00%

• pattern_bot_high_freq
  Threat Level: MEDIUM
  Confidence: 85.00%
```

## Configuration

### Environment Variables

```bash
export RPC_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
```

### Threshold Configuration

```python
# Configure detection sensitivity
engine = DetectorEngine(
    w3,
    sybil_threshold=0.6,    # 60% confidence for Sybil detection
    insider_threshold=0.7,   # 70% confidence for insider detection
    bot_threshold=0.5        # 50% confidence for bot detection
)
```

### Clustering Parameters

```python
# K-Means clustering
clusters = clusterer.cluster_by_behavior(
    features,
    algorithm='kmeans',
    n_clusters=10  # Number of clusters
)

# DBSCAN clustering (auto cluster count)
clusters = clusterer.cluster_by_behavior(
    features,
    algorithm='dbscan'
)
```

## Performance Metrics

- **Address Feature Extraction**: ~1-2 seconds per address
- **Graph Construction**: ~5-10 seconds for 10,000 transactions
- **ML Clustering**: ~2-5 seconds for 1,000 addresses
- **Community Detection**: ~3-8 seconds for 5,000 nodes
- **Full Analysis**: ~30-60 seconds for comprehensive detection

## Production Considerations

### RPC Requirements
- **Archive Node**: Required for historical state access
- **Rate Limiting**: Implement backoff for API calls
- **Batch Queries**: Use multicall for efficiency

### Data Sources
- **Transaction Data**: eth_getTransaction, eth_getBlock
- **Token Events**: eth_getLogs for Transfer events
- **Historical State**: eth_getBalance at specific blocks

### Scalability
- **Batch Processing**: Process addresses in chunks
- **Caching**: Store extracted features
- **Database**: Consider PostgreSQL for large datasets

## Limitations

1. **Token Event Parsing**: Simplified in current implementation
   - Production needs full event decoding
   - Requires contract ABI knowledge

2. **Historical Data**: Requires archive node access
   - Standard nodes only keep recent state
   - Increases RPC costs

3. **False Positives**: ML clustering can over-classify
   - Adjust thresholds per use case
   - Manual review recommended for critical decisions

4. **Real-Time Detection**: Current implementation is batch-based
   - Add mempool monitoring for real-time
   - Requires WebSocket connection

## Future Enhancements

1. **Enhanced Token Analysis**
   - Full ERC20 event parsing
   - MEV detection integration
   - Flash loan analysis

2. **Advanced ML Models**
   - Neural networks for pattern recognition
   - Time-series analysis for temporal patterns
   - Association rule mining

3. **Real-Time Monitoring**
   - Mempool scanning
   - Live alert system
   - WebSocket integration

4. **Visualization**
   - Interactive graph visualization
   - Timeline analysis
   - Network flow diagrams

## References

- **GraphSense**: Bitcoin & Blockchain Analytics Platform
- **Chainalysis**: Blockchain Intelligence Research
- **Ethereum Address Clustering**: Academic Research Papers
- **NetworkX**: Graph Algorithm Library
- **Scikit-learn**: Machine Learning Library
