#!/usr/bin/env python3
"""
Detect smart contract project framework and chain type.
"""

import os
import sys
import json
from pathlib import Path

FRAMEWORK_CONFIGS = {
    "foundry": {
        "files": ["foundry.toml"],
        "chain": "evm",
        "extensions": [".sol"],
        "test_cmd": "forge test",
        "build_cmd": "forge build",
    },
    "hardhat": {
        "files": ["hardhat.config.js", "hardhat.config.ts"],
        "chain": "evm",
        "extensions": [".sol"],
        "test_cmd": "npx hardhat test",
        "build_cmd": "npx hardhat compile",
    },
    "anchor": {
        "files": ["Anchor.toml"],
        "chain": "solana",
        "extensions": [".rs"],
        "test_cmd": "anchor test",
        "build_cmd": "anchor build",
    },
    "neo_csharp": {
        "files": ["*.csproj"],
        "markers": ["Neo.SmartContract"],
        "chain": "neo",
        "extensions": [".cs"],
        "test_cmd": "dotnet test",
        "build_cmd": "dotnet build",
    },
    "neo_python": {
        "files": ["requirements.txt"],
        "markers": ["neo3-boa"],
        "chain": "neo",
        "extensions": [".py"],
        "test_cmd": "pytest",
        "build_cmd": "neo3-boa compile",
    },
    "blueprint": {
        "files": ["blueprint.config.ts"],
        "chain": "ton",
        "extensions": [".fc", ".tact"],
        "test_cmd": "npx blueprint test",
        "build_cmd": "npx blueprint build",
    },
    "tact": {
        "files": ["tact.config.json"],
        "chain": "ton",
        "extensions": [".tact"],
        "test_cmd": "npx blueprint test",
        "build_cmd": "npx tact build",
    },
    "aptos": {
        "files": ["Move.toml"],
        "markers": ["AptosFramework", "aptos_framework"],
        "chain": "move_aptos",
        "extensions": [".move"],
        "test_cmd": "aptos move test",
        "build_cmd": "aptos move compile",
    },
    "sui": {
        "files": ["Move.toml"],
        "markers": ["Sui", "sui_framework"],
        "chain": "move_sui",
        "extensions": [".move"],
        "test_cmd": "sui move test",
        "build_cmd": "sui move build",
    },
    "starknet_foundry": {
        "files": ["Scarb.toml"],
        "chain": "cairo",
        "extensions": [".cairo"],
        "test_cmd": "snforge test",
        "build_cmd": "scarb build",
    },
    "cosmwasm": {
        "files": ["Cargo.toml"],
        "markers": ["cosmwasm-std"],
        "chain": "cosmwasm",
        "extensions": [".rs"],
        "test_cmd": "cargo test",
        "build_cmd": "cargo wasm",
    },
}

CHAIN_INFO = {
    "evm": {
        "name": "EVM (Ethereum/BSC/Polygon/etc)",
        "languages": ["Solidity", "Vyper"],
        "frameworks": ["foundry", "hardhat"],
    },
    "solana": {
        "name": "Solana",
        "languages": ["Rust"],
        "frameworks": ["anchor"],
    },
    "neo": {
        "name": "Neo N3",
        "languages": ["C#", "Python"],
        "frameworks": ["neo_csharp", "neo_python"],
    },
    "ton": {
        "name": "TON",
        "languages": ["FunC", "Tact"],
        "frameworks": ["blueprint", "tact"],
    },
    "move_aptos": {
        "name": "Aptos",
        "languages": ["Move"],
        "frameworks": ["aptos"],
    },
    "move_sui": {
        "name": "Sui",
        "languages": ["Move"],
        "frameworks": ["sui"],
    },
    "cairo": {
        "name": "Starknet",
        "languages": ["Cairo"],
        "frameworks": ["starknet_foundry"],
    },
    "cosmwasm": {
        "name": "CosmWasm",
        "languages": ["Rust"],
        "frameworks": ["cosmwasm"],
    },
}


def find_files(project_path, pattern):
    path = Path(project_path)
    if "*" in pattern:
        return list(path.glob(pattern))
    return [path / pattern] if (path / pattern).exists() else []


def check_file_contains(filepath, markers):
    try:
        content = filepath.read_text()
        return any(marker in content for marker in markers)
    except:
        return False


def detect_framework(project_path):
    path = Path(project_path)
    if not path.exists():
        return {"error": f"Path not found: {project_path}"}
    
    detected = []
    
    for framework, config in FRAMEWORK_CONFIGS.items():
        for file_pattern in config["files"]:
            matches = find_files(project_path, file_pattern)
            if matches:
                if "markers" in config:
                    for match in matches:
                        if check_file_contains(match, config["markers"]):
                            detected.append(framework)
                            break
                else:
                    detected.append(framework)
                break
    
    if not detected:
        extensions = set()
        for f in path.rglob("*"):
            if f.is_file():
                extensions.add(f.suffix.lower())
        
        for framework, config in FRAMEWORK_CONFIGS.items():
            if any(ext in extensions for ext in config["extensions"]):
                detected.append(framework)
    
    if not detected:
        return {
            "detected": False,
            "message": "No framework detected",
            "suggestion": "Check if project has config files (foundry.toml, Anchor.toml, etc.)",
        }
    
    primary = detected[0]
    config = FRAMEWORK_CONFIGS[primary]
    chain = config["chain"]
    chain_info = CHAIN_INFO[chain]
    
    return {
        "detected": True,
        "framework": primary,
        "chain": chain,
        "chain_name": chain_info["name"],
        "languages": chain_info["languages"],
        "test_cmd": config["test_cmd"],
        "build_cmd": config["build_cmd"],
        "extensions": config["extensions"],
        "all_detected": detected,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: project_detector.py <project_path> [--json]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_json = "--json" in sys.argv
    
    result = detect_framework(project_path)
    
    if output_json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("detected"):
            print(f"Framework: {result['framework']}")
            print(f"Chain: {result['chain_name']}")
            print(f"Languages: {', '.join(result['languages'])}")
            print(f"Test command: {result['test_cmd']}")
            print(f"Build command: {result['build_cmd']}")
            if len(result.get("all_detected", [])) > 1:
                print(f"Also detected: {', '.join(result['all_detected'][1:])}")
        else:
            print(result.get("message", "Detection failed"))
            if result.get("suggestion"):
                print(f"Suggestion: {result['suggestion']}")


if __name__ == "__main__":
    main()
