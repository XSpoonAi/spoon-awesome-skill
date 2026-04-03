"""
Safety Scorer - Comprehensive token safety analysis and scoring
Combines contract, holder, and liquidity analyses
"""

import os
from typing import Dict
from datetime import datetime
from contract_analyzer import ContractAnalyzer
from holder_analyzer import HolderAnalyzer
from liquidity_analyzer import LiquidityAnalyzer

class SafetyScorer:
    """Calculates comprehensive token safety score"""
    
    # Risk level thresholds
    RISK_LEVELS = {
        "Very Low": (86, 100),
        "Low": (71, 85),
        "Moderate": (51, 70),
        "High": (31, 50),
        "Critical": (0, 30)
    }
    
    # Scoring weights
    WEIGHTS = {
        "contract": 30,   # 30% - Contract security
        "holder": 25,     # 25% - Holder distribution
        "liquidity": 35,  # 35% - Liquidity status
        "trading": 10     # 10% - Trading analysis
    }
    
    def __init__(self):
        """Initialize safety scorer with all analyzers"""
        self.contract_analyzer = ContractAnalyzer()
        self.holder_analyzer = HolderAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()
        
    def analyze_token(
        self,
        token_address: str,
        chain: str = "ethereum",
        detailed: bool = True
    ) -> Dict:
        """
        Perform comprehensive token safety analysis
        
        Args:
            token_address: Token contract address
            chain: Blockchain network
            detailed: Include detailed breakdown
            
        Returns:
            Complete safety analysis with score (0-100)
        """
        print(f"\n{'='*60}")
        print(f"TOKEN SAFETY ANALYSIS")
        print(f"{'='*60}")
        print(f"Token: {token_address}")
        print(f"Chain: {chain}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        # Run all analyses
        print("\n[1/3] Running contract analysis...")
        contract_result = self.contract_analyzer.analyze_contract(token_address, chain)
        
        print("\n[2/3] Running holder analysis...")
        holder_result = self.holder_analyzer.analyze_holders(token_address, chain)
        
        print("\n[3/3] Running liquidity analysis...")
        liquidity_result = self.liquidity_analyzer.analyze_liquidity(token_address, chain)
        
        # Calculate total score
        total_score = self._calculate_total_score(
            contract_result,
            holder_result,
            liquidity_result
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(total_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            contract_result,
            holder_result,
            liquidity_result
        )
        
        # Aggregate warnings and red flags
        all_warnings = []
        all_red_flags = []
        
        if contract_result.get('success'):
            all_warnings.extend(contract_result.get('warnings', []))
            all_red_flags.extend(contract_result.get('red_flags', []))
        
        if holder_result.get('success'):
            all_warnings.extend(holder_result.get('warnings', []))
        
        if liquidity_result.get('success'):
            all_warnings.extend(liquidity_result.get('warnings', []))
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            total_score,
            risk_level,
            all_red_flags
        )
        
        # Calculate analysis time
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Safety Score: {total_score}/100")
        print(f"Risk Level: {risk_level}")
        print(f"Confidence: {confidence}%")
        print(f"Analysis Time: {analysis_time:.2f}s")
        print(f"{'='*60}")
        
        # Build result
        result = {
            "success": True,
            "token_address": token_address,
            "chain": chain,
            "safety_score": total_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "recommendation": recommendation,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_time_seconds": round(analysis_time, 2),
            "breakdown": {
                "contract_score": contract_result.get('security_score', 0) if contract_result.get('success') else 0,
                "holder_score": holder_result.get('score', 0) if holder_result.get('success') else 0,
                "liquidity_score": liquidity_result.get('score', 0) if liquidity_result.get('success') else 0,
                "trading_score": self._calculate_trading_score(contract_result) if contract_result.get('success') else 0
            },
            "warnings": all_warnings,
            "red_flags": all_red_flags
        }
        
        # Add detailed analysis if requested
        if detailed:
            result["contract_analysis"] = {
                "is_verified": contract_result.get('is_verified', False),
                "is_open_source": contract_result.get('is_open_source', False),
                "has_mint_function": contract_result.get('has_mint_function', False),
                "ownership_renounced": contract_result.get('ownership_renounced', False),
                "has_proxy": contract_result.get('has_proxy', False),
                "has_blacklist": contract_result.get('has_blacklist', False),
                "hidden_fees": contract_result.get('hidden_fees', False),
                "transfer_pausable": contract_result.get('transfer_pausable', False),
                "malicious_functions": contract_result.get('malicious_functions', [])
            }
            
            result["holder_distribution"] = {
                "total_holders": holder_result.get('holder_count', 0),
                "top_holder_percentage": holder_result.get('top_holder_percentage', 0),
                "top_10_percentage": holder_result.get('top_10_percentage', 0),
                "centralization_risk": holder_result.get('centralization_risk', 'Unknown')
            }
            
            result["liquidity_status"] = {
                "is_locked": liquidity_result.get('is_locked', False),
                "lock_duration_days": liquidity_result.get('lock_duration_days', 0),
                "locked_value_usd": liquidity_result.get('locked_value_usd', 0),
                "liquidity_pools": liquidity_result.get('liquidity_pools', 0),
                "total_liquidity_usd": liquidity_result.get('total_liquidity_usd', 0)
            }
            
            result["trading_analysis"] = {
                "is_honeypot": contract_result.get('is_honeypot', False),
                "can_buy": not contract_result.get('is_honeypot', False),
                "can_sell": not contract_result.get('is_honeypot', False),
                "buy_tax": contract_result.get('buy_tax', 0),
                "sell_tax": contract_result.get('sell_tax', 0),
                "transfer_pausable": contract_result.get('transfer_pausable', False)
            }
        
        return result
    
    def _calculate_total_score(
        self,
        contract_result: Dict,
        holder_result: Dict,
        liquidity_result: Dict
    ) -> int:
        """Calculate total safety score (0-100)"""
        
        # Get individual scores
        contract_score = contract_result.get('security_score', 0) if contract_result.get('success') else 0
        holder_score = holder_result.get('score', 0) if holder_result.get('success') else 0
        liquidity_score = liquidity_result.get('score', 0) if liquidity_result.get('success') else 0
        
        # Calculate trading score from contract analysis
        trading_score = self._calculate_trading_score(contract_result)
        
        # Weight and sum
        total = (
            contract_score +
            holder_score +
            liquidity_score +
            trading_score
        )
        
        return min(100, round(total))
    
    def _calculate_trading_score(self, contract_result: Dict) -> int:
        """Calculate trading analysis score (0-10 points)"""
        if not contract_result.get('success'):
            return 0
        
        score = 0
        
        # Not a honeypot (5 points)
        if not contract_result.get('is_honeypot', False):
            score += 5
        
        # Reasonable taxes (3 points)
        buy_tax = contract_result.get('buy_tax', 0)
        sell_tax = contract_result.get('sell_tax', 0)
        
        # Convert to float if it's a number
        try:
            buy_tax = float(buy_tax) if buy_tax else 0
            sell_tax = float(sell_tax) if sell_tax else 0
        except:
            buy_tax = 0
            sell_tax = 0
        
        if buy_tax <= 5 and sell_tax <= 5:
            score += 3
        elif buy_tax <= 10 and sell_tax <= 10:
            score += 2
        elif buy_tax <= 15 and sell_tax <= 15:
            score += 1
        
        # Can sell (2 points)
        if not contract_result.get('is_honeypot', False):
            score += 2
        
        return min(10, score)
    
    def _determine_risk_level(self, score: int) -> str:
        """Determine risk level from score"""
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score <= max_score:
                return level
        return "Unknown"
    
    def _calculate_confidence(
        self,
        contract_result: Dict,
        holder_result: Dict,
        liquidity_result: Dict
    ) -> int:
        """Calculate confidence in the analysis"""
        confidence = 100
        
        # Reduce confidence if any analysis failed
        if not contract_result.get('success'):
            confidence -= 30
        
        if not holder_result.get('success'):
            confidence -= 20
        
        if not liquidity_result.get('success'):
            confidence -= 15
        
        # Reduce confidence for unverified contracts
        if contract_result.get('success') and not contract_result.get('is_verified'):
            confidence -= 10
        
        # Reduce confidence for low holder data
        if holder_result.get('success'):
            holder_count = holder_result.get('holder_count', 0)
            if holder_count == 0:
                confidence -= 15
            elif holder_count < 100:
                confidence -= 5
        
        # Reduce confidence for no liquidity data
        if liquidity_result.get('success'):
            if liquidity_result.get('liquidity_pools', 0) == 0:
                confidence -= 10
        
        return max(0, min(100, confidence))
    
    def _generate_recommendation(self, score: int, risk_level: str, red_flags: list) -> str:
        """Generate investment recommendation"""
        if red_flags:
            return f"❌ DO NOT INVEST - {len(red_flags)} critical issues detected"
        
        if score >= 86:
            return "✅ Safe to trade - High confidence, well-established token"
        elif score >= 71:
            return "✅ Generally safe - Low risk, suitable for trading"
        elif score >= 51:
            return "⚠️ Proceed with caution - Moderate risk, invest small amounts only"
        elif score >= 31:
            return "⚠️ High risk - Not recommended, high chance of losses"
        else:
            return "❌ Critical risk - DO NOT INVEST, likely scam"

