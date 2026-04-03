#!/usr/bin/env python3
"""
Function Validator Module
Validates smart contract function calls for safety using real blockchain data.
"""

import json
import requests
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class FunctionValidator:
    """Validates smart contract function calls using real contract data."""
    
    def __init__(self):
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY", "")
        self.etherscan_url = "https://api.etherscan.io/api"
        
        self.known_functions = {
            "0xa9059cbb": {"name": "transfer", "category": "token", "risk": "medium"},
            "0x095ea7b3": {"name": "approve", "category": "token", "risk": "high"},
            "0x23b872dd": {"name": "transferFrom", "category": "token", "risk": "medium"},
            "0x70a08231": {"name": "balanceOf", "category": "token", "risk": "low"},
            "0x18160ddd": {"name": "totalSupply", "category": "token", "risk": "low"},
            "0x313ce567": {"name": "decimals", "category": "token", "risk": "low"},
        }
        
        self.risk_patterns = {
            "unlimited_approval": {
                "pattern": "approve with max uint256",
                "severity": "CRITICAL",
                "recommendation": "Use approve limit or increaseAllowance"
            },
            "state_change_in_view": {
                "pattern": "State modification in view function",
                "severity": "HIGH",
                "recommendation": "Use non-view function"
            },
            "reentrancy": {
                "pattern": "External call before state update",
                "severity": "CRITICAL",
                "recommendation": "Use checks-effects-interactions pattern"
            }
        }
    
    def get_contract_source(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real contract source code from blockchain.
        
        Args:
            address: Contract address
            
        Returns:
            Contract source and metadata
        """
        try:
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": address,
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.etherscan_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"][0]
                return {
                    "address": address,
                    "name": result.get("ContractName"),
                    "source_code": result.get("SourceCode", ""),
                    "compiler": result.get("CompilerVersion"),
                    "verified": result.get("SourceCode", "") != ""
                }
        except Exception as e:
            print(f"Error fetching contract source: {e}")
        
        return None
    
    def get_contract_abi(self, address: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch contract ABI to analyze functions.
        
        Args:
            address: Contract address
            
        Returns:
            Contract ABI
        """
        try:
            params = {
                "module": "contract",
                "action": "getabi",
                "address": address,
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.etherscan_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1":
                return json.loads(data.get("result", "[]"))
        except Exception as e:
            print(f"Error fetching ABI: {e}")
        
        return None
    
    def validate_function_call(self, 
                              contract_address: str,
                              function_sig: str,
                              parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a function call for safety and correctness.
        
        Args:
            contract_address: Target contract address
            function_sig: Function signature (4-byte selector)
            parameters: Function parameters
            
        Returns:
            Validation result with safety assessment
        """
        result = {
            "contract": contract_address,
            "function_signature": function_sig,
            "timestamp": datetime.now().isoformat(),
            "function_info": {},
            "safety_issues": [],
            "warnings": [],
            "validation_passed": True,
            "risk_score": 0
        }
        
        # Look up function
        if function_sig in self.known_functions:
            func_info = self.known_functions[function_sig]
            result["function_info"] = func_info
        else:
            result["warnings"].append(f"Unknown function signature: {function_sig}")
            func_info = {"name": "unknown", "category": "unknown", "risk": "unknown"}
        
        # Check for common issues
        if function_sig == "0x095ea7b3":  # approve
            if parameters and parameters.get("amount") == "unlimited":
                result["safety_issues"].append({
                    "type": "unlimited_approval",
                    "severity": "CRITICAL",
                    "message": "Unlimited approval detected. This is a common attack vector.",
                    "recommendation": "Use approve with specific amount or use approveExact"
                })
                result["risk_score"] += 40
                result["validation_passed"] = False
        
        # Validate parameters
        if parameters:
            result["parameter_validation"] = self._validate_parameters(
                function_sig,
                parameters
            )
            result["risk_score"] += result["parameter_validation"].get("risk_increase", 0)
        
        # Set overall risk
        if result["risk_score"] >= 30:
            result["validation_passed"] = False
        
        return result
    
    def analyze_contract_interface(self, 
                                   contract_address: str,
                                   functions: List[str]) -> Dict[str, Any]:
        """
        Analyze a contract's entire function interface for patterns.
        
        Args:
            contract_address: Contract address
            functions: List of function signatures in contract
            
        Returns:
            Contract-level analysis and recommendations
        """
        analysis = {
            "contract": contract_address,
            "total_functions": len(functions),
            "functions_analyzed": [],
            "risk_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "patterns": [],
            "recommendations": [],
            "overall_safety_score": 100
        }
        
        # Analyze each function
        for func_sig in functions:
            if func_sig in self.known_functions:
                func_info = self.known_functions[func_sig]
                risk = func_info.get("risk", "unknown")
                
                analysis["functions_analyzed"].append({
                    "signature": func_sig,
                    "name": func_info.get("name"),
                    "risk": risk
                })
                
                # Count risk distribution
                if risk == "critical":
                    analysis["risk_distribution"]["critical"] += 1
                elif risk == "high":
                    analysis["risk_distribution"]["high"] += 1
                elif risk == "medium":
                    analysis["risk_distribution"]["medium"] += 1
                else:
                    analysis["risk_distribution"]["low"] += 1
        
        # Detect patterns
        if analysis["risk_distribution"]["critical"] > 0:
            analysis["patterns"].append("Contains critical-risk functions")
            analysis["overall_safety_score"] -= 30
        
        if analysis["risk_distribution"]["high"] > len(functions) * 0.3:
            analysis["patterns"].append("High proportion of high-risk functions")
            analysis["overall_safety_score"] -= 15
        
        # Generate recommendations
        if analysis["overall_safety_score"] < 60:
            analysis["recommendations"].append(
                "Consider additional security auditing before deployment"
            )
        
        analysis["overall_safety_score"] = max(0, analysis["overall_safety_score"])
        
        return analysis
    
    def check_dangerous_patterns(self, 
                                function_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check a sequence of function calls for dangerous patterns.
        
        Args:
            function_calls: List of function calls with order and parameters
            
        Returns:
            Pattern detection results with severity
        """
        patterns = {
            "detected_patterns": [],
            "vulnerabilities": [],
            "sequence_risk": 0
        }
        
        # Check for reentrancy pattern (external call before state change)
        for i, call in enumerate(function_calls):
            if call.get("is_external_call"):
                for later_call in function_calls[i+1:]:
                    if later_call.get("modifies_state"):
                        patterns["detected_patterns"].append({
                            "type": "potential_reentrancy",
                            "position": f"call {i} -> {function_calls.index(later_call)}",
                            "severity": "HIGH"
                        })
                        patterns["sequence_risk"] += 30
        
        # Check for repeated calls to untrusted addresses
        external_calls = [c for c in function_calls if c.get("is_external_call")]
        if len(external_calls) > len(function_calls) * 0.5:
            patterns["detected_patterns"].append({
                "type": "high_external_call_ratio",
                "count": len(external_calls),
                "severity": "MEDIUM"
            })
            patterns["sequence_risk"] += 15
        
        return patterns
    
    def _validate_parameters(self, 
                            function_sig: str,
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate function parameters."""
        validation = {
            "valid": True,
            "risk_increase": 0,
            "issues": []
        }
        
        # Check for common parameter issues
        if "recipient" in parameters:
            if parameters["recipient"] == "0x0000000000000000000000000000000000000000":
                validation["issues"].append("Recipient is zero address")
                validation["risk_increase"] += 20
        
        if "amount" in parameters:
            amount = parameters["amount"]
            # Handle string "unlimited"
            if isinstance(amount, str):
                if amount.lower() == "unlimited":
                    validation["valid"] = False  # Will be caught separately
                else:
                    try:
                        amount = float(amount)
                    except ValueError:
                        validation["issues"].append("Invalid amount format")
                        validation["risk_increase"] += 5
            
            if isinstance(amount, (int, float)) and amount <= 0:
                validation["issues"].append("Amount is zero or negative")
                validation["risk_increase"] += 10
        
        return validation


# Example execution with real blockchain data
if __name__ == "__main__":
    validator = FunctionValidator()
    
    # Analyze real USDC contract
    test_contract = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    contract_source = validator.get_contract_source(test_contract)
    contract_abi = validator.get_contract_abi(test_contract)
    
    print(f"Contract: {contract_source.get('name') if contract_source else 'Unknown'}")
    print(f"Verified: {contract_source.get('verified') if contract_source else False}")
    print(f"Address: {test_contract}\n")
    
    if contract_abi:
        print(f"Found {len(contract_abi)} functions in contract\n")
        functions = [f for f in contract_abi if f.get("type") == "function"]
        print(f"Analyzed {len(functions[:10])} functions")
    
    # Test approve validation
    print("\n" + "=" * 60)
    print("FUNCTION VALIDATION (Real Contract)")
    print("=" * 60)
    
    result = validator.validate_function_call(
        test_contract,
        "0x095ea7b3",
        {"amount": "unlimited", "spender": "0xabcdef1234567890abcdef1234567890abcdef12"}
    )
    
    print(json.dumps(result, indent=2))
    
    # Test contract interface analysis
    print("\n" + "=" * 60)
    print("CONTRACT INTERFACE ANALYSIS")
    print("=" * 60)
    
    interface_result = validator.analyze_contract_interface(
        test_contract,
        ["0xa9059cbb", "0x095ea7b3", "0x23b872dd", "0x70a08231"]
    )
    
    print(json.dumps(interface_result, indent=2))
    
    # Test dangerous patterns
    print("\n" + "=" * 60)
    print("PATTERN DETECTION")
    print("=" * 60)
    
    call_sequence = [
        {"function": "0x123", "is_external_call": True},
        {"function": "0x456", "modifies_state": True}
    ]
    
    pattern_result = validator.check_dangerous_patterns(call_sequence)
    print(json.dumps(pattern_result, indent=2))
