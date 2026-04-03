---
name: Web3 Smart Contract Auditor
description: A specialized RAG agent for auditing Smart Contracts and Web3 documentation with line-level citation precision.
author: SpoonUser
tags: [web3-data-intelligence, security, web3-core-operations]
---

# Web3 Smart Contract Auditor

The **Web3 Smart Contract Auditor** is an advanced RAG (Retrieval-Augmented Generation) Skill designed to help developers and auditors quickly understand, verify, and audit complex blockchain codebases and whitepapers.

Unlike generic RAG tools, this skill is optimized for:
1.  **Smart Contract Code**: Native parsing of `.sol`, `.rs`, `.go` and `GitHub` repositories.
2.  **Precise Citations**: Every answer includes strict `[file_name_line]` citations to prevent hallucinations.
3.  **Security Filtering**: Automatically ignores `.env`, private keys, and build artifacts during ingestion.

## 🚀 Features

- **GitHub & Local Ingestion**: One-click ingestion of any public contract repo.
- **Deep Search**: Hybrid search (Vector + Keyword) to find exact function definitions.
- **Audit-Ready QA**: tailored prompts for finding vulnerabilities (Reentrancy, Overflow, Permission checks).

## 📦 Requirements

- Python 3.9+
- OpenAI API Key (or other supported LLM)
- Jina AI API Key (Optional, for web parsing)

## 🛠️ Usage

### 1. Ingest a Repository
Load the target protocol's code into the vector index.
```python
await agents.execute_tool("rag_ingest", inputs=["https://github.com/OpenZeppelin/openzeppelin-contracts/tree/master/contracts/token/ERC20"])
```

### 2. Perform Audit / QA
Ask specific security or logic questions.
```python
result = await agents.execute_tool("rag_qa", question="Does the _transfer function check for zero address?")
print(result)
```
**Output Example:**
> Yes, the `_transfer` function checks for zero addresses at the beginning of the execution.
> Source: `[ERC20.sol_245]` `if (to == address(0)) revert ERC20InvalidReceiver(address(0));`

## 🔧 Configuration

The skill uses standard standard SpoonOS RAG configuration. You can customize:
- `chunk_size`: 800 (default, optimized for code)
- `chunk_overlap`: 120

## 🛡️ Security Note

This skill runs locally or within your secure SpoonOS environment. It does not upload your private code to any third-party training service (other than the configured LLM provider for inference).
