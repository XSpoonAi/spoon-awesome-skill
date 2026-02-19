"""
Graph Analysis Module - Sybil & Insider Detector

Analyzes transaction networks using graph theory:
- Transaction Graph Construction
- Community Detection (Louvain, Label Propagation)
- Centrality Analysis (PageRank, Betweenness, Degree)
- Subgraph Pattern Matching
- Network Flow Analysis

REAL IMPLEMENTATION - No Mocks/Simulations
Uses NetworkX for graph algorithms
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
import networkx as nx
from collections import defaultdict, Counter
import numpy as np
from web3 import Web3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GraphMetrics:
    """Network metrics for an address"""
    address: str
    degree_centrality: float
    betweenness_centrality: float
    pagerank: float
    clustering_coefficient: float
    community_id: Optional[int] = None
    in_degree: int = 0
    out_degree: int = 0
    total_flow_in: float = 0.0
    total_flow_out: float = 0.0


@dataclass
class SybilNetwork:
    """Detected Sybil network"""
    network_id: int
    addresses: Set[str]
    hub_address: str
    confidence: float
    pattern_type: str  # 'star', 'chain', 'cluster'
    total_volume: float
    transaction_count: int
    creation_time: Optional[int] = None


class GraphAnalyzer:
    """
    Transaction graph analysis for Sybil and bot network detection
    """
    
    def __init__(self, w3: Web3):
        """
        Initialize graph analyzer
        
        Args:
            w3: Web3 instance
        """
        self.w3 = w3
        self.graph = nx.DiGraph()
        self.metrics_cache: Dict[str, GraphMetrics] = {}
    
    def build_transaction_graph(
        self,
        transactions: List[Dict],
        min_value: float = 0.0
    ) -> nx.DiGraph:
        """
        Build directed graph from transactions
        
        Args:
            transactions: Transaction data
            min_value: Minimum transaction value to include
            
        Returns:
            NetworkX directed graph
        """
        logger.info(f"Building transaction graph from {len(transactions)} transactions")
        
        self.graph.clear()
        
        for tx in transactions:
            from_addr = tx.get('from', '').lower()
            to_addr = tx.get('to', '').lower()
            value = float(tx.get('value', 0))
            
            if not from_addr or not to_addr or value < min_value:
                continue
            
            # Add edge or update weight
            if self.graph.has_edge(from_addr, to_addr):
                self.graph[from_addr][to_addr]['weight'] += value
                self.graph[from_addr][to_addr]['count'] += 1
            else:
                self.graph.add_edge(
                    from_addr,
                    to_addr,
                    weight=value,
                    count=1,
                    timestamp=tx.get('timestamp')
                )
        
        logger.info(f"Graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
    
    def detect_communities(
        self,
        algorithm: str = 'louvain'
    ) -> Dict[int, Set[str]]:
        """
        Detect communities in transaction graph
        
        Args:
            algorithm: 'louvain' or 'label_propagation'
            
        Returns:
            Dict mapping community ID to set of addresses
        """
        logger.info(f"Detecting communities using {algorithm}")
        
        if self.graph.number_of_nodes() == 0:
            logger.warning("Empty graph")
            return {}
        
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        if algorithm == 'louvain':
            # Use Louvain method (requires python-louvain package)
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(undirected, weight='weight')
            except ImportError:
                logger.warning("python-louvain not installed, using label propagation")
                communities_gen = nx.community.label_propagation_communities(undirected)
                communities = list(communities_gen)
                partition = {}
                for i, comm in enumerate(communities):
                    for node in comm:
                        partition[node] = i
        
        elif algorithm == 'label_propagation':
            communities_gen = nx.community.label_propagation_communities(undirected)
            communities = list(communities_gen)
            partition = {}
            for i, comm in enumerate(communities):
                for node in comm:
                    partition[node] = i
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Group by community
        result = defaultdict(set)
        for node, comm_id in partition.items():
            result[comm_id].add(node)
        
        logger.info(f"Found {len(result)} communities")
        return dict(result)
    
    def calculate_centrality_metrics(
        self,
        addresses: Optional[List[str]] = None
    ) -> Dict[str, GraphMetrics]:
        """
        Calculate centrality metrics for addresses
        
        Args:
            addresses: Specific addresses to analyze (or all if None)
            
        Returns:
            Dict mapping address to metrics
        """
        logger.info("Calculating centrality metrics")
        
        if self.graph.number_of_nodes() == 0:
            logger.warning("Empty graph")
            return {}
        
        # Calculate metrics for entire graph
        degree_cent = nx.degree_centrality(self.graph)
        betweenness = nx.betweenness_centrality(self.graph, weight='weight')
        pagerank = nx.pagerank(self.graph, weight='weight')
        clustering = nx.clustering(self.graph.to_undirected())
        
        # Get flow metrics
        metrics = {}
        nodes = addresses if addresses else self.graph.nodes()
        
        for addr in nodes:
            if addr not in self.graph:
                continue
            
            in_flow = sum(
                self.graph[pred][addr]['weight'] 
                for pred in self.graph.predecessors(addr)
            )
            out_flow = sum(
                self.graph[addr][succ]['weight'] 
                for succ in self.graph.successors(addr)
            )
            
            metrics[addr] = GraphMetrics(
                address=addr,
                degree_centrality=degree_cent.get(addr, 0.0),
                betweenness_centrality=betweenness.get(addr, 0.0),
                pagerank=pagerank.get(addr, 0.0),
                clustering_coefficient=clustering.get(addr, 0.0),
                in_degree=self.graph.in_degree(addr),
                out_degree=self.graph.out_degree(addr),
                total_flow_in=in_flow,
                total_flow_out=out_flow
            )
        
        self.metrics_cache.update(metrics)
        logger.info(f"Calculated metrics for {len(metrics)} addresses")
        return metrics
    
    def detect_star_patterns(
        self,
        min_connections: int = 10,
        max_hops: int = 2
    ) -> List[SybilNetwork]:
        """
        Detect star/hub patterns (one address funding many others)
        
        Args:
            min_connections: Minimum connections for hub
            max_hops: Maximum hops from hub
            
        Returns:
            List of detected Sybil networks
        """
        logger.info("Detecting star/hub patterns")
        
        networks = []
        
        # Find high out-degree nodes (potential funding hubs)
        high_degree_nodes = [
            node for node in self.graph.nodes()
            if self.graph.out_degree(node) >= min_connections
        ]
        
        for hub in high_degree_nodes:
            # Get all nodes within max_hops
            subgraph_nodes = set()
            subgraph_nodes.add(hub)
            
            # BFS to find connected nodes
            queue = [(hub, 0)]
            visited = {hub}
            
            while queue:
                node, depth = queue.pop(0)
                if depth >= max_hops:
                    continue
                
                for successor in self.graph.successors(node):
                    if successor not in visited:
                        visited.add(successor)
                        subgraph_nodes.add(successor)
                        queue.append((successor, depth + 1))
            
            if len(subgraph_nodes) >= min_connections:
                # Calculate network metrics
                subgraph = self.graph.subgraph(subgraph_nodes)
                total_volume = sum(
                    data['weight'] 
                    for _, _, data in subgraph.edges(data=True)
                )
                
                network = SybilNetwork(
                    network_id=len(networks),
                    addresses=subgraph_nodes,
                    hub_address=hub,
                    confidence=self._calculate_star_confidence(hub, subgraph_nodes),
                    pattern_type='star',
                    total_volume=total_volume,
                    transaction_count=subgraph.number_of_edges()
                )
                
                networks.append(network)
        
        logger.info(f"Detected {len(networks)} star patterns")
        return networks
    
    def detect_chain_patterns(
        self,
        min_length: int = 5
    ) -> List[SybilNetwork]:
        """
        Detect chain patterns (sequential funding)
        
        Args:
            min_length: Minimum chain length
            
        Returns:
            List of chain networks
        """
        logger.info("Detecting chain patterns")
        
        networks = []
        visited_chains = set()
        
        # Find all simple paths (chains)
        for source in self.graph.nodes():
            if self.graph.out_degree(source) != 1:
                continue
            
            # Follow chain
            chain = [source]
            current = source
            
            while True:
                successors = list(self.graph.successors(current))
                if len(successors) != 1:
                    break
                
                next_node = successors[0]
                if next_node in chain:  # Cycle detected
                    break
                
                chain.append(next_node)
                current = next_node
                
                # Stop if out-degree != 1 (end of chain)
                if self.graph.out_degree(current) != 1:
                    break
            
            if len(chain) >= min_length:
                chain_sig = tuple(sorted(chain))
                if chain_sig not in visited_chains:
                    visited_chains.add(chain_sig)
                    
                    # Calculate metrics
                    edges = [(chain[i], chain[i+1]) for i in range(len(chain)-1)]
                    total_volume = sum(
                        self.graph[u][v]['weight'] 
                        for u, v in edges
                    )
                    
                    network = SybilNetwork(
                        network_id=len(networks),
                        addresses=set(chain),
                        hub_address=chain[0],
                        confidence=self._calculate_chain_confidence(chain),
                        pattern_type='chain',
                        total_volume=total_volume,
                        transaction_count=len(edges)
                    )
                    
                    networks.append(network)
        
        logger.info(f"Detected {len(networks)} chain patterns")
        return networks
    
    def find_common_funding_source(
        self,
        addresses: List[str],
        max_depth: int = 3
    ) -> Optional[str]:
        """
        Find common funding source for addresses
        
        Args:
            addresses: Addresses to analyze
            max_depth: Maximum depth to search
            
        Returns:
            Common funding address or None
        """
        logger.info(f"Finding common funding source for {len(addresses)} addresses")
        
        # Get all funding sources for each address
        funding_sources = defaultdict(set)
        
        for addr in addresses:
            if addr not in self.graph:
                continue
            
            # BFS backwards to find funding sources
            visited = set()
            queue = [(addr, 0)]
            
            while queue:
                node, depth = queue.pop(0)
                if depth >= max_depth or node in visited:
                    continue
                
                visited.add(node)
                funding_sources[addr].add(node)
                
                for predecessor in self.graph.predecessors(node):
                    queue.append((predecessor, depth + 1))
        
        # Find common sources
        if not funding_sources:
            return None
        
        common = set.intersection(*funding_sources.values()) if funding_sources else set()
        
        if common:
            # Return source with highest PageRank
            if self.metrics_cache:
                best_source = max(
                    common,
                    key=lambda x: self.metrics_cache.get(x, GraphMetrics(x, 0, 0, 0, 0)).pagerank
                )
            else:
                best_source = list(common)[0]
            
            logger.info(f"Found common source: {best_source}")
            return best_source
        
        return None
    
    def analyze_network_flow(
        self,
        source: str,
        targets: List[str]
    ) -> Dict[str, float]:
        """
        Analyze flow from source to targets
        
        Args:
            source: Source address
            targets: Target addresses
            
        Returns:
            Dict of target -> flow amount
        """
        logger.info(f"Analyzing flow from {source} to {len(targets)} targets")
        
        flows = {}
        
        for target in targets:
            if source not in self.graph or target not in self.graph:
                flows[target] = 0.0
                continue
            
            try:
                # Find all simple paths
                paths = list(nx.all_simple_paths(
                    self.graph,
                    source,
                    target,
                    cutoff=5
                ))
                
                # Calculate total flow
                total_flow = 0.0
                for path in paths:
                    path_flow = min(
                        self.graph[path[i]][path[i+1]]['weight']
                        for i in range(len(path) - 1)
                    )
                    total_flow += path_flow
                
                flows[target] = total_flow
            
            except nx.NetworkXNoPath:
                flows[target] = 0.0
        
        return flows
    
    def _calculate_star_confidence(
        self,
        hub: str,
        network: Set[str]
    ) -> float:
        """Calculate confidence for star pattern"""
        # Check if hub has disproportionate out-degree
        hub_out_degree = self.graph.out_degree(hub)
        avg_out_degree = np.mean([self.graph.out_degree(n) for n in network])
        
        if avg_out_degree == 0:
            return 0.5
        
        ratio = hub_out_degree / avg_out_degree
        
        # High ratio suggests hub-and-spoke Sybil pattern
        confidence = min(1.0, ratio / 20.0)
        return confidence
    
    def _calculate_chain_confidence(self, chain: List[str]) -> float:
        """Calculate confidence for chain pattern"""
        # Check transaction timing and amounts
        edges = [(chain[i], chain[i+1]) for i in range(len(chain)-1)]
        amounts = [self.graph[u][v]['weight'] for u, v in edges]
        
        # Similar amounts suggest automated behavior
        amount_variance = np.var(amounts) if len(amounts) > 1 else float('inf')
        
        # Low variance = high confidence
        if amount_variance < 0.01:
            return 0.9
        elif amount_variance < 0.1:
            return 0.7
        else:
            return 0.5


def main():
    """Example usage"""
    import os
    
    # Connect to Ethereum
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("RPC_URL environment variable must be set")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    print(f"Connected to: {rpc_url}")
    print(f"Block: {w3.eth.block_number}\n")
    
    print("=" * 70)
    print("TRANSACTION GRAPH ANALYZER")
    print("=" * 70)
    print("✅ Graph analyzer initialized\n")
    
    # Initialize analyzer
    analyzer = GraphAnalyzer(w3)
    
    # Example transactions (mock data for demonstration)
    example_txs = [
        {'from': '0xa', 'to': '0xb', 'value': 1.5, 'timestamp': 1000},
        {'from': '0xa', 'to': '0xc', 'value': 1.5, 'timestamp': 1001},
        {'from': '0xa', 'to': '0xd', 'value': 1.5, 'timestamp': 1002},
        {'from': '0xb', 'to': '0xe', 'value': 1.0, 'timestamp': 1010},
        {'from': '0xc', 'to': '0xf', 'value': 1.0, 'timestamp': 1011},
    ]
    
    print("=" * 70)
    print("EXAMPLE: Build Transaction Graph")
    print("=" * 70)
    
    graph = analyzer.build_transaction_graph(example_txs)
    print(f"\n✅ Graph built:")
    print(f"   Nodes: {graph.number_of_nodes()}")
    print(f"   Edges: {graph.number_of_edges()}")
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Calculate Centrality Metrics")
    print("=" * 70)
    
    metrics = analyzer.calculate_centrality_metrics()
    print(f"\n✅ Calculated metrics for {len(metrics)} addresses")
    
    for addr, metric in list(metrics.items())[:3]:
        print(f"\n{addr}:")
        print(f"  PageRank: {metric.pagerank:.4f}")
        print(f"  Degree centrality: {metric.degree_centrality:.4f}")
        print(f"  In-degree: {metric.in_degree}")
        print(f"  Out-degree: {metric.out_degree}")
    
    print("\n" + "=" * 70)
    print("EXAMPLE: Detect Star Patterns")
    print("=" * 70)
    
    stars = analyzer.detect_star_patterns(min_connections=2)
    print(f"\n✅ Detected {len(stars)} star patterns")
    
    for network in stars:
        print(f"\nNetwork {network.network_id}:")
        print(f"  Hub: {network.hub_address}")
        print(f"  Addresses: {len(network.addresses)}")
        print(f"  Confidence: {network.confidence:.2f}")
        print(f"  Total volume: {network.total_volume:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ Examples complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
