"""
Mempool Monitor - Real-time WebSocket monitoring of pending transactions

This module provides real-time monitoring of the Ethereum mempool (pending transaction pool)
using WebSocket connections. It filters transactions targeting specific contracts and
extracts relevant data for exploit detection.

Key Features:
- WebSocket connection management with automatic reconnection
- Real-time pending transaction stream processing
- Contract address filtering
- Transaction decoding and metadata extraction
- Event-driven architecture with callback system
- Connection health monitoring and error recovery
- Rate limiting and backoff strategies

Author: SpoonOS Skills
Category: Web3 Data Intelligence - Security Analysis
"""

import asyncio
import logging
from typing import Callable, Optional, Dict, Any, List, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

from web3 import Web3
from eth_utils import to_checksum_address
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """WebSocket connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class PendingTransaction:
    """Pending transaction data structure"""
    hash: str
    from_address: str
    to_address: Optional[str]
    value: int  # Wei
    gas: int
    gas_price: int  # Wei
    max_fee_per_gas: Optional[int]  # Wei (EIP-1559)
    max_priority_fee_per_gas: Optional[int]  # Wei (EIP-1559)
    nonce: int
    input_data: str  # Hex string
    timestamp: datetime
    
    # Decoded function data
    function_selector: Optional[str] = None
    function_name: Optional[str] = None
    decoded_input: Optional[Dict[str, Any]] = None
    
    # Metadata
    is_contract_creation: bool = False
    targets_monitored_contract: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'hash': self.hash,
            'from': self.from_address,
            'to': self.to_address,
            'value': self.value,
            'gas': self.gas,
            'gas_price': self.gas_price,
            'max_fee_per_gas': self.max_fee_per_gas,
            'max_priority_fee_per_gas': self.max_priority_fee_per_gas,
            'nonce': self.nonce,
            'input_data': self.input_data,
            'timestamp': self.timestamp.isoformat(),
            'function_selector': self.function_selector,
            'function_name': self.function_name,
            'decoded_input': self.decoded_input,
            'is_contract_creation': self.is_contract_creation,
            'targets_monitored_contract': self.targets_monitored_contract
        }


@dataclass
class MonitoringStats:
    """Statistics for monitoring session"""
    start_time: datetime
    transactions_seen: int = 0
    transactions_filtered: int = 0
    reconnections: int = 0
    errors: int = 0
    last_transaction_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_time': self.start_time.isoformat(),
            'transactions_seen': self.transactions_seen,
            'transactions_filtered': self.transactions_filtered,
            'reconnections': self.reconnections,
            'errors': self.errors,
            'last_transaction_time': self.last_transaction_time.isoformat() if self.last_transaction_time else None,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
        }


class MempoolMonitor:
    """
    Real-time mempool monitoring system using WebSocket subscription
    
    This class manages WebSocket connections to Ethereum nodes and monitors
    pending transactions in real-time. It provides filtering, decoding, and
    callback mechanisms for downstream analysis.
    """
    
    def __init__(
        self,
        websocket_url: str,
        monitored_contracts: List[str],
        callback: Callable[[PendingTransaction], None],
        rpc_url: Optional[str] = None,
        contract_abis: Optional[Dict[str, List[Dict]]] = None,
        reconnect_delay: int = 5,
        max_reconnect_attempts: int = 10
    ):
        """
        Initialize mempool monitor
        
        Args:
            websocket_url: WebSocket endpoint (e.g., wss://eth-mainnet.g.alchemy.com/v2/KEY)
            monitored_contracts: List of contract addresses to monitor
            callback: Function to call when relevant transaction detected
            rpc_url: Optional HTTP RPC endpoint for transaction lookups (derived from websocket_url if not provided)
            contract_abis: Optional ABIs for decoding function calls
            reconnect_delay: Seconds to wait before reconnecting
            max_reconnect_attempts: Maximum reconnection attempts
        """
        self.websocket_url = websocket_url
        self.monitored_contracts = set(to_checksum_address(addr) for addr in monitored_contracts)
        self.callback = callback
        self.contract_abis = contract_abis or {}
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        
        # Web3 instance for transaction processing (use HTTP provider)
        # Convert wss:// to https:// if rpc_url not provided
        http_url = rpc_url or websocket_url.replace('wss://', 'https://').replace('ws://', 'http://')
        self.w3 = Web3(Web3.HTTPProvider(http_url))
        
        # Connection state
        self.status = ConnectionStatus.DISCONNECTED
        self.ws = None
        self.reconnect_count = 0
        self.should_run = False
        
        # Statistics
        self.stats = MonitoringStats(start_time=datetime.now())
        
        # Contract function selectors (for quick lookup)
        self.function_signatures: Dict[str, str] = {}
        self._build_function_signatures()
        
        logger.info(f"MempoolMonitor initialized for {len(self.monitored_contracts)} contracts")
    
    def _build_function_signatures(self):
        """Build function selector to name mapping from ABIs"""
        for contract_addr, abi in self.contract_abis.items():
            for item in abi:
                if item.get('type') == 'function':
                    name = item['name']
                    inputs = ','.join([inp['type'] for inp in item.get('inputs', [])])
                    signature = f"{name}({inputs})"
                    selector = Web3.keccak(text=signature)[:4].hex()
                    self.function_signatures[selector] = name
        
        logger.info(f"Built {len(self.function_signatures)} function signatures")
    
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.status = ConnectionStatus.CONNECTING
            logger.info(f"Connecting to {self.websocket_url}")
            
            # Create WebSocket connection
            async with aiohttp.ClientSession() as session:
                self.ws = await session.ws_connect(self.websocket_url)
                self.status = ConnectionStatus.CONNECTED
                self.reconnect_count = 0
                
                logger.info("✅ WebSocket connected successfully")
                
                # Subscribe to pending transactions
                await self.subscribe_pending_transactions()
                
                # Start listening for messages
                await self.listen()
                
        except Exception as e:
            self.status = ConnectionStatus.FAILED
            self.stats.errors += 1
            logger.error(f"Connection failed: {e}")
            
            if self.reconnect_count < self.max_reconnect_attempts:
                await self.reconnect()
            else:
                logger.error("Max reconnection attempts reached")
                raise
    
    async def subscribe_pending_transactions(self):
        """Subscribe to pending transaction events"""
        subscription_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"]
        }
        
        await self.ws.send_json(subscription_request)
        logger.info("Subscribed to pending transactions")
    
    async def listen(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.process_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {msg.data}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("WebSocket closed")
                    break
                    
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self.stats.errors += 1
        
        finally:
            if self.should_run and self.reconnect_count < self.max_reconnect_attempts:
                await self.reconnect()
    
    async def process_message(self, data: str):
        """Process incoming WebSocket message"""
        try:
            message = json.loads(data)
            
            # Check if it's a transaction hash notification
            if 'params' in message and 'result' in message['params']:
                tx_hash = message['params']['result']
                await self.process_transaction(tx_hash)
                
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            self.stats.errors += 1
    
    async def process_transaction(self, tx_hash: str):
        """Fetch and process transaction details"""
        try:
            self.stats.transactions_seen += 1
            
            # Fetch full transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            
            # Convert to our data structure
            pending_tx = self._parse_transaction(tx)
            
            # Filter: only process transactions targeting monitored contracts
            if pending_tx.to_address and to_checksum_address(pending_tx.to_address) in self.monitored_contracts:
                pending_tx.targets_monitored_contract = True
                self.stats.transactions_filtered += 1
                self.stats.last_transaction_time = datetime.now()
                
                # Decode function call if ABI available
                self._decode_function_call(pending_tx)
                
                # Invoke callback for downstream processing
                try:
                    self.callback(pending_tx)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
        except Exception as e:
            logger.debug(f"Transaction processing error for {tx_hash}: {e}")
            # Don't increment error count for transaction fetch failures (normal)
    
    def _parse_transaction(self, tx: Dict) -> PendingTransaction:
        """Parse raw transaction into PendingTransaction object"""
        return PendingTransaction(
            hash=tx['hash'].hex(),
            from_address=tx['from'],
            to_address=tx.get('to'),
            value=tx['value'],
            gas=tx['gas'],
            gas_price=tx.get('gasPrice', 0),
            max_fee_per_gas=tx.get('maxFeePerGas'),
            max_priority_fee_per_gas=tx.get('maxPriorityFeePerGas'),
            nonce=tx['nonce'],
            input_data=tx['input'].hex() if isinstance(tx['input'], bytes) else tx['input'],
            timestamp=datetime.now(),
            is_contract_creation=(tx.get('to') is None),
            function_selector=tx['input'][:10] if len(tx['input']) >= 10 else None
        )
    
    def _decode_function_call(self, tx: PendingTransaction):
        """Decode function call using ABI if available"""
        if not tx.to_address or not tx.input_data or len(tx.input_data) < 10:
            return
        
        # Extract function selector
        selector = tx.input_data[:10]
        tx.function_selector = selector
        
        # Lookup function name
        if selector in self.function_signatures:
            tx.function_name = self.function_signatures[selector]
        
        # Try to decode parameters (if ABI available)
        contract_abi = self.contract_abis.get(to_checksum_address(tx.to_address))
        if contract_abi:
            try:
                contract = self.w3.eth.contract(
                    address=to_checksum_address(tx.to_address),
                    abi=contract_abi
                )
                func_obj, func_params = contract.decode_function_input(tx.input_data)
                tx.decoded_input = dict(func_params)
                tx.function_name = func_obj.fn_name
            except Exception as e:
                logger.debug(f"Function decoding failed: {e}")
    
    async def reconnect(self):
        """Reconnect to WebSocket"""
        self.status = ConnectionStatus.RECONNECTING
        self.reconnect_count += 1
        self.stats.reconnections += 1
        
        logger.warning(f"Reconnecting... (attempt {self.reconnect_count}/{self.max_reconnect_attempts})")
        await asyncio.sleep(self.reconnect_delay)
        
        await self.connect()
    
    async def start(self):
        """Start monitoring"""
        self.should_run = True
        logger.info("Starting mempool monitoring...")
        await self.connect()
    
    async def stop(self):
        """Stop monitoring and close connection"""
        self.should_run = False
        if self.ws:
            await self.ws.close()
        self.status = ConnectionStatus.DISCONNECTED
        logger.info("Monitoring stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return self.stats.to_dict()



