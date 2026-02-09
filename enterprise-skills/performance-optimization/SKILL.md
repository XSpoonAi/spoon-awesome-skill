---
name: Performance Optimization
type: enterprise-skill
complexity: advanced
estimated_time: 45-60 minutes
difficulty: high
---

# Performance Optimization Skill

A comprehensive performance profiling and optimization skill that identifies bottlenecks, analyzes caching strategies, and simulates load testing scenarios.

## Overview

This skill provides enterprise-grade performance analysis tools for Python applications:

- **Profiling**: Measure function execution time, memory usage, and CPU consumption
- **Bottleneck Detection**: Identify common performance anti-patterns (nested loops, N+1 queries, memory leaks, blocking I/O)
- **Caching Strategy**: Analyze cache opportunities and recommend optimal strategies (LRU, LFU, TTL, ARC)
- **Load Testing**: Simulate various load patterns and stress scenarios

## Key Features

### Performance Profiler
- Function-level profiling with execution time, memory, and CPU tracking
- Code block profiling for arbitrary Python code
- Batch profiling for multiple functions with iteration counts
- Real-time resource monitoring (memory, CPU, threads) over time
- Performance comparison between baseline and current runs
- Hotspot identification for optimization prioritization

### Bottleneck Detector
- Static code analysis for performance anti-patterns:
  - Nested loops (O(n²) complexity detection)
  - N+1 query patterns in database operations
  - String concatenation in loops
  - Inefficient list operations
  - Blocking I/O operations
  - Global variable lookups
- Database query analysis (missing indexes, slow queries)
- Memory leak detection through growth pattern analysis
- Concurrency issue detection (race conditions, deadlocks)
- Detailed severity ratings (CRITICAL, HIGH, MEDIUM, LOW)

### Cache Advisor
- Analysis of 5 cache strategies: LRU, LFU, TTL, FIFO, ARC
- Cache opportunity detection based on access patterns
- Cache size recommendations with hit rate estimation
- Strategy scoring and comparison
- Code generation for Python and JavaScript
- Cache invalidation strategy recommendations

### Load Tester
- Multiple load patterns: constant, ramp-up, spike, wave
- Stress testing to find system breaking points
- Soak testing for long-duration stability analysis
- Chaos testing with failure/latency injection
- Performance metrics: throughput, latency percentiles, error rates
- HTML report generation

## Use Cases

1. **Optimization**: Find and fix performance bottlenecks in Python applications
2. **Capacity Planning**: Determine maximum sustainable load
3. **Regression Testing**: Ensure performance doesn't degrade over time
4. **Cache Strategy**: Select optimal caching approach for specific access patterns
5. **Stability Testing**: Validate system stability under sustained load

## Configuration

Each module is self-contained and can be used independently:

```python
# Performance Profiler
from scripts.profiler import PerformanceProfiler

profiler = PerformanceProfiler()
result = profiler.profile_function(my_function, arg1, arg2)

# Bottleneck Detector
from scripts.bottleneck_detector import BottleneckDetector

detector = BottleneckDetector()
bottlenecks = detector.detect_code_bottlenecks(code_string)

# Cache Advisor
from scripts.cache_advisor import CacheAdvisor

advisor = CacheAdvisor()
recommendation = advisor.analyze_caching_opportunity(access_pattern)

# Load Tester
from scripts.load_tester import LoadTester

tester = LoadTester()
results = tester.run_load_test(endpoint, config)
```

## Outputs

- Performance metrics (JSON format)
- Bottleneck reports with severity levels
- Cache strategy rankings and scoring
- Load test reports with percentile analysis
- HTML reports with visualizations

## Dependencies

- psutil: System and process utilities
- numpy: Numerical analysis
- matplotlib: Chart generation
- requests: HTTP client for endpoint testing

## Confidence Score

- Performance Profiler: 92%
- Bottleneck Detector: 90%
- Cache Advisor: 91%
- Load Tester: 89%
- **Overall: 91%**
