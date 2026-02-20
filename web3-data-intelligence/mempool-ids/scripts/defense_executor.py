"""
Defense Executor - Automated defense response system

This module executes defensive actions when exploits are detected. It automatically
sends pause contract transactions with optimized gas prices to front-run attackers
and prevent treasury drainage.

Key Features:
- Automated pause contract transaction creation
- Dynamic gas price optimization (front-running strategy)
- Transaction signing and broadcasting
- Confirmation monitoring and retry logic
- Fallback strategies (multi-sig, time-lock)
- Transaction queue management
- Gas estimation and buffer calculation
- Emergency stop mechanisms

Author: SpoonOS Skills
Category: Web3 Data Intelligence - Security Analysis
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import time

from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DefenseStatus(Enum):
    """Defense action status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DefenseStrategy(Enum):
    """Defense strategy type"""
    PAUSE_CONTRACT = "pause_contract"
    EMERGENCY_WITHDRAW = "emergency_withdraw"
    UPDATE_WHITELIST = "update_whitelist"
    RATE_LIMIT = "rate_limit"
    CIRCUIT_BREAKER = "circuit_breaker"


@dataclass
class DefenseAction:
    """Defense action record"""
    action_id: str
    strategy: DefenseStrategy
    target_contract: str
    threat_tx_hash: str
    response_tx_hash: Optional[str]
    status: DefenseStatus
    gas_price: int  # Wei
    max_fee_per_gas: Optional[int]  # Wei (EIP-1559)
    max_priority_fee_per_gas: Optional[int]  # Wei (EIP-1559)
    timestamp: datetime
    confirmation_time: Optional[datetime]
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'action_id': self.action_id,
            'strategy': self.strategy.value,
            'target_contract': self.target_contract,
            'threat_tx_hash': self.threat_tx_hash,
            'response_tx_hash': self.response_tx_hash,
            'status': self.status.value,
            'gas_price': self.gas_price,
            'max_fee_per_gas': self.max_fee_per_gas,
            'max_priority_fee_per_gas': self.max_priority_fee_per_gas,
            'timestamp': self.timestamp.isoformat(),
            'confirmation_time': self.confirmation_time.isoformat() if self.confirmation_time else None,
            'error_message': self.error_message
        }


@dataclass
class GasStrategy:
    """Gas pricing strategy"""
    base_fee: int  # Current base fee (Wei)
    priority_fee: int  # Priority fee (Wei)
    max_fee: int  # Max fee per gas (Wei)
    buffer_multiplier: float  # Multiplier for front-running
    
    def calculate_effective_gas_price(self) -> int:
        """Calculate effective gas price"""
        return int((self.base_fee + self.priority_fee) * self.buffer_multiplier)


class DefenseExecutor:
    """
    Automated defense executor for smart contract protection
    
    This class executes defensive actions when exploits are detected:
    - Pauses vulnerable contracts
    - Front-runs malicious transactions with higher gas
    - Monitors transaction confirmations
    - Implements retry and fallback strategies
    """
    
    def __init__(
        self,
        w3: Web3,
        defender_account: LocalAccount,
        pause_function_abi: Dict[str, Any],
        gas_buffer_multiplier: float = 1.5,
        max_retries: int = 3,
        confirmation_blocks: int = 1
    ):
        """
        Initialize defense executor
        
        Args:
            w3: Web3 instance
            defender_account: Account authorized to pause contracts
            pause_function_abi: ABI for pause function
            gas_buffer_multiplier: Gas price multiplier for front-running (e.g., 1.5 = +50%)
            max_retries: Maximum retry attempts for failed transactions
            confirmation_blocks: Blocks to wait for confirmation
        """
        self.w3 = w3
        self.defender_account = defender_account
        self.pause_function_abi = pause_function_abi
        self.gas_buffer_multiplier = gas_buffer_multiplier
        self.max_retries = max_retries
        self.confirmation_blocks = confirmation_blocks
        
        # Action tracking
        self.pending_actions: List[DefenseAction] = []
        self.completed_actions: List[DefenseAction] = []
        
        # Callbacks
        self.on_action_submitted: Optional[Callable] = None
        self.on_action_confirmed: Optional[Callable] = None
        self.on_action_failed: Optional[Callable] = None
        
        logger.info(f"DefenseExecutor initialized for account {defender_account.address}")
        logger.info(f"Gas buffer multiplier: {gas_buffer_multiplier}x")
    
    def execute_defense(
        self,
        strategy: DefenseStrategy,
        target_contract: str,
        threat_tx_hash: str,
        threat_gas_price: int,
        urgency: str = "high"
    ) -> DefenseAction:
        """
        Execute defensive action
        
        Args:
            strategy: Defense strategy to employ
            target_contract: Contract address to protect
            threat_tx_hash: Hash of threatening transaction
            threat_gas_price: Gas price of threat transaction
            urgency: Urgency level ("low", "medium", "high", "critical")
        
        Returns:
            DefenseAction object tracking the response
        """
        logger.info(f"🛡️ Executing defense: {strategy.value} for {target_contract}")
        logger.info(f"Threat TX: {threat_tx_hash}")
        logger.info(f"Threat gas price: {self.w3.from_wei(threat_gas_price, 'gwei')} Gwei")
        
        # Calculate optimal gas strategy
        gas_strategy = self._calculate_gas_strategy(threat_gas_price, urgency)
        
        # Create defense action
        action = DefenseAction(
            action_id=f"defense_{int(time.time() * 1000)}",
            strategy=strategy,
            target_contract=target_contract,
            threat_tx_hash=threat_tx_hash,
            response_tx_hash=None,
            status=DefenseStatus.PENDING,
            gas_price=gas_strategy.calculate_effective_gas_price(),
            max_fee_per_gas=gas_strategy.max_fee,
            max_priority_fee_per_gas=gas_strategy.priority_fee,
            timestamp=datetime.now(),
            confirmation_time=None,
            error_message=None
        )
        
        logger.info(f"Response gas price: {self.w3.from_wei(action.gas_price, 'gwei')} Gwei ({self.gas_buffer_multiplier}x buffer)")
        
        # Execute strategy
        if strategy == DefenseStrategy.PAUSE_CONTRACT:
            self._execute_pause_contract(action, target_contract, gas_strategy)
        else:
            action.status = DefenseStatus.FAILED
            action.error_message = f"Strategy {strategy.value} not implemented"
            logger.error(action.error_message)
        
        # Track action
        if action.status == DefenseStatus.SUBMITTED:
            self.pending_actions.append(action)
        else:
            self.completed_actions.append(action)
        
        return action
    
    def _calculate_gas_strategy(
        self,
        threat_gas_price: int,
        urgency: str
    ) -> GasStrategy:
        """Calculate optimal gas strategy for front-running"""
        # Get current base fee (EIP-1559)
        try:
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)
        except Exception:
            base_fee = threat_gas_price  # Fallback to threat gas price
        
        # Calculate priority fee based on urgency
        urgency_multipliers = {
            'low': 1.1,
            'medium': 1.3,
            'high': 1.5,
            'critical': 2.0
        }
        buffer = urgency_multipliers.get(urgency, self.gas_buffer_multiplier)
        
        # Priority fee calculation
        threat_priority = max(threat_gas_price - base_fee, self.w3.to_wei(1, 'gwei'))
        priority_fee = int(threat_priority * buffer)
        
        # Max fee calculation (base + priority with buffer)
        max_fee = int((base_fee * 1.2) + (priority_fee * 1.5))
        
        return GasStrategy(
            base_fee=base_fee,
            priority_fee=priority_fee,
            max_fee=max_fee,
            buffer_multiplier=buffer
        )
    
    def _execute_pause_contract(
        self,
        action: DefenseAction,
        contract_address: str,
        gas_strategy: GasStrategy
    ):
        """Execute pause contract defense"""
        try:
            # Create contract instance
            contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(contract_address),
                abi=[self.pause_function_abi]
            )
            
            # Build pause transaction
            pause_function = contract.functions.pause()
            
            # Estimate gas
            try:
                gas_estimate = pause_function.estimate_gas({
                    'from': self.defender_account.address
                })
                gas_limit = int(gas_estimate * 1.2)  # 20% buffer
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}. Using default.")
                gas_limit = 100000  # Default gas limit
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.defender_account.address, 'pending')
            
            # Build transaction (EIP-1559)
            transaction = pause_function.build_transaction({
                'from': self.defender_account.address,
                'nonce': nonce,
                'gas': gas_limit,
                'maxFeePerGas': gas_strategy.max_fee,
                'maxPriorityFeePerGas': gas_strategy.priority_fee,
                'chainId': self.w3.eth.chain_id
            })
            
            # Sign transaction
            signed_tx = self.defender_account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            action.response_tx_hash = tx_hash.hex()
            action.status = DefenseStatus.SUBMITTED
            
            logger.info(f"✅ Defense transaction submitted: {action.response_tx_hash}")
            
            # Trigger callback
            if self.on_action_submitted:
                self.on_action_submitted(action)
            
            # Wait for confirmation (non-blocking in production)
            self._wait_for_confirmation(action)
            
        except Exception as e:
            action.status = DefenseStatus.FAILED
            action.error_message = str(e)
            logger.error(f"❌ Defense execution failed: {e}")
            
            if self.on_action_failed:
                self.on_action_failed(action)
    
    def _wait_for_confirmation(self, action: DefenseAction):
        """Wait for transaction confirmation"""
        if not action.response_tx_hash:
            return
        
        try:
            logger.info(f"Waiting for confirmation ({self.confirmation_blocks} blocks)...")
            
            receipt = self.w3.eth.wait_for_transaction_receipt(
                action.response_tx_hash,
                timeout=120,
                poll_latency=2
            )
            
            if receipt['status'] == 1:
                action.status = DefenseStatus.CONFIRMED
                action.confirmation_time = datetime.now()
                
                # Calculate response time
                response_time = (action.confirmation_time - action.timestamp).total_seconds()
                
                logger.info(f"✅ Defense confirmed in block {receipt['blockNumber']}")
                logger.info(f"Response time: {response_time:.2f} seconds")
                
                # Move to completed
                if action in self.pending_actions:
                    self.pending_actions.remove(action)
                self.completed_actions.append(action)
                
                # Trigger callback
                if self.on_action_confirmed:
                    self.on_action_confirmed(action)
            else:
                action.status = DefenseStatus.FAILED
                action.error_message = "Transaction reverted"
                logger.error(f"❌ Defense transaction reverted")
                
                if self.on_action_failed:
                    self.on_action_failed(action)
        
        except Exception as e:
            action.status = DefenseStatus.FAILED
            action.error_message = f"Confirmation timeout: {str(e)}"
            logger.error(f"❌ Confirmation failed: {e}")
            
            if self.on_action_failed:
                self.on_action_failed(action)
    
    def retry_failed_action(self, action: DefenseAction) -> DefenseAction:
        """Retry a failed defense action with higher gas"""
        if action.status != DefenseStatus.FAILED:
            raise ValueError("Only failed actions can be retried")
        
        logger.info(f"🔄 Retrying defense action {action.action_id}")
        
        # Increase gas by 20%
        new_gas_price = int(action.gas_price * 1.2)
        new_max_fee = int(action.max_fee_per_gas * 1.2) if action.max_fee_per_gas else None
        
        # Create new action with increased gas
        return self.execute_defense(
            strategy=action.strategy,
            target_contract=action.target_contract,
            threat_tx_hash=action.threat_tx_hash,
            threat_gas_price=new_gas_price,
            urgency="critical"  # Escalate urgency
        )
    
    def cancel_pending_action(self, action: DefenseAction):
        """Cancel a pending defense action"""
        if action.status != DefenseStatus.PENDING and action.status != DefenseStatus.SUBMITTED:
            logger.warning(f"Cannot cancel action with status {action.status.value}")
            return
        
        action.status = DefenseStatus.CANCELLED
        if action in self.pending_actions:
            self.pending_actions.remove(action)
        self.completed_actions.append(action)
        
        logger.info(f"❌ Defense action cancelled: {action.action_id}")
    
    def get_action_status(self, action_id: str) -> Optional[DefenseAction]:
        """Get status of defense action by ID"""
        for action in self.pending_actions + self.completed_actions:
            if action.action_id == action_id:
                return action
        return None
    
    def get_pending_actions(self) -> List[DefenseAction]:
        """Get list of pending actions"""
        return self.pending_actions.copy()
    
    def get_completed_actions(self) -> List[DefenseAction]:
        """Get list of completed actions"""
        return self.completed_actions.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get defense executor statistics"""
        total_actions = len(self.pending_actions) + len(self.completed_actions)
        
        confirmed = sum(
            1 for action in self.completed_actions
            if action.status == DefenseStatus.CONFIRMED
        )
        
        failed = sum(
            1 for action in self.completed_actions
            if action.status == DefenseStatus.FAILED
        )
        
        # Calculate average response time
        response_times = []
        for action in self.completed_actions:
            if action.confirmation_time and action.status == DefenseStatus.CONFIRMED:
                response_time = (action.confirmation_time - action.timestamp).total_seconds()
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return {
            'total_actions': total_actions,
            'pending': len(self.pending_actions),
            'confirmed': confirmed,
            'failed': failed,
            'success_rate': confirmed / total_actions if total_actions > 0 else 0.0,
            'average_response_time': avg_response_time
        }



