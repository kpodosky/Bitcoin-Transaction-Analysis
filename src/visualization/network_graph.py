"""
Bitcoin transaction network visualization

Creates network graphs of Bitcoin transactions to visualize relationships
between addresses and identify patterns.
"""

import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import logging
from tqdm import tqdm
import json

logger = logging.getLogger(__name__)

class TransactionNetworkVisualizer:
    """Visualizes Bitcoin transaction networks."""
    
    def __init__(self, data_dir, output_dir):
        """
        Initialize the visualizer.
        
        Args:
            data_dir: Directory containing transaction data
            output_dir: Directory to save visualization outputs
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.graph = nx.DiGraph()
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'network_graphs'), exist_ok=True)
    
    def load_transactions(self, max_transactions=10000):
        """
        Load transaction data and build network graph.
        
        Args:
            max_transactions: Maximum number of transactions to include in the graph
        """
        logger.info(f"Loading transactions for network visualization (max: {max_transactions})")
        
        # Find transaction files
        tx_files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) 
                   if f.startswith('transactions_') and f.endswith('.parquet')]
        
        # Limit the number of files if necessary
        tx_count = 0
        
        for tx_file in tqdm(tx_files, desc="Building network graph"):
            df = pd.read_parquet(tx_file)
            
            for _, tx in df.iterrows():
                tx_id = tx['txid']
                
                # Process each input and output combination
                for input_addr, input_amount in tx['inputs']:
                    for output_addr, output_amount in tx['outputs']:
                        # Skip self-transactions
                        if input_addr == output_addr:
                            continue
                            
                        # Add edge to graph with transaction amount as weight
                        if self.graph.has_edge(input_addr, output_addr):
                            # Increment weight for existing edge
                            self.graph[input_addr][output_addr]['weight'] += output_amount
                            self.graph[input_addr][output_addr]['count'] += 1
                        else:
                            # Create new edge
                            self.graph.add_edge(
                                input_addr, 
                                output_addr, 
                                weight=output_amount,
                                count=1
                            )
                
                tx_count += 1
                if tx_count >= max_transactions:
                    logger.info(f"Reached maximum transaction count ({max_transactions})")
                    break
            
            if tx_count >= max_transactions:
                break
        
        logger.info(f"Built network with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def identify_hubs(self, top_n=50):
        """
        Identify hub addresses in the network.
        
        Args:
            top_n: Number of top hubs to identify
            
        Returns:
            DataFrame of top hubs
        """
        logger.info("Identifying network hubs")
        
        # Calculate node degrees
        in_degree = dict(self.graph.in_degree())
        out_degree = dict(self.graph.out_degree())
        
        # Create DataFrame
        hub_data = []
        for node in self.graph.nodes():
            hub_data.append({
                'address': node,
                'in_degree': in_degree.get(node, 0),
                'out_degree': out_degree.get(node, 0),
                'total_degree': in_degree.get(node, 0) + out_degree.get(node, 0)
            })
        
        hub_df = pd.DataFrame(hub_data)
        hub_df.sort_values('total_degree', ascending=False, inplace=True)
        
        # Save to file
        top_hubs = hub_df.head(top_n)
        top_hubs.to_csv(os.path.join(self.output_dir, 'top_hubs.csv'), index=False)
        
        logger.info(f"Identified top {top_n} network hubs")
        
        return top_hubs
    
    def create_subgraph(self, addresses, depth=1):
        """
        Create a subgraph centered on specific addresses.
        
        Args:
            addresses: List of addresses to include in the subgraph
            depth: Number of hops from center addresses to include
            
        Returns:
            NetworkX subgraph
        """
        logger.info(f"Creating subgraph with depth {depth} around {len(addresses)} addresses")
        
        # Start with given addresses
        subgraph_nodes = set(addresses)
        
        # Add neighbors up to specified depth
        current_nodes = set(addresses)
        for _ in range(depth):
            neighbors = set()
            for node in current_nodes:
                # Add successors (outgoing)
                neighbors.update(self.graph.successors(node))
                # Add predecessors (incoming)
                neighbors.update(self.graph.predecessors(node))
            
            # Update sets
            subgraph_nodes.update(neighbors)
            current_nodes = neighbors
        
        # Create subgraph
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        logger.info(f"Created subgraph with {subgraph.number_of_nodes()} nodes and {subgraph.number_of_edges()} edges")
        
        return subgraph
    
    def visualize_full_network(self, max_nodes=1000):
        """
        Create a visualization of the full network (limited to max_nodes).
        
        Args:
            max_nodes: Maximum number of nodes to include in visualization
        """
        logger.info(f"Creating full network visualization (max nodes: {max_nodes})")
        
        # If graph is too large, take a subset based on node degree
        if self.graph.number_of_nodes() > max_nodes:
            # Calculate node degrees
            degrees = dict(self.graph.degree())
            # Sort nodes by degree
            sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
            # Take top nodes
            top_nodes = [n for n, _ in sorted_nodes[:max_nodes]]
            # Create subgraph
            viz_graph = self.graph.subgraph(top_nodes)
            logger.info(f"Using top {max_nodes} nodes by degree for visualization")
        else:
            viz_graph = self.graph
        
        # Create network visualization
        net = Network(height="800px", width="100%", notebook=False, directed=True)
        
        # Add nodes
        for node in viz_graph.nodes():
            in_degree = viz_graph.in_degree(node)
            out_degree = viz_graph.out_degree(node)
            size = min(30, 5 + (in_degree + out_degree) / 2)
            net.add_node(node, label=node[:8] + "...", size=size)
        
        # Add edges
        for source, target, data in viz_graph.edges(data=True):
            width = 1 + min(5, np.log1p(data['weight']) / 2)
            net.add_edge(source, target, value=width, title=f"Amount: {data['weight']:.4f} BTC")
        
        # Set physics layout
        net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250)
        
        # Save visualization
        output_file = os.path.join(self.output_dir, 'network_graphs', 'full_network.html')
        net.save_graph(output_file)
        
        logger.info(f"Network visualization saved to {output_file}")
    
    def visualize_hub_subgraphs(self, top_n=5, depth=1):
        """
        Create visualizations for subgraphs around top hub addresses.
        
        Args:
            top_n: Number of top hubs to visualize
            depth: Neighborhood depth around each hub
        """
        logger.info(f"Creating hub subgraph visualizations (top {top_n}, depth {depth})")
        
        # Get top hubs
        top_hubs = self.identify_hubs(top_n=top_n)
        
        # Create visualization for each hub
        for idx, row in top_hubs.head(top_n).iterrows():
            address = row['address']
            logger.info(f"Creating visualization for hub {address}")
            
            # Create subgraph
            subgraph = self.create_subgraph([address], depth=depth)
            
            # Create network visualization
            net = Network(height="800px", width="100%", notebook=False, directed=True)
            
            # Add nodes
            for node in subgraph.nodes():
                # Make the hub node larger and highlighted
                if node == address:
                    size = 30
                    color = "#ff0000"
                else:
                    in_degree = subgraph.in_degree(node)
                    out_degree = subgraph.out_degree(node)
                    size = min(20, 5 + (in_degree + out_degree) / 2)
                    color = "#97c2fc"
                
                net.add_node(node, label=node[:8] + "...", size=size, color=color)
            
            # Add edges
            for source, target, data in subgraph.edges(data=True):
                width = 1 + min(5, np.log1p(data['weight']) / 2)
                net.add_edge(source, target, value=width, title=f"Amount: {data['weight']:.4f} BTC")
            
            # Set physics layout
            net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250)
            
            # Save visualization
            output_file = os.path.join(self.output_dir, 'network_graphs', f'hub_{idx+1}_{address[:8]}.html')
            net.save_graph(output_file)
            
            logger.info(f"Hub visualization saved to {output_file}")
    
    def generate_static_network_plot(self):
        """Generate a static network plot for thumbnail/preview."""
        logger.info("Generating static network plot")
        
        # Create a manageable subgraph
        if self.graph.number_of_nodes() > 200:
            # Get top nodes by degree
            degrees = dict(self.graph.degree())
            sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
            top_nodes = [n for n, _ in sorted_nodes[:200]]
            plot_graph = self.graph.subgraph(top_nodes)
        else:
            plot_graph = self.graph
        
        # Create plot
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(plot_graph, k=0.15, iterations=50)
        
        # Draw nodes
        node_sizes = [5 + (plot_graph.in_degree(n) + plot_graph.out_degree(n)) for n in plot_graph.nodes()]
        nx.draw_networkx_nodes(
            plot_graph, 
            pos, 
            node_size=node_sizes,
            node_color='skyblue', 
            alpha=0.8
        )
        
        # Draw edges with varying width based on weight
        edge_weights = [min(5, 0.5 + np.log1p(plot_graph[u][v]['weight'])) for u, v in plot_graph.edges()]
        nx.draw_networkx_edges(
            plot_graph, 
            pos, 
            width=edge_weights,
            alpha=0.5,
            edge_color='gray',
            arrows=True,
            arrowsize=10,
            connectionstyle='arc3,rad=0.1'
        )
        
        # Minimal labels for top nodes
        top_degrees = sorted([(n, plot_graph.degree(n)) for n in plot_graph.nodes()], key=lambda x: x[1], reverse=True)
        labels = {n: n[:8] + "..." for n, _ in top_degrees[:20]}
        nx.draw_networkx_labels(plot_graph, pos, labels=labels, font_size=8)
        
        plt.title("Bitcoin Transaction Network")
        plt.axis('off')
        
        # Save figure
        output_file = os.path.join(self.output_dir, 'network_graphs', 'static_network.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Static network plot saved to {output_file}")

def main():
    """Run network visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize Bitcoin transaction networks')
    parser.add_argument('--data-dir', required=True, help='Directory with transaction data')
    parser.add_argument('--output-dir', required=True, help='Directory to save visualization outputs')
    parser.add_argument('--max-transactions', type=int, default=10000, help='Maximum transactions to include')
    parser.add_argument('--hub-depth', type=int, default=1, help='Neighborhood depth for hub subgraphs')
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = TransactionNetworkVisualizer(
        args.data_dir,
        args.output_dir
    )
    
    # Load data and build graph
    visualizer.load_transactions(max_transactions=args.max_transactions)
    
    # Generate visualizations
    visualizer.identify_hubs()
    visualizer.visualize_full_network()
    visualizer.visualize_hub_subgraphs(depth=args.hub_depth)
    visualizer.generate_static_network_plot()
    
    logger.info("Visualization complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
