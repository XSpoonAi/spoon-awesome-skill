#!/usr/bin/env python3
"""
Fetch verified smart contract source code from blockchain explorers.
Supports 40+ chains including EVM, Solana, TON, Near, Aptos, Sui, etc.
"""

import os
import sys
import json
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

EXPLORERS = {
    "ethereum": {
        "api": "https://api.etherscan.io/api",
        "env_key": "ETHERSCAN_API_KEY",
        "type": "etherscan",
    },
    "goerli": {
        "api": "https://api-goerli.etherscan.io/api",
        "env_key": "ETHERSCAN_API_KEY",
        "type": "etherscan",
    },
    "sepolia": {
        "api": "https://api-sepolia.etherscan.io/api",
        "env_key": "ETHERSCAN_API_KEY",
        "type": "etherscan",
    },
    "bsc": {
        "api": "https://api.bscscan.com/api",
        "env_key": "BSCSCAN_API_KEY",
        "type": "etherscan",
    },
    "bsc_testnet": {
        "api": "https://api-testnet.bscscan.com/api",
        "env_key": "BSCSCAN_API_KEY",
        "type": "etherscan",
    },
    "polygon": {
        "api": "https://api.polygonscan.com/api",
        "env_key": "POLYGONSCAN_API_KEY",
        "type": "etherscan",
    },
    "polygon_zkevm": {
        "api": "https://api-zkevm.polygonscan.com/api",
        "env_key": "POLYGONSCAN_API_KEY",
        "type": "etherscan",
    },
    "arbitrum": {
        "api": "https://api.arbiscan.io/api",
        "env_key": "ARBISCAN_API_KEY",
        "type": "etherscan",
    },
    "arbitrum_nova": {
        "api": "https://api-nova.arbiscan.io/api",
        "env_key": "ARBISCAN_API_KEY",
        "type": "etherscan",
    },
    "optimism": {
        "api": "https://api-optimistic.etherscan.io/api",
        "env_key": "OPTIMISM_API_KEY",
        "type": "etherscan",
    },
    "avalanche": {
        "api": "https://api.snowtrace.io/api",
        "env_key": "SNOWTRACE_API_KEY",
        "type": "etherscan",
    },
    "fantom": {
        "api": "https://api.ftmscan.com/api",
        "env_key": "FTMSCAN_API_KEY",
        "type": "etherscan",
    },
    "base": {
        "api": "https://api.basescan.org/api",
        "env_key": "BASESCAN_API_KEY",
        "type": "etherscan",
    },
    "linea": {
        "api": "https://api.lineascan.build/api",
        "env_key": "LINEASCAN_API_KEY",
        "type": "etherscan",
    },
    "zksync": {
        "api": "https://block-explorer-api.mainnet.zksync.io/api",
        "env_key": "ZKSYNC_API_KEY",
        "type": "etherscan",
    },
    "scroll": {
        "api": "https://api.scrollscan.com/api",
        "env_key": "SCROLLSCAN_API_KEY",
        "type": "etherscan",
    },
    "mantle": {
        "api": "https://api.mantlescan.xyz/api",
        "env_key": "MANTLESCAN_API_KEY",
        "type": "etherscan",
    },
    "blast": {
        "api": "https://api.blastscan.io/api",
        "env_key": "BLASTSCAN_API_KEY",
        "type": "etherscan",
    },
    "celo": {
        "api": "https://api.celoscan.io/api",
        "env_key": "CELOSCAN_API_KEY",
        "type": "etherscan",
    },
    "gnosis": {
        "api": "https://api.gnosisscan.io/api",
        "env_key": "GNOSISSCAN_API_KEY",
        "type": "etherscan",
    },
    "moonbeam": {
        "api": "https://api-moonbeam.moonscan.io/api",
        "env_key": "MOONSCAN_API_KEY",
        "type": "etherscan",
    },
    "moonriver": {
        "api": "https://api-moonriver.moonscan.io/api",
        "env_key": "MOONSCAN_API_KEY",
        "type": "etherscan",
    },
    "cronos": {
        "api": "https://api.cronoscan.com/api",
        "env_key": "CRONOSCAN_API_KEY",
        "type": "etherscan",
    },
    "aurora": {
        "api": "https://api.aurorascan.dev/api",
        "env_key": "AURORASCAN_API_KEY",
        "type": "etherscan",
    },
    "metis": {
        "api": "https://api.andromeda-explorer.metis.io/api",
        "env_key": "METIS_API_KEY",
        "type": "etherscan",
    },
    "boba": {
        "api": "https://api.bobascan.com/api",
        "env_key": "BOBASCAN_API_KEY",
        "type": "etherscan",
    },
    "kava": {
        "api": "https://kavascan.com/api",
        "env_key": "KAVASCAN_API_KEY",
        "type": "etherscan",
    },
    "mode": {
        "api": "https://api.modescan.io/api",
        "env_key": "MODESCAN_API_KEY",
        "type": "etherscan",
    },
    "taiko": {
        "api": "https://api.taikoscan.io/api",
        "env_key": "TAIKOSCAN_API_KEY",
        "type": "etherscan",
    },
    "solana": {
        "api": "https://api.solscan.io",
        "env_key": "SOLSCAN_API_KEY",
        "type": "solana",
    },
    "ton": {
        "api": "https://tonapi.io/v2",
        "env_key": "TONAPI_KEY",
        "type": "ton",
    },
    "near": {
        "api": "https://api.nearblocks.io/v1",
        "env_key": "NEARBLOCKS_API_KEY",
        "type": "near",
    },
    "aptos": {
        "api": "https://api.aptoscan.com/api",
        "env_key": "APTOSCAN_API_KEY",
        "type": "aptos",
    },
    "sui": {
        "api": "https://suiscan.xyz/api",
        "env_key": "SUISCAN_API_KEY",
        "type": "sui",
    },
    "starknet": {
        "api": "https://api.starkscan.co/api",
        "env_key": "STARKSCAN_API_KEY",
        "type": "starknet",
    },
    "tron": {
        "api": "https://apilist.tronscanapi.com/api",
        "env_key": "TRONSCAN_API_KEY",
        "type": "tron",
    },
    "neo": {
        "api": "https://neotube.io/api",
        "env_key": "NEOTUBE_API_KEY",
        "type": "neo",
    },
}

URL_PATTERNS = {
    r"etherscan\.io": "ethereum",
    r"goerli\.etherscan\.io": "goerli",
    r"sepolia\.etherscan\.io": "sepolia",
    r"bscscan\.com": "bsc",
    r"testnet\.bscscan\.com": "bsc_testnet",
    r"polygonscan\.com": "polygon",
    r"zkevm\.polygonscan\.com": "polygon_zkevm",
    r"arbiscan\.io": "arbitrum",
    r"nova\.arbiscan\.io": "arbitrum_nova",
    r"optimistic\.etherscan\.io": "optimism",
    r"snowtrace\.io": "avalanche",
    r"ftmscan\.com": "fantom",
    r"basescan\.org": "base",
    r"lineascan\.build": "linea",
    r"explorer\.zksync\.io": "zksync",
    r"scrollscan\.com": "scroll",
    r"mantlescan\.xyz": "mantle",
    r"blastscan\.io": "blast",
    r"celoscan\.io": "celo",
    r"gnosisscan\.io": "gnosis",
    r"moonscan\.io": "moonbeam",
    r"moonriver\.moonscan\.io": "moonriver",
    r"cronoscan\.com": "cronos",
    r"aurorascan\.dev": "aurora",
    r"andromeda-explorer\.metis\.io": "metis",
    r"bobascan\.com": "boba",
    r"kavascan\.com": "kava",
    r"modescan\.io": "mode",
    r"taikoscan\.io": "taiko",
    r"solscan\.io": "solana",
    r"solana\.fm": "solana",
    r"explorer\.solana\.com": "solana",
    r"tonapi\.io": "ton",
    r"tonscan\.org": "ton",
    r"ton\.cx": "ton",
    r"nearblocks\.io": "near",
    r"explorer\.near\.org": "near",
    r"aptoscan\.com": "aptos",
    r"explorer\.aptoslabs\.com": "aptos",
    r"suiscan\.xyz": "sui",
    r"suivision\.xyz": "sui",
    r"starkscan\.co": "starknet",
    r"voyager\.online": "starknet",
    r"tronscan\.org": "tron",
    r"neotube\.io": "neo",
    r"explorer\.neo\.org": "neo",
}


def detect_chain_from_url(url):
    for pattern, chain in URL_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return chain
    return None


def extract_address_from_url(url):
    evm_match = re.search(r"0x[a-fA-F0-9]{40}", url)
    if evm_match:
        return evm_match.group(0)
    
    solana_match = re.search(r"[1-9A-HJ-NP-Za-km-z]{32,44}", url)
    if solana_match:
        return solana_match.group(0)
    
    ton_match = re.search(r"(EQ|UQ)[A-Za-z0-9_-]{46}", url)
    if ton_match:
        return ton_match.group(0)
    
    near_match = re.search(r"[a-z0-9_-]+\.near", url)
    if near_match:
        return near_match.group(0)
    
    return None


def get_api_key(chain):
    explorer = EXPLORERS.get(chain)
    if not explorer:
        return None
    return os.environ.get(explorer["env_key"])


def fetch_etherscan_source(chain, address):
    explorer = EXPLORERS.get(chain)
    if not explorer:
        return {"error": f"Unsupported chain: {chain}"}
    
    api_key = get_api_key(chain) or ""
    
    url = (
        f"{explorer['api']}?module=contract&action=getsourcecode"
        f"&address={address}&apikey={api_key}"
    )
    
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as e:
        return {"error": str(e)}
    
    if data.get("status") != "1":
        return {"error": data.get("message", "Unknown error")}
    
    result = data.get("result", [{}])[0]
    if not result.get("SourceCode"):
        return {"error": "Contract source not verified"}
    
    return result


def fetch_solana_source(address):
    url = f"https://api.solscan.io/account?address={address}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {
            "ContractName": data.get("data", {}).get("programId", address),
            "SourceCode": f"# Solana Program: {address}\n# Use: anchor idl fetch {address}",
            "note": "Solana programs require 'anchor idl fetch' or check GitHub for source",
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_ton_source(address):
    api_key = get_api_key("ton") or ""
    headers = {"User-Agent": "Mozilla/5.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    url = f"https://tonapi.io/v2/blockchain/accounts/{address}"
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        code_hash = data.get("code_hash", "")
        return {
            "ContractName": address[:20],
            "SourceCode": f"# TON Contract: {address}\n# Code Hash: {code_hash}\n# Use 'toncli' or check GitHub for source",
            "code_hash": code_hash,
            "note": "TON contracts need decompilation or GitHub source",
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_starknet_source(address):
    url = f"https://api.starkscan.co/api/v0/class/{address}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {
            "ContractName": data.get("name", address[:20]),
            "SourceCode": json.dumps(data.get("abi", []), indent=2),
            "note": "Cairo source may need decompilation",
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_contract_source(chain, address):
    explorer = EXPLORERS.get(chain)
    if not explorer:
        return {"error": f"Unsupported chain: {chain}"}
    
    explorer_type = explorer.get("type", "etherscan")
    
    if explorer_type == "etherscan":
        return fetch_etherscan_source(chain, address)
    elif explorer_type == "solana":
        return fetch_solana_source(address)
    elif explorer_type == "ton":
        return fetch_ton_source(address)
    elif explorer_type == "starknet":
        return fetch_starknet_source(address)
    else:
        return {
            "ContractName": address[:20],
            "SourceCode": f"# {chain.upper()} Contract: {address}\n# Manual source retrieval required",
            "note": f"Auto-fetch not fully supported for {chain}. Check explorer manually.",
        }


def save_contract(result, output_dir, chain):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    contract_name = result.get("ContractName", "Contract")
    source_code = result.get("SourceCode", "")
    
    if source_code.startswith("{{"):
        source_code = source_code[1:-1]
        try:
            sources = json.loads(source_code)
            if "sources" in sources:
                sources = sources["sources"]
            
            for filename, content in sources.items():
                file_path = output_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                code = content.get("content", content) if isinstance(content, dict) else content
                file_path.write_text(code)
                print(f"Saved: {file_path}")
        except json.JSONDecodeError:
            ext = ".sol" if chain in ["ethereum", "bsc", "polygon", "arbitrum"] else ".txt"
            main_file = output_path / f"{contract_name}{ext}"
            main_file.write_text(source_code)
            print(f"Saved: {main_file}")
    else:
        ext = ".sol"
        if chain == "starknet":
            ext = ".cairo"
        elif chain in ["solana"]:
            ext = ".rs"
        elif chain == "ton":
            ext = ".fc"
        elif chain in ["aptos", "sui"]:
            ext = ".move"
        elif chain == "near":
            ext = ".rs"
        
        main_file = output_path / f"{contract_name}{ext}"
        main_file.write_text(source_code)
        print(f"Saved: {main_file}")
    
    metadata = {
        "chain": chain,
        "ContractName": result.get("ContractName"),
        "CompilerVersion": result.get("CompilerVersion"),
        "OptimizationUsed": result.get("OptimizationUsed"),
        "Proxy": result.get("Proxy"),
        "Implementation": result.get("Implementation"),
        "note": result.get("note"),
    }
    
    metadata_file = output_path / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"Saved: {metadata_file}")
    
    if result.get("ABI"):
        abi_file = output_path / "abi.json"
        abi_file.write_text(result.get("ABI"))
        print(f"Saved: {abi_file}")


def list_supported_chains():
    print("Supported chains:\n")
    print("EVM Chains (Etherscan-compatible):")
    evm_chains = [k for k, v in EXPLORERS.items() if v.get("type") == "etherscan"]
    for i, chain in enumerate(evm_chains):
        print(f"  {chain}", end="")
        if (i + 1) % 5 == 0:
            print()
    print("\n")
    
    print("Non-EVM Chains:")
    non_evm = [k for k, v in EXPLORERS.items() if v.get("type") != "etherscan"]
    for chain in non_evm:
        print(f"  {chain}")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch verified contract source from 40+ blockchain explorers"
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Contract address or explorer URL"
    )
    parser.add_argument(
        "--chain", "-c",
        choices=list(EXPLORERS.keys()),
        help="Blockchain (auto-detected from URL)"
    )
    parser.add_argument(
        "--output", "-o",
        default="./contracts",
        help="Output directory (default: ./contracts)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of saving files"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all supported chains"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_supported_chains()
        return
    
    if not args.target:
        parser.print_help()
        return
    
    if args.target.startswith("http"):
        chain = detect_chain_from_url(args.target)
        address = extract_address_from_url(args.target)
        if not chain:
            print("Error: Could not detect chain from URL", file=sys.stderr)
            print("Use --list to see supported chains", file=sys.stderr)
            sys.exit(1)
        if not address:
            print("Error: Could not extract address from URL", file=sys.stderr)
            sys.exit(1)
    else:
        address = args.target
        chain = args.chain
        if not chain:
            print("Error: --chain required when providing address directly", file=sys.stderr)
            print("Use --list to see supported chains", file=sys.stderr)
            sys.exit(1)
    
    print(f"Fetching {address} from {chain}...")
    result = fetch_contract_source(chain, address)
    
    if result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        output_dir = Path(args.output) / f"{result.get('ContractName', address[:20])}"
        save_contract(result, output_dir, chain)
        print(f"\nContract saved to: {output_dir}")
        
        if result.get("note"):
            print(f"\nNote: {result['note']}")
        
        if result.get("Proxy") == "1" and result.get("Implementation"):
            print(f"\nThis is a proxy contract!")
            print(f"Implementation: {result.get('Implementation')}")
            print(f"Run: python3 fetch_contract.py {result.get('Implementation')} -c {chain}")


if __name__ == "__main__":
    main()
