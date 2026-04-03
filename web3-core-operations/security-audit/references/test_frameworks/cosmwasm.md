# CosmWasm Testing

## Commands
```bash
cargo generate --git https://github.com/CosmWasm/cw-template.git  # Create project
cargo build                          # Build
cargo wasm                           # Build optimized WASM
cargo test                           # Run tests
cargo schema                         # Generate JSON schema
```

## cw-multi-test

### Test Template
```rust
use cosmwasm_std::{Addr, Coin, Empty, Uint128};
use cw_multi_test::{App, ContractWrapper, Executor};
use crate::contract::{execute, instantiate, query};
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};

fn mock_app() -> App {
    App::default()
}

fn store_code(app: &mut App) -> u64 {
    let contract = ContractWrapper::new(execute, instantiate, query);
    app.store_code(Box::new(contract))
}

#[test]
fn test_exploit() {
    let mut app = mock_app();
    let code_id = store_code(&mut app);
    
    let owner = Addr::unchecked("owner");
    let attacker = Addr::unchecked("attacker");
    let victim = Addr::unchecked("victim");
    
    // Fund accounts
    app.init_modules(|router, _, storage| {
        router.bank.init_balance(
            storage,
            &victim,
            vec![Coin::new(10000, "uatom")]
        ).unwrap();
    });
    
    // Instantiate contract
    let contract_addr = app
        .instantiate_contract(
            code_id,
            owner.clone(),
            &InstantiateMsg { admin: owner.clone() },
            &[],
            "target",
            None,
        )
        .unwrap();
    
    // Victim deposits
    app.execute_contract(
        victim.clone(),
        contract_addr.clone(),
        &ExecuteMsg::Deposit {},
        &[Coin::new(10000, "uatom")],
    ).unwrap();
    
    // Attacker exploits
    let attacker_balance_before = app.wrap().query_balance(&attacker, "uatom").unwrap();
    
    app.execute_contract(
        attacker.clone(),
        contract_addr.clone(),
        &ExecuteMsg::VulnerableWithdraw { amount: Uint128::new(10000) },
        &[],
    ).unwrap();
    
    let attacker_balance_after = app.wrap().query_balance(&attacker, "uatom").unwrap();
    
    assert!(attacker_balance_after.amount > attacker_balance_before.amount);
}
```

### Mock Dependencies
```rust
use cosmwasm_std::testing::{mock_dependencies, mock_env, mock_info};

#[test]
fn test_with_mock_deps() {
    let mut deps = mock_dependencies();
    let env = mock_env();
    let info = mock_info("sender", &[Coin::new(1000, "uatom")]);
    
    // Instantiate
    let msg = InstantiateMsg { admin: "admin".to_string() };
    let res = instantiate(deps.as_mut(), env.clone(), info.clone(), msg).unwrap();
    assert_eq!(0, res.messages.len());
    
    // Execute
    let msg = ExecuteMsg::DoSomething {};
    let res = execute(deps.as_mut(), env.clone(), info, msg).unwrap();
    
    // Query
    let res = query(deps.as_ref(), env, QueryMsg::GetState {}).unwrap();
}
```

### Time Manipulation
```rust
use cosmwasm_std::testing::mock_env;
use cosmwasm_std::Timestamp;

#[test]
fn test_time_dependent() {
    let mut env = mock_env();
    
    // Set specific time
    env.block.time = Timestamp::from_seconds(1000000);
    env.block.height = 12345;
    
    // Execute with this time
    let res = execute(deps.as_mut(), env, info, msg);
}
```

### Custom Modules
```rust
use cw_multi_test::{App, AppBuilder, Module, BankKeeper};

fn custom_app() -> App {
    AppBuilder::new()
        .with_bank(BankKeeper::new())
        .build(|router, api, storage| {
            // Custom initialization
        })
}

// With staking module
use cw_multi_test::StakingInfo;

fn app_with_staking() -> App {
    AppBuilder::new()
        .with_staking(StakingInfo {
            bonded_denom: "uatom".to_string(),
            unbonding_time: 1814400, // 21 days
            apr: Decimal::percent(10),
        })
        .build(|_, _, _| {})
}
```

## Common Exploit Patterns

### Reentrancy
```rust
// Vulnerable
pub fn execute_withdraw(
    deps: DepsMut,
    env: Env,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let balance = BALANCES.load(deps.storage, &info.sender)?;
    
    // External call first (vulnerable)
    let msg = BankMsg::Send {
        to_address: info.sender.to_string(),
        amount: vec![Coin::new(amount.u128(), "uatom")],
    };
    
    // State update after
    BALANCES.save(deps.storage, &info.sender, &(balance - amount))?;
    
    Ok(Response::new().add_message(msg))
}

// Fixed - state update first
pub fn execute_withdraw(
    deps: DepsMut,
    env: Env,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let balance = BALANCES.load(deps.storage, &info.sender)?;
    
    // State update first
    BALANCES.save(deps.storage, &info.sender, &(balance - amount))?;
    
    // External call last
    let msg = BankMsg::Send {
        to_address: info.sender.to_string(),
        amount: vec![Coin::new(amount.u128(), "uatom")],
    };
    
    Ok(Response::new().add_message(msg))
}
```

### Missing Admin Check
```rust
// Vulnerable
pub fn execute_set_config(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,  // Not checked
    new_config: Config,
) -> Result<Response, ContractError> {
    CONFIG.save(deps.storage, &new_config)?;
    Ok(Response::new())
}

// Fixed
pub fn execute_set_config(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    new_config: Config,
) -> Result<Response, ContractError> {
    let config = CONFIG.load(deps.storage)?;
    if info.sender != config.admin {
        return Err(ContractError::Unauthorized {});
    }
    CONFIG.save(deps.storage, &new_config)?;
    Ok(Response::new())
}
```
