import asyncio
import os
import sys

# Ensure we can import from local directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tool import RAGIngestTool, RAGQATool

async def main():
    print("🚀 Auto-Auditor Demo Starting...")
    
    # 1. Ingest a sample (using a mock or real simple repo if internet available)
    # We will use a dummy local file for this smoke test to ensure no network dependency failure in CI
    os.makedirs("temp_audit_target", exist_ok=True)
    with open("temp_audit_target/Token.sol", "w") as f:
        f.write("""
        contract Token {
            mapping(address => uint) public balances;
            
            // INTENTIONAL VULNERABILITY: No check for overflow (if older solidity) or arbitrary minting
            function mint(address to, uint amount) public {
                balances[to] += amount;
            }
        }
        """)
        
    print("\n📦 Ingesting 'temp_audit_target'...")
    ingest = RAGIngestTool()
    res = await ingest.execute(inputs=[os.path.abspath("temp_audit_target")])
    print(f"Result: {res.output}")
    
    # 2. Audit Question
    print("\n🕵️‍♂️ Auditing: 'Identify potential risks in the mint function.'")
    qa = RAGQATool()
    
    # Note: This requires an LLM to be configured. 
    # If no LLM is present, RAGQATool might fallback or error depending on config.
    # For this demo, we assume the user has set OPENAI_API_KEY or similar.
    try:
        res = await qa.execute(question="Identify potential risks in the mint function.")
        print("\n📝 Audit Report:")
        print(res.output)
        if res.system:
            print(f"\nCorrection Data: {res.system}")
    except Exception as e:
        print(f"\n⚠️ QA Execution skipped (LLM likely missing): {e}")

if __name__ == "__main__":
    asyncio.run(main())
