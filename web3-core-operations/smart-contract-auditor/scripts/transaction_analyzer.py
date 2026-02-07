#!/usr/bin/env python3
"""
Transaction Analysis Module
Analyzes blockchain transactions for safety, patterns, and anomalies.
"""

import json
import requests
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class TransactionAnalyzer:
    """Analyzes transactions for safety, efficiency, and patterns using real blockchain data."""
    
    def __init__(self):
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY", "")
        self.etherscan_url = "https://api.etherscan.io/api"
        
        self.gas_price_thresholds = {
            "low": 20,      # Gwei
            "normal": 50,
            "high": 100,
            "critical": 200
        }
        self.transaction_patterns = {
            "normal": {"frequency": "low", "complexity": "simple"},
            "sandwich_attack": {"rapid_sequence": True, "same_function": True},
            "flash_loan": {"large_value": True, "repaid_same_block": True}
        }
    
    def get_transaction_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real transaction data from blockchain using Etherscan API.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction data or None if not found
        """
        try:
            params = {
                "module": "proxy",
                "action": "eth_getTransactionByHash",
                "txhash": tx_hash,
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.etherscan_url, params=params, timeout=10)
            data = response.json()
            return data.get("result")
        except Exception as e:
            print(f"Error fetching transaction: {e}")
        return None
    
    def get_recent_transactions(self, address: str = None) -> List[Dict[str, Any]]:
        """
        Get real recent transactions from Etherscan.
        
        Args:
            address: Ethereum address (optional)
            
        Returns:
            List of recent transactions
        """
        try:
            if not address:
                address = "0x68b3465833fb72B5A828cCEEf89B9d26a3bB09b0"  # Uniswap Router
            
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.etherscan_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1":
                return data.get("result", [])[:10]
        except Exception as e:
            print(f"Error fetching transactions: {e}")
        
        return []
    
    def analyze_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single transaction for multiple risk factors.
        
        Args:
            tx_data: Transaction data including to, from, value, data, gasPrice
            
        Returns:
            Analysis result with risk assessment and recommendations
        """
        analysis = {
            "transaction_hash": tx_data.get("hash", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "basic_info": self._extract_basic_info(tx_data),
            "gas_analysis": self._analyze_gas(tx_data),
            "value_analysis": self._analyze_value(tx_data),
            "safety_score": 0,
            "risk_level": "UNKNOWN",
            "recommendations": []
        }
        
        # Calculate safety score
        safety_score = 100
        
        # Gas price check
        gas_gwei = tx_data.get("gasPrice", 50) / 1e9
        if gas_gwei > self.gas_price_thresholds["critical"]:
            safety_score -= 25
            analysis["recommendations"].append(
                "Critical gas price detected. Transaction may be expensive."
            )
        elif gas_gwei > self.gas_price_thresholds["high"]:
            safety_score -= 15
        
        # Value check
        tx_value = float(tx_data.get("value", 0))
        if tx_value > 100:  # > 100 ETH equivalent
            safety_score -= 20
            analysis["recommendations"].append(
                f"High value transaction ({tx_value} ETH). Verify recipient."
            )
        
        # Function signature check
        func_sig = tx_data.get("data", "")[:10]
        if func_sig == "0x":  # Likely value transfer
            pass  # Safe
        else:  # Contract interaction
            if self._is_suspicious_function(func_sig):
                safety_score -= 30
                analysis["recommendations"].append(
                    "Suspicious function signature detected."
                )
        
        analysis["safety_score"] = max(0, safety_score)
        analysis["risk_level"] = self._calculate_risk_level(safety_score)
        
        return analysis
    
    def analyze_transaction_sequence(self, 
                                    transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze multiple transactions for patterns and anomalies.
        
        Args:
            transactions: List of transaction objects
            
        Returns:
            Pattern analysis and anomaly detection results
        """
        if not transactions:
            return {"error": "No transactions provided"}
        
        analysis = {
            "transaction_count": len(transactions),
            "time_window": f"{len(transactions)} transactions",
            "patterns_detected": [],
            "anomalies": [],
            "average_gas_price": 0,
            "total_value": 0,
            "sequence_risk_score": 0
        }
        
        gas_prices = []
        total_value = 0
        functions = {}
        
        for tx in transactions:
            # Collect metrics
            gas_price = float(tx.get("gasPrice", 0))
            if gas_price > 0:
                gas_prices.append(gas_price)
            
            total_value += float(tx.get("value", 0))
            
            # Track function calls
            func_sig = tx.get("data", "")[:10]
            functions[func_sig] = functions.get(func_sig, 0) + 1
        
        # Calculate averages
        if gas_prices:
            analysis["average_gas_price"] = sum(gas_prices) / len(gas_prices)
        analysis["total_value"] = total_value
        
        # Detect patterns
        if len(transactions) > 3:
            analysis["patterns_detected"].append("Batch transaction pattern")
        
        # Check for repeated functions (potential sandwich attack indicator)
        for func, count in functions.items():
            if count > len(transactions) * 0.5:  # Same function > 50%
                analysis["anomalies"].append(
                    f"High repetition of function {func} ({count}/{len(transactions)})"
                )
                analysis["sequence_risk_score"] += 25
        
        # High total value check
        if total_value > 500:  # > 500 ETH equivalent
            analysis["anomalies"].append(
                f"Large total value in sequence: {total_value} ETH"
            )
            analysis["sequence_risk_score"] += 20
        
        analysis["sequence_risk_score"] = min(100, analysis["sequence_risk_score"])
        
        return analysis
    
    def _extract_basic_info(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic transaction information."""
        return {
            "from": tx_data.get("from", "unknown"),
            "to": tx_data.get("to", "unknown"),
            "value_eth": float(tx_data.get("value", 0)),
            "function_sig": tx_data.get("data", "0x")[:10]
        }
    
    def _analyze_gas(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gas pricing and limits."""
        gas_price = float(tx_data.get("gasPrice", 50))
        gas_limit = float(tx_data.get("gas", 21000))
        
        gas_cost = (gas_price / 1e9) * (gas_limit / 1e18)  # Rough ETH cost
        
        return {
            "gas_price_gwei": gas_price / 1e9,
            "gas_limit": gas_limit,
            "estimated_cost_eth": gas_cost,
            "efficiency": "High" if gas_limit < 50000 else "Normal" if gas_limit < 200000 else "Low"
        }
    
    def _analyze_value(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transaction value and thresholds."""
        value = float(tx_data.get("value", 0))
        
        return {
            "amount_eth": value,
            "is_high_value": value > 100,
            "is_suspicious_round": value % 10 == 0 and value > 50
        }
    
    def _is_suspicious_function(self, func_sig: str) -> bool:
        """Check if function signature matches known suspicious patterns."""
        suspicious_patterns = [
            "0xa9059cbb",  # Transfer (common in phishing)
            "0x095ea7b3",  # Approve unlimited
            "0xd0e30db0",  # WETH deposit/withdraw
        ]
        return func_sig in suspicious_patterns
    
    def _calculate_risk_level(self, score: int) -> str:
        """Convert safety score to risk level."""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"


# Example execution with real blockchain data
if __name__ == "__main__":
    analyzer = TransactionAnalyzer()
    
    print("=" * 60)
    print("FETCHING REAL TRANSACTION DATA")
    print("=" * 60)
    
    # Get recent real transactions
    recent_txs = analyzer.get_recent_transactions()
    
    print(f"Found {len(recent_txs)} recent transactions\n")
    
    # Analyze first real transaction
    test_tx = recent_txs[0]
    result = analyzer.analyze_transaction({
        "hash": test_tx.get("hash"),
        "from": test_tx.get("from"),
        "to": test_tx.get("to"),
        "value": int(test_tx.get("value", 0)) / 1e18,
        "gasPrice": int(test_tx.get("gasPrice", 0)),
        "gas": int(test_tx.get("gas", 0)),
        "data": test_tx.get("input", "0x")
    })
    
    print("=" * 60)
    print("REAL TRANSACTION ANALYSIS")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    
    # Analyze sequence of real transactions
    if len(recent_txs) > 1:
        print("\n" + "=" * 60)
        print("REAL SEQUENCE ANALYSIS")
        print("=" * 60)
        
        sequence_txs = []
        for tx in recent_txs[:5]:
            sequence_txs.append({
                "hash": tx.get("hash"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": int(tx.get("value", 0)) / 1e18,
                "gasPrice": int(tx.get("gasPrice", 0)),
                "gas": int(tx.get("gas", 0)),
                "data": tx.get("input", "0x")
            })
        
        sequence_result = analyzer.analyze_transaction_sequence(sequence_txs)
        print(json.dumps(sequence_result, indent=2))
