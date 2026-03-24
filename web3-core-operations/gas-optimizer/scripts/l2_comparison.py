"""
Layer 2 Gas Comparison - Compare gas costs across different networks
"""

import os
from web3 import Web3
import requests
from typing import Dict, List, Any
from decimal import Decimal


class L2GasComparison:
    """Compare gas costs across Ethereum L1 and L2 solutions"""
    
    def __init__(self):
        self.infura_key = os.getenv('INFURA_KEY', '')
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        
        # Network configurations
        self.networks = {
            'ethereum': {
                'chain_id': 1,
                'name': 'Ethereum Mainnet',
                'rpc': f"https://mainnet.infura.io/v3/{self.infura_key}",
                'explorer_api': 'https://api.etherscan.io/api',
                'type': 'L1'
            },
            'arbitrum': {
                'chain_id': 42161,
                'name': 'Arbitrum One',
                'rpc': 'https://arb1.arbitrum.io/rpc',
                'explorer_api': 'https://api.arbiscan.io/api',
                'type': 'L2-Optimistic'
            },
            'optimism': {
                'chain_id': 10,
                'name': 'Optimism',
                'rpc': 'https://mainnet.optimism.io',
                'explorer_api': 'https://api-optimistic.etherscan.io/api',
                'type': 'L2-Optimistic'
            },
            'polygon': {
                'chain_id': 137,
                'name': 'Polygon',
                'rpc': 'https://polygon-rpc.com',
                'explorer_api': 'https://api.polygonscan.com/api',
                'type': 'Sidechain'
            },
            'base': {
                'chain_id': 8453,
                'name': 'Base',
                'rpc': 'https://mainnet.base.org',
                'explorer_api': 'https://api.basescan.org/api',
                'type': 'L2-Optimistic'
            },
            'zksync': {
                'chain_id': 324,
                'name': 'zkSync Era',
                'rpc': 'https://mainnet.era.zksync.io',
                'explorer_api': 'https://api-era.zksync.network/api',
                'type': 'L2-ZK'
            }
        }
        
        self.web3_instances = {}
        self._init_connections()
    
    def _init_connections(self):
        """Initialize Web3 connections for all networks"""
        for network, config in self.networks.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config['rpc']))
                if w3.is_connected():
                    self.web3_instances[network] = w3
            except:
                pass
    
    def get_network_gas_price(self, network: str) -> Dict[str, Any]:
        """Get current gas price for a network"""
        try:
            w3 = self.web3_instances.get(network)
            if not w3:
                return {'success': False, 'error': 'Network not connected'}
            
            # Get gas price in Wei
            gas_price_wei = w3.eth.gas_price
            gas_price_gwei = gas_price_wei / 1e9
            
            # Get native token price (ETH/MATIC)
            native_token = 'ETH' if network != 'polygon' else 'MATIC'
            token_price_usd = self._get_token_price(native_token)
            
            return {
                'success': True,
                'network': network,
                'gas_price_wei': gas_price_wei,
                'gas_price_gwei': round(gas_price_gwei, 2),
                'native_token': native_token,
                'token_price_usd': token_price_usd
            }
        except Exception as e:
            return {
                'success': False,
                'network': network,
                'error': str(e)
            }
    
    def _get_token_price(self, token: str) -> float:
        """Get token price in USD from CoinGecko"""
        try:
            token_ids = {
                'ETH': 'ethereum',
                'MATIC': 'matic-network'
            }
            
            token_id = token_ids.get(token, 'ethereum')
            url = f'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': token_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            return data.get(token_id, {}).get('usd', 0.0)
        except:
            # Fallback prices
            return 2500.0 if token == 'ETH' else 0.8
    
    def compare_transaction_costs(
        self,
        transaction_type: str = 'transfer',
        networks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare transaction costs across multiple networks
        
        Args:
            transaction_type: Type of transaction ('transfer', 'swap', 'mint')
            networks: List of networks to compare (None = all)
            
        Returns:
            Cost comparison across networks
        """
        if networks is None:
            networks = list(self.networks.keys())
        
        # Base gas estimates by transaction type
        gas_estimates = {
            'transfer': 21000,
            'erc20_transfer': 65000,
            'swap': 150000,
            'mint': 100000,
            'complex': 300000
        }
        
        base_gas = gas_estimates.get(transaction_type, 65000)
        
        comparisons = []
        
        for network in networks:
            if network not in self.web3_instances:
                continue
            
            gas_info = self.get_network_gas_price(network)
            if not gas_info['success']:
                continue
            
            network_config = self.networks[network]
            
            # Calculate costs
            gas_cost_wei = base_gas * gas_info['gas_price_wei']
            gas_cost_native = gas_cost_wei / 1e18
            gas_cost_usd = gas_cost_native * gas_info['token_price_usd']
            
            # L2 specific costs (data availability)
            if network_config['type'].startswith('L2'):
                # Estimate L1 data cost (for rollups)
                l1_data_cost_usd = 0.0
                if transaction_type != 'transfer':
                    # Approximate L1 calldata cost
                    calldata_bytes = 200  # Approximate
                    l1_gas_per_byte = 16
                    l1_gas_price_gwei = 30  # Approximate
                    l1_cost_wei = calldata_bytes * l1_gas_per_byte * l1_gas_price_gwei * 1e9
                    l1_cost_eth = l1_cost_wei / 1e18
                    l1_data_cost_usd = l1_cost_eth * self._get_token_price('ETH')
                
                total_cost_usd = gas_cost_usd + l1_data_cost_usd
            else:
                l1_data_cost_usd = 0.0
                total_cost_usd = gas_cost_usd
            
            comparisons.append({
                'network': network_config['name'],
                'type': network_config['type'],
                'chain_id': network_config['chain_id'],
                'gas_price_gwei': gas_info['gas_price_gwei'],
                'estimated_gas_units': base_gas,
                'gas_cost_native': round(gas_cost_native, 8),
                'native_token': gas_info['native_token'],
                'gas_cost_usd': round(gas_cost_usd, 4),
                'l1_data_cost_usd': round(l1_data_cost_usd, 4),
                'total_cost_usd': round(total_cost_usd, 4),
                'confirmation_time': self._get_confirmation_time(network)
            })
        
        # Sort by total cost
        comparisons.sort(key=lambda x: x['total_cost_usd'])
        
        # Calculate savings
        if len(comparisons) > 1:
            most_expensive = comparisons[-1]['total_cost_usd']
            for comp in comparisons:
                savings = most_expensive - comp['total_cost_usd']
                comp['savings_vs_most_expensive_usd'] = round(savings, 4)
                comp['savings_percentage'] = round((savings / most_expensive) * 100, 2) if most_expensive > 0 else 0
        
        return {
            'success': True,
            'transaction_type': transaction_type,
            'networks_compared': len(comparisons),
            'comparison': comparisons,
            'recommendation': {
                'cheapest_network': comparisons[0]['network'] if comparisons else None,
                'cheapest_cost_usd': comparisons[0]['total_cost_usd'] if comparisons else None,
                'most_expensive_network': comparisons[-1]['network'] if comparisons else None,
                'most_expensive_cost_usd': comparisons[-1]['total_cost_usd'] if comparisons else None,
                'max_savings_usd': comparisons[0]['savings_vs_most_expensive_usd'] if len(comparisons) > 1 else 0,
                'max_savings_percentage': comparisons[0]['savings_percentage'] if len(comparisons) > 1 else 0
            }
        }
    
    def _get_confirmation_time(self, network: str) -> str:
        """Get typical confirmation time for network"""
        times = {
            'ethereum': '12-15 seconds',
            'arbitrum': '1-2 seconds',
            'optimism': '1-2 seconds',
            'polygon': '2-3 seconds',
            'base': '1-2 seconds',
            'zksync': '10-15 seconds'
        }
        return times.get(network, '10-15 seconds')
    
    def get_bridge_costs(
        self,
        from_network: str,
        to_network: str,
        amount_usd: float = 1000.0
    ) -> Dict[str, Any]:
        """
        Estimate bridging costs between networks
        
        Args:
            from_network: Source network
            to_network: Destination network
            amount_usd: Amount to bridge in USD
            
        Returns:
            Bridge cost estimates
        """
        # Approximate bridge fees (varies by bridge protocol)
        bridge_fees = {
            ('ethereum', 'arbitrum'): {'fixed_usd': 5.0, 'percentage': 0.1},
            ('ethereum', 'optimism'): {'fixed_usd': 5.0, 'percentage': 0.1},
            ('ethereum', 'polygon'): {'fixed_usd': 3.0, 'percentage': 0.1},
            ('ethereum', 'base'): {'fixed_usd': 5.0, 'percentage': 0.1},
            ('ethereum', 'zksync'): {'fixed_usd': 8.0, 'percentage': 0.15}
        }
        
        # Reverse direction typically cheaper (withdrawals)
        if (to_network, from_network) in bridge_fees:
            bridge_fees[(from_network, to_network)] = {
                'fixed_usd': bridge_fees[(to_network, from_network)]['fixed_usd'] * 0.5,
                'percentage': bridge_fees[(to_network, from_network)]['percentage'] * 0.5
            }
        
        bridge_key = (from_network, to_network)
        
        if bridge_key not in bridge_fees:
            return {
                'success': False,
                'error': f'Bridge route {from_network} -> {to_network} not supported'
            }
        
        fees = bridge_fees[bridge_key]
        
        # Calculate costs
        fixed_cost = fees['fixed_usd']
        variable_cost = amount_usd * (fees['percentage'] / 100)
        total_cost = fixed_cost + variable_cost
        
        # Get gas costs for bridge transaction
        from_gas = self.get_network_gas_price(from_network)
        bridge_gas_cost_usd = 0.0
        if from_gas['success']:
            # Bridging is complex operation (~200k gas)
            bridge_gas = 200000
            gas_cost_native = (bridge_gas * from_gas['gas_price_wei']) / 1e18
            bridge_gas_cost_usd = gas_cost_native * from_gas['token_price_usd']
        
        total_cost_with_gas = total_cost + bridge_gas_cost_usd
        
        # Estimate time
        bridge_times = {
            ('ethereum', 'arbitrum'): '10-15 minutes',
            ('ethereum', 'optimism'): '10-15 minutes',
            ('ethereum', 'polygon'): '20-30 minutes',
            ('arbitrum', 'ethereum'): '7 days',  # Challenge period
            ('optimism', 'ethereum'): '7 days'
        }
        
        estimated_time = bridge_times.get(bridge_key, '1-2 hours')
        
        return {
            'success': True,
            'route': {
                'from': self.networks[from_network]['name'],
                'to': self.networks[to_network]['name']
            },
            'amount_usd': amount_usd,
            'costs': {
                'fixed_fee_usd': round(fixed_cost, 2),
                'variable_fee_usd': round(variable_cost, 2),
                'variable_fee_percentage': fees['percentage'],
                'gas_cost_usd': round(bridge_gas_cost_usd, 2),
                'total_cost_usd': round(total_cost_with_gas, 2),
                'total_fee_percentage': round((total_cost_with_gas / amount_usd) * 100, 3)
            },
            'estimated_time': estimated_time,
            'recommendations': [
                'Consider using official bridges for security',
                'Check for cheaper routes via aggregators (Socket, LI.FI)',
                f'For amounts < $100, fees ({round((total_cost_with_gas / amount_usd) * 100, 1)}%) may be high'
            ] if total_cost_with_gas / amount_usd > 0.05 else []
        }
