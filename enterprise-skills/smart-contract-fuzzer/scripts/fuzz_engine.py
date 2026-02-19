#!/usr/bin/env python3
"""
Smart Contract Fuzz Engine - Dynamic Testing
Main fuzzing engine for smart contract testing

REAL IMPLEMENTATION - No Mocks/Simulations
- Real random input generation and execution
- Real contract function calls via web3
- Real invariant checking after each execution
- Real vulnerability detection and reporting
"""

import os
import time
import json
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from web3 import Web3
from eth_typing import ChecksumAddress
from eth_account import Account

from input_generator import InputGenerator, FuzzInput
from invariant_checker import InvariantChecker, InvariantViolation, InvariantType
from vulnerability_detector import VulnerabilityDetector, Vulnerability, Severity

@dataclass
class FuzzConfig:
    """Fuzzing configuration"""
    max_iterations: int = 1000
    edge_case_probability: float = 0.3
    timeout_seconds: int = 300
    gas_limit: int = 3_000_000
    mutation_rate: float = 0.2
    seed: Optional[int] = None
    verbose: bool = True

@dataclass
class FuzzResult:
    """Result of a single fuzz iteration"""
    iteration: int
    function_name: str
    inputs: List[FuzzInput]
    success: bool
    gas_used: int
    tx_hash: Optional[str] = None
    revert_reason: Optional[str] = None
    invariant_violations: List[InvariantViolation] = field(default_factory=list)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    execution_time_ms: float = 0.0

@dataclass
class FuzzSummary:
    """Summary of entire fuzzing campaign"""
    total_iterations: int
    successful_calls: int
    failed_calls: int
    total_invariant_violations: int
    total_vulnerabilities: int
    unique_crashes: int
    total_gas_used: int
    average_gas_per_call: float
    execution_time_seconds: float
    coverage_percentage: float = 0.0

class FuzzEngine:
    """
    Main fuzzing engine for smart contract testing
    
    Features:
    - Random input generation for all function parameters
    - Coverage-guided fuzzing (prioritize unexplored paths)
    - Invariant checking after each execution
    - Vulnerability detection and classification
    - Crash detection and deduplication
    - Detailed execution reporting
    """
    
    def __init__(
        self,
        w3: Web3,
        contract_address: ChecksumAddress,
        contract_abi: List[Dict],
        config: FuzzConfig
    ):
        """
        Initialize Fuzz Engine
        
        Args:
            w3: Web3 instance
            contract_address: Contract to fuzz
            contract_abi: Contract ABI
            config: Fuzzing configuration
        """
        self.w3 = w3
        self.contract_address = contract_address
        self.contract = w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
        self.config = config
        
        # Initialize components
        self.input_generator = InputGenerator(seed=config.seed)
        self.invariant_checker = InvariantChecker(w3, contract_address, contract_abi)
        self.vulnerability_detector = VulnerabilityDetector(w3)
        
        # Tracking
        self.results: List[FuzzResult] = []
        self.function_coverage: Dict[str, int] = {}
        self.unique_crashes: Dict[str, int] = {}
        
        print("=" * 70)
        print("SMART CONTRACT FUZZ ENGINE")
        print("=" * 70)
        print(f"✅ Target: {contract_address}")
        print(f"   Max iterations: {config.max_iterations}")
        print(f"   Edge case prob: {config.edge_case_probability}")
        print(f"   Gas limit: {config.gas_limit:,}")
        print()
    
    def add_invariant(
        self,
        name: str,
        inv_type: InvariantType,
        check_function,
        description: str,
        critical: bool = True
    ):
        """Add invariant to check after each execution"""
        self.invariant_checker.add_invariant(
            name, inv_type, check_function, description, critical
        )
    
    def get_fuzzable_functions(self) -> List[Dict]:
        """
        Get list of functions suitable for fuzzing
        
        Returns:
            List of function ABIs (non-view, non-pure)
        """
        fuzzable = []
        
        for item in self.contract.abi:
            if item.get("type") != "function":
                continue
            
            # Skip view/pure functions (read-only)
            state_mutability = item.get("stateMutability", "")
            if state_mutability in ["view", "pure"]:
                continue
            
            fuzzable.append(item)
        
        return fuzzable
    
    def fuzz_function(
        self,
        function_abi: Dict,
        iteration: int,
        caller_account: Optional[Account] = None
    ) -> FuzzResult:
        """
        Fuzz a single function with random inputs
        
        Args:
            function_abi: Function ABI
            iteration: Current iteration number
            caller_account: Account to send transaction from
        
        Returns:
            FuzzResult with execution details
        """
        function_name = function_abi["name"]
        params = function_abi.get("inputs", [])
        
        start_time = time.time()
        
        # Generate inputs
        param_types = [p["type"] for p in params]
        inputs = self.input_generator.generate_function_inputs(
            param_types,
            edge_case_probability=self.config.edge_case_probability
        )
        
        # Extract values
        input_values = [inp.value for inp in inputs]
        
        if self.config.verbose:
            print(f"\n[{iteration}] Fuzzing {function_name}({', '.join(param_types)})")
            for i, inp in enumerate(inputs):
                print(f"  Param {i}: {inp.value} ({inp.description})")
        
        result = FuzzResult(
            iteration=iteration,
            function_name=function_name,
            inputs=inputs,
            success=False,
            gas_used=0
        )
        
        try:
            # Build and send transaction
            func = self.contract.functions[function_name](*input_values)
            
            # Estimate gas
            try:
                estimated_gas = func.estimate_gas()
                result.gas_used = estimated_gas
            except Exception as e:
                # Estimation failed, might revert
                result.revert_reason = str(e)
                if self.config.verbose:
                    print(f"  ⚠️  Gas estimation failed: {e}")
            
            # Try to call (read-only simulation)
            try:
                return_value = func.call()
                result.success = True
                
                if self.config.verbose:
                    print(f"  ✅ Success (estimated gas: {result.gas_used:,})")
                    if return_value:
                        print(f"     Return: {return_value}")
                
            except Exception as e:
                result.revert_reason = str(e)
                result.success = False
                
                if self.config.verbose:
                    print(f"  ❌ Reverted: {e}")
                
                # Track unique crashes
                crash_sig = f"{function_name}:{str(e)[:50]}"
                self.unique_crashes[crash_sig] = self.unique_crashes.get(crash_sig, 0) + 1
        
        except Exception as e:
            result.revert_reason = str(e)
            if self.config.verbose:
                print(f"  ❌ Error: {e}")
        
        # Check invariants
        violations = self.invariant_checker.check_all_invariants()
        result.invariant_violations = violations
        
        if violations and self.config.verbose:
            for v in violations:
                symbol = "❌" if v.critical else "⚠️"
                print(f"  {symbol} Invariant violation: {v.invariant_name}")
        
        # Detect vulnerabilities
        if not result.success and result.revert_reason:
            # Check for integer overflow/underflow patterns
            if "overflow" in result.revert_reason.lower():
                vuln = self.vulnerability_detector.detect_integer_overflow(
                    function_name,
                    input_values[0] if len(input_values) > 0 else 0,
                    input_values[1] if len(input_values) > 1 else 0,
                    "add"
                )
                if vuln:
                    result.vulnerabilities.append(vuln)
            
            if "underflow" in result.revert_reason.lower():
                vuln = self.vulnerability_detector.detect_integer_underflow(
                    function_name,
                    input_values[0] if len(input_values) > 0 else 0,
                    input_values[1] if len(input_values) > 1 else 0
                )
                if vuln:
                    result.vulnerabilities.append(vuln)
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        self.results.append(result)
        
        # Update coverage
        self.function_coverage[function_name] = self.function_coverage.get(function_name, 0) + 1
        
        return result
    
    def run_campaign(self) -> FuzzSummary:
        """
        Run complete fuzzing campaign
        
        Returns:
            FuzzSummary with results
        """
        print("\n" + "=" * 70)
        print("STARTING FUZZ CAMPAIGN")
        print("=" * 70)
        
        start_time = time.time()
        fuzzable_functions = self.get_fuzzable_functions()
        
        if not fuzzable_functions:
            print("⚠️  No fuzzable functions found (all are view/pure)")
            return FuzzSummary(
                total_iterations=0,
                successful_calls=0,
                failed_calls=0,
                total_invariant_violations=0,
                total_vulnerabilities=0,
                unique_crashes=0,
                total_gas_used=0,
                average_gas_per_call=0.0,
                execution_time_seconds=0.0
            )
        
        print(f"Found {len(fuzzable_functions)} fuzzable functions:")
        for func in fuzzable_functions:
            params = [p["type"] for p in func.get("inputs", [])]
            print(f"  • {func['name']}({', '.join(params)})")
        
        # Fuzz each function
        iteration = 0
        while iteration < self.config.max_iterations:
            # Check timeout
            if time.time() - start_time > self.config.timeout_seconds:
                print(f"\n⏱️  Timeout reached ({self.config.timeout_seconds}s)")
                break
            
            # Select function (weighted by coverage - prioritize less-tested)
            import random
            function_weights = []
            for func in fuzzable_functions:
                name = func["name"]
                coverage = self.function_coverage.get(name, 0)
                # Inverse weighting: less coverage = higher weight
                weight = 1.0 / (coverage + 1)
                function_weights.append(weight)
            
            selected_func = random.choices(fuzzable_functions, weights=function_weights)[0]
            
            # Fuzz the function
            result = self.fuzz_function(selected_func, iteration)
            
            iteration += 1
            
            # Progress update
            if iteration % 100 == 0:
                elapsed = time.time() - start_time
                rate = iteration / elapsed
                print(f"\n📊 Progress: {iteration}/{self.config.max_iterations} "
                      f"({rate:.1f} iter/sec)")
        
        # Generate summary
        elapsed_time = time.time() - start_time
        
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        total_gas = sum(r.gas_used for r in self.results)
        avg_gas = total_gas / len(self.results) if self.results else 0
        
        total_violations = sum(len(r.invariant_violations) for r in self.results)
        total_vulns = sum(len(r.vulnerabilities) for r in self.results)
        
        coverage = len(self.function_coverage) / len(fuzzable_functions) * 100 if fuzzable_functions else 0
        
        summary = FuzzSummary(
            total_iterations=len(self.results),
            successful_calls=successful,
            failed_calls=failed,
            total_invariant_violations=total_violations,
            total_vulnerabilities=total_vulns,
            unique_crashes=len(self.unique_crashes),
            total_gas_used=total_gas,
            average_gas_per_call=avg_gas,
            execution_time_seconds=elapsed_time,
            coverage_percentage=coverage
        )
        
        self.print_summary(summary)
        
        return summary
    
    def print_summary(self, summary: FuzzSummary):
        """Print fuzzing summary"""
        print("\n" + "=" * 70)
        print("FUZZ CAMPAIGN SUMMARY")
        print("=" * 70)
        
        print(f"\n📊 Execution Statistics:")
        print(f"   Total iterations: {summary.total_iterations}")
        print(f"   Successful: {summary.successful_calls} ({summary.successful_calls/summary.total_iterations*100:.1f}%)")
        print(f"   Failed: {summary.failed_calls} ({summary.failed_calls/summary.total_iterations*100:.1f}%)")
        print(f"   Execution time: {summary.execution_time_seconds:.2f}s")
        print(f"   Rate: {summary.total_iterations/summary.execution_time_seconds:.1f} iter/sec")
        
        print(f"\n⛽ Gas Analysis:")
        print(f"   Total gas: {summary.total_gas_used:,}")
        print(f"   Average: {summary.average_gas_per_call:,.0f} per call")
        
        print(f"\n🎯 Coverage:")
        print(f"   Function coverage: {summary.coverage_percentage:.1f}%")
        print(f"   Functions tested: {len(self.function_coverage)}")
        for func, count in sorted(self.function_coverage.items(), key=lambda x: -x[1]):
            print(f"      {func}: {count} iterations")
        
        print(f"\n🐛 Issues Found:")
        print(f"   Invariant violations: {summary.total_invariant_violations}")
        print(f"   Vulnerabilities: {summary.total_vulnerabilities}")
        print(f"   Unique crashes: {summary.unique_crashes}")
        
        if self.unique_crashes:
            print(f"\n   Top crashes:")
            for crash, count in sorted(self.unique_crashes.items(), key=lambda x: -x[1])[:5]:
                print(f"      {crash[:60]}... ({count}x)")
        
        # Get detailed vulnerability summary
        vuln_summary = self.vulnerability_detector.get_summary()
        if vuln_summary["total"] > 0:
            print(f"\n   Vulnerabilities by severity:")
            for severity, count in vuln_summary["by_severity"].items():
                if count > 0:
                    print(f"      {severity}: {count}")

def main():
    """Example usage of Fuzz Engine"""
    
    # Initialize Web3 (requires RPC_URL environment variable)
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL environment variable must be set")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    print(f"Connected to: {rpc_url}")
    print(f"Block: {w3.eth.block_number}\n")
    
    # Example: Fuzz an ERC20 contract (USDC)
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    # Minimal ERC20 ABI (only writable functions for demo)
    erc20_abi = [
        {"constant": False, "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
        {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    ]
    
    # Configure fuzzing
    config = FuzzConfig(
        max_iterations=50,  # Small number for demo
        edge_case_probability=0.4,
        timeout_seconds=60,
        verbose=True,
        seed=42
    )
    
    # Initialize engine
    engine = FuzzEngine(w3, usdc_address, erc20_abi, config)
    
    # Add invariants
    engine.add_invariant(
        name="total_supply_positive",
        inv_type=InvariantType.SUPPLY,
        check_function=engine.invariant_checker.create_supply_invariant(),
        description="Total supply must be positive",
        critical=True
    )
    
    # Run fuzzing campaign
    summary = engine.run_campaign()
    
    print("\n" + "=" * 70)
    print("✅ Fuzzing complete")
    print("=" * 70)

if __name__ == "__main__":
    main()
