# Smart Contract Fuzz Tester

**Dynamic testing for smart contracts with random input generation**

Comprehensive fuzzing framework that generates random inputs to discover vulnerabilities, invariant violations, and crashes in Solidity smart contracts.

## Overview

The Smart Contract Fuzz Tester implements property-based testing and dynamic analysis through:

- **Input Generation**: Random and edge-case inputs for all Solidity types
- **Invariant Checking**: Property-based testing to verify contract guarantees
- **Vulnerability Detection**: Pattern matching for common security issues
- **Coverage-Guided Fuzzing**: Prioritize unexplored code paths

### Key Features

✅ **Complete Type Support** - All Solidity types (uint, int, address, bytes, arrays)  
✅ **Edge Case Generation** - Zero, max, overflow, underflow, special values  
✅ **Invariant Verification** - Balance, supply, ownership, arithmetic checks  
✅ **Vulnerability Detection** - Reentrancy, overflow, access control, etc.  
✅ **Coverage Tracking** - Function coverage with weighted selection  
✅ **Detailed Reporting** - Gas analysis, crash deduplication, severity classification  

## Installation

### Prerequisites

- Python 3.8 or higher
- Ethereum node access (local or RPC)

### Setup

1. **Install dependencies**:
   ```bash
   pip install web3 eth-abi eth-utils eth-account
   ```

2. **Set environment variables**:
   ```bash
   export RPC_URL="https://eth.llamarpc.com"  # Or your RPC endpoint
   ```

## Quick Start

### Basic Fuzzing

```python
from web3 import Web3
from fuzz_engine import FuzzEngine, FuzzConfig
from invariant_checker import InvariantType

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))

# Configure fuzzing
config = FuzzConfig(
    max_iterations=1000,
    edge_case_probability=0.3,
    timeout_seconds=300,
    verbose=True
)

# Initialize engine with your contract
engine = FuzzEngine(
    w3=w3,
    contract_address="0x...",
    contract_abi=your_abi,
    config=config
)

# Add invariants
engine.add_invariant(
    name="total_supply_positive",
    inv_type=InvariantType.SUPPLY,
    check_function=lambda: engine.contract.functions.totalSupply().call() >= 0,
    description="Total supply must be non-negative",
    critical=True
)

# Run fuzzing campaign
summary = engine.run_campaign()
```

### Input Generation

```python
from input_generator import InputGenerator

generator = InputGenerator(seed=12345)

# Generate single values
uint_input = generator.generate_uint(256, edge_case=True)
address_input = generator.generate_address(edge_case=False)
bytes_input = generator.generate_bytes(32, edge_case=True)

# Generate function inputs
param_types = ["address", "uint256", "bytes", "bool"]
inputs = generator.generate_function_inputs(param_types, edge_case_probability=0.3)

for inp in inputs:
    print(f"{inp.type_name}: {inp.value} ({inp.description})")
```

### Invariant Checking

```python
from invariant_checker import InvariantChecker, InvariantType

checker = InvariantChecker(w3, contract_address, contract_abi)

# Balance invariant
checker.add_invariant(
    name="user_balance_valid",
    inv_type=InvariantType.BALANCE,
    check_function=checker.create_balance_invariant(
        address="0x...",
        min_balance=0,
        max_balance=1000000
    ),
    description="User balance within bounds",
    critical=True
)

# Check all invariants
violations = checker.check_all_invariants()
```

### Vulnerability Detection

```python
from vulnerability_detector import VulnerabilityDetector

detector = VulnerabilityDetector(w3)

# Detect integer overflow
overflow_vuln = detector.detect_integer_overflow(
    function_name="add",
    a=2**256 - 10,
    b=20,
    operation="add"
)

# Detect access control bypass
access_vuln = detector.detect_access_control_bypass(
    function_name="withdrawAll",
    caller="0x1234...",
    expected_caller="0xowner...",
    execution_succeeded=True
)

# Get summary
summary = detector.get_summary()
print(f"Total vulnerabilities: {summary['total']}")
print(f"By severity: {summary['by_severity']}")
```

## Usage Examples

### Example 1: Fuzz an ERC20 Token

```python
from web3 import Web3
from fuzz_engine import FuzzEngine, FuzzConfig
from invariant_checker import InvariantType

w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))

erc20_abi = [
    # Your ERC20 ABI here
]

config = FuzzConfig(
    max_iterations=500,
    edge_case_probability=0.4,
    gas_limit=3_000_000,
    verbose=False
)

engine = FuzzEngine(w3, "0xTokenAddress", erc20_abi, config)

# Add ERC20 invariants
engine.add_invariant(
    name="supply_equals_sum_balances",
    inv_type=InvariantType.SUPPLY,
    check_function=lambda: verify_supply_invariant(engine.contract),
    description="Total supply = sum of all balances",
    critical=True
)

engine.add_invariant(
    name="no_negative_balances",
    inv_type=InvariantType.BALANCE,
    check_function=lambda: all_balances_positive(engine.contract),
    description="All balances non-negative",
    critical=True
)

summary = engine.run_campaign()

print(f"Issues found: {summary.total_vulnerabilities + summary.total_invariant_violations}")
print(f"Coverage: {summary.coverage_percentage:.1f}%")
```

### Example 2: Test Arithmetic Operations

```python
from input_generator import InputGenerator

generator = InputGenerator()

# Test add function with overflow cases
test_cases = []
for _ in range(100):
    a = generator.generate_uint(256, edge_case=True)
    b = generator.generate_uint(256, edge_case=True)
    test_cases.append((a.value, b.value))

for a, b in test_cases:
    try:
        result = contract.functions.add(a, b).call()
        print(f"✅ add({a}, {b}) = {result}")
    except Exception as e:
        print(f"❌ add({a}, {b}) reverted: {e}")
```

### Example 3: Detect Reentrancy

```python
from vulnerability_detector import VulnerabilityDetector

detector = VulnerabilityDetector(w3)

# Simulate execution trace (in real usage, get from tracing)
execution_trace = [
    {"opcode": "SLOAD", "address": "0x..."},
    {"opcode": "CALL", "to": "0xExternal..."},  # External call
    {"opcode": "SSTORE", "address": "0x..."},   # State change after call
]

vuln = detector.detect_reentrancy(
    contract_address="0xYourContract",
    function_name="withdraw",
    trace=execution_trace
)

if vuln:
    print(f"❌ {vuln.vuln_type.value}: {vuln.description}")
    print(f"   Severity: {vuln.severity.value}")
    print(f"   Fix: {vuln.recommendation}")
```

## Configuration

### FuzzConfig Options

```python
config = FuzzConfig(
    max_iterations=1000,        # Maximum fuzz iterations
    edge_case_probability=0.3,  # Probability of edge cases (0.0-1.0)
    timeout_seconds=300,        # Campaign timeout
    gas_limit=3_000_000,        # Gas limit per transaction
    mutation_rate=0.2,          # Mutation-based fuzzing rate
    seed=None,                  # Random seed (for reproducibility)
    verbose=True                # Print detailed logs
)
```

### Invariant Types

- **BALANCE**: Token balance constraints
- **SUPPLY**: Total supply rules
- **OWNERSHIP**: Owner/role verification
- **ARITHMETIC**: Math relationships (a + b >= a)
- **STATE**: State transition rules
- **ACCESS**: Permission checks

### Vulnerability Types

- **REENTRANCY**: State changes after external calls
- **INTEGER_OVERFLOW**: Arithmetic overflow
- **INTEGER_UNDERFLOW**: Arithmetic underflow
- **ACCESS_CONTROL**: Authorization bypass
- **UNCHECKED_CALL**: Failed external calls
- **DELEGATECALL**: Dangerous delegatecall usage
- **TX_ORIGIN**: tx.origin authentication
- **TIMESTAMP_DEPENDENCE**: block.timestamp logic
- **GAS_LIMIT**: DoS via gas limits
- **FRONT_RUNNING**: Transaction ordering issues

## API Reference

### FuzzEngine

| Method | Description |
|--------|-------------|
| `__init__(w3, contract_address, contract_abi, config)` | Initialize engine |
| `add_invariant(name, inv_type, check_function, description, critical)` | Add invariant |
| `get_fuzzable_functions()` | Get non-view/pure functions |
| `fuzz_function(function_abi, iteration, caller_account)` | Fuzz single function |
| `run_campaign()` | Run complete fuzzing campaign |

### InputGenerator

| Method | Description |
|--------|-------------|
| `generate_uint(bits, edge_case)` | Generate unsigned integer |
| `generate_int(bits, edge_case)` | Generate signed integer |
| `generate_address(edge_case)` | Generate Ethereum address |
| `generate_bytes(size, edge_case)` | Generate bytes value |
| `generate_string(edge_case)` | Generate string |
| `generate_array(base_type, length, edge_case)` | Generate array |
| `generate_for_type(type_str, edge_case)` | Generate for any type |
| `generate_function_inputs(param_types, edge_case_probability)` | Generate all function params |
| `mutate_input(original)` | Mutate existing input |

### InvariantChecker

| Method | Description |
|--------|-------------|
| `add_invariant(name, inv_type, check_function, description, critical)` | Add invariant |
| `check_all_invariants()` | Check all invariants |
| `create_balance_invariant(address, min_balance, max_balance)` | Balance check |
| `create_supply_invariant()` | Supply check |
| `create_ownership_invariant(expected_owner)` | Ownership check |
| `create_arithmetic_invariant(function_name, args, expected_min, expected_max)` | Arithmetic check |
| `create_no_overflow_invariant(a, b, operation)` | Overflow check |

### VulnerabilityDetector

| Method | Description |
|--------|-------------|
| `detect_reentrancy(contract_address, function_name, trace)` | Reentrancy check |
| `detect_integer_overflow(function_name, a, b, operation)` | Overflow check |
| `detect_integer_underflow(function_name, a, b)` | Underflow check |
| `detect_access_control_bypass(function_name, caller, expected_caller, execution_succeeded)` | Access control check |
| `detect_unchecked_call(function_name, call_result, call_checked)` | Unchecked call |
| `analyze_transaction(tx_receipt, function_name)` | Transaction analysis |

## Troubleshooting

### Error: "No fuzzable functions found"
**Solution**: Contract only has view/pure functions. Add state-changing functions to fuzz.

### Error: Gas estimation failed
**Solution**: Function would revert. This is expected - fuzzer detects reverts.

### Low coverage percentage
**Solution**: Increase `max_iterations` or add more test cases.

### Too many false positives
**Solution**: Adjust invariant criticality or refine check conditions.

## Production Checklist

- [ ] Define comprehensive invariants for your contract
- [ ] Set appropriate gas limits for your functions
- [ ] Configure edge case probability based on risk
- [ ] Enable verbose logging for detailed analysis
- [ ] Review all detected vulnerabilities
- [ ] Fix critical issues before deployment
- [ ] Re-run fuzzing after fixes
- [ ] Document known limitations

## References

- **Echidna**: https://github.com/crytic/echidna
- **Foundry Fuzz**: https://book.getfoundry.sh/forge/fuzz-testing
- **Trail of Bits Testing Guide**: https://blog.trailofbits.com/
- **Solidity Security Considerations**: https://docs.soliditylang.org/en/latest/security-considerations.html
- **Smart Contract Weakness Classification**: https://swcregistry.io/

## Support

For issues or questions:
- Ethereum Security: https://ethereum.org/en/security/
- OpenZeppelin Forum: https://forum.openzeppelin.com/
- GitHub Issues: [Your repository]

## License

MIT License - See LICENSE file for details

---

**Built for Spoon Awesome Skills** - Enterprise Code Quality & Security
