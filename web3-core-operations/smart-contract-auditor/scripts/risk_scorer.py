#!/usr/bin/env python3
"""
Risk Scorer Module
Assigns risk scores to smart contract interactions.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class RiskScorer:
    """Calculates comprehensive risk scores for contract interactions."""
    
    def __init__(self):
        self.risk_factors = {
            "contract_age": {"weight": 0.15, "newer_is_riskier": True},
            "audit_status": {"weight": 0.25, "unaudited_risk": 40},
            "tvl_concentration": {"weight": 0.15, "high_concentration_risk": 30},
            "liquidity_score": {"weight": 0.12, "low_liquidity_risk": 20},
            "upgrade_risk": {"weight": 0.10, "proxy_risk": 25},
            "function_complexity": {"weight": 0.12, "complex_risk": 35},
            "interaction_history": {"weight": 0.11, "unusual_pattern_risk": 20}
        }
    
    def score_contract(self, contract_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for a contract.
        
        Args:
            contract_info: Contract details including age, audit status, TVL, etc.
            
        Returns:
            Risk assessment with component scores
        """
        assessment = {
            "contract": contract_info.get("address", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "risk_components": {},
            "total_risk_score": 0,
            "risk_level": "UNKNOWN",
            "overall_assessment": "",
            "recommendations": []
        }
        
        # Score contract age
        contract_age_days = contract_info.get("age_days", 30)
        age_risk = min(100, max(0, 100 - (contract_age_days * 2)))
        assessment["risk_components"]["contract_age"] = {
            "score": age_risk,
            "age_days": contract_age_days,
            "description": "Newer contracts have higher risk"
        }
        
        # Score audit status
        is_audited = contract_info.get("is_audited", False)
        audit_risk = 0 if is_audited else 40
        assessment["risk_components"]["audit_status"] = {
            "score": audit_risk,
            "is_audited": is_audited,
            "description": "Unaudited contracts have significant risk"
        }
        if not is_audited:
            assessment["recommendations"].append(
                "Contract lacks professional security audit - High risk"
            )
        
        # Score TVL concentration
        tvl = contract_info.get("tvl_millions", 10)
        tvl_risk = min(100, max(0, 50 - (tvl * 2)))  # Higher TVL = lower risk
        assessment["risk_components"]["tvl_concentration"] = {
            "score": tvl_risk,
            "tvl_millions": tvl,
            "description": "Lower TVL indicates higher concentration risk"
        }
        
        # Score liquidity
        has_good_liquidity = contract_info.get("has_good_liquidity", False)
        liquidity_risk = 0 if has_good_liquidity else 20
        assessment["risk_components"]["liquidity"] = {
            "score": liquidity_risk,
            "has_good_liquidity": has_good_liquidity,
            "description": "Poor liquidity increases slippage risk"
        }
        
        # Score upgrade risk (proxy)
        is_upgradeable = contract_info.get("is_upgradeable", False)
        upgrade_risk = 25 if is_upgradeable else 0
        assessment["risk_components"]["upgrade_risk"] = {
            "score": upgrade_risk,
            "is_upgradeable": is_upgradeable,
            "description": "Upgradeable proxies introduce admin risk"
        }
        if is_upgradeable:
            assessment["recommendations"].append(
                "Contract is upgradeable (proxy pattern) - Admin risk present"
            )
        
        # Score function complexity
        function_count = contract_info.get("function_count", 10)
        complexity_risk = min(100, function_count * 3)
        assessment["risk_components"]["function_complexity"] = {
            "score": complexity_risk,
            "function_count": function_count,
            "description": "More functions = more attack surface"
        }
        
        # Score interaction history
        unusual_interactions = contract_info.get("unusual_interaction_count", 0)
        history_risk = min(100, unusual_interactions * 5)
        assessment["risk_components"]["interaction_history"] = {
            "score": history_risk,
            "unusual_count": unusual_interactions,
            "description": "Unusual patterns suggest potential issues"
        }
        
        # Calculate weighted total
        total = 0
        weight_sum = 0
        
        component_map = {
            "contract_age": ("contract_age", age_risk),
            "audit_status": ("audit_status", audit_risk),
            "tvl_concentration": ("tvl_concentration", tvl_risk),
            "liquidity_score": ("liquidity", liquidity_risk),
            "upgrade_risk": ("upgrade_risk", upgrade_risk),
            "function_complexity": ("function_complexity", complexity_risk),
            "interaction_history": ("interaction_history", history_risk)
        }
        
        for factor, (comp_name, score) in component_map.items():
            weight = self.risk_factors[factor]["weight"]
            total += score * weight
            weight_sum += weight
        
        assessment["total_risk_score"] = round(total / weight_sum, 2) if weight_sum > 0 else 0
        assessment["risk_level"] = self._score_to_level(assessment["total_risk_score"])
        
        # Overall assessment
        if assessment["total_risk_score"] < 20:
            assessment["overall_assessment"] = "Low risk - Safe to interact"
        elif assessment["total_risk_score"] < 50:
            assessment["overall_assessment"] = "Moderate risk - Proceed with caution"
        elif assessment["total_risk_score"] < 75:
            assessment["overall_assessment"] = "High risk - Not recommended"
        else:
            assessment["overall_assessment"] = "Critical risk - Avoid interaction"
        
        return assessment
    
    def score_interaction(self,
                         sender: str,
                         contract: str,
                         function: str,
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score a specific interaction for risk.
        
        Args:
            sender: Address initiating interaction
            contract: Target contract
            function: Function being called
            parameters: Function parameters
            
        Returns:
            Interaction-specific risk assessment
        """
        interaction_score = {
            "sender": sender,
            "contract": contract,
            "function": function,
            "timestamp": datetime.now().isoformat(),
            "risk_factors": {},
            "interaction_risk": 0,
            "risk_level": "UNKNOWN",
            "safety_verdict": ""
        }
        
        # Check sender reputation
        is_contract = sender.startswith("0x") and len(sender) == 42
        sender_risk = 15 if is_contract else 0
        interaction_score["risk_factors"]["sender_type"] = {
            "score": sender_risk,
            "is_contract": is_contract
        }
        
        # Check function risk
        high_risk_functions = {
            "0x095ea7b3": 40,  # approve
            "0x23b872dd": 20,  # transferFrom
            "0x1cff79cd": 35,  # execute
        }
        function_risk = high_risk_functions.get(function, 10)
        interaction_score["risk_factors"]["function_risk"] = {
            "score": function_risk,
            "function": function
        }
        
        # Check parameters
        param_risk = 0
        if parameters:
            if parameters.get("recipient") == "0x0":
                param_risk += 25
            if parameters.get("value", 0) > 100:
                param_risk += 10
        
        interaction_score["risk_factors"]["parameter_risk"] = {
            "score": min(100, param_risk),
            "parameters": parameters
        }
        
        # Total interaction risk
        total_param_risk = sum(
            f["score"] for f in interaction_score["risk_factors"].values()
        )
        interaction_score["interaction_risk"] = min(100, total_param_risk)
        interaction_score["risk_level"] = self._score_to_level(
            interaction_score["interaction_risk"]
        )
        
        # Safety verdict
        if interaction_score["interaction_risk"] < 30:
            interaction_score["safety_verdict"] = "Proceed - Low risk interaction"
        elif interaction_score["interaction_risk"] < 60:
            interaction_score["safety_verdict"] = "Caution - Verify transaction details"
        else:
            interaction_score["safety_verdict"] = "NOT RECOMMENDED - High risk detected"
        
        return interaction_score
    
    def compare_contracts(self, contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare risk scores across multiple contracts.
        
        Args:
            contracts: List of contracts to compare
            
        Returns:
            Comparative risk analysis and ranking
        """
        comparison = {
            "contract_count": len(contracts),
            "contracts": [],
            "ranking": [],
            "risk_distribution": {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        }
        
        # Score each contract
        for contract in contracts:
            score = self.score_contract(contract)
            comparison["contracts"].append(score)
            
            # Count distribution
            level = score["risk_level"]
            if level == "LOW":
                comparison["risk_distribution"]["low"] += 1
            elif level == "MODERATE":
                comparison["risk_distribution"]["moderate"] += 1
            elif level == "HIGH":
                comparison["risk_distribution"]["high"] += 1
            elif level == "CRITICAL":
                comparison["risk_distribution"]["critical"] += 1
        
        # Create ranking
        comparison["ranking"] = sorted(
            comparison["contracts"],
            key=lambda x: x["total_risk_score"]
        )
        
        return comparison
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level."""
        if score < 25:
            return "LOW"
        elif score < 50:
            return "MODERATE"
        elif score < 75:
            return "HIGH"
        else:
            return "CRITICAL"


# Example execution
if __name__ == "__main__":
    scorer = RiskScorer()
    
    print("=" * 60)
    print("CONTRACT RISK ASSESSMENT")
    print("=" * 60)
    
    contract_info = {
        "address": "0x1234567890abcdef1234567890abcdef12345678",
        "age_days": 180,
        "is_audited": False,
        "tvl_millions": 50,
        "has_good_liquidity": True,
        "is_upgradeable": False,
        "function_count": 15,
        "unusual_interaction_count": 2
    }
    
    risk_score = scorer.score_contract(contract_info)
    print(json.dumps(risk_score, indent=2))
    
    # Test interaction risk
    print("\n" + "=" * 60)
    print("INTERACTION RISK ASSESSMENT")
    print("=" * 60)
    
    interaction = scorer.score_interaction(
        "0xabcdef1234567890abcdef1234567890abcdef12",
        "0x1234567890abcdef1234567890abcdef12345678",
        "0x095ea7b3",  # approve
        {"value": 150, "recipient": "0xdeadbeef"}
    )
    
    print(json.dumps(interaction, indent=2))
