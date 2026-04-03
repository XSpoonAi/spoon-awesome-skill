#!/usr/bin/env python3
"""
Bridge Safety Scorer
Combines TVL monitoring and withdrawal detection to generate comprehensive bridge safety scores
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from bridge_tvl_monitor import BridgeTVLMonitor
from withdrawal_detector import WithdrawalDetector


class BridgeSafetyScorer:
    """
    Main orchestrator for bridge security monitoring.
    
    Generates safety scores (0-100) based on:
    - TVL changes (40 points): Sudden TVL drops indicate risk
    - Withdrawal patterns (35 points): Large/suspicious withdrawals
    - Historical stability (15 points): Bridge track record
    - Volume analysis (10 points): Normal trading activity
    
    Safety Levels:
    - 90-100: SAFE - Bridge operating normally
    - 70-89: LOW RISK - Minor concerns, safe to use with caution
    - 50-69: MEDIUM RISK - Notable issues, reduce transfer amounts
    - 30-49: HIGH RISK - Significant problems, avoid if possible
    - 0-29: CRITICAL - DO NOT USE
    """
    
    def __init__(self):
        self.tvl_monitor = BridgeTVLMonitor()
        self.withdrawal_detector = WithdrawalDetector()
        
        # Scoring weights
        self.weights = {
            "tvl_stability": 40,        # TVL change analysis
            "withdrawal_safety": 35,     # Withdrawal pattern analysis
            "historical_stability": 15,  # Track record
            "volume_health": 10          # Trading volume
        }
    
    def score_tvl_stability(
        self,
        tvl_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score TVL stability (0-40 points).
        
        Args:
            tvl_analysis: TVL analysis from monitor
            
        Returns:
            Score and breakdown
        """
        max_score = self.weights["tvl_stability"]
        change_percent = tvl_analysis.get("change_percent", 0)
        
        # Positive change = good
        if change_percent >= 0:
            score = max_score
            status = "STABLE"
        # Negative change = deduct points
        elif change_percent >= -2:  # <2% drop
            score = max_score * 0.9
            status = "MINOR_DECREASE"
        elif change_percent >= -5:  # 2-5% drop
            score = max_score * 0.7
            status = "MODERATE_DECREASE"
        elif change_percent >= -10:  # 5-10% drop
            score = max_score * 0.4
            status = "SIGNIFICANT_DECREASE"
        elif change_percent >= -20:  # 10-20% drop
            score = max_score * 0.2
            status = "MAJOR_DECREASE"
        else:  # >20% drop
            score = 0
            status = "CRITICAL_DECREASE"
        
        return {
            "score": round(score, 2),
            "max_score": max_score,
            "status": status,
            "tvl_change_percent": round(change_percent, 2),
            "reasoning": self._get_tvl_reasoning(change_percent, status)
        }
    
    def score_withdrawal_safety(
        self,
        withdrawal_monitoring: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score withdrawal safety (0-35 points).
        
        Args:
            withdrawal_monitoring: Withdrawal detection results
            
        Returns:
            Score and breakdown
        """
        max_score = self.weights["withdrawal_safety"]
        
        monitoring_summary = withdrawal_monitoring.get("monitoring_summary", {})
        alerts = withdrawal_monitoring.get("alerts", [])
        
        critical_count = monitoring_summary.get("critical_alerts", 0)
        high_count = monitoring_summary.get("high_alerts", 0)
        total_alerts = len(alerts)
        
        # Calculate score based on alerts
        if critical_count > 0:
            score = 0
            status = "CRITICAL_ALERTS"
        elif high_count >= 2:
            score = max_score * 0.2
            status = "MULTIPLE_HIGH_ALERTS"
        elif high_count == 1:
            score = max_score * 0.5
            status = "SINGLE_HIGH_ALERT"
        elif total_alerts >= 3:
            score = max_score * 0.7
            status = "MULTIPLE_MEDIUM_ALERTS"
        elif total_alerts > 0:
            score = max_score * 0.85
            status = "MINOR_ALERTS"
        else:
            score = max_score
            status = "NO_ALERTS"
        
        return {
            "score": round(score, 2),
            "max_score": max_score,
            "status": status,
            "alert_summary": {
                "critical": critical_count,
                "high": high_count,
                "total": total_alerts
            },
            "reasoning": self._get_withdrawal_reasoning(status, critical_count, high_count)
        }
    
    def score_historical_stability(
        self,
        bridge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score historical stability (0-15 points).
        Based on bridge's track record and reputation.
        
        Args:
            bridge_data: Bridge information
            
        Returns:
            Score and breakdown
        """
        max_score = self.weights["historical_stability"]
        bridge_name = bridge_data.get("bridge_name", "").lower()
        
        # Known bridges with good track records
        trusted_bridges = {
            "stargate": 15,
            "across": 14,
            "hop": 13,
            "synapse": 12,
            "portal": 11,
            "wormhole": 10
        }
        
        # Check if bridge is known and trusted
        for known_bridge, reputation_score in trusted_bridges.items():
            if known_bridge in bridge_name:
                return {
                    "score": reputation_score,
                    "max_score": max_score,
                    "status": "ESTABLISHED",
                    "reasoning": f"Well-established bridge with strong track record"
                }
        
        # Unknown bridge = lower score
        return {
            "score": max_score * 0.6,
            "max_score": max_score,
            "status": "UNKNOWN",
            "reasoning": "Bridge has limited track record or is relatively new"
        }
    
    def score_volume_health(
        self,
        withdrawal_monitoring: Dict[str, Any],
        tvl_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score volume health (0-10 points).
        Healthy bridges have consistent volume.
        
        Args:
            withdrawal_monitoring: Withdrawal data
            tvl_analysis: TVL data
            
        Returns:
            Score and breakdown
        """
        max_score = self.weights["volume_health"]
        
        monitoring_summary = withdrawal_monitoring.get("monitoring_summary", {})
        withdrawal_count = monitoring_summary.get("total_withdrawals", 0)
        volume_usd = monitoring_summary.get("total_volume_usd", 0)
        
        # Score based on withdrawal activity
        if withdrawal_count > 20 and volume_usd > 1000000:
            score = max_score
            status = "HEALTHY_VOLUME"
        elif withdrawal_count > 10 and volume_usd > 500000:
            score = max_score * 0.8
            status = "MODERATE_VOLUME"
        elif withdrawal_count > 5:
            score = max_score * 0.6
            status = "LOW_VOLUME"
        else:
            score = max_score * 0.4
            status = "MINIMAL_VOLUME"
        
        return {
            "score": round(score, 2),
            "max_score": max_score,
            "status": status,
            "withdrawal_count": withdrawal_count,
            "volume_usd": round(volume_usd, 2),
            "reasoning": f"{withdrawal_count} withdrawals, ${volume_usd:,.0f} volume"
        }
    
    def calculate_safety_score(
        self,
        bridge_id: str,
        chain: str = "ethereum",
        time_window_hours: int = 24,
        blocks_to_scan: int = 1000,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive safety score for a bridge.
        
        Args:
            bridge_id: Bridge identifier (stargate, portal, across, etc.)
            chain: Blockchain name
            time_window_hours: TVL analysis window
            blocks_to_scan: Blocks to scan for withdrawals
            detailed: Include detailed breakdown
            
        Returns:
            Comprehensive safety assessment
        """
        # Monitor TVL
        tvl_result = self.tvl_monitor.monitor_bridge(bridge_id, time_window_hours)
        
        # Monitor withdrawals
        withdrawal_result = self.withdrawal_detector.monitor_bridge(
            bridge_id,
            chain,
            blocks_to_scan
        )
        
        # Handle errors
        if "error" in tvl_result or "error" in withdrawal_result:
            return {
                "error": "Unable to analyze bridge",
                "bridge_id": bridge_id,
                "chain": chain,
                "details": {
                    "tvl_error": tvl_result.get("error"),
                    "withdrawal_error": withdrawal_result.get("error")
                }
            }
        
        # Calculate component scores
        tvl_score = self.score_tvl_stability(tvl_result.get("tvl_analysis", {}))
        withdrawal_score = self.score_withdrawal_safety(withdrawal_result)
        historical_score = self.score_historical_stability(tvl_result)
        volume_score = self.score_volume_health(
            withdrawal_result,
            tvl_result.get("tvl_analysis", {})
        )
        
        # Calculate total score
        total_score = (
            tvl_score["score"] +
            withdrawal_score["score"] +
            historical_score["score"] +
            volume_score["score"]
        )
        
        # Determine risk level
        risk_level, recommendation = self._assess_risk_level(
            total_score,
            tvl_result.get("risk_level", ""),
            withdrawal_result.get("monitoring_summary", {})
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            withdrawal_result.get("monitoring_summary", {}),
            tvl_result.get("tvl_analysis", {})
        )
        
        result = {
            "bridge_id": bridge_id,
            "bridge_name": tvl_result.get("bridge_name", bridge_id),
            "chain": chain,
            "safety_score": round(total_score, 2),
            "risk_level": risk_level,
            "confidence": confidence,
            "recommendation": recommendation,
            "score_breakdown": {
                "tvl_stability": f"{tvl_score['score']}/{tvl_score['max_score']}",
                "withdrawal_safety": f"{withdrawal_score['score']}/{withdrawal_score['max_score']}",
                "historical_stability": f"{historical_score['score']}/{historical_score['max_score']}",
                "volume_health": f"{volume_score['score']}/{volume_score['max_score']}"
            },
            "key_metrics": {
                "current_tvl": tvl_result.get("tvl_analysis", {}).get("current_tvl", 0),
                "tvl_change_24h": tvl_result.get("tvl_analysis", {}).get("change_percent", 0),
                "withdrawal_alerts": withdrawal_result.get("monitoring_summary", {}).get("alerts_triggered", 0),
                "monitored_withdrawals": withdrawal_result.get("monitoring_summary", {}).get("total_withdrawals", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add detailed breakdown if requested
        if detailed:
            result["detailed_analysis"] = {
                "tvl_analysis": tvl_score,
                "withdrawal_analysis": withdrawal_score,
                "historical_analysis": historical_score,
                "volume_analysis": volume_score,
                "tvl_raw_data": tvl_result,
                "withdrawal_raw_data": withdrawal_result
            }
        
        return result
    
    def compare_bridges(
        self,
        bridge_ids: List[str],
        chain: str = "ethereum"
    ) -> Dict[str, Any]:
        """
        Compare safety scores across multiple bridges.
        
        Args:
            bridge_ids: List of bridge identifiers
            chain: Blockchain name
            
        Returns:
            Comparative analysis
        """
        results = []
        
        for bridge_id in bridge_ids:
            score_result = self.calculate_safety_score(bridge_id, chain)
            if "error" not in score_result:
                results.append(score_result)
        
        if not results:
            return {"error": "No bridges could be analyzed"}
        
        # Sort by safety score
        sorted_results = sorted(results, key=lambda x: x["safety_score"], reverse=True)
        
        return {
            "comparison_summary": {
                "bridges_analyzed": len(sorted_results),
                "safest_bridge": sorted_results[0]["bridge_name"],
                "highest_score": sorted_results[0]["safety_score"],
                "chain": chain,
                "timestamp": datetime.now().isoformat()
            },
            "rankings": [
                {
                    "rank": idx + 1,
                    "bridge": result["bridge_name"],
                    "safety_score": result["safety_score"],
                    "risk_level": result["risk_level"],
                    "recommendation": result["recommendation"]
                }
                for idx, result in enumerate(sorted_results)
            ],
            "detailed_results": sorted_results
        }
    
    def _assess_risk_level(
        self,
        total_score: float,
        tvl_risk: str,
        withdrawal_summary: Dict[str, Any]
    ) -> tuple[str, str]:
        """Assess overall risk level and recommendation"""
        critical_alerts = withdrawal_summary.get("critical_alerts", 0)
        
        # Critical alerts override score
        if critical_alerts > 0 or tvl_risk == "CRITICAL":
            return "CRITICAL", "🚨 DO NOT USE THIS BRIDGE - Critical security issues detected"
        
        if total_score >= 90:
            return "SAFE", "✅ Bridge is safe to use - All security indicators are positive"
        elif total_score >= 70:
            return "LOW RISK", "✅ Bridge appears safe with minor concerns - Use with normal precautions"
        elif total_score >= 50:
            return "MEDIUM RISK", "⚡ Use with caution - Notable security concerns detected. Reduce transfer amounts."
        elif total_score >= 30:
            return "HIGH RISK", "⚠️ High risk detected - Avoid using this bridge if possible"
        else:
            return "CRITICAL", "🚨 DO NOT USE - Multiple critical issues detected"
    
    def _calculate_confidence(
        self,
        withdrawal_summary: Dict[str, Any],
        tvl_analysis: Dict[str, Any]
    ) -> int:
        """Calculate confidence level (0-100%)"""
        confidence = 70  # Base confidence
        
        # More data = higher confidence
        withdrawal_count = withdrawal_summary.get("total_withdrawals", 0)
        if withdrawal_count > 20:
            confidence += 20
        elif withdrawal_count > 10:
            confidence += 10
        elif withdrawal_count > 5:
            confidence += 5
        
        # TVL data availability
        if tvl_analysis.get("current_tvl", 0) > 0:
            confidence += 10
        
        return min(confidence, 100)
    
    def _get_tvl_reasoning(self, change_percent: float, status: str) -> str:
        """Get reasoning for TVL score"""
        if change_percent >= 0:
            return f"TVL increased by {change_percent:.2f}% - Positive indicator"
        else:
            return f"TVL decreased by {abs(change_percent):.2f}% - {status.replace('_', ' ').title()}"
    
    def _get_withdrawal_reasoning(
        self,
        status: str,
        critical_count: int,
        high_count: int
    ) -> str:
        """Get reasoning for withdrawal score"""
        if status == "NO_ALERTS":
            return "No suspicious withdrawal activity detected"
        elif status == "CRITICAL_ALERTS":
            return f"{critical_count} critical withdrawal alert(s) - Immediate risk"
        elif "HIGH" in status:
            return f"{high_count} high-risk withdrawal(s) detected"
        else:
            return "Minor withdrawal concerns detected"


def main():
    """Example usage"""
    scorer = BridgeSafetyScorer()
    
    print("\n" + "="*80)
    print("BRIDGE SECURITY WATCHDOG - COMPREHENSIVE SAFETY ANALYSIS")
    print("="*80)
    
    # Analyze single bridge
    print("\n📊 Analyzing Stargate Bridge Safety...")
    result = scorer.calculate_safety_score(
        bridge_id="stargate",
        chain="ethereum",
        detailed=True
    )
    
    print("\n" + "="*80)
    print(f"SAFETY SCORE: {result['safety_score']}/100")
    print(f"RISK LEVEL: {result['risk_level']}")
    print(f"CONFIDENCE: {result['confidence']}%")
    print("="*80)
    
    print(f"\n📈 SCORE BREAKDOWN:")
    for component, score in result['score_breakdown'].items():
        print(f"  • {component.replace('_', ' ').title()}: {score}")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"  {result['recommendation']}")
    
    print(f"\n🔍 KEY METRICS:")
    for metric, value in result['key_metrics'].items():
        print(f"  • {metric.replace('_', ' ').title()}: {value:,.0f}" if isinstance(value, (int, float)) else f"  • {metric.replace('_', ' ').title()}: {value}")
    
    # Compare multiple bridges
    print("\n" + "="*80)
    print("COMPARING MULTIPLE BRIDGES")
    print("="*80)
    
    comparison = scorer.compare_bridges(
        ["stargate", "across", "hop"],
        chain="ethereum"
    )
    
    print("\n🏆 BRIDGE SAFETY RANKINGS:")
    for rank_info in comparison.get("rankings", []):
        print(f"  {rank_info['rank']}. {rank_info['bridge']}: {rank_info['safety_score']}/100 ({rank_info['risk_level']})")


if __name__ == "__main__":
    main()
