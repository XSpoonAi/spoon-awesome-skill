# Anchor (Solana)

## Commands
```bash
anchor init <project>        # Initialize project
anchor build                 # Build program
anchor test                  # Run tests
anchor deploy                # Deploy to cluster
anchor localnet              # Start local validator
solana-test-validator        # Alternative local validator
anchor idl init              # Initialize IDL
anchor verify <program_id>   # Verify deployed program
```

## Test Template (TypeScript)
```typescript
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { Target } from "../target/types/target";
import { expect } from "chai";

describe("exploit-test", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.Target as Program<Target>;
  
  let attacker: anchor.web3.Keypair;
  let victim: anchor.web3.Keypair;
  let targetPda: anchor.web3.PublicKey;

  before(async () => {
    attacker = anchor.web3.Keypair.generate();
    victim = anchor.web3.Keypair.generate();
    
    // Airdrop SOL
    await provider.connection.requestAirdrop(
      attacker.publicKey,
      10 * anchor.web3.LAMPORTS_PER_SOL
    );
    
    // Derive PDA
    [targetPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("target"), attacker.publicKey.toBuffer()],
      program.programId
    );
  });

  it("demonstrates exploit", async () => {
    const balanceBefore = await provider.connection.getBalance(attacker.publicKey);
    
    await program.methods
      .vulnerableInstruction()
      .accounts({
        attacker: attacker.publicKey,
        target: targetPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([attacker])
      .rpc();
    
    const balanceAfter = await provider.connection.getBalance(attacker.publicKey);
    expect(balanceAfter).to.be.gt(balanceBefore);
  });
});
```

## Program Template (Rust)
```rust
use anchor_lang::prelude::*;

declare_id!("YOUR_PROGRAM_ID");

#[program]
pub mod target {
    use super::*;

    pub fn vulnerable_instruction(ctx: Context<VulnerableContext>) -> Result<()> {
        // Vulnerable logic here
        Ok(())
    }
}

#[derive(Accounts)]
pub struct VulnerableContext<'info> {
    #[account(mut)]
    pub attacker: Signer<'info>,
    
    #[account(
        mut,
        seeds = [b"target", attacker.key().as_ref()],
        bump
    )]
    pub target: Account<'info, TargetState>,
    
    pub system_program: Program<'info, System>,
}

#[account]
pub struct TargetState {
    pub owner: Pubkey,
    pub balance: u64,
}
```

## Common Exploit Patterns

### Missing Signer Check
```rust
// Vulnerable
#[derive(Accounts)]
pub struct Withdraw<'info> {
    pub authority: AccountInfo<'info>,  // Missing Signer constraint
    #[account(mut)]
    pub vault: Account<'info, Vault>,
}

// Fixed
#[derive(Accounts)]
pub struct Withdraw<'info> {
    pub authority: Signer<'info>,  // Now requires signature
    #[account(mut, has_one = authority)]
    pub vault: Account<'info, Vault>,
}
```

### Missing Owner Check
```rust
// Vulnerable
#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,  // Any token account
}

// Fixed
#[derive(Accounts)]
pub struct Transfer<'info> {
    #[account(mut, constraint = from.owner == authority.key())]
    pub from: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
}
```

## Bankrun Testing (Alternative)
```typescript
import { start } from "solana-bankrun";
import { Program } from "@coral-xyz/anchor";

describe("bankrun tests", () => {
  it("fast test with bankrun", async () => {
    const context = await start([], []);
    const client = context.banksClient;
    
    // Fast transaction simulation
    const tx = new Transaction().add(instruction);
    await client.processTransaction(tx);
  });
});
```
