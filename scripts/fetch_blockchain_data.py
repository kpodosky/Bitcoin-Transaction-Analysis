#!/usr/bin/env python3
"""
Bitcoin blockchain data fetcher

This script fetches Bitcoin transaction data for analysis using either
Bitcoin Core RPC or public blockchain APIs.
"""

import os
import sys
import argparse
import datetime
import logging
import json
import time
from pathlib import Path

import requests
import pandas as pd
from tqdm import tqdm
import yaml

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils.config import load_config
from src.data.blockchain_api import BlockchainAPI
from src.data.bitcoin_rpc import BitcoinRPC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch Bitcoin blockchain data')
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=str, required=True,
                        help='End date in YYYY-MM-DD format')
    parser.add_argument('--output-dir', type=str, default='data/raw',
                        help='Directory to save downloaded data')
    parser.add_argument('--use-rpc', action='store_true',
                        help='Use Bitcoin Core RPC instead of public API')
    parser.add_argument('--config', type=str, default='config.yml',
                        help='Path to configuration file')
    return parser.parse_args()

def ensure_directory(directory):
    """Ensure output directory exists."""
    os.makedirs(directory, exist_ok=True)
    return directory

def fetch_blocks_by_date_range(api, start_date, end_date, output_dir):
    """Fetch block data for a date range."""
    start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get block heights for date range
    logger.info(f"Getting block heights for date range: {start_date} to {end_date}")
    block_heights = api.get_block_heights_by_date_range(start_datetime, end_datetime)
    
    logger.info(f"Found {len(block_heights)} blocks in date range")
    
    # Fetch each block and its transactions
    for height in tqdm(block_heights, desc="Fetching blocks"):
        block_data = api.get_block_by_height(height)
        if block_data:
            # Save block data
            block_file = os.path.join(output_dir, f"block_{height}.json")
            with open(block_file, 'w') as f:
                json.dump(block_data, f, indent=2)
            
            # Fetch and save transaction data for this block
            fetch_transactions_for_block(api, block_data, output_dir)
            
            # Be nice to the API
            time.sleep(0.5)
        else:
            logger.warning(f"Failed to fetch block at height {height}")

def fetch_transactions_for_block(api, block_data, output_dir):
    """Fetch transaction data for a block."""
    tx_dir = os.path.join(output_dir, f"block_{block_data['height']}_txs")
    ensure_directory(tx_dir)
    
    for tx_id in tqdm(block_data['tx'], 
                    desc=f"Fetching txs for block {block_data['height']}", 
                    leave=False):
        tx_file = os.path.join(tx_dir, f"{tx_id}.json")
        
        # Skip if already downloaded
        if os.path.exists(tx_file):
            continue
            
        tx_data = api.get_transaction(tx_id)
        if tx_data:
            with open(tx_file, 'w') as f:
                json.dump(tx_data, f, indent=2)
            
            # Be nice to the API
            time.sleep(0.1)
        else:
            logger.warning(f"Failed to fetch transaction {tx_id}")

def main():
    """Main function to fetch blockchain data."""
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create output directory
    output_dir = ensure_directory(args.output_dir)
    
    # Create API client
    if args.use_rpc:
        logger.info("Using Bitcoin Core RPC")
        api = BitcoinRPC(
            config['bitcoin_rpc']['host'],
            config['bitcoin_rpc']['port'],
            config['bitcoin_rpc']['user'],
            config['bitcoin_rpc']['password']
        )
    else:
        logger.info("Using public blockchain API")
        api = BlockchainAPI(config['api']['url'], config['api']['key'])
    
    # Fetch data
    fetch_blocks_by_date_range(api, args.start_date, args.end_date, output_dir)
    
    logger.info("Data collection complete")

if __name__ == "__main__":
    main()
