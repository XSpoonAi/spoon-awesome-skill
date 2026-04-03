"""
Payload Analyzer - Transaction payload analysis and feature extraction

This module analyzes transaction payloads to extract features for exploit detection.
It identifies suspicious patterns, known vulnerability signatures, and behavioral
anomalies that may indicate malicious intent.

Key Features:
- Function selector analysis and entropy calculation
- Parameter pattern detection (reentrancy, flash loans, etc.)
- Known exploit signature matching
- Behavioral feature extraction for ML classification
- Gas price anomaly detection
- Value transfer pattern analysis
- Call depth and complexity estimation
- External call pattern detection

Author: SpoonOS Skills
Category: Web3 Data Intelligence - Security Analysis
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
from collections import Counter

from web3 import Web3
from eth_utils import function_signature_to_4byte_selector
from eth_abi import decode


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExploitPattern(Enum):
    """Known exploit patterns"""
    REENTRANCY = "reentrancy"
    FLASH_LOAN = "flash_loan"
    PRICE_MANIPULATION = "price_manipulation"
    ACCESS_CONTROL_BYPASS = "access_control_bypass"
    INTEGER_OVERFLOW = "integer_overflow"
    DELEGATECALL_INJECTION = "delegatecall_injection"
    FRONT_RUNNING = "front_running"
    SANDWICH_ATTACK = "sandwich_attack"
    UNKNOWN = "unknown"


@dataclass
class PayloadFeatures:
    """
    Feature vector extracted from transaction payload
    Used for ML-based exploit classification
    """
    # Function characteristics
    function_selector: str
    function_selector_entropy: float  # Entropy of selector (randomness indicator)
    has_unknown_function: bool  # Function not in common databases
    
    # Parameter patterns
    has_zero_address: bool  # Contains 0x0 address
    has_max_uint: bool  # Contains max uint256 value
    has_small_values: bool  # Contains suspiciously small values
    has_large_values: bool  # Contains suspiciously large values
    parameter_count: int
    parameter_complexity: float  # Complexity score based on types
    
    # Value and gas patterns
    value_wei: int
    is_zero_value: bool
    gas_price_gwei: float
    gas_price_percentile: float  # Percentile vs recent average
    gas_price_anomaly: bool  # Significantly higher than normal
    
    # Call patterns
    estimated_call_depth: int  # Estimated based on data complexity
    has_delegatecall_pattern: bool
    has_external_call_pattern: bool
    has_state_change_pattern: bool
    
    # Known exploit signatures
    matches_reentrancy_pattern: bool
    matches_flash_loan_pattern: bool
    matches_price_manipulation_pattern: bool
    
    # Behavioral indicators
    sender_is_new: bool  # First-time sender
    sender_nonce: int
    unusual_timing: bool  # Transaction timing anomaly
    
    # Metadata
    timestamp: float
    detected_patterns: List[ExploitPattern] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def to_feature_vector(self) -> List[float]:
        """
        Convert to numerical feature vector for ML model
        Returns 22-dimensional feature vector
        """
        return [
            self.function_selector_entropy,
            float(self.has_unknown_function),
            float(self.has_zero_address),
            float(self.has_max_uint),
            float(self.has_small_values),
            float(self.has_large_values),
            float(self.parameter_count),
            self.parameter_complexity,
            math.log10(self.value_wei + 1),  # Log-scaled value
            float(self.is_zero_value),
            self.gas_price_gwei,
            self.gas_price_percentile,
            float(self.gas_price_anomaly),
            float(self.estimated_call_depth),
            float(self.has_delegatecall_pattern),
            float(self.has_external_call_pattern),
            float(self.has_state_change_pattern),
            float(self.matches_reentrancy_pattern),
            float(self.matches_flash_loan_pattern),
            float(self.matches_price_manipulation_pattern),
            float(self.sender_is_new),
            float(self.unusual_timing)
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'function_selector': self.function_selector,
            'function_selector_entropy': self.function_selector_entropy,
            'has_unknown_function': self.has_unknown_function,
            'has_zero_address': self.has_zero_address,
            'has_max_uint': self.has_max_uint,
            'has_small_values': self.has_small_values,
            'has_large_values': self.has_large_values,
            'parameter_count': self.parameter_count,
            'parameter_complexity': self.parameter_complexity,
            'value_wei': self.value_wei,
            'is_zero_value': self.is_zero_value,
            'gas_price_gwei': self.gas_price_gwei,
            'gas_price_percentile': self.gas_price_percentile,
            'gas_price_anomaly': self.gas_price_anomaly,
            'estimated_call_depth': self.estimated_call_depth,
            'has_delegatecall_pattern': self.has_delegatecall_pattern,
            'has_external_call_pattern': self.has_external_call_pattern,
            'has_state_change_pattern': self.has_state_change_pattern,
            'matches_reentrancy_pattern': self.matches_reentrancy_pattern,
            'matches_flash_loan_pattern': self.matches_flash_loan_pattern,
            'matches_price_manipulation_pattern': self.matches_price_manipulation_pattern,
            'sender_is_new': self.sender_is_new,
            'sender_nonce': self.sender_nonce,
            'unusual_timing': self.unusual_timing,
            'detected_patterns': [p.value for p in self.detected_patterns],
            'confidence_score': self.confidence_score,
            'feature_vector': self.to_feature_vector()
        }


class PayloadAnalyzer:
    """
    Advanced transaction payload analyzer for exploit detection
    
    This class extracts features from transaction payloads and identifies
    suspicious patterns that may indicate exploit attempts. It combines
    signature-based detection with behavioral analysis.
    """
    
    # Known malicious function selectors (4-byte signatures)
    SUSPICIOUS_SELECTORS = {
        '0xa9059cbb',  # transfer (often used in token theft)
        '0x095ea7b3',  # approve (can enable theft)
        '0x23b872dd',  # transferFrom (can drain approved tokens)
        '0xe8e33700',  # add_liquidity (flash loan attacks)
        '0x6a627842',  # minting functions
    }
    
    # Known flash loan function signatures
    FLASH_LOAN_SIGNATURES = {
        '0xab9c4b5d',  # flashLoan (Aave)
        '0x5cffe9de',  # flashLoan (generic)
        '0xe0232b42',  # borrow (Compound-style)
    }
    
    # Reentrancy indicators (external calls)
    EXTERNAL_CALL_SELECTORS = {
        '0x70a08231',  # balanceOf
        '0x18160ddd',  # totalSupply
        '0xa9059cbb',  # transfer
    }
    
    def __init__(
        self,
        w3: Web3,
        known_functions: Optional[Dict[str, str]] = None,
        gas_price_window: int = 100
    ):
        """
        Initialize payload analyzer
        
        Args:
            w3: Web3 instance for blockchain interaction
            known_functions: Dictionary of known function selectors to names
            gas_price_window: Number of recent blocks for gas price analysis
        """
        self.w3 = w3
        self.known_functions = known_functions or {}
        self.gas_price_window = gas_price_window
        
        # Gas price statistics for anomaly detection
        self.recent_gas_prices: List[int] = []
        self.avg_gas_price: float = 0.0
        self.gas_price_std: float = 0.0
        
        # Sender tracking
        self.known_senders: set = set()
        
        logger.info(f"PayloadAnalyzer initialized with {len(self.known_functions)} known functions")
    
    def analyze(
        self,
        tx_hash: str,
        from_address: str,
        to_address: Optional[str],
        value: int,
        gas_price: int,
        input_data: str,
        nonce: int,
        timestamp: float
    ) -> PayloadFeatures:
        """
        Analyze transaction payload and extract features
        
        Args:
            tx_hash: Transaction hash
            from_address: Sender address
            to_address: Recipient address
            value: Transaction value in Wei
            gas_price: Gas price in Wei
            input_data: Transaction input data (hex)
            nonce: Sender nonce
            timestamp: Transaction timestamp
        
        Returns:
            PayloadFeatures object with extracted features
        """
        # Extract function selector
        function_selector = input_data[:10] if len(input_data) >= 10 else "0x"
        
        # Calculate function selector entropy
        selector_entropy = self._calculate_entropy(function_selector)
        
        # Check if function is known
        has_unknown_function = (
            function_selector not in self.known_functions and
            len(input_data) >= 10
        )
        
        # Analyze parameters
        param_analysis = self._analyze_parameters(input_data)
        
        # Gas price analysis
        gas_price_gwei = self.w3.from_wei(gas_price, 'gwei')
        gas_percentile = self._calculate_gas_percentile(gas_price)
        gas_anomaly = gas_percentile > 95.0  # Top 5% = anomaly
        
        # Update gas price tracking
        self._update_gas_price_stats(gas_price)
        
        # Call pattern detection
        call_depth = self._estimate_call_depth(input_data)
        has_delegatecall = self._detect_delegatecall_pattern(input_data)
        has_external_call = self._detect_external_call_pattern(function_selector)
        has_state_change = self._detect_state_change_pattern(function_selector)
        
        # Exploit pattern matching
        reentrancy_match = self._match_reentrancy_pattern(
            function_selector, param_analysis, value
        )
        flash_loan_match = self._match_flash_loan_pattern(
            function_selector, value, param_analysis
        )
        price_manipulation_match = self._match_price_manipulation_pattern(
            function_selector, param_analysis
        )
        
        # Sender analysis
        sender_is_new = from_address not in self.known_senders
        self.known_senders.add(from_address)
        
        # Timing analysis
        unusual_timing = self._detect_timing_anomaly(timestamp)
        
        # Collect detected patterns
        detected_patterns = []
        if reentrancy_match:
            detected_patterns.append(ExploitPattern.REENTRANCY)
        if flash_loan_match:
            detected_patterns.append(ExploitPattern.FLASH_LOAN)
        if price_manipulation_match:
            detected_patterns.append(ExploitPattern.PRICE_MANIPULATION)
        if gas_anomaly:
            detected_patterns.append(ExploitPattern.FRONT_RUNNING)
        
        # Build feature object
        features = PayloadFeatures(
            function_selector=function_selector,
            function_selector_entropy=selector_entropy,
            has_unknown_function=has_unknown_function,
            has_zero_address=param_analysis['has_zero_address'],
            has_max_uint=param_analysis['has_max_uint'],
            has_small_values=param_analysis['has_small_values'],
            has_large_values=param_analysis['has_large_values'],
            parameter_count=param_analysis['count'],
            parameter_complexity=param_analysis['complexity'],
            value_wei=value,
            is_zero_value=(value == 0),
            gas_price_gwei=gas_price_gwei,
            gas_price_percentile=gas_percentile,
            gas_price_anomaly=gas_anomaly,
            estimated_call_depth=call_depth,
            has_delegatecall_pattern=has_delegatecall,
            has_external_call_pattern=has_external_call,
            has_state_change_pattern=has_state_change,
            matches_reentrancy_pattern=reentrancy_match,
            matches_flash_loan_pattern=flash_loan_match,
            matches_price_manipulation_pattern=price_manipulation_match,
            sender_is_new=sender_is_new,
            sender_nonce=nonce,
            unusual_timing=unusual_timing,
            timestamp=timestamp,
            detected_patterns=detected_patterns
        )
        
        # Calculate confidence score based on pattern matches
        features.confidence_score = self._calculate_confidence_score(features)
        
        return features
    
    def _calculate_entropy(self, hex_string: str) -> float:
        """Calculate Shannon entropy of hex string"""
        if len(hex_string) < 4:
            return 0.0
        
        # Remove 0x prefix
        hex_string = hex_string[2:] if hex_string.startswith('0x') else hex_string
        
        # Count character frequencies
        counter = Counter(hex_string)
        length = len(hex_string)
        
        # Calculate entropy
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _analyze_parameters(self, input_data: str) -> Dict[str, Any]:
        """Analyze transaction parameters for suspicious patterns"""
        if len(input_data) < 10:
            return {
                'count': 0,
                'complexity': 0.0,
                'has_zero_address': False,
                'has_max_uint': False,
                'has_small_values': False,
                'has_large_values': False
            }
        
        # Extract parameter data (after function selector)
        param_data = input_data[10:]
        
        # Count parameters (rough estimate: 32 bytes per param)
        param_count = len(param_data) // 64
        
        # Check for suspicious patterns
        has_zero_address = '0000000000000000000000000000000000000000' in param_data
        has_max_uint = 'f' * 64 in param_data.lower()
        
        # Detect small/large values (heuristic)
        has_small_values = '0000000000000000000000000000000000000000000000000000000000000001' in param_data
        has_large_values = any(
            int(param_data[i:i+64], 16) > 10**24  # > 1M tokens (18 decimals)
            for i in range(0, len(param_data), 64)
            if len(param_data[i:i+64]) == 64
        ) if len(param_data) >= 64 else False
        
        # Complexity score based on param count and data length
        complexity = min(1.0, (param_count * len(param_data)) / 10000.0)
        
        return {
            'count': param_count,
            'complexity': complexity,
            'has_zero_address': has_zero_address,
            'has_max_uint': has_max_uint,
            'has_small_values': has_small_values,
            'has_large_values': has_large_values
        }
    
    def _calculate_gas_percentile(self, gas_price: int) -> float:
        """Calculate gas price percentile vs recent transactions"""
        if not self.recent_gas_prices:
            return 50.0  # Default to median
        
        # Count how many recent gas prices are lower
        lower_count = sum(1 for gp in self.recent_gas_prices if gp < gas_price)
        percentile = (lower_count / len(self.recent_gas_prices)) * 100.0
        
        return percentile
    
    def _update_gas_price_stats(self, gas_price: int):
        """Update rolling gas price statistics"""
        self.recent_gas_prices.append(gas_price)
        
        # Keep only recent window
        if len(self.recent_gas_prices) > self.gas_price_window:
            self.recent_gas_prices.pop(0)
        
        # Recalculate statistics
        if self.recent_gas_prices:
            self.avg_gas_price = sum(self.recent_gas_prices) / len(self.recent_gas_prices)
            
            # Standard deviation
            variance = sum(
                (gp - self.avg_gas_price) ** 2
                for gp in self.recent_gas_prices
            ) / len(self.recent_gas_prices)
            self.gas_price_std = math.sqrt(variance)
    
    def _estimate_call_depth(self, input_data: str) -> int:
        """Estimate call depth based on data complexity"""
        # Heuristic: longer/more complex data suggests deeper call stack
        if len(input_data) < 10:
            return 1
        
        data_length = len(input_data)
        if data_length < 200:
            return 1
        elif data_length < 1000:
            return 2
        elif data_length < 5000:
            return 3
        else:
            return 4
    
    def _detect_delegatecall_pattern(self, input_data: str) -> bool:
        """Detect delegatecall patterns in transaction data"""
        # Check for delegatecall-related function selectors
        delegatecall_selectors = {
            '0x5c60da1b',  # implementation() - proxy pattern
            '0xf851a440',  # admin() - proxy admin
        }
        
        if len(input_data) >= 10:
            selector = input_data[:10]
            return selector in delegatecall_selectors
        
        return False
    
    def _detect_external_call_pattern(self, function_selector: str) -> bool:
        """Detect external call patterns"""
        return function_selector in self.EXTERNAL_CALL_SELECTORS
    
    def _detect_state_change_pattern(self, function_selector: str) -> bool:
        """Detect state-changing function patterns"""
        # State-changing functions typically modify storage
        state_changing_selectors = {
            '0xa9059cbb',  # transfer
            '0x23b872dd',  # transferFrom
            '0x095ea7b3',  # approve
            '0x40c10f19',  # mint
            '0x42966c68',  # burn
        }
        
        return function_selector in state_changing_selectors
    
    def _match_reentrancy_pattern(
        self,
        function_selector: str,
        param_analysis: Dict,
        value: int
    ) -> bool:
        """Detect reentrancy attack patterns"""
        # Reentrancy typically involves:
        # 1. External call with value transfer
        # 2. State-changing function
        # 3. Complex call pattern
        
        has_external_call = self._detect_external_call_pattern(function_selector)
        has_value = value > 0
        is_complex = param_analysis['complexity'] > 0.5
        
        return has_external_call and has_value and is_complex
    
    def _match_flash_loan_pattern(
        self,
        function_selector: str,
        value: int,
        param_analysis: Dict
    ) -> bool:
        """Detect flash loan attack patterns"""
        # Flash loan indicators:
        # 1. Known flash loan function
        # 2. Large value transfer
        # 3. Complex parameters
        
        is_flash_loan_function = function_selector in self.FLASH_LOAN_SIGNATURES
        has_large_value = value > self.w3.to_wei(100, 'ether')  # > 100 ETH
        has_large_params = param_analysis['has_large_values']
        
        return is_flash_loan_function or (has_large_value and has_large_params)
    
    def _match_price_manipulation_pattern(
        self,
        function_selector: str,
        param_analysis: Dict
    ) -> bool:
        """Detect price manipulation patterns"""
        # Price manipulation indicators:
        # 1. DEX-related functions
        # 2. Unusual parameter patterns (max values, zero addresses)
        
        # DEX swap function selectors
        dex_selectors = {
            '0x38ed1739',  # swapExactTokensForTokens
            '0x8803dbee',  # swapTokensForExactTokens
            '0x7ff36ab5',  # swapExactETHForTokens
        }
        
        is_dex_function = function_selector in dex_selectors
        has_unusual_params = (
            param_analysis['has_zero_address'] or
            param_analysis['has_max_uint'] or
            param_analysis['has_small_values']
        )
        
        return is_dex_function and has_unusual_params
    
    def _detect_timing_anomaly(self, timestamp: float) -> bool:
        """Detect unusual transaction timing patterns"""
        # Heuristic: Could be expanded to detect coordinated timing
        # For now, always return False (requires historical data)
        return False
    
    def _calculate_confidence_score(self, features: PayloadFeatures) -> float:
        """Calculate confidence score for exploit detection"""
        score = 0.0
        
        # Pattern matches (high weight)
        if features.matches_reentrancy_pattern:
            score += 0.3
        if features.matches_flash_loan_pattern:
            score += 0.3
        if features.matches_price_manipulation_pattern:
            score += 0.3
        
        # Gas price anomaly (medium weight)
        if features.gas_price_anomaly:
            score += 0.2
        
        # Unknown function (low weight)
        if features.has_unknown_function:
            score += 0.1
        
        # Suspicious parameters (low weight)
        if features.has_zero_address or features.has_max_uint:
            score += 0.1
        
        # High complexity (low weight)
        if features.parameter_complexity > 0.7:
            score += 0.1
        
        # Normalize to [0, 1]
        return min(1.0, score)



