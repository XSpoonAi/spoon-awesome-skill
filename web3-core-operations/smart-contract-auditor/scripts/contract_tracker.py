#!/usr/bin/env python3
"""
Contract Tracker Module
Tracks and monitors smart contract interactions over time.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class ContractTracker:
    """Tracks and analyzes smart contract interactions."""
    
    def __init__(self):
        self.contract_profiles = {}
        self.interaction_history = []
        self.alerts = []
    
    def track_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track a single contract interaction.
        
        Args:
            interaction: Interaction data
            
        Returns:
            Tracking confirmation with assigned ID
        """
        interaction_id = f"int_{len(self.interaction_history) + 1:06d}"
        
        tracked = {
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "interaction": interaction,
            "status": "tracked",
            "profile_created": False
        }
        
        contract = interaction.get("contract")
        if contract not in self.contract_profiles:
            self.contract_profiles[contract] = {
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "interaction_count": 0,
                "functions_called": set(),
                "senders": set(),
                "total_value": 0
            }
            tracked["profile_created"] = True
        else:
            self.contract_profiles[contract]["last_seen"] = datetime.now().isoformat()
        
        # Update profile
        profile = self.contract_profiles[contract]
        profile["interaction_count"] += 1
        profile["functions_called"].add(interaction.get("function", "unknown"))
        profile["senders"].add(interaction.get("sender", "unknown"))
        profile["total_value"] += float(interaction.get("value", 0))
        
        self.interaction_history.append(interaction)
        
        return tracked
    
    def get_contract_profile(self, contract_address: str) -> Dict[str, Any]:
        """
        Get detailed profile of a tracked contract.
        
        Args:
            contract_address: Contract address to profile
            
        Returns:
            Comprehensive contract profile
        """
        if contract_address not in self.contract_profiles:
            return {"error": f"Contract {contract_address} not tracked"}
        
        profile_data = self.contract_profiles[contract_address]
        
        profile = {
            "contract": contract_address,
            "first_interaction": profile_data.get("first_seen"),
            "last_interaction": profile_data.get("last_seen"),
            "total_interactions": profile_data.get("interaction_count", 0),
            "unique_functions": len(profile_data.get("functions_called", set())),
            "functions": list(profile_data.get("functions_called", set())),
            "unique_senders": len(profile_data.get("senders", set())),
            "senders": list(profile_data.get("senders", set())),
            "total_value_transacted": profile_data.get("total_value", 0),
            "average_value_per_transaction": 0
        }
        
        if profile["total_interactions"] > 0:
            profile["average_value_per_transaction"] = (
                profile["total_value_transacted"] / profile["total_interactions"]
            )
        
        return profile
    
    def detect_anomalies(self, 
                        contract_address: str,
                        window_hours: int = 24) -> Dict[str, Any]:
        """
        Detect anomalies in contract interaction patterns.
        
        Args:
            contract_address: Contract to analyze
            window_hours: Time window for analysis
            
        Returns:
            Anomaly detection results
        """
        anomalies = {
            "contract": contract_address,
            "analysis_window_hours": window_hours,
            "detected_anomalies": [],
            "anomaly_score": 0,
            "recommendations": []
        }
        
        profile = self.get_contract_profile(contract_address)
        if "error" in profile:
            return profile
        
        # Check for unusual activity
        if profile["total_interactions"] > 50:
            anomalies["detected_anomalies"].append({
                "type": "high_interaction_frequency",
                "count": profile["total_interactions"],
                "severity": "MEDIUM"
            })
            anomalies["anomaly_score"] += 15
        
        # Check for many unique senders
        if profile["unique_senders"] > profile["total_interactions"] * 0.7:
            anomalies["detected_anomalies"].append({
                "type": "many_unique_senders",
                "ratio": profile["unique_senders"] / profile["total_interactions"],
                "severity": "MEDIUM"
            })
            anomalies["anomaly_score"] += 10
        
        # Check for function concentration
        if profile["unique_functions"] == 1 and profile["total_interactions"] > 5:
            anomalies["detected_anomalies"].append({
                "type": "single_function_repetition",
                "function": list(profile["functions"])[0],
                "count": profile["total_interactions"],
                "severity": "MEDIUM"
            })
            anomalies["anomaly_score"] += 10
            anomalies["recommendations"].append(
                "Multiple calls to same function - possible automated attack"
            )
        
        # Check for large value anomalies
        avg_value = profile["average_value_per_transaction"]
        if avg_value > 100:
            anomalies["detected_anomalies"].append({
                "type": "high_average_value",
                "avg_value_eth": avg_value,
                "severity": "HIGH"
            })
            anomalies["anomaly_score"] += 20
            anomalies["recommendations"].append(
                "Large transaction values detected - verify legitimacy"
            )
        
        return anomalies
    
    def get_interaction_summary(self, 
                               contract_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of all tracked interactions.
        
        Args:
            contract_address: Optional - filter by contract
            
        Returns:
            Summary statistics of interactions
        """
        summary = {
            "total_contracts_tracked": len(self.contract_profiles),
            "total_interactions": len(self.interaction_history),
            "timestamp": datetime.now().isoformat(),
            "contracts": []
        }
        
        # Get data for each contract
        for contract_addr, profile_data in self.contract_profiles.items():
            if contract_address and contract_addr != contract_address:
                continue
            
            contract_summary = {
                "address": contract_addr,
                "interactions": profile_data.get("interaction_count", 0),
                "functions": len(profile_data.get("functions_called", set())),
                "senders": len(profile_data.get("senders", set())),
                "total_value": profile_data.get("total_value", 0),
                "risk_flag": profile_data.get("interaction_count", 0) > 20
            }
            summary["contracts"].append(contract_summary)
        
        # Sort by interaction count
        summary["contracts"].sort(
            key=lambda x: x["interactions"],
            reverse=True
        )
        
        return summary
    
    def generate_report(self, 
                       contract_address: str,
                       include_anomalies: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive report for a contract.
        
        Args:
            contract_address: Contract to report on
            include_anomalies: Whether to include anomaly detection
            
        Returns:
            Detailed contract monitoring report
        """
        report = {
            "contract": contract_address,
            "generated_at": datetime.now().isoformat(),
            "profile": self.get_contract_profile(contract_address),
            "anomalies": {},
            "alerts": [],
            "recommendations": []
        }
        
        if "error" in report["profile"]:
            return report
        
        # Add anomalies if requested
        if include_anomalies:
            report["anomalies"] = self.detect_anomalies(contract_address)
        
        # Generate alerts
        profile = report["profile"]
        
        if profile["total_interactions"] < 5:
            report["alerts"].append({
                "level": "INFO",
                "message": "New contract with limited interaction history"
            })
        
        if profile["unique_senders"] == 1:
            report["alerts"].append({
                "level": "INFO",
                "message": "All interactions from single sender"
            })
        
        if profile["total_value_transacted"] > 1000:
            report["alerts"].append({
                "level": "WARNING",
                "message": f"High total value transacted: {profile['total_value_transacted']} ETH"
            })
        
        # Recommendations
        if profile["total_interactions"] > 100:
            report["recommendations"].append(
                "Contract has very high interaction frequency - monitor closely"
            )
        
        return report


# Example execution
if __name__ == "__main__":
    tracker = ContractTracker()
    
    print("=" * 60)
    print("CONTRACT TRACKING")
    print("=" * 60)
    
    # Track some interactions
    interactions = [
        {
            "contract": "0x1234567890abcdef1234567890abcdef12345678",
            "sender": "0xabcd1234",
            "function": "0xa9059cbb",
            "value": 50
        },
        {
            "contract": "0x1234567890abcdef1234567890abcdef12345678",
            "sender": "0xabcd1234",
            "function": "0xa9059cbb",
            "value": 45
        },
        {
            "contract": "0x1234567890abcdef1234567890abcdef12345678",
            "sender": "0xabcd1234",
            "function": "0xa9059cbb",
            "value": 55
        }
    ]
    
    for interaction in interactions:
        result = tracker.track_interaction(interaction)
        print(f"Tracked: {result['interaction_id']}")
    
    # Get profile
    print("\n" + "=" * 60)
    print("CONTRACT PROFILE")
    print("=" * 60)
    
    profile = tracker.get_contract_profile("0x1234567890abcdef1234567890abcdef12345678")
    print(json.dumps(profile, indent=2))
    
    # Detect anomalies
    print("\n" + "=" * 60)
    print("ANOMALY DETECTION")
    print("=" * 60)
    
    anomalies = tracker.detect_anomalies("0x1234567890abcdef1234567890abcdef12345678")
    print(json.dumps(anomalies, indent=2))
    
    # Generate report
    print("\n" + "=" * 60)
    print("MONITORING REPORT")
    print("=" * 60)
    
    report = tracker.generate_report("0x1234567890abcdef1234567890abcdef12345678")
    print(json.dumps(report, indent=2, default=str))
