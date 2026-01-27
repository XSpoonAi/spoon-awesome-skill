# Neo N3 Testing Frameworks

## Neo-Express (Local Network)

### Commands
```bash
neoxp create                     # Create private network
neoxp run                        # Start network
neoxp wallet create <name>       # Create wallet
neoxp transfer <amount> GAS <from> <to>
neoxp contract deploy <nef>      # Deploy contract
neoxp contract invoke <hash> <method> [args]
neoxp checkpoint create <name>   # Save state
neoxp checkpoint restore <name>  # Restore state
neoxp batch <file>               # Batch commands
```

### Express Config (.neo-express)
```json
{
  "magic": 1234567890,
  "address-version": 53,
  "accounts": [
    {
      "name": "node1",
      "script-hash": "0x..."
    }
  ],
  "consensus-nodes": [...]
}
```

## Neo-Test (C# Unit Testing)

### Test Template
```csharp
using Neo.SmartContract.Testing;
using Neo.SmartContract.Testing.TestingStandards;

[TestClass]
public class TargetContractTests : TestBase<TargetContract>
{
    [TestInitialize]
    public void Setup()
    {
        // Deploy contract
        var nef = File.ReadAllBytes("./Target.nef");
        var manifest = File.ReadAllText("./Target.manifest.json");
        Contract = Engine.Deploy<TargetContract>(nef, manifest);
    }

    [TestMethod]
    public void TestExploit()
    {
        // Setup attacker
        var attacker = Engine.CreateNewWallet();
        Engine.SetTransactionSigners(attacker);
        
        // Execute exploit
        var balanceBefore = Engine.Native.GAS.BalanceOf(attacker.Account);
        Contract.VulnerableMethod();
        var balanceAfter = Engine.Native.GAS.BalanceOf(attacker.Account);
        
        Assert.IsTrue(balanceAfter > balanceBefore);
    }
}
```

### NeoTestRunner Commands
```bash
dotnet test                          # Run all tests
dotnet test --filter "Name=TestX"    # Run specific test
dotnet test --logger "console;verbosity=detailed"
```

## Neo-Fairy-Test (Mainnet Fork)

### Setup
```bash
# Install as NeoCLI plugin
dotnet add package Neo.Plugins.Fairy

# Or use Docker
docker pull neo3-fairy
```

### Fairy Operations
```python
from neo_fairy_client import FairyClient

client = FairyClient("http://localhost:16868")

# Simulate transaction against real network state
result = client.invoke_script(
    script=script_bytes,
    signers=[signer],
    fairy=True  # Use fairy transaction (doesn't affect real state)
)

# Deploy fairy contract
client.deploy_fairy_contract(nef_bytes, manifest)

# Test with real mainnet data
client.set_network("mainnet")
balance = client.get_balance(account, "NEO")
```

## NEO•ONE (TypeScript)

### Test Template
```typescript
import { withContracts } from '../neo-one/test';

describe('Target', () => {
  test('exploit demonstration', async () => {
    await withContracts(async ({ target, accountIDs, masterAccountID }) => {
      const attacker = accountIDs[0];
      
      // Get initial state
      const balanceBefore = await target.balanceOf(attacker);
      
      // Execute exploit
      const receipt = await target.vulnerableMethod.confirmed({
        from: attacker
      });
      
      expect(receipt.result.state).toEqual('HALT');
      
      // Verify exploit success
      const balanceAfter = await target.balanceOf(attacker);
      expect(balanceAfter.toNumber()).toBeGreaterThan(balanceBefore.toNumber());
    });
  });
});
```

### NEO•ONE Commands
```bash
npx neo-one init                 # Initialize project
npx neo-one build               # Build contracts
npx neo-one test                # Run tests
npx neo-one start network       # Start local network
```

## Neo3-Boa (Python)

### Debugger Config (launch.json)
```json
{
  "version": "0.2.0",
  "configurations": [{
    "name": "target.nef",
    "type": "neo-contract",
    "request": "launch",
    "program": "${workspaceFolder}/target.nef",
    "operation": "main",
    "args": [],
    "storage": []
  }]
}
```

### Test with Python
```python
from boa3.boa3 import Boa3
from boa3_test.tests.boa_test import BoaTest

class TestTarget(BoaTest):
    def test_exploit(self):
        path = self.get_contract_path('target.py')
        output = Boa3.compile(path)
        
        engine = self.prepare_testengine()
        
        # Deploy
        result = self.run_smart_contract(engine, path, 'deploy')
        
        # Execute exploit
        attacker = self.generate_account()
        result = self.run_smart_contract(
            engine, path, 'vulnerableMethod',
            signer=attacker
        )
        
        self.assertEqual(result, expected_value)
```

### Commands
```bash
neo3-boa compile target.py           # Compile
neo3-boa compile target.py -d        # Compile with debug info
pytest tests/                        # Run Python tests
```
