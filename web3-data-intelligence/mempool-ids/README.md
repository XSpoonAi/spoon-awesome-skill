# Mempool Intrusion Detection System (IDS)

Real-time blockchain intrusion detection system that monitors the Ethereum mempool for exploit attempts and automatically executes defensive responses.

## Overview

The Mempool IDS acts as an active network intrusion detection system for blockchain networks. It continuously monitors pending transactions in the mempool, analyzes payloads for malicious patterns using machine learning, and automatically front-runs attackers by pausing vulnerable contracts with higher gas prices.

**Problem Solved**: Smart contract hacks happen in seconds. Standard scanners only look at static code, not live execution. This system provides real-time threat detection and automated response.

**Key Features**:
- Real-time WebSocket mempool monitoring
- ML-based exploit classification (Random Forest, Gradient Boosting)
- Automated defense execution with gas optimization
- Pattern-based threat detection (reentrancy, flash loans, price manipulation)
- Front-running malicious transactions-ahead protection
- Comprehensive logging and alerting

## Architecture

### Components

```
mempool-ids/
├── scripts/
│   ├── mempool_monitor.py (550 lines) - WebSocket monitoring
│   ├── payload_analyzer.py (650 lines) - Feature extraction
│   ├── exploit_classifier.py (600 lines) - ML classification  │   ├── defense_executor.py (550 lines) - Automated defense
│   └── ids_engine.py (550 lines) - Main orchestration
├── README.md
├── SKILL.md
└── PULL.md
```

**Total Code**: 2,900 lines of Python

### System Flow

```
1. Mempool Monitor (WebSocket)
   ↓ Filters transactions targeting monitored contracts
2. Payload Analyzer
   ↓ Extracts 22-dimensional feature vector
3. Exploit Classifier (ML)
   ↓ Classifies as benign/malicious with confidence score
4. IDS Engine (Decision)
   ↓ If threat detected above threshold
5. Defense Executor
   ↓ Fires pause transaction with higher gas
6. Contract Paused
   ✓ Treasury protected
```

## Installation

### Prerequisites

- Python 3.8+
- Ethereum RPC access (Infura, Alchemy, or local node)
- WebSocket endpoint for mempool monitoring

### Install Dependencies

```bash
pip install web3>=6.0.0 \
    scikit-learn>=1.3.0 \
    numpy>=1.24.0 \
    aiohttp>=3.9.0 \
    eth-account>=0.9.0 \
    python-dotenv
```

### Environment Setup

Create `.env` file:

```env
# Network endpoints
WEBSOCKET_URL=wss://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Defense configuration (KEEP SECURE!)
DEFENDER_PRIVATE_KEY=0xyour_private_key_here

# Alert configuration
ALERT_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Usage

### Monitor-Only Mode (Safe for Testing)

```python
from ids_engine import IDSEngine, IDSConfig, IDSMode, ThreatLevel

# Configuration
config = IDSConfig(
    websocket_url="wss://ethereum-rpc.publicnode.com",
    rpc_url="https://ethereum-rpc.publicnode.com",
    chain_id=1,
    monitored_contracts=[
        "0xYourContractAddress"
    ],
    operational_mode=IDSMode.MONITOR_ONLY,  # Only monitor and log
    classification_threshold=0.7,
    threat_level_threshold=ThreatLevel.HIGH
)

# Initialize IDS
ids = IDSEngine(config)

# Start monitoring
import asyncio
asyncio.run(ids.start())
```

### Active Defense Mode (Production)

```python
config = IDSConfig(
    websocket_url=os.getenv("WEBSOCKET_URL"),
    rpc_url=os.getenv("RPC_URL"),
    chain_id=1,
    monitored_contracts=[
        "0xYourContractAddress"
    ],
    operational_mode=IDSMode.ACTIVE_DEFENSE,  # Auto-execute defense
    defender_private_key=os.getenv("DEFENDER_PRIVATE_KEY"),
    gas_buffer_multiplier=1.5,  # 50% higher gas than attacker
    auto_pause_enabled=True,
    classification_threshold=0.8,  # Higher threshold for auto-defense
    threat_level_threshold=ThreatLevel.CRITICAL
)

# Register alert callbacks
def on_threat_detected(detection):
    print(f"🚨 THREAT: {detection.transaction.hash}")
    send_slack_alert(detection)  # Your alert logic

def on_defense_executed(detection):
    print(f"🛡️ DEFENSE: {detection.defense_action.response_tx_hash}")
    log_to_security_system(detection)

ids = IDSEngine(config)
ids.on_threat_detected = on_threat_detected
ids.on_defense_executed = on_defense_executed

# Start IDS
asyncio.run(ids.start())
```

### Individual Component Usage

#### Mempool Monitor

```python
from mempool_monitor import MempoolMonitor

def on_transaction(tx):
    print(f"Transaction: {tx.hash}")
    print(f"Function: {tx.function_name}")

monitor = MempoolMonitor(
    websocket_url="wss://ethereum-rpc.publicnode.com",
    monitored_contracts=["0xContractAddress"],
    callback=on_transaction
)

asyncio.run(monitor.start())
```

#### Payload Analyzer

```python
from payload_analyzer import PayloadAnalyzer

analyzer = PayloadAnalyzer(w3=w3)

features = analyzer.analyze(
    tx_hash=tx_hash,
    from_address=from_addr,
    to_address=to_addr,
    value=value,
    gas_price=gas_price,
    input_data=input_data,
    nonce=nonce,
    timestamp=timestamp
)

print(f"Confidence Score: {features.confidence_score}")
print(f"Detected Patterns: {features.detected_patterns}")
```

#### Exploit Classifier

```python
from exploit_classifier import ExploitClassifier

classifier = ExploitClassifier(
    model_type='random_forest',
    threshold=0.7
)

# Train with synthetic data
X, y = classifier.generate_synthetic_training_data()
metrics = classifier.train(X, y)

# Predict
result = classifier.predict(features)
print(f"Is Malicious: {result.is_malicious}")
print(f"Threat Level: {result.threat_level}")
print(f"Confidence: {result.confidence}")
```

#### Defense Executor

```python
from defense_executor import DefenseExecutor, DefenseStrategy

executor = DefenseExecutor(
    w3=w3,
    defender_account=account,
    pause_function_abi=pause_abi,
    gas_buffer_multiplier=1.5
)

action = executor.execute_defense(
    strategy=DefenseStrategy.PAUSE_CONTRACT,
    target_contract=contract_address,
    threat_tx_hash=threat_tx,
    threat_gas_price=threat_gas,
    urgency="critical"
)

print(f"Defense TX: {action.response_tx_hash}")
```

## Configuration

### Operational Modes

- **MONITOR_ONLY**: Only monitor and log transactions (safe for testing)
- **ALERT_ONLY**: Monitor and trigger alerts, no automated defense
- **ACTIVE_DEFENSE**: Full automation with defense execution

### Classification Thresholds

- `classification_threshold`: Minimum confidence score (0.0-1.0)
  - Recommended: 0.7 for alerts, 0.8+ for auto-defense
  
- `threat_level_threshold`: Minimum threat level for action
  - Options: BENIGN, LOW, MEDIUM, HIGH, CRITICAL
  - Recommended: HIGH for auto-defense

### Gas Strategy

- `gas_buffer_multiplier`: Multiplier for front-running
  - 1.5 = 50% higher gas than attacker
  - Higher values increase success rate but cost more
  - Recommended: 1.5-2.0 for critical contracts

## Security Considerations

### Private Key Management

⚠️ **CRITICAL**: Never expose defender private keys
- Use environment variables
- Store in secure key management system (AWS KMS, HashiCorp Vault)
- Use multi-sig wallets for production
- Rotate keys regularly

### False Positives

- Start with MONITOR_ONLY mode
- Tune thresholds based on your traffic
- Monitor false positive rate
- Consider manual approval for high-stakes contracts

### Gas Costs

- Each defense action costs gas
- Budget for emergency responses
- Monitor defender account balance
- Set up low-balance alerts

## Performance Metrics

Typical performance (depends on network conditions):
- **Transaction Detection**: <100ms (WebSocket latency)
- **Feature Extraction**: ~50-100ms per transaction
- **ML Classification**: ~10-20ms per transaction
- **Defense Execution**: 2-5 seconds (depends on gas and network)
- **Total Response Time**: 3-6 seconds from detection to contract pause

## Troubleshooting

### WebSocket Connection Issues

```python
# Use retry logic
monitor = MempoolMonitor(
    reconnect_delay=5,
    max_reconnect_attempts=10
)
```

### High False Positive Rate

```python
# Increase threshold
config.classification_threshold = 0.85
config.threat_level_threshold = ThreatLevel.CRITICAL

# Or tune threshold on validation data
classifier.tune_threshold(X_val, y_val, target_fpr=0.01)  # 1% FPR
```

### Gas Price Too Low

```python
# Increase buffer
config.gas_buffer_multiplier = 2.0  # 100% higher than attacker
```

### Defender Account Out of Gas

```python
# Monitor balance
balance = w3.eth.get_balance(defender_account.address)
if balance < w3.to_wei(0.1, 'ether'):
    send_alert("Low defender balance!")
```

## Testing

### Synthetic Data Generation

```python
# Test ML model
classifier = ExploitClassifier()
X_train, y_train = classifier.generate_synthetic_training_data(
    n_benign=1000,
    n_malicious=200
)
metrics = classifier.train(X_train, y_train)
print(f"Accuracy: {metrics.accuracy}")
print(f"False Positive Rate: {metrics.false_positive_rate}")
```

### Simulation Mode

```python
# Test without real transactions
config.operational_mode = IDSMode.MONITOR_ONLY
ids = IDSEngine(config)

# Inject test transaction
test_tx = create_test_transaction(exploit_type="reentrancy")
ids._on_transaction_detected(test_tx)
```

## Production Deployment

### Recommended Architecture

```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┬─────────┐
    │         │         │
┌───▼──┐  ┌──▼──┐  ┌──▼──┐
│ IDS  │  │ IDS │  │ IDS │  (Multiple instances)
│ Node │  │ Node│  │ Node│
└───┬──┘  └──┬──┘  └──┬──┘
    │        │        │
    └────┬───┴────┬───┘
         │        │
    ┌────▼────────▼────┐
    │  Consensus Layer  │  (Multi-sig or voting)
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │  Defense Executor │  (Single execution point)
    └───────────────────┘
```

### High Availability

- Deploy multiple IDS instances
- Use consensus mechanism for defense decisions
- Implement health checks and auto-recovery
- Monitor with Prometheus/Grafana

### Alerting

- Integrate with PagerDuty, OpsGenie for critical alerts
- Send notifications via Slack, Discord, Telegram
- Log to centralized security system (Splunk, ELK)
- Generate incident reports

## Examples

See individual module files for complete runnable examples:
- `mempool_monitor.py` - WebSocket monitoring example
- `payload_analyzer.py` - Feature extraction example
- `exploit_classifier.py` - ML classification example
- `defense_executor.py` - Defense execution example
- `ids_engine.py` - Complete IDS setup

## License

MIT License - See LICENSE file for details

## Contributing

Part of the SpoonOS Skills ecosystem. See CONTRIBUTING.md for guidelines.

## Support

For issues and questions:
- GitHub Issues: https://github.com/XSpoonAi/spoon-awesome-skill
- Documentation: See SKILL.md for detailed technical documentation
