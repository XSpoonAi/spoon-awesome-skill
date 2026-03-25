# Move Testing (Aptos & Sui)

## Aptos CLI

### Commands
```bash
aptos init                           # Initialize project
aptos move compile                   # Compile modules
aptos move test                      # Run tests
aptos move test --filter test_name   # Run specific test
aptos move prove                     # Run Move Prover
aptos move publish                   # Publish to network
aptos move run                       # Execute entry function
aptos account fund-with-faucet       # Get testnet tokens
```

### Test Template (Aptos)
```move
#[test_only]
module exploit::exploit_tests {
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::aptos_coin::AptosCoin;
    use target::vulnerable_module;

    #[test(attacker = @0x123, victim = @0x456, framework = @aptos_framework)]
    public fun test_exploit(
        attacker: &signer,
        victim: &signer,
        framework: &signer
    ) {
        // Setup
        let attacker_addr = signer::address_of(attacker);
        let victim_addr = signer::address_of(victim);
        
        // Fund accounts
        coin::register<AptosCoin>(attacker);
        coin::register<AptosCoin>(victim);
        aptos_coin::mint(framework, attacker_addr, 1000);
        aptos_coin::mint(framework, victim_addr, 10000);
        
        // Execute exploit
        let balance_before = coin::balance<AptosCoin>(attacker_addr);
        vulnerable_module::vulnerable_function(attacker);
        let balance_after = coin::balance<AptosCoin>(attacker_addr);
        
        // Assert
        assert!(balance_after > balance_before, 0);
    }

    #[test]
    #[expected_failure(abort_code = 1)]
    public fun test_should_fail() {
        vulnerable_module::should_abort();
    }
}
```

### Move Prover Specification
```move
module target::vulnerable_module {
    spec withdraw {
        aborts_if !exists<Balance>(signer::address_of(account));
        ensures global<Balance>(addr).value == old(global<Balance>(addr).value) - amount;
    }
}
```

## Sui CLI

### Commands
```bash
sui move new <project>              # Create project
sui move build                      # Build package
sui move test                       # Run tests
sui move test --filter name         # Run specific test
sui client publish                  # Publish package
sui client call                     # Call function
sui client faucet                   # Get testnet tokens
```

### Test Template (Sui)
```move
#[test_only]
module exploit::exploit_tests {
    use sui::test_scenario::{Self as ts, Scenario};
    use sui::coin::{Self, Coin};
    use sui::sui::SUI;
    use target::vulnerable_module::{Self, Target};

    const ATTACKER: address = @0x1;
    const VICTIM: address = @0x2;

    #[test]
    fun test_exploit() {
        let mut scenario = ts::begin(ATTACKER);
        
        // Deploy contract
        {
            vulnerable_module::init_for_testing(ts::ctx(&mut scenario));
        };
        
        // Setup victim
        ts::next_tx(&mut scenario, VICTIM);
        {
            let mut target = ts::take_shared<Target>(&scenario);
            let coin = coin::mint_for_testing<SUI>(10000, ts::ctx(&mut scenario));
            vulnerable_module::deposit(&mut target, coin);
            ts::return_shared(target);
        };
        
        // Execute exploit
        ts::next_tx(&mut scenario, ATTACKER);
        {
            let mut target = ts::take_shared<Target>(&scenario);
            let stolen = vulnerable_module::vulnerable_withdraw(
                &mut target,
                ts::ctx(&mut scenario)
            );
            assert!(coin::value(&stolen) > 0, 0);
            transfer::public_transfer(stolen, ATTACKER);
            ts::return_shared(target);
        };
        
        ts::end(scenario);
    }

    #[test]
    #[expected_failure(abort_code = vulnerable_module::E_NOT_OWNER)]
    fun test_access_control() {
        let mut scenario = ts::begin(ATTACKER);
        // Test should abort
        ts::end(scenario);
    }
}
```

### Test Utilities (Sui)
```move
use sui::test_scenario::{Self as ts};
use sui::test_utils;

// Create test scenario
let mut scenario = ts::begin(ADMIN);

// Advance to next transaction
ts::next_tx(&mut scenario, USER);

// Take objects
let obj = ts::take_from_sender<Object>(&scenario);
let shared = ts::take_shared<SharedObject>(&scenario);

// Return objects
ts::return_to_sender(&scenario, obj);
ts::return_shared(shared);

// Check effects
let effects = ts::next_tx(&mut scenario, USER);
assert!(ts::num_user_events(&effects) == 1, 0);

// End scenario
ts::end(scenario);
```

## Common Exploit Patterns

### Missing Capability Check (Aptos)
```move
// Vulnerable
public fun admin_withdraw(account: &signer, amount: u64) {
    // No capability check
    let coins = coin::withdraw<AptosCoin>(account, amount);
    coin::deposit(@treasury, coins);
}

// Fixed
public fun admin_withdraw(account: &signer, amount: u64) acquires AdminCap {
    let cap = borrow_global<AdminCap>(signer::address_of(account));
    // Now requires AdminCap
}
```

### Object Ownership Bypass (Sui)
```move
// Vulnerable
public fun withdraw(target: &mut Target, ctx: &mut TxContext) {
    // No owner check
    let coin = coin::take(&mut target.balance, amount, ctx);
    transfer::public_transfer(coin, tx_context::sender(ctx));
}

// Fixed
public fun withdraw(target: &mut Target, cap: &OwnerCap, ctx: &mut TxContext) {
    assert!(object::id(target) == cap.target_id, E_NOT_OWNER);
    // ...
}
```
