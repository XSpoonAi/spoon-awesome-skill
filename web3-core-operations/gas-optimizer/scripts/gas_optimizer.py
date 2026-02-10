"""
Gas Optimizer Core - Main optimization strategies
"""

import os
from web3 import Web3
from typing import Dict, List, Any
import requests
from eth_utils import to_checksum_address


class GasOptimizer:
    """Core gas optimization logic"""
    
    def __init__(self):
        self.rpc_url = os.getenv('ETHEREUM_RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/demo')
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
    
    def optimize_contract_call(
        self,
        contract_address: str,
        function_signature: str,
        params: List[Any]
    ) -> Dict[str, Any]:
        """
        Optimize a contract call by finding the most gas-efficient execution path
        
        Args:
            contract_address: Target contract address
            function_signature: Function signature (e.g., 'transfer(address,uint256)')
            params: Function parameters
            
        Returns:
            Optimization recommendations
        """
        try:
            # Get contract code
            contract_code = self.w3.eth.get_code(to_checksum_address(contract_address))
            code_size = len(contract_code)
            
            # Estimate base gas
            function_selector = Web3.keccak(text=function_signature)[:4]
            
            # Build transaction for estimation
            tx = {
                'to': to_checksum_address(contract_address),
                'data': function_selector.hex(),
                'from': '0x0000000000000000000000000000000000000000'
            }
            
            try:
                estimated_gas = self.w3.eth.estimate_gas(tx)
            except:
                estimated_gas = 100000  # Fallback
            
            # Analyze optimization opportunities
            optimizations = []
            potential_savings = 0
            
            # Check for storage operations
            if estimated_gas > 50000:
                optimizations.append({
                    'type': 'storage_optimization',
                    'description': 'High gas suggests SSTORE operations. Consider batching updates.',
                    'potential_saving_gas': int(estimated_gas * 0.15),
                    'priority': 'high'
                })
                potential_savings += int(estimated_gas * 0.15)
            
            # Check contract size
            if code_size > 10000:
                optimizations.append({
                    'type': 'contract_size',
                    'description': 'Large contract may benefit from proxy pattern or library delegation',
                    'potential_saving_gas': int(estimated_gas * 0.10),
                    'priority': 'medium'
                })
                potential_savings += int(estimated_gas * 0.10)
            
            # Check for events
            optimizations.append({
                'type': 'event_emission',
                'description': 'Consider removing non-essential events to save gas',
                'potential_saving_gas': 2000,
                'priority': 'low'
            })
            potential_savings += 2000
            
            return {
                'success': True,
                'contract': contract_address,
                'function': function_signature,
                'analysis': {
                    'estimated_gas': estimated_gas,
                    'contract_code_size': code_size,
                    'complexity_level': 'high' if estimated_gas > 100000 else 'medium' if estimated_gas > 50000 else 'low'
                },
                'optimizations': optimizations,
                'total_potential_savings': potential_savings,
                'savings_percentage': round((potential_savings / estimated_gas) * 100, 2) if estimated_gas > 0 else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'contract': contract_address
            }
    
    def analyze_transaction_pattern(
        self,
        address: str,
        num_transactions: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze historical transactions to find gas optimization patterns
        
        Args:
            address: Ethereum address to analyze
            num_transactions: Number of recent transactions to analyze
            
        Returns:
            Pattern analysis with optimization suggestions
        """
        try:
            # Fetch transactions from Etherscan
            url = f"https://api.etherscan.io/api"
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': num_transactions,
                'sort': 'desc',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] != '1':
                return {
                    'success': False,
                    'error': 'Failed to fetch transactions',
                    'address': address
                }
            
            transactions = data['result']
            
            # Analyze patterns
            total_gas_used = 0
            total_gas_price = 0
            failed_txs = 0
            contract_interactions = 0
            
            gas_prices = []
            gas_used_amounts = []
            
            for tx in transactions:
                gas_used = int(tx.get('gasUsed', 0))
                gas_price = int(tx.get('gasPrice', 0))
                
                total_gas_used += gas_used
                total_gas_price += gas_price
                
                gas_prices.append(gas_price / 1e9)  # Convert to Gwei
                gas_used_amounts.append(gas_used)
                
                if tx.get('isError') == '1':
                    failed_txs += 1
                
                if tx.get('to', '') and len(tx.get('input', '0x')) > 10:
                    contract_interactions += 1
            
            avg_gas_used = total_gas_used / len(transactions) if transactions else 0
            avg_gas_price = total_gas_price / len(transactions) if transactions else 0
            
            # Find optimization opportunities
            optimizations = []
            
            if failed_txs > len(transactions) * 0.05:
                optimizations.append({
                    'issue': 'high_failure_rate',
                    'description': f'{failed_txs} failed transactions wasted gas',
                    'recommendation': 'Use eth_estimateGas and simulation before sending',
                    'estimated_waste': sum(gas_used_amounts[:failed_txs]) if failed_txs <= len(gas_used_amounts) else 0,
                    'priority': 'high'
                })
            
            if contract_interactions > len(transactions) * 0.7:
                optimizations.append({
                    'issue': 'frequent_contract_calls',
                    'description': f'{contract_interactions} contract interactions detected',
                    'recommendation': 'Consider batching calls using Multicall',
                    'estimated_savings': int(avg_gas_used * contract_interactions * 0.3),
                    'priority': 'high'
                })
            
            # Analyze gas price strategy
            if gas_prices:
                max_gp = max(gas_prices)
                min_gp = min(gas_prices)
                if max_gp > min_gp * 3:
                    optimizations.append({
                        'issue': 'inefficient_gas_pricing',
                        'description': f'Gas prices range from {min_gp:.2f} to {max_gp:.2f} Gwei',
                        'recommendation': 'Use EIP-1559 with dynamic maxPriorityFeePerGas',
                        'estimated_savings': int((max_gp - min_gp) * avg_gas_used),
                        'priority': 'medium'
                    })
            
            return {
                'success': True,
                'address': address,
                'transactions_analyzed': len(transactions),
                'statistics': {
                    'total_gas_used': total_gas_used,
                    'average_gas_used': int(avg_gas_used),
                    'average_gas_price_gwei': round(avg_gas_price / 1e9, 2),
                    'failed_transactions': failed_txs,
                    'contract_interactions': contract_interactions,
                    'failure_rate_percentage': round((failed_txs / len(transactions)) * 100, 2) if transactions else 0
                },
                'gas_price_range': {
                    'min_gwei': round(min(gas_prices), 2) if gas_prices else 0,
                    'max_gwei': round(max(gas_prices), 2) if gas_prices else 0,
                    'median_gwei': round(sorted(gas_prices)[len(gas_prices)//2], 2) if gas_prices else 0
                },
                'optimizations': optimizations,
                'total_potential_savings_gas': sum(opt.get('estimated_savings', opt.get('estimated_waste', 0)) for opt in optimizations)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'address': address
            }
    
    def suggest_optimal_gas_strategy(
        self,
        transaction_type: str,
        urgency: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Suggest optimal gas strategy based on transaction type and urgency
        
        Args:
            transaction_type: Type of transaction ('transfer', 'swap', 'mint', 'stake')
            urgency: Transaction urgency ('low', 'medium', 'high', 'urgent')
            
        Returns:
            Gas strategy recommendations
        """
        # Get current gas prices
        try:
            url = f"https://api.etherscan.io/api"
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            gas_data = response.json()
            
            if gas_data['status'] != '1':
                raise Exception("Failed to fetch gas prices")
            
            result = gas_data['result']
            safe_gas = float(result['SafeGasPrice'])
            propose_gas = float(result['ProposeGasPrice'])
            fast_gas = float(result['FastGasPrice'])
            
        except:
            # Fallback values
            safe_gas = 20.0
            propose_gas = 30.0
            fast_gas = 50.0
        
        # Base gas estimates by transaction type
        gas_estimates = {
            'transfer': 21000,
            'erc20_transfer': 65000,
            'swap': 150000,
            'mint': 100000,
            'stake': 120000,
            'complex_defi': 300000
        }
        
        base_gas = gas_estimates.get(transaction_type, 100000)
        
        # Strategy based on urgency
        strategies = {
            'low': {
                'gas_price': safe_gas,
                'description': 'Wait for low network activity',
                'estimated_wait_time': '10-30 minutes',
                'priority_fee': safe_gas * 0.1
            },
            'medium': {
                'gas_price': propose_gas,
                'description': 'Standard confirmation time',
                'estimated_wait_time': '3-5 minutes',
                'priority_fee': propose_gas * 0.15
            },
            'high': {
                'gas_price': fast_gas,
                'description': 'Fast confirmation',
                'estimated_wait_time': '< 2 minutes',
                'priority_fee': fast_gas * 0.2
            },
            'urgent': {
                'gas_price': fast_gas * 1.5,
                'description': 'Next block inclusion',
                'estimated_wait_time': '< 30 seconds',
                'priority_fee': fast_gas * 0.5
            }
        }
        
        strategy = strategies.get(urgency, strategies['medium'])
        
        # Calculate costs
        gas_cost_wei = int(base_gas * strategy['gas_price'] * 1e9)
        gas_cost_eth = gas_cost_wei / 1e18
        
        # Additional recommendations
        recommendations = []
        
        if transaction_type in ['swap', 'complex_defi'] and urgency in ['low', 'medium']:
            recommendations.append("Consider using Layer 2 solutions (Arbitrum, Optimism) for 95% gas savings")
        
        if base_gas > 100000:
            recommendations.append("Use Flashbots or MEV protection for large transactions")
        
        if urgency == 'low':
            recommendations.append("Schedule transaction during off-peak hours (weekends, early UTC morning)")
        
        return {
            'success': True,
            'transaction_type': transaction_type,
            'urgency': urgency,
            'recommended_strategy': {
                'base_fee_gwei': round(strategy['gas_price'], 2),
                'priority_fee_gwei': round(strategy['priority_fee'], 2),
                'total_gas_price_gwei': round(strategy['gas_price'] + strategy['priority_fee'], 2),
                'estimated_gas_units': base_gas,
                'estimated_cost_eth': round(gas_cost_eth, 6),
                'estimated_wait_time': strategy['estimated_wait_time'],
                'description': strategy['description']
            },
            'current_network_conditions': {
                'safe_gas_gwei': safe_gas,
                'standard_gas_gwei': propose_gas,
                'fast_gas_gwei': fast_gas,
                'network_congestion': 'high' if fast_gas > 100 else 'medium' if fast_gas > 50 else 'low'
            },
            'recommendations': recommendations
        }
