# Smart Contract Audit Tools

## Static Analysis

### Slither (Trail of Bits)
```bash
# Install
pip install slither-analyzer

# Basic scan
slither .

# With specific detectors
slither . --detect reentrancy-eth,reentrancy-no-eth

# Generate report
slither . --json report.json

# Print contract summary
slither . --print contract-summary

# Check specific contract
slither src/Contract.sol

# Exclude dependencies
slither . --filter-paths "node_modules|lib"
```

**Key Detectors:**
- `reentrancy-eth` - Reentrancy with ETH transfer
- `reentrancy-no-eth` - Reentrancy without ETH
- `arbitrary-send-eth` - Arbitrary ETH send
- `suicidal` - Unprotected selfdestruct
- `uninitialized-state` - Uninitialized state variables
- `locked-ether` - Contracts that lock ETH
- `tx-origin` - Dangerous tx.origin usage

### Aderyn (Cyfrin)
```bash
# Install
cargo install aderyn

# Basic scan
aderyn .

# Output to file
aderyn . -o report.md

# Specific path
aderyn ./src

# JSON output
aderyn . --output-format json
```

**Faster than Slither, written in Rust.**

### Mythril (ConsenSys)
```bash
# Install
pip install mythril

# Analyze contract
myth analyze src/Contract.sol

# With timeout
myth analyze src/Contract.sol --execution-timeout 300

# Specific address (mainnet)
myth analyze --rpc infura-mainnet -a 0x...

# JSON output
myth analyze src/Contract.sol -o json
```

**Symbolic execution - finds deeper bugs but slower.**

### Solhint (Linter)
```bash
# Install
npm install -g solhint

# Initialize config
solhint --init

# Lint files
solhint 'contracts/**/*.sol'

# Auto-fix
solhint 'contracts/**/*.sol' --fix
```

### 4naly3er (Picodes)
```bash
# Clone and run
git clone https://github.com/Picodes/4naly3er
cd 4naly3er
yarn install
yarn analyze /path/to/project
```

**Generates comprehensive QA/Gas reports automatically.**

### Wake (Ackee Blockchain)
```bash
# Install
pip install eth-wake

# Initialize
wake init

# Detect vulnerabilities
wake detect all

# Specific detectors
wake detect reentrancy

# Print AST
wake print
```

**Python-based framework with custom detector support.**

---

## Fuzzing

### Echidna (Trail of Bits)
```bash
# Install
pip install echidna

# Or via Docker
docker pull trailofbits/echidna

# Run fuzzer
echidna . --contract TestContract

# With config
echidna . --contract TestContract --config echidna.yaml
```

**echidna.yaml:**
```yaml
testLimit: 50000
timeout: 300
corpusDir: "corpus"
coverage: true
```

**Test Example:**
```solidity
contract EchidnaTest {
    Target target;
    
    constructor() {
        target = new Target();
    }
    
    // Invariant: balance should never exceed deposit
    function echidna_balance_check() public view returns (bool) {
        return target.balance() <= target.totalDeposits();
    }
    
    // Property test
    function test_withdraw(uint256 amount) public {
        target.withdraw(amount);
        assert(target.balance() >= 0);
    }
}
```

### Medusa (Trail of Bits)
```bash
# Install
go install github.com/crytic/medusa@latest

# Run
medusa fuzz --config medusa.json
```

**medusa.json:**
```json
{
  "fuzzing": {
    "workers": 10,
    "timeout": 300,
    "testLimit": 100000
  },
  "compilation": {
    "platform": "foundry"
  }
}
```

**Faster than Echidna, better parallelization.**

### Foundry Fuzz
```bash
# Run fuzz tests
forge test --fuzz-runs 10000

# With seed
forge test --fuzz-seed 12345
```

```solidity
function testFuzz_Deposit(uint256 amount) public {
    vm.assume(amount > 0 && amount < 1e30);
    
    target.deposit{value: amount}();
    assertEq(target.balanceOf(address(this)), amount);
}
```

---

## Formal Verification

### Certora Prover
```bash
# Install CLI
pip install certora-cli

# Run verification
certoraRun Contract.sol --verify Contract:spec.spec
```

**spec.spec:**
```cvl
rule withdrawPreservesInvariant {
    env e;
    uint256 balanceBefore = balance(e.msg.sender);
    
    withdraw(e, amount);
    
    uint256 balanceAfter = balance(e.msg.sender);
    assert balanceAfter == balanceBefore - amount;
}

invariant totalSupplyCorrect()
    totalSupply() == sum(balances)
```

### Halmos (a16z)
```bash
# Install
pip install halmos

# Run symbolic tests
halmos --contract TestContract
```

```solidity
function check_withdraw(uint256 amount) public {
    uint256 before = target.balanceOf(address(this));
    
    target.withdraw(amount);
    
    uint256 after = target.balanceOf(address(this));
    assert(after == before - amount);
}
```

### Move Prover (Aptos/Sui)
```bash
# Run prover
aptos move prove

# With specific options
aptos move prove --filter function_name
```

---

## Transaction Analysis & Debugging

### Phalcon (BlockSec)
```
URL: https://phalcon.blocksec.com/explorer

Features:
- Transaction visualization
- Fund flow analysis
- Attack replay
- Cross-chain tracing
```

**Usage:**
1. Paste transaction hash
2. View call trace tree
3. Analyze fund flows
4. Export attack path

### MetaSleuth (BlockSec)
```
URL: https://metasleuth.io

Features:
- Address profiling
- Fund tracing
- Entity labeling
- Risk scoring
```

### Tenderly
```bash
# Install CLI
npm install -g @tenderly/cli

# Initialize
tenderly init

# Debug transaction
tenderly debug tx <tx_hash>

# Fork network
tenderly fork mainnet
```

```
Web Dashboard: https://dashboard.tenderly.co

Features:
- Transaction simulation
- Gas profiler
- State diff
- Debugger
```

### Foundry Debug
```bash
# Debug test
forge test --debug testFunction

# Debug transaction (fork)
cast run <tx_hash> --rpc-url mainnet --debug
```

---

## Attack Simulation

### DeFiHackLabs
```bash
git clone https://github.com/SunWeb3Sec/DeFiHackLabs
cd DeFiHackLabs
forge test --match-contract Exploit
```

**Collection of real-world exploit PoCs.**

### Damn Vulnerable DeFi
```bash
git clone https://github.com/tinchoabbate/damn-vulnerable-defi
cd damn-vulnerable-defi
forge test
```

**Practice challenges for security researchers.**

---

## Multi-Chain Tools

### Solana

**Soteria (Static Analysis):**
```bash
# Install
cargo install soteria

# Analyze
soteria .
```

**Anchor Test:**
```bash
anchor test
anchor test --skip-local-validator
```

### Move (Aptos/Sui)

**Move Prover:**
```bash
aptos move prove
sui move prove
```

**Move Analyzer:**
```bash
# VS Code extension provides analysis
```

### Cairo (Starknet)

**Cairo-lint:**
```bash
scarb cairo-lint
```

**Starknet Foundry:**
```bash
snforge test
```

---

## Recommended Workflow

### Quick Scan (5 min)
```bash
# 1. Static analysis
slither . --filter-paths "test|lib"
aderyn .

# 2. Check common issues
solhint 'src/**/*.sol'
```

### Standard Audit
```bash
# 1. Static analysis
slither . --json slither-report.json
aderyn . -o aderyn-report.md

# 2. Generate QA report
4naly3er /path/to/project

# 3. Run existing tests
forge test -vvv

# 4. Fuzz critical functions
forge test --fuzz-runs 10000

# 5. Manual review with findings from tools
```

### Deep Audit
```bash
# All of the above, plus:

# 1. Symbolic execution
halmos --contract TargetTest

# 2. Extended fuzzing
echidna . --contract InvariantTest --config echidna.yaml

# 3. Formal verification (if specs exist)
certoraRun ...

# 4. Transaction analysis of similar protocols
# Use Phalcon/Tenderly to study past exploits
```

---

## Tool Comparison

| Tool | Speed | Depth | False Positives | Best For |
|------|-------|-------|-----------------|----------|
| Slither | Fast | Medium | Medium | Quick scans |
| Aderyn | Very Fast | Medium | Low | CI/CD |
| Mythril | Slow | Deep | Low | Complex bugs |
| Echidna | Medium | Deep | Very Low | Invariants |
| Halmos | Slow | Very Deep | Very Low | Formal props |
| 4naly3er | Fast | Shallow | Medium | QA reports |

## Environment Variables
```bash
# API Keys for blockchain explorers
export ETHERSCAN_API_KEY=xxx
export BSCSCAN_API_KEY=xxx

# RPC endpoints for forking
export ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/xxx
export BSC_RPC_URL=https://bsc-dataseed.binance.org

# Solodit API
export SOLODIT_API_KEY=sk_xxx
```
