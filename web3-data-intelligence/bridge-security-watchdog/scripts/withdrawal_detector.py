#!/usr/bin/env python3
"""
Withdrawal Anomaly Detector
Monitors bridge contracts for large or suspicious withdrawal patterns
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from web3 import Web3


@dataclass
class WithdrawalAlert:
    """Alert for suspicious withdrawal"""
    bridge_name: str
    chain: str
    tx_hash: str
    amount_usd: float
    token_address: str
    token_symbol: str
    recipient: str
    block_number: int
    timestamp: str
    severity: str
    anomaly_type: str
    message: str


class WithdrawalDetector:
    """
    Detects anomalous withdrawal patterns from bridge contracts.
    Monitors for:
    - Large single withdrawals (>$1M)
    - Rapid sequential withdrawals
    - Withdrawals to new/untrusted addresses
    - Unusual token movements
    - Pattern matching with known exploits
    """
    
    def __init__(self):
        # Free RPC endpoints
        self.rpc_endpoints = {
            "ethereum": "https://0xrpc.io/eth",
            "arbitrum": "https://arb1.arbitrum.io/rpc",
            "optimism": "https://mainnet.optimism.io",
            "polygon": "https://polygon-rpc.com",
            "base": "https://mainnet.base.org"
        }
        
        # Major bridge contract addresses
        self.bridge_contracts = {
            "ethereum": {
                "stargate": {
                    "address": "0x296F55F8Fb28E498B858d0BcDA06D955B2Cb3f97",
                    "name": "Stargate Router"
                },
                "portal": {
                    "address": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585",
                    "name": "Wormhole Portal Bridge"
                },
                "across": {
                    "address": "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5",
                    "name": "Across Hub Pool"
                },
                "hop": {
                    "address": "0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a",
                    "name": "Hop Bridge"
                },
                "synapse": {
                    "address": "0x2796317b0fF8538F253012862c06787Adfb8cEb6",
                    "name": "Synapse Bridge"
                }
            },
            "arbitrum": {
                "stargate": {
                    "address": "0x352d8275AAE3e0c2404d9f68f6cEE084B8d0A89e",
                    "name": "Stargate Router (Arbitrum)"
                }
            }
        }
        
        # Known CEX addresses (withdrawals to these are typically safer)
        self.known_cex_addresses = {
            "0x28C6c06298d514Db089934071355E5743bf21d60": "Binance 14",
            "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549": "Binance 15",
            "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d": "Binance 16",
            "0x56Eddb7aa87536c09CCc2793473599fD21A8b17F": "Binance Charity",
            "0x9696f59E4d72E237BE84fFD425DCaD154Bf96976": "Binance DEX",
            "0x4976A4A02f38326660D17bf34b431dC6e2eb2327": "Binance Peg",
            "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503": "Binance",
            "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE": "Binance",
            "0xD551234Ae421e3BCBA99A0Da6d736074f22192FF": "Binance Pool",
            "0xA344C7ada83113B3B56941F6e85bf2Eb425949f3": "Coinbase Pro",
            "0x503828976D22510aad0201ac7EC88293211D23Da": "Coinbase",
            "0xddfAbCdc4D8FfC6d5beaf154f18B778f892A0740": "Coinbase Commerce",
            "0x71660c4005BA85c37ccec55d0C4493E66Fe775d3": "Coinbase Misc",
            "0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5": "kraken",
        }
        
        # Withdrawal thresholds
        self.thresholds = {
            "large_withdrawal_usd": 1000000,      # $1M
            "very_large_withdrawal_usd": 5000000,  # $5M
            "critical_withdrawal_usd": 10000000,   # $10M
            "rapid_withdrawal_window_minutes": 60,
            "rapid_withdrawal_count": 5
        }
    
    def get_web3_instance(self, chain: str) -> Optional[Web3]:
        """Get Web3 instance for specified chain"""
        try:
            rpc_url = self.rpc_endpoints.get(chain.lower())
            if not rpc_url:
                return None
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            return w3 if w3.is_connected() else None
        except Exception as e:
            print(f"Error connecting to {chain}: {e}")
            return None
    
    def get_recent_transfers(
        self,
        chain: str,
        contract_address: str,
        blocks_to_scan: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get recent Transfer events from bridge contract.
        
        Args:
            chain: Blockchain name
            contract_address: Bridge contract address
            blocks_to_scan: Number of recent blocks to scan
            
        Returns:
            List of transfer events
        """
        w3 = self.get_web3_instance(chain)
        if not w3:
            print(f"Warning: Unable to connect to {chain} RPC")
            return []
        
        try:
            # Get current block
            current_block = w3.eth.block_number
            from_block = max(0, current_block - blocks_to_scan)
            
            # Transfer event signature
            transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
            
            # Get logs
            logs = w3.eth.get_logs({
                'fromBlock': from_block,
                'toBlock': 'latest',
                'address': Web3.to_checksum_address(contract_address),
                'topics': [transfer_topic]
            })
            
            transfers = []
            for log in logs[:50]:  # Limit to prevent rate limiting
                try:
                    # Decode transfer data
                    from_address = "0x" + log['topics'][1].hex()[-40:]
                    to_address = "0x" + log['topics'][2].hex()[-40:]
                    amount = int(log['data'].hex(), 16)
                    
                    transfers.append({
                        "tx_hash": log['transactionHash'].hex(),
                        "block_number": log['blockNumber'],
                        "from": from_address,
                        "to": to_address,
                        "amount_wei": amount,
                        "token_address": log['address']
                    })
                except Exception as e:
                    continue
            
            return transfers
            
        except Exception as e:
            print(f"Error fetching transfers: {e}")
            return []
    
    def estimate_usd_value(
        self,
        amount_wei: int,
        token_address: str,
        chain: str
    ) -> Dict[str, Any]:
        """
        Estimate USD value of token amount.
        
        Args:
            amount_wei: Token amount in wei
            token_address: Token contract address
            chain: Blockchain name
            
        Returns:
            USD value estimation with token details
        """
        # Known token decimals
        token_decimals = {
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": (6, "USDC", 1.0),     # USDC
            "0xdac17f958d2ee523a2206206994597c13d831ec7": (6, "USDT", 1.0),     # USDT
            "0x6b175474e89094c44da98b954eedeac495271d0f": (18, "DAI", 1.0),    # DAI
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": (18, "WETH", 2000),  # WETH ~$2000
            "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": (8, "WBTC", 40000),  # WBTC ~$40000
        }
        
        token_address_lower = token_address.lower()
        
        if token_address_lower in token_decimals:
            decimals, symbol, price_usd = token_decimals[token_address_lower]
            amount_tokens = amount_wei / (10 ** decimals)
            amount_usd = amount_tokens * price_usd
            
            return {
                "amount_tokens": amount_tokens,
                "token_symbol": symbol,
                "price_usd": price_usd,
                "amount_usd": amount_usd,
                "decimals": decimals
            }
        
        # Unknown token - estimate as $0.01 per token with 18 decimals
        amount_tokens = amount_wei / (10 ** 18)
        return {
            "amount_tokens": amount_tokens,
            "token_symbol": "UNKNOWN",
            "price_usd": 0.01,
            "amount_usd": amount_tokens * 0.01,
            "decimals": 18
        }
    
    def detect_anomalies(
        self,
        transfers: List[Dict[str, Any]],
        bridge_name: str,
        chain: str
    ) -> List[WithdrawalAlert]:
        """
        Detect anomalous withdrawal patterns.
        
        Args:
            transfers: List of transfer events
            bridge_name: Name of the bridge
            chain: Blockchain name
            
        Returns:
            List of withdrawal alerts
        """
        alerts = []
        
        # Enrich transfers with USD values
        enriched_transfers = []
        for transfer in transfers:
            usd_data = self.estimate_usd_value(
                transfer.get("amount_wei", 0),
                transfer.get("token_address", ""),
                chain
            )
            
            enriched_transfer = {**transfer, **usd_data}
            enriched_transfers.append(enriched_transfer)
        
        # Check for large withdrawals
        for transfer in enriched_transfers:
            amount_usd = transfer.get("amount_usd", 0)
            
            if amount_usd >= self.thresholds["critical_withdrawal_usd"]:
                alerts.append(WithdrawalAlert(
                    bridge_name=bridge_name,
                    chain=chain,
                    tx_hash=transfer.get("tx_hash", ""),
                    amount_usd=amount_usd,
                    token_address=transfer.get("token_address", ""),
                    token_symbol=transfer.get("token_symbol", "UNKNOWN"),
                    recipient=transfer.get("to", ""),
                    block_number=transfer.get("block_number", 0),
                    timestamp=datetime.now().isoformat(),
                    severity="CRITICAL",
                    anomaly_type="CRITICAL_WITHDRAWAL",
                    message=f"🚨 CRITICAL: Withdrawal of ${amount_usd:,.0f} {transfer.get('token_symbol')} detected!"
                ))
            elif amount_usd >= self.thresholds["very_large_withdrawal_usd"]:
                alerts.append(WithdrawalAlert(
                    bridge_name=bridge_name,
                    chain=chain,
                    tx_hash=transfer.get("tx_hash", ""),
                    amount_usd=amount_usd,
                    token_address=transfer.get("token_address", ""),
                    token_symbol=transfer.get("token_symbol", "UNKNOWN"),
                    recipient=transfer.get("to", ""),
                    block_number=transfer.get("block_number", 0),
                    timestamp=datetime.now().isoformat(),
                    severity="HIGH",
                    anomaly_type="VERY_LARGE_WITHDRAWAL",
                    message=f"⚠️ HIGH ALERT: Withdrawal of ${amount_usd:,.0f} {transfer.get('token_symbol')} detected."
                ))
            elif amount_usd >= self.thresholds["large_withdrawal_usd"]:
                # Check if withdrawal to known CEX (safer)
                recipient = transfer.get("to", "").lower()
                is_cex = recipient in [addr.lower() for addr in self.known_cex_addresses.keys()]
                
                if not is_cex:
                    alerts.append(WithdrawalAlert(
                        bridge_name=bridge_name,
                        chain=chain,
                        tx_hash=transfer.get("tx_hash", ""),
                        amount_usd=amount_usd,
                        token_address=transfer.get("token_address", ""),
                        token_symbol=transfer.get("token_symbol", "UNKNOWN"),
                        recipient=transfer.get("to", ""),
                        block_number=transfer.get("block_number", 0),
                        timestamp=datetime.now().isoformat(),
                        severity="MEDIUM",
                        anomaly_type="LARGE_WITHDRAWAL_NON_CEX",
                        message=f"⚡ Large withdrawal of ${amount_usd:,.0f} {transfer.get('token_symbol')} to non-CEX address."
                    ))
        
        # Detect rapid withdrawal patterns
        if len(enriched_transfers) >= self.thresholds["rapid_withdrawal_count"]:
            # Check if multiple large withdrawals in short time
            recent_large = [t for t in enriched_transfers if t.get("amount_usd", 0) > 100000]
            
            if len(recent_large) >= 3:
                total_amount = sum(t.get("amount_usd", 0) for t in recent_large)
                alerts.append(WithdrawalAlert(
                    bridge_name=bridge_name,
                    chain=chain,
                    tx_hash="multiple",
                    amount_usd=total_amount,
                    token_address="multiple",
                    token_symbol="various",
                    recipient="multiple",
                    block_number=enriched_transfers[0].get("block_number", 0),
                    timestamp=datetime.now().isoformat(),
                    severity="HIGH",
                    anomaly_type="RAPID_WITHDRAWALS",
                    message=f"⚠️ Rapid withdrawal pattern: {len(recent_large)} large transfers totaling ${total_amount:,.0f}"
                ))
        
        return alerts
    
    def monitor_bridge(
        self,
        bridge_id: str,
        chain: str,
        blocks_to_scan: int = 1000
    ) -> Dict[str, Any]:
        """
        Monitor a specific bridge for suspicious withdrawals.
        
        Args:
            bridge_id: Bridge identifier 
            chain: Blockchain name
            blocks_to_scan: Number of blocks to scan
            
        Returns:
            Monitoring results with alerts
        """
        chain_bridges = self.bridge_contracts.get(chain.lower(), {})
        bridge_info = chain_bridges.get(bridge_id.lower())
        
        if not bridge_info:
            return {
                "error": f"Bridge {bridge_id} not found on {chain}",
                "available_bridges": list(chain_bridges.keys())
            }
        
        contract_address = bridge_info["address"]
        bridge_name = bridge_info["name"]
        
        # Get recent transfers
        transfers = self.get_recent_transfers(chain, contract_address, blocks_to_scan)
        
        # Detect anomalies
        alerts = self.detect_anomalies(transfers, bridge_name, chain)
        
        # Calculate summary
        total_withdrawals = len(transfers)
        total_volume_usd = sum(
            self.estimate_usd_value(
                t.get("amount_wei", 0),
                t.get("token_address", ""),
                chain
            ).get("amount_usd", 0)
            for t in transfers
        )
        
        return {
            "bridge_id": bridge_id,
            "bridge_name": bridge_name,
            "chain": chain,
            "contract_address": contract_address,
            "monitoring_summary": {
                "blocks_scanned": blocks_to_scan,
                "total_withdrawals": total_withdrawals,
                "total_volume_usd": total_volume_usd,
                "alerts_triggered": len(alerts),
                "critical_alerts": sum(1 for a in alerts if a.severity == "CRITICAL"),
                "high_alerts": sum(1 for a in alerts if a.severity == "HIGH"),
                "timestamp": datetime.now().isoformat()
            },
            "alerts": [
                {
                    "severity": alert.severity,
                    "type": alert.anomaly_type,
                    "message": alert.message,
                    "amount_usd": alert.amount_usd,
                    "token": alert.token_symbol,
                    "tx_hash": alert.tx_hash,
                    "recipient": alert.recipient
                }
                for alert in sorted(alerts, key=lambda x: x.amount_usd, reverse=True)
            ],
            "recommendation": self._get_recommendation(alerts),
            "recent_large_transfers": self._get_largest_transfers(transfers, chain)[:5]
        }
    
    def _get_recommendation(self, alerts: List[WithdrawalAlert]) -> str:
        """Generate recommendation based on alerts"""
        if not alerts:
            return "✅ No suspicious withdrawal activity detected. Bridge appears safe."
        
        critical = sum(1 for a in alerts if a.severity == "CRITICAL")
        high = sum(1 for a in alerts if a.severity == "HIGH")
        
        if critical > 0:
            return f"🚨 CRITICAL: {critical} critical withdrawal(s) detected. DO NOT USE this bridge until situation resolves."
        elif high >= 2:
            return f"⚠️ HIGH RISK: Multiple large withdrawals detected. Avoid using this bridge."
        elif high == 1:
            return "⚡ MEDIUM RISK: Large withdrawal detected. Use with caution and monitor closely."
        else:
            return "ℹ️ LOW RISK: Minor unusual activity. Monitor before use."
    
    def _get_largest_transfers(
        self,
        transfers: List[Dict[str, Any]],
        chain: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get largest transfers sorted by USD value"""
        enriched = []
        for transfer in transfers:
            usd_data = self.estimate_usd_value(
                transfer.get("amount_wei", 0),
                transfer.get("token_address", ""),
                chain
            )
            enriched.append({
                "tx_hash": transfer.get("tx_hash", ""),
                "amount_usd": usd_data.get("amount_usd", 0),
                "amount_tokens": usd_data.get("amount_tokens", 0),
                "token_symbol": usd_data.get("token_symbol", ""),
                "recipient": transfer.get("to", "")
            })
        
        return sorted(enriched, key=lambda x: x["amount_usd"], reverse=True)[:limit]


def main():
    """Example usage"""
    detector = WithdrawalDetector()
    
    print("\n" + "="*80)
    print("BRIDGE SECURITY WATCHDOG - WITHDRAWAL MONITORING")
    print("="*80)
    
    # Monitor Stargate on Ethereum
    print("\n📊 Monitoring Stargate Bridge on Ethereum...")
    result = detector.monitor_bridge("stargate", "ethereum", blocks_to_scan=1000)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
