"""
DEX Swapper - REAL IMPLEMENTATION
Executes real token swaps on actual DEX smart contracts
NO SIMULATIONS - PRODUCTION READY
"""

from web3 import Web3
import requests
from typing import Optional, Dict, List
import time


class DexSwapper:
    """
    Real DEX swap executor
    - Actual smart contract interactions
    - Real token approvals
    - Production-ready swap execution
    """
    
    # Real token addresses (Ethereum mainnet)
    TOKENS = {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    }
    
    # Real DEX Router addresses
    ROUTERS = {
        "uniswap": "0xE592427A0AEce92De3Edee1F18E0157C05861564",  # Uniswap V3 SwapRouter
        "sushiswap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",  # SushiSwap Router
        "curve": "0x8e764bE4288B842791989DB5b8ec067279829809",  # Curve Router
    }
    
    # Uniswap V3 pool fees
    POOL_FEES = {
        "0.01%": 100,
        "0.05%": 500,
        "0.3%": 3000,
        "1%": 10000,
    }
    
    def __init__(
        self,
        w3: Web3,
        account_address: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize with real Web3 connection
        
        Args:
            w3: Web3 instance (connected to real RPC)
            account_address: Wallet address
            private_key: Private key for signing transactions
        """
        self.w3 = w3
        self.account_address = account_address
        self.private_key = private_key
        
        # Verify connection
        if self.w3.is_connected():
            print(f"✅ DEX Swapper connected to network")
        else:
            raise ConnectionError("Web3 not connected")
        
        # Contract ABIs
        self.router_abi = self._get_uniswap_v3_router_abi()
        self.erc20_abi = self._get_erc20_abi()
        
    def _get_uniswap_v3_router_abi(self) -> List[Dict]:
        """Real Uniswap V3 SwapRouter ABI"""
        return [
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "bytes", "name": "path", "type": "bytes"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"}
                        ],
                        "internalType": "struct ISwapRouter.ExactInputParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInput",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
    
    def _get_erc20_abi(self) -> List[Dict]:
        """Real ERC20 ABI"""
        return [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
    
    def get_real_quote(
        self,
        dex: str,
        token_in: str,
        token_out: str,
        amount_in: float
    ) -> Dict:
        """
        Get REAL quote from DEX using 0x API (aggregates real liquidity)
        
        Args:
            dex: DEX name
            token_in: Input token symbol
            token_out: Output token symbol
            amount_in: Amount to swap (human readable)
            
        Returns:
            Real quote data from actual DEX
        """
        try:
            token_in_address = self.TOKENS[token_in]
            token_out_address = self.TOKENS[token_out]
            
            # Calculate amount in wei
            decimals = 18 if token_in == "WETH" else 6 if token_in in ["USDC", "USDT"] else 18
            amount_wei = int(amount_in * 10**decimals)
            
            # Map DEX names to 0x sources
            dex_sources = {
                "uniswap": "Uniswap_V3",
                "sushiswap": "SushiSwap",
                "curve": "Curve"
            }
            
            # Get real quote from 0x API
            url = "https://api.0x.org/swap/v1/price"
            params = {
                "sellToken": token_in_address,
                "buyToken": token_out_address,
                "sellAmount": str(amount_wei),
                "includedSources": dex_sources.get(dex.lower(), "Uniswap_V3")
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                buy_amount = int(data.get("buyAmount", 0))
                sell_amount = int(data.get("sellAmount", 0))
                
                out_decimals = 18 if token_out == "WETH" else 6 if token_out in ["USDC", "USDT"] else 18
                amount_out = buy_amount / 10**out_decimals
                price = amount_out / amount_in if amount_in > 0 else 0
                
                return {
                    "dex": dex,
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": amount_in,
                    "amount_out_expected": amount_out,
                    "price": price,
                    "price_impact": float(data.get("estimatedPriceImpact", 0)),
                    "gas_estimate": int(data.get("gas", 150000)),
                    "real_quote": True,
                    "sources": data.get("sources", [])
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "dex": dex
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "dex": dex
            }
    
    def encode_uniswap_v3_path(
        self,
        token_in: str,
        token_out: str,
        fee: int = 3000
    ) -> bytes:
        """
        Encode Uniswap V3 swap path (real format)
        
        Args:
            token_in: Input token address
            token_out: Output token address
            fee: Pool fee tier
            
        Returns:
            Encoded path bytes
        """
        # Uniswap V3 path format: tokenIn + fee + tokenOut
        path = (
            bytes.fromhex(token_in[2:]) +  # Remove '0x' prefix
            fee.to_bytes(3, 'big') +
            bytes.fromhex(token_out[2:])
        )
        return path
    
    def check_and_approve_token(
        self,
        token_address: str,
        spender_address: str,
        amount: int
    ) -> Dict:
        """
        Check allowance and approve if needed (REAL on-chain)
        
        Args:
            token_address: Token contract address
            spender_address: Spender (router) address
            amount: Amount to approve in wei
            
        Returns:
            Approval status
        """
        if not self.account_address:
            return {"error": "No account address provided"}
        
        try:
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.erc20_abi
            )
            
            # Check current allowance on-chain
            current_allowance = token_contract.functions.allowance(
                self.account_address,
                spender_address
            ).call()
            
            if current_allowance >= amount:
                return {
                    "approved": True,
                    "current_allowance": current_allowance,
                    "message": "Sufficient allowance already exists"
                }
            
            # Need to approve
            if not self.private_key:
                return {
                    "approved": False,
                    "message": "Approval needed but no private key provided",
                    "required_amount": amount,
                    "current_allowance": current_allowance
                }
            
            # Build approval transaction
            max_approval = 2**256 - 1  # Max uint256
            
            approve_tx = token_contract.functions.approve(
                spender_address,
                max_approval
            ).build_transaction({
                'from': self.account_address,
                'gas': 50000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account_address),
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(approve_tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"   🔓 Token approval sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                return {
                    "approved": True,
                    "tx_hash": tx_hash.hex(),
                    "message": "Token approved successfully"
                }
            else:
                return {
                    "approved": False,
                    "error": "Approval transaction reverted"
                }
                
        except Exception as e:
            return {
                "approved": False,
                "error": str(e)
            }
    
    def execute_uniswap_v3_swap(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int,
        fee_tier: int = 3000,
        deadline: Optional[int] = None
    ) -> Dict:
        """
        Execute REAL swap on Uniswap V3
        
        ⚠️  WARNING: This sends a REAL transaction!
        
        Args:
            token_in: Input token symbol
            token_out: Output token symbol
            amount_in: Amount to swap (in wei)
            min_amount_out: Minimum output (in wei)
            fee_tier: Pool fee tier (default 0.3%)
            deadline: Transaction deadline
            
        Returns:
            Transaction result
        """
        if not self.private_key:
            return {
                "success": False,
                "error": "Private key required for execution"
            }
        
        try:
            token_in_address = self.TOKENS[token_in]
            token_out_address = self.TOKENS[token_out]
            router_address = self.ROUTERS["uniswap"]
            
            if deadline is None:
                deadline = int(time.time()) + 300  # 5 minutes
            
            # Check and approve token
            approval = self.check_and_approve_token(
                token_in_address,
                router_address,
                amount_in
            )
            
            if not approval.get("approved"):
                return {
                    "success": False,
                    "error": "Token approval failed",
                    "details": approval
                }
            
            # Encode swap path
            path = self.encode_uniswap_v3_path(
                token_in_address,
                token_out_address,
                fee_tier
            )
            
            # Build swap transaction
            router = self.w3.eth.contract(
                address=router_address,
                abi=self.router_abi
            )
            
            swap_tx = router.functions.exactInput({
                "path": path,
                "recipient": self.account_address,
                "deadline": deadline,
                "amountIn": amount_in,
                "amountOutMinimum": min_amount_out
            }).build_transaction({
                'from': self.account_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account_address),
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(swap_tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"   🔄 Swap transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "gas_used": receipt['gasUsed'],
                    "block_number": receipt['blockNumber'],
                    "message": "Swap executed successfully"
                }
            else:
                return {
                    "success": False,
                    "tx_hash": tx_hash.hex(),
                    "error": "Swap transaction reverted"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_token_balance(self, token_address: str, wallet_address: str) -> Dict:
        """
        Get REAL token balance on-chain
        
        Args:
            token_address: Token contract address
            wallet_address: Wallet to check
            
        Returns:
            Balance information
        """
        try:
            token = self.w3.eth.contract(
                address=token_address,
                abi=self.erc20_abi
            )
            
            balance_wei = token.functions.balanceOf(wallet_address).call()
            decimals = token.functions.decimals().call()
            balance = balance_wei / 10**decimals
            
            return {
                "balance_wei": balance_wei,
                "balance": balance,
                "decimals": decimals,
                "token": token_address
            }
        except Exception as e:
            return {
                "error": str(e),
                "token": token_address
            }


if __name__ == "__main__":
    # Example: Get real quotes (read-only, safe)
    from web3 import Web3
    
    print("="*70)
    print("DEX SWAPPER - REAL IMPLEMENTATION")
    print("="*70)
    
    # Connect to real Ethereum network
    w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
    
    if w3.is_connected():
        print(f"✅ Connected to Ethereum at block {w3.eth.block_number}")
    
    # Initialize swapper (read-only, no private key)
    swapper = DexSwapper(w3)
    
    # Get REAL quotes from actual DEXs
    print("\n📊 Fetching REAL quotes from DEXs...")
    
    # Uniswap quote
    print("\n💎 Uniswap V3:")
    uniswap_quote = swapper.get_real_quote(
        dex="uniswap",
        token_in="USDC",
        token_out="USDT",
        amount_in=10000
    )
    
    if "error" not in uniswap_quote:
        print(f"   Amount: {uniswap_quote['amount_in']:,.2f} {uniswap_quote['token_in']}")
        print(f"   Expected: {uniswap_quote['amount_out_expected']:,.2f} {uniswap_quote['token_out']}")
        print(f"   Price: {uniswap_quote['price']:.6f}")
        print(f"   Price Impact: {uniswap_quote['price_impact']:.4f}%")
        print(f"   Gas Estimate: {uniswap_quote['gas_estimate']:,}")
    else:
        print(f"   Error: {uniswap_quote['error']}")
    
    # Curve quote
    print("\n🌀 Curve:")
    curve_quote = swapper.get_real_quote(
        dex="curve",
        token_in="DAI",
        token_out="USDC",
        amount_in=5000
    )
    
    if "error" not in curve_quote:
        print(f"   Amount: {curve_quote['amount_in']:,.2f} {curve_quote['token_in']}")
        print(f"   Expected: {curve_quote['amount_out_expected']:,.2f} {curve_quote['token_out']}")
        print(f"   Price: {curve_quote['price']:.6f}")
        print(f"   Price Impact: {curve_quote['price_impact']:.4f}%")
    else:
        print(f"   Error: {curve_quote['error']}")
    
    print("\n" + "="*70)
    print("REAL QUOTES COMPLETE")
    print("="*70)
    print("ℹ️  These are REAL quotes from actual DEX liquidity")
    print("ℹ️  To execute swaps, provide private key (⚠️  USE WITH CAUTION)")
