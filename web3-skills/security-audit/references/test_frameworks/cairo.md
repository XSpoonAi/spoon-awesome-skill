# Cairo Testing (Starknet)

## Starknet Foundry

### Commands
```bash
snforge init                         # Initialize project
snforge test                         # Run all tests
snforge test -e test_name            # Run specific test
snforge test --exact                 # Exact match filter
sncast declare                       # Declare contract
sncast deploy                        # Deploy contract
sncast invoke                        # Invoke function
sncast call                          # Call function (view)
scarb build                          # Build contracts
```

### Test Template
```cairo
use snforge_std::{
    declare, ContractClassTrait, DeclareResultTrait,
    start_cheat_caller_address, stop_cheat_caller_address,
    spy_events, EventSpy, EventSpyTrait, EventSpyAssertionsTrait
};
use starknet::ContractAddress;

#[starknet::interface]
trait ITarget<TContractState> {
    fn vulnerable_function(ref self: TContractState, amount: u256);
    fn get_balance(self: @TContractState, account: ContractAddress) -> u256;
}

fn deploy_target() -> ContractAddress {
    let contract = declare("Target").unwrap().contract_class();
    let (contract_address, _) = contract.deploy(@array![]).unwrap();
    contract_address
}

#[test]
fn test_exploit() {
    let target_address = deploy_target();
    let target = ITargetDispatcher { contract_address: target_address };
    
    let attacker: ContractAddress = 0x123.try_into().unwrap();
    let victim: ContractAddress = 0x456.try_into().unwrap();
    
    // Setup: victim deposits
    start_cheat_caller_address(target_address, victim);
    target.deposit(1000);
    stop_cheat_caller_address(target_address);
    
    // Attack
    start_cheat_caller_address(target_address, attacker);
    let balance_before = target.get_balance(attacker);
    target.vulnerable_function(1000);
    let balance_after = target.get_balance(attacker);
    stop_cheat_caller_address(target_address);
    
    assert(balance_after > balance_before, 'Exploit failed');
}

#[test]
#[should_panic(expected: ('Unauthorized',))]
fn test_access_control() {
    let target_address = deploy_target();
    let target = ITargetDispatcher { contract_address: target_address };
    
    let attacker: ContractAddress = 0x123.try_into().unwrap();
    start_cheat_caller_address(target_address, attacker);
    target.admin_function(); // Should panic
}
```

### Cheatcodes
```cairo
use snforge_std::{
    start_cheat_caller_address,
    stop_cheat_caller_address,
    start_cheat_block_timestamp,
    stop_cheat_block_timestamp,
    start_cheat_block_number,
    stop_cheat_block_number,
    start_cheat_sequencer_address,
    start_cheat_caller_address_global,
};

// Caller spoofing
start_cheat_caller_address(contract_address, spoofed_caller);
// ... calls here use spoofed_caller
stop_cheat_caller_address(contract_address);

// Time manipulation
start_cheat_block_timestamp(contract_address, 1000000);
// ... calls here see timestamp = 1000000
stop_cheat_block_timestamp(contract_address);

// Block number manipulation
start_cheat_block_number(contract_address, 12345);

// Global cheat (affects all contracts)
start_cheat_caller_address_global(spoofed_caller);
```

### Event Testing
```cairo
use snforge_std::{spy_events, EventSpy, EventSpyTrait, EventSpyAssertionsTrait};

#[test]
fn test_events() {
    let target_address = deploy_target();
    let target = ITargetDispatcher { contract_address: target_address };
    
    let mut spy = spy_events();
    
    target.do_something();
    
    spy.assert_emitted(@array![
        (
            target_address,
            Target::Event::SomethingDone(Target::SomethingDone { value: 42 })
        )
    ]);
}
```

### Fork Testing
```cairo
#[fork(url: "https://starknet-mainnet.g.alchemy.com/v2/xxx", block_id: BlockId::Number(123456))]
#[test]
fn test_on_fork() {
    let eth_address: ContractAddress = 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7.try_into().unwrap();
    let eth = IERC20Dispatcher { contract_address: eth_address };
    
    let whale: ContractAddress = 0x123.try_into().unwrap();
    let balance = eth.balance_of(whale);
    assert(balance > 0, 'Whale should have balance');
}
```

## Protostar (Legacy)

### Commands (deprecated, use Starknet Foundry)
```bash
protostar init                       # Initialize
protostar build                      # Build
protostar test                       # Test
protostar deploy                     # Deploy
```

## Common Exploit Patterns

### Reentrancy (Cairo)
```cairo
// Vulnerable
#[external(v0)]
fn withdraw(ref self: ContractState, amount: u256) {
    let caller = get_caller_address();
    let balance = self.balances.read(caller);
    assert(balance >= amount, 'Insufficient');
    
    // External call before state update (vulnerable)
    IERC20Dispatcher { contract_address: self.token.read() }
        .transfer(caller, amount);
    
    self.balances.write(caller, balance - amount);
}

// Fixed - Checks-Effects-Interactions
#[external(v0)]
fn withdraw(ref self: ContractState, amount: u256) {
    let caller = get_caller_address();
    let balance = self.balances.read(caller);
    assert(balance >= amount, 'Insufficient');
    
    // State update first
    self.balances.write(caller, balance - amount);
    
    // External call last
    IERC20Dispatcher { contract_address: self.token.read() }
        .transfer(caller, amount);
}
```

### Access Control
```cairo
// Vulnerable
#[external(v0)]
fn set_admin(ref self: ContractState, new_admin: ContractAddress) {
    // No check
    self.admin.write(new_admin);
}

// Fixed
#[external(v0)]
fn set_admin(ref self: ContractState, new_admin: ContractAddress) {
    assert(get_caller_address() == self.admin.read(), 'Unauthorized');
    self.admin.write(new_admin);
}
```
