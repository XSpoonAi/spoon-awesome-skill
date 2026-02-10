"""
Gas Estimator - Real-time gas estimation using Etherscan API and Web3 RPC
"""

import os
import requests
from web3 import Web3
from typing import Dict, Any, Optional
from decimal import Decimal


class GasEstimator:
    """Estimates gas costs using real blockchain data"""
    
    def __init__(self):
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.infura_key = os.getenv('INFURA_KEY', '')
        self.alchemy_key = os.getenv('ALCHEMY_KEY', '')
        
        # RPC endpoints
        self.rpc_endpoints = {
            1: f"https://mainnet.infura.io/v3/{self.infura_key}",
            137: "https://polygon-rpc.com",
            42161: "https://arb1.arbitrum.io/rpc",
            10: "https://mainnet.optimism.io",
            56: "https://bsc-dataseed.binance.org"
        }
        
        # Etherscan-like APIs
        self.explorer_apis = {
            1: "https://api.etherscan.io/api",
            137: "https://api.polygonscan.com/api",
            42161: "https://api.arbiscan.io/api",
            10: "https://api-optimistic.etherscan.io/api",
            56: "https://api.bscscan.com/api"
        }
        
        self.web3_instances = {}
        self._init_web3_connections()
    
    def _init_web3_connections(self):
        """Initialize Web3 connections for supported chains"""
        for chain_id, rpc_url in self.rpc_endpoints.items():
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    self.web3_instances[chain_id] = w3
            except Exception as e:
                print(f"Failed to connect to chain {chain_id}: {e}")
    
    def estimate_gas(
        self,
        transaction: Dict[str, Any],
        chain_id: int = 1,
        from_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate gas for a transaction using real RPC call
        
        Args:
            transaction: Transaction dict with 'to', 'data', 'value'
            chain_id: Network chain ID
            from_address: Sender address for estimation
            
        Returns:
            Gas estimation with cost in ETH and USD
        """
        w3 = self.web3_instances.get(chain_id)
        if not w3:
            raise ValueError(f"Chain {chain_id} not supported or RPC unavailable")
        
        # Prepare transaction for estimation
        tx = {
            'to': Web3.to_checksum_address(transaction['to']),
            'data': transaction.get('data', '0x'),
            'value': int(transaction.get('value', 0))
        }
        
        if from_address:
            tx['from'] = Web3.to_checksum_address(from_address)
        
        # Estimate gas using RPC
        try:
            gas_estimate = w3.eth.estimate_gas(tx)
        except Exception as e:
            # Fallback to higher estimate if estimation fails
            gas_estimate = 21000 if tx['data'] == '0x' else 150000
            print(f"Gas estimation failed, using fallback: {e}")
        
        # Get current gas prices
        gas_prices = self.get_gas_prices(chain_id)
        
        # Calculate costs
        gas_price_wei = Web3.to_wei(gas_prices['standard'], 'gwei')
        cost_wei = gas_estimate * gas_price_wei
        cost_eth = Web3.from_wei(cost_wei, 'ether')
        
        # Get ETH price in USD
        eth_price_usd = self._get_token_price(chain_id)
        cost_usd = float(cost_eth) * eth_price_usd
        
        return {
            'success': True,
            'chain_id': chain_id,
            'gas_limit': gas_estimate,
            'gas_price_gwei': gas_prices['standard'],
            'gas_prices': gas_prices,
            'cost_wei': cost_wei,
            'cost_eth': str(cost_eth),
            'cost_usd': round(cost_usd, 2),
            'transaction': {
                'to': transaction['to'],
                'data_length': len(transaction.get('data', '0x')),
                'value': transaction.get('value', 0)
            }
        }
    
    def get_gas_prices(self, chain_id: int = 1) -> Dict[str, float]:
        """
        Get real-time gas prices from Etherscan API
        
        Args:
            chain_id: Network chain ID
            
        Returns:
            Dict with fast, standard, and economical gas prices in Gwei
        """
        api_url = self.explorer_apis.get(chain_id)
        
        if not api_url:
            return self._get_gas_prices_from_rpc(chain_id)
        
        # Try Etherscan API first
        try:
            params = {
                'module': 'gastracker',
                'action': 'gasoracle',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1' and 'result' in data:
                result = data['result']
                return {
                    'fast': float(result.get('FastGasPrice', 0)),
                    'standard': float(result.get('ProposeGasPrice', 0)),
                    'economical': float(result.get('SafeGasPrice', 0)),
                    'base_fee': float(result.get('suggestBaseFee', 0))
                }
        except Exception as e:
            print(f"Etherscan API failed: {e}")
        
        # Fallback to RPC
        return self._get_gas_prices_from_rpc(chain_id)
    
    def _get_gas_prices_from_rpc(self, chain_id: int) -> Dict[str, float]:
        """Get gas prices directly from RPC as fallback"""
        w3 = self.web3_instances.get(chain_id)
        if not w3:
            raise ValueError(f"Chain {chain_id} not supported")
        
        try:
            gas_price = w3.eth.gas_price
            gas_price_gwei = Web3.from_wei(gas_price, 'gwei')
            
            # Calculate different speed tiers
            return {
                'fast': float(gas_price_gwei) * 1.2,
                'standard': float(gas_price_gwei),
                'economical': float(gas_price_gwei) * 0.8,
                'base_fee': float(gas_price_gwei)
            }
        except Exception as e:
            raise Exception(f"Failed to get gas price from RPC: {e}")
    
    def _get_token_price(self, chain_id: int) -> float:
        """Get native token price in USD from CoinGecko"""
        token_ids = {
            1: 'ethereum',
            137: 'matic-network',
            42161: 'ethereum',
            10: 'ethereum',
            56: 'binancecoin'
        }
        
        token_id = token_ids.get(chain_id, 'ethereum')
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': token_id,
                'vs_currencies': 'usd'
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data[token_id]['usd']
        except:
            # Fallback prices
            fallback_prices = {
                'ethereum': 2800.0,
                'matic-network': 0.85,
                'binancecoin': 310.0
            }
            return fallback_prices.get(token_id, 2800.0)
    
    def estimate_eip1559_fees(self, chain_id: int = 1) -> Dict[str, Any]:
        """
        Get EIP-1559 fee estimation (base fee + priority fee)
        
        Args:
            chain_id: Network chain ID
            
        Returns:
            Base fee and priority fee recommendations
        """
        w3 = self.web3_instances.get(chain_id)
        if not w3:
            raise ValueError(f"Chain {chain_id} not supported")
        
        try:
            # Get latest block
            latest_block = w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)
            base_fee_gwei = Web3.from_wei(base_fee, 'gwei')
            
            # Get priority fee
            try:
                max_priority_fee = w3.eth.max_priority_fee
            except:
                max_priority_fee = Web3.to_wei(2, 'gwei')
            
            priority_fee_gwei = Web3.from_wei(max_priority_fee, 'gwei')
            
            # Calculate max fee per gas (base + priority)
            max_fee_gwei = float(base_fee_gwei) + float(priority_fee_gwei)
            
            return {
                'success': True,
                'chain_id': chain_id,
                'base_fee_gwei': float(base_fee_gwei),
                'priority_fee_gwei': float(priority_fee_gwei),
                'max_fee_gwei': max_fee_gwei,
                'eip1559_support': True,
                'recommendations': {
                    'fast': {
                        'max_fee': max_fee_gwei * 1.2,
                        'priority_fee': float(priority_fee_gwei) * 1.5
                    },
                    'standard': {
                        'max_fee': max_fee_gwei,
                        'priority_fee': float(priority_fee_gwei)
                    },
                    'economical': {
                        'max_fee': max_fee_gwei * 0.9,
                        'priority_fee': float(priority_fee_gwei) * 0.8
                    }
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'EIP-1559 not supported or RPC error'
            }
    
    def get_historical_gas_data(
        self,
        chain_id: int = 1,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get historical gas price data from Etherscan
        
        Args:
            chain_id: Network chain ID
            hours: Number of hours of historical data
            
        Returns:
            Historical gas prices and statistics
        """
        api_url = self.explorer_apis.get(chain_id)
        if not api_url:
            return {'success': False, 'error': 'Chain not supported'}
        
        try:
            params = {
                'module': 'stats',
                'action': 'dailyavggasprice',
                'apikey': self.etherscan_api_key
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1':
                return {
                    'success': True,
                    'chain_id': chain_id,
                    'historical_data': data['result'],
                    'data_points': len(data['result'])
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
        return {'success': False, 'error': 'No data available'}
