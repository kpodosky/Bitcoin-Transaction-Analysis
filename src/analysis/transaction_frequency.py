"""
Transaction frequency analysis module

Analyzes transaction frequencies for Bitcoin addresses.
"""

import os
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import logging
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

from ..data.blockchain_parser import parse_transaction_data
from ..utils.address_labels import load_address_labels

logger = logging.getLogger(__name__)

class TransactionFrequencyAnalyzer:
    """Analyzes transaction frequencies for Bitcoin addresses."""
    
    def __init__(self, data_dir, output_dir, exchange_addresses=None):
        """
        Initialize the analyzer.
        
        Args:
            data_dir: Directory containing parsed transaction data
            output_dir: Directory to save analysis results
            exchange_addresses: Dictionary mapping exchange names to address lists
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.exchange_addresses = exchange_addresses or {}
        self.address_tx_count = defaultdict(lambda: {'sent': 0, 'received': 0, 'volume_btc': 0})
        self.exchange_tx_count = defaultdict(lambda: {'inflow': 0, 'outflow': 0, 'volume_btc': 0})
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_transaction_data(self, file_pattern='transactions_*.parquet'):
        """Load transaction data from parquet files."""
        logger.info(f"Loading transaction data from {self.data_dir}")
        
        # Find all transaction files
        tx_files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) 
                   if f.startswith('transactions_') and f.endswith('.parquet')]
        
        if not tx_files:
            raise FileNotFoundError(f"No transaction files found in {self.data_dir}")
        
        # Load and process each file
        for tx_file in tqdm(tx_files, desc="Processing transaction files"):
            df = pd.read_parquet(tx_file)
            self._process_transaction_df(df)
            
        logger.info(f"Processed {len(tx_files)} transaction files")
        logger.info(f"Found {len(self.address_tx_count)} unique addresses")
        
    def _process_transaction_df(self, df):
        """Process a transaction dataframe to count transactions by address."""
        # Count sending transactions
        for _, row in df.iterrows():
            # Process inputs (sending addresses)
            for address, amount in row['inputs']:
                self.address_tx_count[address]['sent'] += 1
                self.address_tx_count[address]['volume_btc'] += amount
                
                # Check if this is an exchange address
                for exchange, addresses in self.exchange_addresses.items():
                    if address in addresses:
                        self.exchange_tx_count[exchange]['outflow'] += 1
                        self.exchange_tx_count[exchange]['volume_btc'] += amount
            
            # Process outputs (receiving addresses)
            for address, amount in row['outputs']:
                self.address_tx_count[address]['received'] += 1
                self.address_tx_count[address]['volume_btc'] += amount
                
                # Check if this is an exchange address
                for exchange, addresses in self.exchange_addresses.items():
                    if address in addresses:
                        self.exchange_tx_count[exchange]['inflow'] += 1
                        self.exchange_tx_count[exchange]['volume_btc'] += amount
    
    def identify_high_frequency_addresses(self, threshold=100):
        """Identify addresses with high transaction frequency."""
        high_frequency = {}
        
        for address, counts in self.address_tx_count.items():
            total_tx = counts['sent'] + counts['received']
            if total_tx >= threshold:
                high_frequency[address] = {
                    'sent': counts['sent'],
                    'received': counts['received'],
                    'total': total_tx,
                    'volume_btc': counts['volume_btc']
                }
        
        # Save to CSV
        hf_df = pd.DataFrame.from_dict(high_frequency, orient='index')
        hf_df.index.name = 'address'
        hf_df.sort_values('total', ascending=False, inplace=True)
        
        output_file = os.path.join(self.output_dir, 'high_frequency_addresses.csv')
        hf_df.to_csv(output_file)
        
        logger.info(f"Identified {len(high_frequency)} high-frequency addresses")
        logger.info(f"Results saved to {output_file}")
        
        return high_frequency
    
    def analyze_exchange_flows(self):
        """Analyze transaction flows through exchanges."""
        # Convert exchange transaction counts to DataFrame
        exchange_df = pd.DataFrame.from_dict(self.exchange_tx_count, orient='index')
        exchange_df['net_flow'] = exchange_df['inflow'] - exchange_df['outflow']
        exchange_df['flow_ratio'] = exchange_df['inflow'] / exchange_df['outflow']
        exchange_df.sort_values('volume_btc', ascending=False, inplace=True)
        
        # Save to CSV
        output_file = os.path.join(self.output_dir, 'exchange_flows.csv')
        exchange_df.to_csv(output_file)
        
        logger.info(f"Analyzed flows for {len(self.exchange_tx_count)} exchanges")
        logger.info(f"Results saved to {output_file}")
        
        return exchange_df
    
    def generate_exchange_flow_charts(self):
        """Generate charts for exchange flows."""
        exchange_df = self.analyze_exchange_flows()
        
        if exchange_df.empty:
            logger.warning("No exchange data available for charts")
            return
            
        # Create directory for charts
        charts_dir = os.path.join(self.output_dir, 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # Top exchanges by volume
        plt.figure(figsize=(12, 8))
        top_n = min(10, len(exchange_df))
        
        # Pie chart of top exchanges by volume
        plt.figure(figsize=(10, 10))
        top_exchanges = exchange_df.head(top_n)
        plt.pie(
            top_exchanges['volume_btc'],
            labels=top_exchanges.index,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90
        )
        plt.axis('equal')
        plt.title(f'Top {top_n} Exchanges by Transaction Volume (BTC)')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'top_exchanges_volume_pie.png'))
        
        # Inflow vs Outflow bar chart
        plt.figure(figsize=(12, 8))
        top_exchanges = exchange_df.head(top_n)
        
        x = np.arange(len(top_exchanges))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width/2, top_exchanges['inflow'], width, label='Inflow')
        ax.bar(x + width/2, top_exchanges['outflow'], width, label='Outflow')
        
        ax.set_ylabel('Number of Transactions')
        ax.set_title('Exchange Inflow vs Outflow')
        ax.set_xticks(x)
        ax.set_xticklabels(top_exchanges.index, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'exchange_inflow_outflow.png'))
        
        logger.info(f"Exchange flow charts saved to {charts_dir}")
    
    def analyze_transaction_patterns(self):
        """Analyze temporal patterns in transactions."""
        # This would require timestamp data from transactions
        # Placeholder for now
        pass

def main():
    """Run transaction frequency analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze transaction frequencies')
    parser.add_argument('--data-dir', required=True, help='Directory with processed transaction data')
    parser.add_argument('--output-dir', required=True, help='Directory to save analysis results')
    parser.add_argument('--exchange-list', help='File with exchange addresses')
    args = parser.parse_args()
    
    # Load exchange addresses if provided
    exchange_addresses = {}
    if args.exchange_list:
        exchange_addresses = load_address_labels(args.exchange_list)
    
    # Run analysis
    analyzer = TransactionFrequencyAnalyzer(
        args.data_dir,
        args.output_dir,
        exchange_addresses
    )
    
    analyzer.load_transaction_data()
    analyzer.identify_high_frequency_addresses()
    analyzer.analyze_exchange_flows()
    analyzer.generate_exchange_flow_charts()
    
    logger.info("Analysis complete")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
