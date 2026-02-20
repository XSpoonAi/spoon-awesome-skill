"""
IDS Engine - Main orchestration for Mempool Intrusion Detection System

This module integrates all components (monitoring, analysis, classification, defense)
into a unified real-time intrusion detection system for blockchain networks.

Key Features:
- Real-time mempool monitoring and transaction interception
- Automated payload analysis and feature extraction
- ML-based exploit classification
- Automated defense execution with front-running
- Alert system and logging
- Performance metrics and reporting
- Configuration management
- Emergency shutdown mechanisms

Author: SpoonOS Skills
Category: Web3 Data Intelligence - Security Analysis
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os

from web3 import Web3
from eth_account import Account

from mempool_monitor import MempoolMonitor, PendingTransaction
from payload_analyzer import PayloadAnalyzer, PayloadFeatures
from exploit_classifier import ExploitClassifier, ClassificationResult, ThreatLevel
from defense_executor import DefenseExecutor, DefenseAction, DefenseStrategy


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IDSMode(Enum):
    """IDS operational mode"""
    MONITOR_ONLY = "monitor_only"  # Only monitor and log
    ALERT_ONLY = "alert_only"  # Monitor and alert
    ACTIVE_DEFENSE = "active_defense"  # Monitor, alert, and execute defense


@dataclass
class IDSConfig:
    """IDS configuration"""
    # Network
    websocket_url: str
    rpc_url: str
    chain_id: int
    
    # Monitored contracts
    monitored_contracts: List[str]
    contract_abis: Dict[str, List[Dict]] = field(default_factory=dict)
    
    # Classification
    classification_threshold: float = 0.7
    threat_level_threshold: ThreatLevel = ThreatLevel.HIGH
    
    # Defense
    operational_mode: IDSMode = IDSMode.MONITOR_ONLY
    defender_private_key: Optional[str] = None
    gas_buffer_multiplier: float = 1.5
    auto_pause_enabled: bool = False
    
    # Alerts
    alert_webhook: Optional[str] = None
    alert_email: Optional[str] = None
    
    # Performance
    max_concurrent_analysis: int = 10
    analysis_timeout: int = 5  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'websocket_url': self.websocket_url,
            'rpc_url': self.rpc_url,
            'chain_id': self.chain_id,
            'monitored_contracts': self.monitored_contracts,
            'classification_threshold': self.classification_threshold,
            'threat_level_threshold': self.threat_level_threshold.value,
            'operational_mode': self.operational_mode.value,
            'gas_buffer_multiplier': self.gas_buffer_multiplier,
            'auto_pause_enabled': self.auto_pause_enabled
        }


@dataclass
class ThreatDetection:
    """Threat detection event"""
    detection_id: str
    transaction: PendingTransaction
    features: PayloadFeatures
    classification: ClassificationResult
    timestamp: datetime
    defense_action: Optional[DefenseAction] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'detection_id': self.detection_id,
            'transaction': self.transaction.to_dict(),
            'features': self.features.to_dict(),
            'classification': self.classification.to_dict(),
            'timestamp': self.timestamp.isoformat(),
            'defense_action': self.defense_action.to_dict() if self.defense_action else None
        }


@dataclass
class IDSStatistics:
    """IDS operational statistics"""
    start_time: datetime
    transactions_monitored: int = 0
    transactions_analyzed: int = 0
    threats_detected: int = 0
    defenses_executed: int = 0
    defenses_successful: int = 0
    false_positives: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime,
            'transactions_monitored': self.transactions_monitored,
            'transactions_analyzed': self.transactions_analyzed,
            'threats_detected': self.threats_detected,
            'defenses_executed': self.defenses_executed,
            'defenses_successful': self.defenses_successful,
            'false_positives': self.false_positives,
            'detection_rate': self.threats_detected / self.transactions_analyzed if self.transactions_analyzed > 0 else 0.0,
            'defense_success_rate': self.defenses_successful / self.defenses_executed if self.defenses_executed > 0 else 0.0
        }


class IDSEngine:
    """
    Main IDS Engine - Real-time blockchain intrusion detection and response
    
    This class orchestrates all components of the mempool IDS:
    - Continuously monitors mempool for suspicious transactions
    - Analyzes payloads and extracts features
    - Classifies threats using ML models
    - Executes automated defense responses
    - Logs and reports all activity
    """
    
    def __init__(self, config: IDSConfig):
        """
        Initialize IDS Engine
        
        Args:
            config: IDS configuration
        """
        self.config = config
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        
        # Initialize components
        self.payload_analyzer = PayloadAnalyzer(
            w3=self.w3,
            known_functions={}
        )
        
        self.classifier = ExploitClassifier(
            model_type='random_forest',
            threshold=config.classification_threshold
        )
        
        # Train classifier with synthetic data (bootstrap)
        logger.info("Training classifier with synthetic data...")
        X, y = self.classifier.generate_synthetic_training_data()
        self.classifier.train(X, y)
        
        # Initialize defense executor (if enabled)
        self.defense_executor: Optional[DefenseExecutor] = None
        if config.operational_mode == IDSMode.ACTIVE_DEFENSE and config.defender_private_key:
            defender_account = Account.from_key(config.defender_private_key)
            
            pause_function_abi = {
                'name': 'pause',
                'type': 'function',
                'inputs': [],
                'outputs': [],
                'stateMutability': 'nonpayable'
            }
            
            self.defense_executor = DefenseExecutor(
                w3=self.w3,
                defender_account=defender_account,
                pause_function_abi=pause_function_abi,
                gas_buffer_multiplier=config.gas_buffer_multiplier
            )
        
        # Initialize mempool monitor
        self.mempool_monitor: Optional[MempoolMonitor] = None
        
        # Detection tracking
        self.detections: List[ThreatDetection] = []
        self.statistics = IDSStatistics(start_time=datetime.now())
        
        # Alert callbacks
        self.on_threat_detected: Optional[Callable] = None
        self.on_defense_executed: Optional[Callable] = None
        
        # Control flags
        self.is_running = False
        
        logger.info(f"✅ IDS Engine initialized in {config.operational_mode.value} mode")
        logger.info(f"Monitoring {len(config.monitored_contracts)} contracts")
    
    async def start(self):
        """Start IDS engine"""
        self.is_running = True
        logger.info("🚀 Starting Mempool IDS...")
        
        # Create mempool monitor
        self.mempool_monitor = MempoolMonitor(
            websocket_url=self.config.websocket_url,
            monitored_contracts=self.config.monitored_contracts,
            callback=self._on_transaction_detected,
            contract_abis=self.config.contract_abis
        )
        
        # Start monitoring
        await self.mempool_monitor.start()
    
    async def stop(self):
        """Stop IDS engine"""
        self.is_running = False
        logger.info("🛑 Stopping Mempool IDS...")
        
        if self.mempool_monitor:
            await self.mempool_monitor.stop()
        
        # Print final statistics
        stats = self.statistics.to_dict()
        logger.info("\n" + "=" * 80)
        logger.info("FINAL STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
        logger.info(f"Transactions monitored: {stats['transactions_monitored']}")
        logger.info(f"Transactions analyzed: {stats['transactions_analyzed']}")
        logger.info(f"Threats detected: {stats['threats_detected']}")
        logger.info(f"Defenses executed: {stats['defenses_executed']}")
        logger.info(f"Defense success rate: {stats['defense_success_rate']:.1%}")
        logger.info("=" * 80)
    
    def _on_transaction_detected(self, tx: PendingTransaction):
        """Callback for detected transactions"""
        self.statistics.transactions_monitored += 1
        
        # Run analysis asynchronously
        asyncio.create_task(self._analyze_transaction(tx))
    
    async def _analyze_transaction(self, tx: PendingTransaction):
        """Analyze transaction for threats"""
        try:
            self.statistics.transactions_analyzed += 1
            
            # Extract features
            features = self.payload_analyzer.analyze(
                tx_hash=tx.hash,
                from_address=tx.from_address,
                to_address=tx.to_address,
                value=tx.value,
                gas_price=tx.gas_price,
                input_data=tx.input_data,
                nonce=tx.nonce,
                timestamp=tx.timestamp.timestamp()
            )
            
            # Classify threat
            classification = self.classifier.predict(features)
            
            # Check if threat meets thresholds
            if self._is_actionable_threat(classification):
                await self._handle_threat(tx, features, classification)
        
        except Exception as e:
            logger.error(f"Analysis error for {tx.hash}: {e}")
    
    def _is_actionable_threat(self, classification: ClassificationResult) -> bool:
        """Check if threat meets action thresholds"""
        # Check classification
        if not classification.is_malicious:
            return False
        
        # Check confidence threshold
        if classification.confidence < self.config.classification_threshold:
            return False
        
        # Check threat level threshold
        threat_levels = [ThreatLevel.BENIGN, ThreatLevel.LOW, ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        min_level_index = threat_levels.index(self.config.threat_level_threshold)
        current_level_index = threat_levels.index(classification.threat_level)
        
        return current_level_index >= min_level_index
    
    async def _handle_threat(
        self,
        tx: PendingTransaction,
        features: PayloadFeatures,
        classification: ClassificationResult
    ):
        """Handle detected threat"""
        self.statistics.threats_detected += 1
        
        # Create detection record
        detection_id = f"threat_{int(datetime.now().timestamp() * 1000)}"
        detection = ThreatDetection(
            detection_id=detection_id,
            transaction=tx,
            features=features,
            classification=classification,
            timestamp=datetime.now()
        )
        
        self.detections.append(detection)
        
        # Log threat
        logger.warning("\n" + "=" * 80)
        logger.warning(f"🚨 THREAT DETECTED: {detection_id}")
        logger.warning("=" * 80)
        logger.warning(f"Transaction: {tx.hash}")
        logger.warning(f"Target Contract: {tx.to_address}")
        logger.warning(f"From: {tx.from_address}")
        logger.warning(f"Threat Level: {classification.threat_level.value.upper()}")
        logger.warning(f"Confidence: {classification.confidence:.2%}")
        logger.warning(f"Probability Malicious: {classification.probability_malicious:.2%}")
        logger.warning(f"Decision Factors: {classification.decision_factors}")
        logger.warning("=" * 80)
        
        # Trigger alert callback
        if self.on_threat_detected:
            self.on_threat_detected(detection)
        
        # Execute defense if enabled
        if self.config.operational_mode == IDSMode.ACTIVE_DEFENSE and self.config.auto_pause_enabled:
            await self._execute_defense(detection)
    
    async def _execute_defense(self, detection: ThreatDetection):
        """Execute automated defense"""
        if not self.defense_executor:
            logger.warning("Defense executor not initialized - skipping defense")
            return
        
        self.statistics.defenses_executed += 1
        
        # Determine urgency based on threat level
        urgency_map = {
            ThreatLevel.HIGH: "high",
            ThreatLevel.CRITICAL: "critical"
        }
        urgency = urgency_map.get(detection.classification.threat_level, "high")
        
        # Execute defense
        defense_action = self.defense_executor.execute_defense(
            strategy=DefenseStrategy.PAUSE_CONTRACT,
            target_contract=detection.transaction.to_address,
            threat_tx_hash=detection.transaction.hash,
            threat_gas_price=detection.transaction.gas_price,
            urgency=urgency
        )
        
        detection.defense_action = defense_action
        
        # Track success
        if defense_action.status.value in ['confirmed', 'submitted']:
            self.statistics.defenses_successful += 1
        
        # Trigger callback
        if self.on_defense_executed:
            self.on_defense_executed(detection)
    
    def mark_false_positive(self, detection_id: str):
        """Mark a detection as false positive"""
        for detection in self.detections:
            if detection.detection_id == detection_id:
                self.statistics.false_positives += 1
                logger.info(f"Marked {detection_id} as false positive")
                return
        logger.warning(f"Detection {detection_id} not found")
    
    def get_recent_detections(self, limit: int = 10) -> List[ThreatDetection]:
        """Get recent threat detections"""
        return self.detections[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get IDS statistics"""
        return self.statistics.to_dict()
    
    def export_detections(self, filepath: str):
        """Export detections to JSON file"""
        detections_data = [d.to_dict() for d in self.detections]
        
        with open(filepath, 'w') as f:
            json.dump({
                'statistics': self.statistics.to_dict(),
                'detections': detections_data
            }, f, indent=2)
        
        logger.info(f"Detections exported to {filepath}")



