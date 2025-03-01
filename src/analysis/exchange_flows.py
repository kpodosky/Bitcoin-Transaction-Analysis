"""
Exchange flow analysis module

Analyzes inflow and outflow of Bitcoin transactions for major exchanges.
"""

import os
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class ExchangeFlowAnalyzer:
    """Analyzes Bitcoin flows through exchanges."""
    
    def __init__(self, data_dir, output_dir, exchange_addresses_file):
        """
        Initialize the analyzer.
        
        Args:
            data_dir: Directory containing processed transaction data
            output_dir: Directory to save analysis results
            exchange_addresses_file: File containing exchange address mappings
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.exchange_addresses_file = exchange_addresses_file
        
        # Exchange data structures
        self.exchange_addresses = {}  # Map of exchange -> set of addresses
        self.exchange_inflow = defaultdict(float)   # Total inflow by exchange
        self.exchange_outflow = defaultdict(float)  # Total outflow by exchange
        self.exchange_tx_count = defaultdict(lambda: {'in': 0, 'out': 0})  # Transaction counts
        self.exchange_volume = defaultdict(float)   # Total volume by exchange
        self.daily_flows = defaultdict(lambda: defaultdict(lambda: {'in': 0, 'out': 0}))  # Daily flows
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'charts'), exist_ok=True)
        
        # Load exchange addresses
        self._load_exchange_addresses()
    
    def _load_exchange_addresses(self):
        """Load exchange address mappings from file."""
        logger.info(f"Loading exchange addresses from {self.exchange_addresses_file}")
        
        try:
            with open(self.exchange_addresses_file, 'r') as f:
                exchange_data = json.load(f)
            
            for exchange, addresses in exchange_data.items():
                self.exchange_addresses[exchange] = set(addresses)
            
            logger.info(f"Loaded addresses for {len(self.exchange_addresses)} exchanges")
            
        except Exception as e:
            logger.error(f"Error loading exchange addresses: {e}")
            raise
    
    def analyze_transactions(self, start_date=None, end_date=None):
        """
        Analyze transactions for exchange flows.
        
        Args:
            start_date: Start date for analysis (YYYY-MM-DD)
            end_date: End date for analysis (YYYY-MM-DD)
        """
        logger.info("Analyzing transactions for exchange flows")
        
        # Find transaction files
        tx_files = [os.path.join(self.data_dir, f) for f in os.listdir(self.data_dir) 
                   if f.startswith('transactions_') and f.endswith('.parquet')]
        
        # Parse date range if provided
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_dt = datetime(2000, 1, 1)  # Very early date
            
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_dt = datetime.now()  # Current date
        
        # Process each transaction file
        for tx_file in tx_files:
            # Check if file is in date range (if filename contains date)
            file_date_str = os.path.basename(tx_file).replace('transactions_', '').replace('.parquet', '')
            try:
                if '_' in file_date_str:
                    file_date = datetime.strptime(file_date_str, '%Y_%m_%d')
                    if file_date < start_dt or file_date > end_dt:
                        continue
            except ValueError:
                # If date parsing fails, include the file
                pass
            
            # Process the file
            self._process_transaction_file(tx_file)
        
        logger.info(f"Analyzed flows for {len(self.exchange_volume)} exchanges")
    
    def _process_transaction_file(self, tx_file):
        """Process a single transaction file for exchange flows."""
        logger.info(f"Processing {os.path.basename(tx_file)}")
        
        try:
            df = pd.read_parquet(tx_file)
            
            # Process each transaction
            for _, tx in df.iterrows():
                tx_date = tx.get('timestamp', datetime.now()).date()
                
                # Check each input address
                for input_addr, input_amount in tx['inputs']:
                    input_exchange = self._get_exchange_for_address(input_addr)
                    
                    if input_exchange:
                        # This is an exchange outflow
                        self.exchange_outflow[input_exchange] += input_amount
                        self.exchange_tx_count[input_exchange]['out'] += 1
                        self.exchange_volume[input_exchange] += input_amount
                        self.daily_flows[tx_date.strftime('%Y-%m-%d')][input_exchange]['out'] += input_amount
                
                # Check each output address
                for output_addr, output_amount in tx['outputs']:
                    output
