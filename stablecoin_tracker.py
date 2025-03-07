import requests
import time
import json
from datetime import datetime
import logging
from typing import Dict, List, Optional
from web3 import Web3
from eth_typing import HexStr
from keys import ETHERSCAN_API_KEY, TRON_API_KEY

class StablecoinTracker:
    def __init__(self, min_amount=100000):
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize tracking parameters
        self.min_amount = min_amount
        self.web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-PROJECT-ID'))
        
        # Contract addresses
        self.contracts = {
            'USDT': {
                'ETH': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                'TRX': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
                'BSC': '0x55d398326f99059fF775485246999027B3197955'
            },
            'USDC': {
                'ETH': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                'BSC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
            }
        }
        
        # Known addresses
        self.known_addresses = {
            'treasury': {
                'USDT': {
                    'ETH': '0xc6cde7c39eb2f0f0095f41570af89efc2c1ea828',
                    'TRX': 'TQjoHaG5HiiadK1usFhZqgmVqpztYsxzKk'
                },
                'USDC': {
                    'ETH': '0x55fe002aeff02f77364de339a1292923a15844b8',
                }
            },
            'exchanges': {
                'binance': ['0x28C6c06298d514Db089934071355E5743bf21d60'],
                'coinbase': ['0x71660c4005BA85c37ccec55d0C4493E66Fe775d3'],
                # Add more exchanges as needed
            }
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stablecoin_tracker.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('StablecoinTracker')

    async def track_eth_stablecoin_events(self):
        """Track USDT/USDC events on Ethereum"""
        # ABI for Transfer events
        transfer_event = self.web3.eth.contract(
            address=self.contracts['USDT']['ETH'],
            abi=[{
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": False, "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }]
        )

        def handle_event(event):
            event_data = {
                'token': 'USDT' if event.address == self.contracts['USDT']['ETH'] else 'USDC',
                'from': event.args['from'],
                'to': event.args['to'],
                'value': event.args['value'] / (10 ** 6),  # Convert from wei
                'timestamp': datetime.now().isoformat()
            }

            if event_data['from'] == '0x0000000000000000000000000000000000000000':
                self._handle_mint(event_data)
            elif event_data['to'] == '0x0000000000000000000000000000000000000000':
                self._handle_burn(event_data)
            elif event_data['value'] >= self.min_amount:
                self._handle_transfer(event_data)

        # Create filters for both USDT and USDC
        transfer_filter = transfer_event.events.Transfer.createFilter(fromBlock='latest')
        
        while True:
            try:
                for event in transfer_filter.get_new_entries():
                    handle_event(event)
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error processing ETH events: {e}")
                await asyncio.sleep(5)

    def _handle_mint(self, event_data: Dict):
        """Handle minting events"""
        self.logger.info(
            f"🌟 NEW {event_data['token']} MINTED:\n"
            f"Amount: ${event_data['value']:,.2f}\n"
            f"To: {self._get_address_label(event_data['to'])}"
        )

    def _handle_burn(self, event_data: Dict):
        """Handle burning events"""
        self.logger.info(
            f"🔥 {event_data['token']} BURNED:\n"
            f"Amount: ${event_data['value']:,.2f}\n"
            f"From: {self._get_address_label(event_data['from'])}"
        )

    def _handle_transfer(self, event_data: Dict):
        """Handle large transfers"""
        self.logger.info(
            f"💸 LARGE {event_data['token']} TRANSFER:\n"
            f"Amount: ${event_data['value']:,.2f}\n"
            f"From: {self._get_address_label(event_data['from'])}\n"
            f"To: {self._get_address_label(event_data['to'])}"
        )

    def _get_address_label(self, address: str) -> str:
        """Get label for known addresses"""
        for entity_type, addresses in self.known_addresses.items():
            if isinstance(addresses, dict):
                for token, chain_addresses in addresses.items():
                    if address in chain_addresses.values():
                        return f"{token} {entity_type}"
            else:
                for name, addr_list in addresses.items():
                    if address in addr_list:
                        return f"{name} ({entity_type})"
        return f"{address[:6]}...{address[-4:]}"

    async def start_tracking(self):
        """Start tracking all stablecoin movements"""
        self.logger.info(f"Starting stablecoin tracker (min amount: ${self.min_amount:,})")
        
        # Create tasks for different chains
        tasks = [
            self.track_eth_stablecoin_events(),
            # Add more chain tracking as needed
        ]
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import asyncio
    
    tracker = StablecoinTracker(min_amount=100000)  # Track transfers >= $100k
    
    try:
        asyncio.run(tracker.start_tracking())
    except KeyboardInterrupt:
        print("\nStopping stablecoin tracker...")
