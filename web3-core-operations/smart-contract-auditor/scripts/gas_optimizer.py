#!/usr/bin/env python3
"""
Gas Optimizer Module
Optimizes smart contract interactions for gas efficiency.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class GasOptimizer:
    """Optimizes transactions for gas efficiency."""
    
    def __init__(self):
        self.base_gas_costs = {
            "transfer": 21000,
            "token_transfer": 65000,
            "swap": 150000,
            "complex_interaction": 300000
        }
        
        self.optimization_rules = {
            "batch_transfers": {
                "potential_savings": 0.4,  # 40% savings
                "recommendation": "Combine multiple transfers into batch"
            },
            "calldata_compression": {
                "potential_savings": 0.15,
                "recommendation": "Compress function parameters"
            },
            "state_batching": {
                "potential_savings": 0.30,
                "recommendation": "Batch state changes together"
            }
        }
    
    def estimate_gas_cost(self,
                         transaction_type: str,
                         transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate gas cost for a transaction.
        
        Args:
            transaction_type: Type of transaction (transfer, swap, etc.)
            transaction_data: Transaction parameters
            
        Returns:
            Gas estimation and cost analysis
        """
        estimation = {
            "transaction_type": transaction_type,
            "timestamp": datetime.now().isoformat(),
            "base_gas": 21000,
            "execution_gas": 0,
            "calldata_gas": 0,
            "total_gas_estimate": 0,
            "cost_analysis": {},
            "optimizations_available": []
        }
        
        # Base transaction cost
        if transaction_type in self.base_gas_costs:
            estimation["execution_gas"] = self.base_gas_costs[transaction_type]
        else:
            estimation["execution_gas"] = 100000  # Conservative estimate
        
        # Calldata costs
        data = transaction_data.get("data", "0x")
        calldata_gas = self._calculate_calldata_gas(data)
        estimation["calldata_gas"] = calldata_gas
        
        # Total estimate
        estimation["total_gas_estimate"] = (
            estimation["base_gas"] + 
            estimation["execution_gas"] + 
            estimation["calldata_gas"]
        )
        
        # Cost at different gas prices
        gas_prices = {"low": 20, "normal": 50, "high": 100}  # Gwei
        for tier, gwei in gas_prices.items():
            eth_cost = (estimation["total_gas_estimate"] * gwei) / 1e9
            estimation["cost_analysis"][tier] = {
                "gas_price_gwei": gwei,
                "cost_eth": eth_cost,
                "cost_usd_approx": eth_cost * 2500  # Rough ETH/USD
            }
        
        return estimation
    
    def optimize_transaction(self,
                            transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze transactions for optimization opportunities.
        
        Args:
            transactions: List of transactions to optimize
            
        Returns:
            Optimization recommendations and potential savings
        """
        optimization = {
            "input_transaction_count": len(transactions),
            "total_input_gas": 0,
            "opportunities": [],
            "potential_savings_gas": 0,
            "potential_savings_percent": 0,
            "optimized_gas": 0,
            "recommendations": []
        }
        
        # Calculate current total
        for tx in transactions:
            gas = float(tx.get("gas", 21000))
            optimization["total_input_gas"] += gas
        
        # Check for batching opportunity
        if len(transactions) > 1:
            # Check if all to same contract
            contracts = set(tx.get("to") for tx in transactions)
            if len(contracts) == 1:
                # Can batch!
                optimization["opportunities"].append({
                    "type": "batch_execution",
                    "savings_percent": 40,
                    "description": "All transactions target same contract"
                })
                optimization["potential_savings_gas"] += optimization["total_input_gas"] * 0.4
                optimization["recommendations"].append(
                    "Use multicall or batch contract method to process all 5 transactions"
                )
        
        # Check for similar transactions (could use batch transfer)
        transfer_txs = [
            tx for tx in transactions 
            if tx.get("data", "").startswith("0xa9059cbb")
        ]
        if len(transfer_txs) > 2:
            optimization["opportunities"].append({
                "type": "batch_transfers",
                "savings_percent": 35,
                "description": f"{len(transfer_txs)} similar transfers detected"
            })
            optimization["potential_savings_gas"] += (
                optimization["total_input_gas"] * 0.35
            )
            optimization["recommendations"].append(
                f"Batch {len(transfer_txs)} transfers with batch transfer contract"
            )
        
        # Calculate optimized total
        optimization["optimized_gas"] = (
            optimization["total_input_gas"] - 
            optimization["potential_savings_gas"]
        )
        
        if optimization["total_input_gas"] > 0:
            optimization["potential_savings_percent"] = (
                optimization["potential_savings_gas"] / 
                optimization["total_input_gas"] * 100
            )
        
        return optimization
    
    def analyze_gas_trends(self, 
                          transaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze gas usage trends over time.
        
        Args:
            transaction_history: Historical transaction data
            
        Returns:
            Trend analysis and predictions
        """
        if not transaction_history:
            return {"error": "No transaction history provided"}
        
        analysis = {
            "transaction_count": len(transaction_history),
            "gas_statistics": {
                "average": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "total": 0
            },
            "trends": [],
            "anomalies": []
        }
        
        # Extract gas values
        gas_values = [float(tx.get("gas", 0)) for tx in transaction_history]
        gas_values.sort()
        
        # Calculate statistics
        analysis["gas_statistics"]["total"] = sum(gas_values)
        analysis["gas_statistics"]["average"] = (
            analysis["gas_statistics"]["total"] / len(gas_values)
            if gas_values else 0
        )
        analysis["gas_statistics"]["min"] = gas_values[0] if gas_values else 0
        analysis["gas_statistics"]["max"] = gas_values[-1] if gas_values else 0
        
        # Median
        mid = len(gas_values) // 2
        if len(gas_values) % 2 == 0:
            analysis["gas_statistics"]["median"] = (
                (gas_values[mid-1] + gas_values[mid]) / 2
            )
        else:
            analysis["gas_statistics"]["median"] = gas_values[mid]
        
        # Detect trends
        if len(gas_values) > 3:
            recent_avg = sum(gas_values[-3:]) / 3
            earlier_avg = sum(gas_values[:3]) / 3
            
            if recent_avg > earlier_avg * 1.2:
                analysis["trends"].append({
                    "trend": "increasing_gas_usage",
                    "change_percent": ((recent_avg - earlier_avg) / earlier_avg) * 100,
                    "recommendation": "Recent transactions using more gas"
                })
            elif recent_avg < earlier_avg * 0.8:
                analysis["trends"].append({
                    "trend": "decreasing_gas_usage",
                    "change_percent": ((earlier_avg - recent_avg) / earlier_avg) * 100,
                    "recommendation": "Optimization efforts paying off"
                })
        
        # Detect anomalies
        mean = analysis["gas_statistics"]["average"]
        std_dev = (sum((x - mean) ** 2 for x in gas_values) / len(gas_values)) ** 0.5
        
        for i, gas in enumerate(gas_values):
            if abs(gas - mean) > 2 * std_dev:
                analysis["anomalies"].append({
                    "transaction_index": i,
                    "gas": gas,
                    "deviation_percent": ((gas - mean) / mean) * 100
                })
        
        return analysis
    
    def _calculate_calldata_gas(self, data: str) -> int:
        """
        Calculate gas cost for calldata.
        Zero bytes: 4 gas each
        Non-zero bytes: 16 gas each
        """
        if data == "0x":
            return 0
        
        data_bytes = data[2:]  # Remove 0x prefix
        zero_bytes = data_bytes.count("00") // 2
        non_zero_bytes = (len(data_bytes) // 2) - zero_bytes
        
        return (zero_bytes * 4) + (non_zero_bytes * 16)


# Example execution
if __name__ == "__main__":
    optimizer = GasOptimizer()
    
    print("=" * 60)
    print("GAS COST ESTIMATION")
    print("=" * 60)
    
    tx_data = {
        "data": "0xa9059cbb000000000000000000000000abcd1234",
        "to": "0x1234567890abcdef"
    }
    
    estimate = optimizer.estimate_gas_cost("token_transfer", tx_data)
    print(json.dumps(estimate, indent=2))
    
    # Test transaction optimization
    print("\n" + "=" * 60)
    print("TRANSACTION OPTIMIZATION")
    print("=" * 60)
    
    transactions = [
        {"gas": 65000, "to": "0x1234", "data": "0xa9059cbb..."},
        {"gas": 65000, "to": "0x1234", "data": "0xa9059cbb..."},
        {"gas": 65000, "to": "0x1234", "data": "0xa9059cbb..."},
        {"gas": 65000, "to": "0x1234", "data": "0xa9059cbb..."},
        {"gas": 65000, "to": "0x1234", "data": "0xa9059cbb..."}
    ]
    
    optimizations = optimizer.optimize_transaction(transactions)
    print(json.dumps(optimizations, indent=2))
    
    # Test gas trends
    print("\n" + "=" * 60)
    print("GAS USAGE TRENDS")
    print("=" * 60)
    
    history = [{"gas": g} for g in [50000, 52000, 51000, 75000, 73000, 72000]]
    trends = optimizer.analyze_gas_trends(history)
    print(json.dumps(trends, indent=2))
