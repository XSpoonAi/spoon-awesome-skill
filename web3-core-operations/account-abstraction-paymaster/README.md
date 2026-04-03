# Account Abstraction Paymaster

> **Sponsor gas fees for users with ERC-4337 Account Abstraction**

A production-ready implementation of ERC-4337 Paymaster for sponsoring gas fees on behalf of users. Features comprehensive policy controls, real-time gas estimation, multi-chain support, and seamless integration with EntryPoint v0.6.0.

## Overview

Account Abstraction (ERC-4337) enables users to interact with smart contracts without holding ETH for gas. This skill provides a complete Paymaster infrastructure to sponsor gas fees with customizable policies, spending limits, and validation rules.

### Key Features

- ✅ **ERC-4337 Compliant** - Full EntryPoint v0.6.0 integration
- ✅ **Gas Sponsorship** - Sponsor transactions for whitelisted users
- ✅ **Policy Controls** - Whitelist, blacklist, spending limits, token gating
- ✅ **Multi-Chain** - Ethereum, Polygon, Arbitrum, Optimism, Base
- ✅ **Real-Time Gas** - Dynamic gas estimation from network
- ✅ **UserOp Builder** - Construct valid UserOperations easily
- ✅ **EntryPoint Integration** - Submit and track operations on-chain
- ✅ **Safety Features** - Daily limits, verification, spending tracking

## What is ERC-4337?

ERC-4337 introduces Account Abstraction without requiring consensus-layer protocol changes. Key concepts:

- **UserOperation**: Transaction-like object containing user intent
- **EntryPoint**: Singleton contract that processes UserOperations
- **Smart Account**: Contract wallet that users interact through
- **Bundler**: Entity that submits UserOperations to EntryPoint
- **Paymaster**: Contract that sponsors gas fees for UserOperations

## Use Cases

### 1. Onboarding New Users
Sponsor gas for new users so they can interact with your dapp without buying ETH first.

### 2. Token-Gated Gasless Transactions
Allow token holders to use your dapp without gas costs (e.g., NFT holders get free transactions).

### 3. Subscription Services
Sponsor transactions for premium subscribers within daily/monthly limits.

### 4. DAO Operations
Enable DAO members to execute governance actions without gas fees.

### 5. Gaming & Metaverse
Provide seamless UX by sponsoring in-game transactions for players.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Dapp                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              UserOperationBuilder                                │
│  • Build UserOperations                                          │
│  • Encode call data                                              │
│  • Estimate gas limits                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              PaymasterSponsor                                    │
│  • Validate sponsorship eligibility                              │
│  • Check policy (whitelist, limits)                              │
│  • Generate paymasterAndData                                     │
│  • Track spending                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              EntryPointInteraction                               │
│  • Submit UserOperations (handleOps)                             │
│  • Monitor transaction status                                    │
│  • Parse events (UserOperationEvent)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            ERC-4337 EntryPoint Contract                          │
│              0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789          │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- web3.py 6.0+
- eth-account 0.9+
- eth-abi 4.0+

### Setup

```bash
# Clone repository
cd web3-core-operations/account-abstraction-paymaster

# Install dependencies
pip install web3 eth-account eth-abi

# Set environment variables
export RPC_URL="https://eth.llamarpc.com"
export PAYMASTER_ADDRESS="0x..."  # Your deployed paymaster contract
export BUNDLER_PRIVATE_KEY="0x..."  # For submitting UserOps
export PAYMASTER_OWNER_KEY="0x..."  # For signing sponsorships
```

## Quick Start

### 1. Build a UserOperation

```python
from web3 import Web3
from user_operation_builder import UserOperationBuilder

# Connect to network
w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
builder = UserOperationBuilder(w3)

# Build ETH transfer operation
user_op = builder.build_eth_transfer_op(
    sender="0xYourSmartAccount...",  # User's smart account
    recipient="0xRecipient...",
    amount_wei=Web3.to_wei(0.1, 'ether')
)

print(f"UserOp built: {user_op.to_dict()}")
```

### 2. Sponsor with Paymaster

```python
from paymaster_sponsor import PaymasterSponsor, SponsorshipPolicy

# Initialize paymaster
sponsor = PaymasterSponsor(
    w3=w3,
    paymaster_address="0xYourPaymaster...",
    owner_private_key="0x..."  # Signs sponsorship data
)

# Define sponsorship policy
policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=500_000,  # Max 500k gas per operation
    max_cost_per_op_eth=0.01,  # Max 0.01 ETH per operation
    daily_limit_eth=0.1,  # 0.1 ETH per user per day
    whitelist=["0xUser1...", "0xUser2..."],  # Allowed users
    blacklist=[],
    require_token_balance=None  # Optional: (token_address, min_balance)
)

# Sponsor the operation
result = sponsor.sponsor_user_operation(
    user_op=user_op.to_dict(),
    policy=policy
)

if result.success:
    print(f"✅ Sponsored! Gas: {result.gas_sponsored}, Cost: {result.cost_eth} ETH")
    # UserOp now has paymasterAndData field filled
else:
    print(f"❌ Not sponsored: {result.reason}")
```

### 3. Submit to EntryPoint

```python
from entrypoint_interaction import EntryPointInteraction

# Initialize EntryPoint interaction
entrypoint = EntryPointInteraction(
    w3=w3,
    bundler_key="0x..."  # Bundler submits UserOps
)

# Submit UserOperation
receipt = entrypoint.submit_user_operations(
    user_ops=[user_op.to_dict()],
    beneficiary="0xBundlerFeeRecipient...",
    wait_for_receipt=True
)

if receipt and receipt.success:
    print(f"✅ UserOp executed!")
    print(f"   TX: {receipt.tx_hash}")
    print(f"   Block: {receipt.block_number}")
    print(f"   Gas used: {receipt.actual_gas_used}")
    print(f"   Cost: {receipt.actual_gas_cost} ETH")
```

## Sponsorship Policies

### Policy Configuration

```python
from paymaster_sponsor import SponsorshipPolicy

# Example 1: Token-gated sponsorship
policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=300_000,
    max_cost_per_op_eth=0.005,
    daily_limit_eth=0.05,
    whitelist=[],  # Empty = anyone with token balance
    blacklist=["0xScammer..."],
    require_token_balance=(
        "0xYourToken...",  # ERC20 token address
        Web3.to_wei(100, 'ether')  # Min 100 tokens required
    )
)

# Example 2: Whitelist-only sponsorship
policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=500_000,
    max_cost_per_op_eth=0.01,
    daily_limit_eth=0.1,
    whitelist=[
        "0xPremiumUser1...",
        "0xPremiumUser2...",
        "0xDAOMember..."
    ],
    blacklist=[],
    require_token_balance=None
)

# Example 3: Open sponsorship with limits
policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=200_000,
    max_cost_per_op_eth=0.002,
    daily_limit_eth=0.02,  # Low daily limit for open access
    whitelist=[],  # Anyone can use
    blacklist=[],
    require_token_balance=None
)
```

### Policy Enforcement

The paymaster automatically validates:
- ✅ User is whitelisted (if whitelist not empty)
- ✅ User is not blacklisted
- ✅ Gas limit within max_gas_per_op
- ✅ Estimated cost within max_cost_per_op_eth
- ✅ Daily spending within daily_limit_eth
- ✅ Token balance meets requirement (if configured)

## Advanced Usage

### Build Complex UserOperations

```python
# ERC20 token transfer
user_op = builder.build_erc20_transfer_op(
    sender="0xSmartAccount...",
    token="0xUSDC...",
    recipient="0xRecipient...",
    amount=1_000_000,  # 1 USDC (6 decimals)
    paymaster_and_data="0x..."  # Add after sponsorship
)

# Batch operations
call_data = builder.encode_execute_batch(
    targets=["0xContract1...", "0xContract2..."],
    values=[0, 0],
    datas=["0xdata1...", "0xdata2..."]
)

user_op = builder.build_user_operation(
    sender="0xSmartAccount...",
    call_data=call_data
)
```

### Manage Paymaster Deposits

```python
# Check paymaster's deposit in EntryPoint
balance = sponsor.get_paymaster_deposit()
print(f"Paymaster deposit: {balance} ETH")

# Deposit more ETH to paymaster's EntryPoint balance
tx_hash = entrypoint.deposit_to_entrypoint(
    account="0xPaymaster...",
    amount_eth=1.0,
    from_key="0xOwnerKey..."
)

# Reset daily limits (call this daily via cron)
sponsor.reset_daily_limits()
```

### Monitor UserOperation Status

```python
# Get UserOp hash
user_op_hash = builder.get_user_op_hash(user_op)
print(f"UserOp hash: {user_op_hash}")

# Get nonce for smart account
nonce = entrypoint.get_nonce("0xSmartAccount...")
print(f"Current nonce: {nonce}")

# Check account balance in EntryPoint
balance = entrypoint.get_deposit_balance("0xSmartAccount...")
print(f"Account deposit: {balance} ETH")
```

## Smart Contract Integration

### EntryPoint Contract

**Address (all chains)**: `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789`

**Supported Networks**:
- Ethereum Mainnet
- Polygon
- Arbitrum One
- Optimism
- Base
- More coming soon

**Key Functions**:
- `handleOps(UserOperation[] ops, address beneficiary)` - Submit UserOperations
- `getUserOpHash(UserOperation userOp)` - Get hash for signing
- `getNonce(address sender, uint192 key)` - Get account nonce
- `depositTo(address account)` - Deposit funds for account
- `balanceOf(address account)` - Check deposit balance

### Paymaster Contract

Deploy your own verifying paymaster contract:

```solidity
contract VerifyingPaymaster is BasePaymaster {
    address public immutable verifyingSigner;
    
    constructor(IEntryPoint _entryPoint, address _verifyingSigner) 
        BasePaymaster(_entryPoint) 
    {
        verifyingSigner = _verifyingSigner;
    }
    
    function _validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) internal override returns (bytes memory context, uint256 validationData) {
        // Extract signature from paymasterAndData
        (uint48 validUntil, uint48 validAfter, bytes memory signature) = 
            abi.decode(userOp.paymasterAndData[20:], (uint48, uint48, bytes));
        
        // Verify signature
        bytes32 hash = keccak256(abi.encode(userOpHash, validUntil, validAfter));
        require(verifyingSigner == hash.recover(signature), "Invalid signature");
        
        // Check time range
        if (block.timestamp > validUntil || block.timestamp < validAfter) {
            return ("", _packValidationData(true, validUntil, validAfter));
        }
        
        return ("", _packValidationData(false, validUntil, validAfter));
    }
}
```

## Examples

### Complete Flow Example

```python
from web3 import Web3
from user_operation_builder import UserOperationBuilder
from paymaster_sponsor import PaymasterSponsor, SponsorshipPolicy
from entrypoint_interaction import EntryPointInteraction

# Setup
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
builder = UserOperationBuilder(w3)
sponsor = PaymasterSponsor(w3, "0xPaymaster...", owner_private_key="0x...")
entrypoint = EntryPointInteraction(w3, bundler_key="0x...")

# Define policy
policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=500_000,
    max_cost_per_op_eth=0.01,
    daily_limit_eth=0.1,
    whitelist=["0xUser..."],
    blacklist=[],
    require_token_balance=None
)

# Build UserOperation
user_op = builder.build_eth_transfer_op(
    sender="0xSmartAccount...",
    recipient="0xRecipient...",
    amount_wei=Web3.to_wei(0.05, 'ether')
)

# Sponsor
result = sponsor.sponsor_user_operation(user_op.to_dict(), policy)
if not result.success:
    print(f"Sponsorship denied: {result.reason}")
    exit()

# Submit
receipt = entrypoint.submit_user_operations([user_op.to_dict()])
if receipt and receipt.success:
    print(f"✅ Transaction executed: {receipt.tx_hash}")
else:
    print("❌ Transaction failed")
```

## Gas Optimization

### Optimize UserOperation Gas

```python
# Use lower gas multiplier for known operations
user_op = builder.build_user_operation(
    sender="0x...",
    call_data="0x...",
    gas_multiplier=1.2  # Default is 1.5
)

# Batch multiple operations to save gas
call_data = builder.encode_execute_batch(
    targets=["0xAddr1", "0xAddr2", "0xAddr3"],
    values=[0, 0, 0],
    datas=["0xdata1", "0xdata2", "0xdata3"]
)
```

### Monitor Paymaster Spending

```python
import json

# Track sponsorships
sponsorships = []

for user in users:
    result = sponsor.sponsor_user_operation(user_op, policy)
    if result.success:
        sponsorships.append({
            'user': user,
            'gas': result.gas_sponsored,
            'cost': result.cost_eth,
            'timestamp': time.time()
        })

# Calculate total spending
total_cost = sum(s['cost'] for s in sponsorships)
print(f"Total sponsored: {total_cost} ETH")

# Save for analytics
with open('sponsorships.json', 'w') as f:
    json.dump(sponsorships, f, indent=2)
```

## Production Deployment

### Infrastructure Requirements

1. **RPC Endpoint** - Reliable RPC with high rate limits (Alchemy, Infura, QuickNode)
2. **Paymaster Contract** - Deploy verifying paymaster on target chain(s)
3. **Bundler** - Run own bundler or use service (Stackup, Pimlico, Biconomy)
4. **Monitoring** - Track sponsorships, gas costs, policy violations
5. **Key Management** - Secure storage for paymaster signing key

### Security Best Practices

- ✅ **Whitelist by default** - Only sponsor known/verified users
- ✅ **Set conservative limits** - Start with low daily limits
- ✅ **Monitor spending** - Alert on unusual patterns
- ✅ **Rotate keys** - Regular keyrotation for paymaster signer
- ✅ **Validate signatures** - Always verify UserOperation signatures
- ✅ **Rate limiting** - Implement per-user rate limits
- ✅ **Audit contracts** - Professional audit before mainnet

### Recommended Limits

```python
# Conservative policy for production start
production_policy = SponsorshipPolicy(
    enabled=True,
    max_gas_per_op=300_000,  # Most operations < 200k
    max_cost_per_op_eth=0.003,  # ~$10 at $3000/ETH
    daily_limit_eth=0.03,  # 10 ops/day max
    whitelist=verified_users,  # Explicit whitelist
    blacklist=flagged_addresses,
    require_token_balance=("0xToken", Web3.to_wei(50, 'ether'))
)
```

## Troubleshooting

### Common Issues

**"Not eligible: Address not in whitelist"**
- Ensure user address is in policy.whitelist
- Check address checksum (use Web3.to_checksum_address)

**"Not eligible: Daily limit exceeded"**
- User has reached daily_limit_eth
- Call sponsor.reset_daily_limits() to reset (once per day)
- Check sponsor.daily_spending dict for current usage

**"Hash error: execution reverted"**
- UserOperation format is invalid
- Check all fields are properly encoded
- Verify EntryPoint address is correct for chain

**"Submission failed: insufficient funds"**
- Bundler account needs ETH for gas
- Paymaster needs deposit in EntryPoint
- Check balances with entrypoint.get_deposit_balance()

## Code Statistics

- **paymaster_sponsor.py**: 450 lines - Gas sponsorship logic
- **entrypoint_interaction.py**: 380 lines - EntryPoint integration
- **user_operation_builder.py**: 420 lines - UserOp construction
- **Total**: 1,250 lines of production code

## References

- [ERC-4337 Specification](https://eips.ethereum.org/EIPS/eip-4337)
- [EntryPoint Contract](https://github.com/eth-infinitism/account-abstraction)
- [Account Abstraction Docs](https://www.erc4337.io/)
- [Bundler Specification](https://github.com/eth-infinitism/bundler-spec)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for ERC-4337 Account Abstraction**
