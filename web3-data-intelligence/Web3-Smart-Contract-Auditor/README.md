# Web3 Smart Contract Auditor Skill 🕵️‍♂️🛡️

This SpoonOS Skill empowers your AI agents to perform deep, evidence-based security audits on Smart Contracts and Web3 documentation.

## Overview

Built on top of the Spoon AI RAG engine, this skill provides specialized ingestion and retrieval capabilities for blockchain developers.

### Why use this?
- **Auditors**: Quickly find potential vulnerabilities across large codebases.
- **Developers**: Onboard to new protocols by "chatting" with the code.
- **Investors**: Verify Whitepaper claims against actual code implementation.

## Quick Start

1. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Example**
   See `example_audit.py` for a full demonstration.

## Tools

| Tool Name | Description |
|-----------|-------------|
| `rag_ingest` | Load GitHub repos (e.g., `https://github.com/compound-finance/compound-protocol`) or local folders. |
| `rag_qa` | Ask questions with precise `[file_line]` citations. |
| `rag_search` | Search for raw code snippets using semantic + keyword search. |

## License

MIT
