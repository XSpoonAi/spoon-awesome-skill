#!/usr/bin/env python3
"""
Bridge TVL Monitor
Monitors Total Value Locked in bridge contracts and detects unusual outflows
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class TVLAlert:
    """Alert for TVL changes"""
    bridge_name: str
    chain: str
    tvl_change_percent: float
    tvl_change_usd: float
    current_tvl: float
    previous_tvl: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp: str
    message: str


class BridgeTVLMonitor:
    """
    Monitors TVL changes across bridge protocols to detect potential security risks.
    Large, sudden TVL decreases may indicate:
    - Bridge exploit in progress
    - Mass withdrawals due to security concerns
    - Liquidity drainage before announced issue
    """
    
    def __init__(self):
        self.defillama_api = "https://api.llama.fi"
        self.bridges_api = "https://bridges.llama.fi"
        self.bridge_contracts = {
            "ethereum": {
                "stargate": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97",
                "portal": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585",  # Wormhole Portal
                "across": "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5",
                "hop": "0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a",
            },
            "arbitrum": {
                "stargate": "0x352d8275AAE3e0c2404d9f68f6cEE084B8d0A89e",
                "across": "0xe35e9842fceaCA96570B734083f4a58e8F7C5f2A",
            },
            "optimism": {
                "stargate": "0xB0D502E938ed5f4df2E681fE6E419ff29631d62b",
                "across": "0xa420b2d1c0841415A695b81E5B867BCD07Dff8C9",
            }
        }
        
        # Thresholds for alerts
        self.alert_thresholds = {
            "CRITICAL": 20.0,  # >20% TVL drop
            "HIGH": 10.0,      # >10% TVL drop
            "MEDIUM": 5.0,     # >5% TVL drop
            "LOW": 2.0,        # >2% TVL drop
        }
    
    def get_all_bridges(self) -> List[Dict[str, Any]]:
        """
        Fetch all bridge protocols from DefiLlama.
        
        Returns:
            List of bridge protocols with current TVL data
        """
        try:
            url = f"{self.bridges_api}/bridges"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                bridges = data.get("bridges", [])
                
                # Filter for major bridge protocols
                major_bridges = []
                for bridge in bridges:
                    if bridge.get("displayName") in [
                        "Stargate", "Wormhole", "Portal", "Across", 
                        "Hop Protocol", "Multichain", "Synapse", "Celer cBridge"
                    ]:
                        major_bridges.append(bridge)
                
                return major_bridges
            else:
                print(f"Warning: DefiLlama API returned status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching bridges: {e}")
            return []
    
    def get_bridge_details(self, bridge_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed TVL history and chain breakdown for a specific bridge.
        
        Args:
            bridge_id: Bridge protocol ID (e.g., "stargate", "wormhole", "portal")
            
        Returns:
            Bridge details with TVL history
        """
        try:
            # Use protocol endpoint which has better data
            url = f"{self.defillama_api}/protocol/{bridge_id}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Bridge API returned status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching bridge details for {bridge_id}: {e}")
            return None
    
    def calculate_tvl_change(
        self,
        bridge_data: Dict[str, Any],
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate TVL change over specified time window.
        
        Args:
            bridge_data: Bridge details from API
            time_window_hours: Time window for comparison (default 24h)
            
        Returns:
            TVL change analysis
        """
        try:
            # Get current TVL from currentChainTvls
            current_chain_tvls = bridge_data.get("currentChainTvls", {})
            total_current_tvl = 0
            chain_changes = {}
            
            for chain, value in current_chain_tvls.items():
                if chain != 'total' and isinstance(value, (int, float)):
                    total_current_tvl += value
            
            # Get historical TVL data
            tvl_history = bridge_data.get("tvl", [])
            
            if len(tvl_history) < 2:
                # Not enough historical data
                return {
                    "bridge_name": bridge_data.get("name", "Unknown"),
                    "current_tvl": total_current_tvl,
                    "previous_tvl": total_current_tvl,
                    "change_usd": 0,
                    "change_percent": 0,
                    "time_window_hours": time_window_hours,
                    "chain_breakdown": {},
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get most recent TVL point
            current_point = tvl_history[-1]
            current_tvl = current_point.get("totalLiquidityUSD", total_current_tvl)
            
            # Find TVL data point closest to time_window_hours ago
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            previous_tvl = current_tvl
            for point in reversed(tvl_history[:-1]):
                point_timestamp = int(point.get("date", 0))
                if point_timestamp <= cutoff_timestamp:
                    previous_tvl = point.get("totalLiquidityUSD", 0)
                    break
            
            # Calculate total change
            if previous_tvl > 0:
                total_change_percent = ((current_tvl - previous_tvl) / previous_tvl) * 100
            else:
                total_change_percent = 0
            
            return {
                "bridge_name": bridge_data.get("name", bridge_data.get("slug", "Unknown")),
                "current_tvl": current_tvl,
                "previous_tvl": previous_tvl,
                "change_usd": current_tvl - previous_tvl,
                "change_percent": total_change_percent,
                "time_window_hours": time_window_hours,
                "chain_breakdown": chain_changes,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating TVL change: {e}")
            return {}
    
    def assess_risk_level(self, tvl_change_percent: float) -> str:
        """
        Assess risk level based on TVL change.
        
        Args:
            tvl_change_percent: Percentage change in TVL (negative = decrease)
            
        Returns:
            Risk level (SAFE, LOW, MEDIUM, HIGH, CRITICAL)
        """
        # Negative change = TVL decrease = potential risk
        if tvl_change_percent >= 0:
            return "SAFE"
        
        abs_change = abs(tvl_change_percent)
        
        if abs_change >= self.alert_thresholds["CRITICAL"]:
            return "CRITICAL"
        elif abs_change >= self.alert_thresholds["HIGH"]:
            return "HIGH"
        elif abs_change >= self.alert_thresholds["MEDIUM"]:
            return "MEDIUM"
        elif abs_change >= self.alert_thresholds["LOW"]:
            return "LOW"
        else:
            return "SAFE"
    
    def generate_alert(
        self,
        bridge_name: str,
        tvl_analysis: Dict[str, Any],
        risk_level: str
    ) -> Optional[TVLAlert]:
        """
        Generate alert if risk level warrants it.
        
        Args:
            bridge_name: Name of the bridge
            tvl_analysis: TVL analysis results
            risk_level: Assessed risk level
            
        Returns:
            TVLAlert if alert needed, None otherwise
        """
        if risk_level == "SAFE":
            return None
        
        change_percent = tvl_analysis.get("change_percent", 0)
        change_usd = tvl_analysis.get("change_usd", 0)
        current_tvl = tvl_analysis.get("current_tvl", 0)
        previous_tvl = tvl_analysis.get("previous_tvl", 0)
        
        # Generate appropriate message
        messages = {
            "CRITICAL": f"🚨 CRITICAL: {bridge_name} TVL dropped by {abs(change_percent):.2f}% (${abs(change_usd):,.0f}). Potential exploit or mass exodus!",
            "HIGH": f"⚠️ HIGH RISK: {bridge_name} TVL decreased by {abs(change_percent):.2f}% (${abs(change_usd):,.0f}). Monitor closely.",
            "MEDIUM": f"⚡ MEDIUM RISK: {bridge_name} TVL down {abs(change_percent):.2f}% (${abs(change_usd):,.0f}). Unusual activity detected.",
            "LOW": f"ℹ️ LOW RISK: {bridge_name} TVL decreased by {abs(change_percent):.2f}%. Within normal fluctuation range."
        }
        
        # Find most affected chain
        most_affected_chain = "Unknown"
        max_chain_drop = 0
        
        chain_breakdown = tvl_analysis.get("chain_breakdown", {})
        for chain, data in chain_breakdown.items():
            chain_change = data.get("change_percent", 0)
            if chain_change < max_chain_drop:
                max_chain_drop = chain_change
                most_affected_chain = chain
        
        return TVLAlert(
            bridge_name=bridge_name,
            chain=most_affected_chain,
            tvl_change_percent=change_percent,
            tvl_change_usd=change_usd,
            current_tvl=current_tvl,
            previous_tvl=previous_tvl,
            severity=risk_level,
            timestamp=datetime.now().isoformat(),
            message=messages.get(risk_level, "TVL change detected")
        )
    
    def monitor_bridge(
        self,
        bridge_id: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Monitor a specific bridge for TVL changes and generate alerts.
        
        Args:
            bridge_id: Bridge protocol ID
            time_window_hours: Time window for analysis
            
        Returns:
            Monitoring results with risk assessment
        """
        # Get bridge details
        bridge_data = self.get_bridge_details(bridge_id)
        if not bridge_data:
            return {
                "error": f"Could not fetch data for bridge: {bridge_id}",
                "bridge_id": bridge_id
            }
        
        # Calculate TVL change
        tvl_analysis = self.calculate_tvl_change(bridge_data, time_window_hours)
        if not tvl_analysis:
            return {
                "error": "Could not calculate TVL change",
                "bridge_id": bridge_id
            }
        
        # Assess risk
        risk_level = self.assess_risk_level(tvl_analysis.get("change_percent", 0))
        
        # Generate alert if needed
        alert = self.generate_alert(
            bridge_data.get("name", bridge_id),
            tvl_analysis,
            risk_level
        )
        
        return {
            "bridge_id": bridge_id,
            "bridge_name": bridge_data.get("name", bridge_id),
            "risk_level": risk_level,
            "tvl_analysis": tvl_analysis,
            "alert": {
                "severity": alert.severity,
                "message": alert.message,
                "chain": alert.chain,
                "timestamp": alert.timestamp
            } if alert else None,
            "recommendation": self._get_recommendation(risk_level),
            "timestamp": datetime.now().isoformat()
        }
    
    def monitor_all_bridges(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Monitor all major bridges and return comprehensive report.
        
        Args:
            time_window_hours: Time window for analysis
            
        Returns:
            Comprehensive monitoring report
        """
        bridges = self.get_all_bridges()
        results = []
        alerts = []
        
        for bridge in bridges:
            bridge_id = bridge.get("id")
            if bridge_id:
                result = self.monitor_bridge(bridge_id, time_window_hours)
                results.append(result)
                
                if result.get("alert"):
                    alerts.append(result["alert"])
        
        # Summarize
        critical_count = sum(1 for r in results if r.get("risk_level") == "CRITICAL")
        high_count = sum(1 for r in results if r.get("risk_level") == "HIGH")
        medium_count = sum(1 for r in results if r.get("risk_level") == "MEDIUM")
        
        return {
            "monitoring_summary": {
                "total_bridges_monitored": len(results),
                "critical_alerts": critical_count,
                "high_risk_alerts": high_count,
                "medium_risk_alerts": medium_count,
                "time_window_hours": time_window_hours,
                "timestamp": datetime.now().isoformat()
            },
            "bridges": results,
            "active_alerts": sorted(alerts, key=lambda x: x["severity"], reverse=True),
            "overall_recommendation": self._get_overall_recommendation(critical_count, high_count)
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "CRITICAL": "🛑 DO NOT USE THIS BRIDGE. Wait for official team response. Consider alternative bridges.",
            "HIGH": "⚠️ AVOID using this bridge until TVL stabilizes. Monitor official channels for updates.",
            "MEDIUM": "⚡ Use with caution. Reduce transfer amounts and monitor transaction status closely.",
            "LOW": "ℹ️ Safe to use with normal precautions. Minor TVL fluctuation detected.",
            "SAFE": "✅ Bridge appears safe to use. TVL stable or increasing."
        }
        return recommendations.get(risk_level, "Monitor bridge activity before use.")
    
    def _get_overall_recommendation(self, critical_count: int, high_count: int) -> str:
        """Get overall recommendation for all bridges"""
        if critical_count > 0:
            return f"🚨 CRITICAL: {critical_count} bridge(s) showing critical risk. Avoid all bridging until situation resolves."
        elif high_count > 0:
            return f"⚠️ WARNING: {high_count} bridge(s) at high risk. Use alternative bridges if possible."
        else:
            return "✅ All monitored bridges appear stable. Normal bridging operations safe."


def main():
    """Example usage"""
    monitor = BridgeTVLMonitor()
    
    print("\n" + "="*80)
    print("BRIDGE SECURITY WATCHDOG - TVL MONITORING")
    print("="*80)
    
    # Monitor specific bridge
    print("\n📊 Monitoring Stargate Bridge...")
    result = monitor.monitor_bridge("stargate", time_window_hours=24)
    print(json.dumps(result, indent=2))
    
    # Monitor all bridges
    print("\n" + "="*80)
    print("MONITORING ALL MAJOR BRIDGES")
    print("="*80)
    
    all_results = monitor.monitor_all_bridges(time_window_hours=24)
    print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
