import asyncio
import logging
from typing import Dict, List
from datetime import datetime

try:
    from web3 import Web3
    from solana.rpc.api import Client as SolanaClient
except ImportError as e:
    print("Error: Required packages are not installed.")
    print("Please run: pip install -r requirements.txt")
    raise SystemExit(1)

from keys import ETHERSCAN_API_KEY, SOLANA_RPC_URL

class UnifiedCryptoTracker:
    def __init__(self):
        self.logger = self._setup_logging()
        self.min_amounts = {
            'BTC': 500,      # 500 BTC
            'ETH': 1000,     # 1000 ETH
            'SOL': 1000,     # 1000 SOL
            'USDT': 100000,  # $100k
            'USDC': 100000,  # $100k
            'LTC': 5000,     # 5000 LTC
            'DOGE': 1000000, # 1M DOGE
            'XRP': 100000,   # 100k XRP
            'ADA': 100000,   # 100k ADA
            'DOT': 10000     # 10k DOT
        }
        
        # Initialize connections
        self.web3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{ETHERSCAN_API_KEY}'))
        self.sol_client = SolanaClient(SOLANA_RPC_URL)
        
        # Initialize individual trackers
        self.btc_tracker = BitcoinWhaleTracker(min_btc=self.min_amounts['BTC'])
        self.stablecoin_tracker = StablecoinTracker(min_amount=self.min_amounts['USDT'])
        
        # Updated Ethereum addresses
        self.eth_addresses = {
            'binance': '0x28C6c06298d514Db089934071355E5743bf21d60',
            'coinbase': '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
            'kraken': '0x2910543af39aba0cd09dbb2d50200b3e800a63d2',
            'ftx': '0xC098B2a3Aa256D2140208C3de6543aAEf5cd3A94',
            'crypto.com': '0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3',
            'thunderpick': '0x8894E0a0c962CB723c1976a4421c95949bE2D4E3'
        }

        # Updated Solana addresses
        self.sol_addresses = {
            'binance': '8FU95xFJhUUkyyCLU13HSzDLs7oC4QZwXTyA3UBZfTeP',
            'ftx': '9WzDXwBYqKRQYtgYdqMJxgwTVjodGYj3LsnUvVa7GYNo',
            'coinbase': '73tF8uN3BwVzUzwETv59WNAafuEBct2zTgYbYXLggYUA',
            'crypto.com': 'E4DLNkFhmbkJ5VvHT8JhWK8WALPyLDnLPsp3FVpp1Vwu',
            'kraken': 'BVxyYhm498L79r4HMQ9sxZ5bi41DmJmeWZ7oGRZwRrPt'
        }

        # Updated Litecoin addresses
        self.ltc_addresses = {
            'binance': 'LQv2reoCwYTGHXskxHEJ7iE2rvNWYpSUDh',
            'coinbase': 'LgmaZ3btzJR3QkMfHaYuoRVH9PXnzXupAQ',
            'kraken': 'LTC5LeZwm4MmXRcXZXrYbgnhqBWZCyFj5h',
            'crypto.com': 'LYgDcZ3oQ3Rc7RzN6Vj9UJB9QEqhVHYqAo',
            'ftx': 'M8T1B2Z4H7W9V6J5N3Q8R1Y5X7P4K2C9G6'
        }

        # Updated Dogecoin addresses
        self.doge_addresses = {
            'binance': 'DDTtqnuZ5kfRT5qh2c7sNtqrJmV3iXYdGG',
            'coinbase': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L',
            'kraken': 'D8RKAHE7Pj4pK4UwcM4AqWpuZsGqoVL6YY',
            'crypto.com': 'DRSqEwcnJX3GZWH9Twtwk8D5ewqdJzi13k',
            'thunderpick': 'DJ2dNvsyQZbeDGZXpH3PJVGJVkKpfHUxKv'
        }

        # Add Polkadot addresses
        self.dot_addresses = {
            'binance': '13NXiLZJ7B1XLpShSR9PccYE9ehrWW7W5UBH8gP8ESgACAHR',
            'kraken': '12Y8b4C9r9AD7x9KFS6Q8QTxGNvxRwPcqp8VFUnvzrZ9WPFJ',
            'crypto.com': '15cervtYqgEDNb7r2PJAJwZVqkQtQpWw5PJxsKtiF7hKUxJf',
            'ftx': '14ShUZUYUR35RBZW6uVVt1zXDxmSQddkeDdXf1JkMA6P8Lbe',
            'coinbase': '16EMKdxvchSxBgVcGwpxoSBJGC8fgXoTSjSoPFHqQVcJwHBN'
        }

        # Updated XRP addresses
        self.xrp_addresses = {
            'binance': 'rLHzPsX6oXkzU2qL12kHCH8G8cnZv1rBJh',
            'coinbase': 'rUocf1ixKzTuEe34kmVhRvGqNCofY1NJzV',
            'kraken': 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh',
            'crypto.com': 'rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh',
            'ftx': 'rJb5KsHsDHF1YS5B5DU6QCkH5NsPaKQTcy'
        }

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('unified_crypto_tracker.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('UnifiedCryptoTracker')

    async def track_eth_transactions(self):
        """Track large ETH transactions"""
        async for block in self.web3.eth.get_block('latest', full_transactions=True):
            for tx in block.transactions:
                eth_value = self.web3.from_wei(tx.value, 'ether')
                if eth_value >= self.min_amounts['ETH']:
                    self._print_eth_transaction({
                        'from': tx['from'],
                        'to': tx['to'],
                        'value': eth_value,
                        'hash': tx['hash'].hex(),
                        'timestamp': datetime.now().isoformat()
                    })

    async def track_solana_transactions(self):
        """Track large Solana transactions"""
        async for signature in self.sol_client.get_signatures():
            tx = self.sol_client.get_transaction(signature)
            if tx and tx.transaction.message.instructions:
                sol_amount = float(tx.transaction.message.instructions[0].data) / 1e9
                if sol_amount >= self.min_amounts['SOL']:
                    self._print_sol_transaction({
                        'from': tx.transaction.message.account_keys[0],
                        'to': tx.transaction.message.account_keys[1],
                        'value': sol_amount,
                        'signature': signature,
                        'timestamp': datetime.now().isoformat()
                    })

    async def track_ltc_transactions(self):
        """Track large Litecoin transactions"""
        try:
            # Implementation using litecoinlib or similar
            async for tx in self._get_ltc_transactions():
                if float(tx.amount) >= self.min_amounts['LTC']:
                    self._print_ltc_transaction({
                        'from': tx.sender,
                        'to': tx.receiver,
                        'value': tx.amount,
                        'hash': tx.hash,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            self.logger.error(f"Error tracking LTC: {e}")

    async def track_doge_transactions(self):
        """Track large Dogecoin transactions"""
        try:
            # Implementation using dogecoin-python or similar
            async for tx in self._get_doge_transactions():
                if float(tx.amount) >= self.min_amounts['DOGE']:
                    self._print_doge_transaction({
                        'from': tx.sender,
                        'to': tx.receiver,
                        'value': tx.amount,
                        'hash': tx.hash,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            self.logger.error(f"Error tracking DOGE: {e}")

    async def track_polkadot_transactions(self):
        """Track large Polkadot transactions"""
        try:
            async for tx in self._get_dot_transactions():
                if float(tx.amount) >= self.min_amounts['DOT']:
                    self._print_dot_transaction({
                        'from': tx.sender,
                        'to': tx.receiver,
                        'value': tx.amount,
                        'hash': tx.hash,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            self.logger.error(f"Error tracking DOT: {e}")

    def _print_eth_transaction(self, tx: Dict):
        """Print Ethereum transaction with emojis"""
        message = (
            f"\n💎 LARGE ETH TRANSFER 💎\n"
            f"Amount: {tx['value']:.2f} ETH 💰\n"
            f"From: {self._get_eth_label(tx['from'])} ➡️\n"
            f"To: {self._get_eth_label(tx['to'])} 🏦\n"
            f"Hash: {tx['hash']}\n"
            f"Time: {tx['timestamp']} ⏰\n"
        )
        print(f"\033[94m{message}\033[0m")
        print("💠" * 40)

    def _print_sol_transaction(self, tx: Dict):
        """Print Solana transaction with emojis"""
        message = (
            f"\n🌟 LARGE SOL TRANSFER 🌟\n"
            f"Amount: {tx['value']:.2f} SOL 💰\n"
            f"From: {self._get_sol_label(tx['from'])} ➡️\n"
            f"To: {self._get_sol_label(tx['to'])} 🏦\n"
            f"Signature: {tx['signature'][:16]}...\n"
            f"Time: {tx['timestamp']} ⏰\n"
        )
        print(f"\033[96m{message}\033[0m")
        print("💠" * 40)

    def _print_ltc_transaction(self, tx: Dict):
        """Print Litecoin transaction with emojis"""
        message = (
            f"\n⚡ LARGE LTC TRANSFER ⚡\n"
            f"Amount: {tx['value']:.2f} LTC 💰\n"
            f"From: {self._get_ltc_label(tx['from'])} ➡️\n"
            f"To: {self._get_ltc_label(tx['to'])} 🏦\n"
            f"Hash: {tx['hash']}\n"
            f"Time: {tx['timestamp']} ⏰\n"
        )
        print(f"\033[95m{message}\033[0m")
        print("💠" * 40)

    def _print_doge_transaction(self, tx: Dict):
        """Print Dogecoin transaction with emojis"""
        message = (
            f"\n🐕 LARGE DOGE TRANSFER 🐕\n"
            f"Amount: {tx['value']:.2f} DOGE 💰\n"
            f"From: {self._get_doge_label(tx['from'])} ➡️\n"
            f"To: {self._get_doge_label(tx['to'])} 🏦\n"
            f"Hash: {tx['hash']}\n"
            f"Time: {tx['timestamp']} ⏰\n"
        )
        print(f"\033[93m{message}\033[0m")
        print("💠" * 40)

    def _print_dot_transaction(self, tx: Dict):
        """Print Polkadot transaction with emojis"""
        message = (
            f"\n🔴 LARGE DOT TRANSFER 🔴\n"
            f"Amount: {tx['value']:.2f} DOT 💰\n"
            f"From: {self._get_dot_label(tx['from'])} ➡️\n"
            f"To: {self._get_dot_label(tx['to'])} 🏦\n"
            f"Hash: {tx['hash']}\n"
            f"Time: {tx['timestamp']} ⏰\n"
        )
        print(f"\033[95m{message}\033[0m")
        print("💠" * 40)

    def _get_eth_label(self, address: str) -> str:
        """Get label for Ethereum address"""
        for name, addr in self.eth_addresses.items():
            if address.lower() == addr.lower():
                return f"{name.upper()}"
        return f"{address[:6]}...{address[-4:]}"

    def _get_sol_label(self, address: str) -> str:
        """Get label for Solana address"""
        for name, addr in self.sol_addresses.items():
            if address == addr:
                return f"{name.upper()}"
        return f"{address[:6]}...{address[-4:]}"

    def _get_ltc_label(self, address: str) -> str:
        """Get label for Litecoin address"""
        for name, addr in self.ltc_addresses.items():
            if address == addr:
                return f"{name.upper()}"
        return f"{address[:6]}...{address[-4:]}"

    def _get_doge_label(self, address: str) -> str:
        """Get label for Dogecoin address"""
        for name, addr in self.doge_addresses.items():
            if address == addr:
                return f"{name.upper()}"
        return f"{address[:6]}...{address[-4:]}"

    def _get_dot_label(self, address: str) -> str:
        """Get label for Polkadot address"""
        for name, addr in self.dot_addresses.items():
            if address == addr:
                return f"{name.upper()}"
        return f"{address[:8]}...{address[-6:]}"

    async def start_tracking(self):
        """Start tracking all cryptocurrencies"""
        self.logger.info("Starting unified crypto tracker...")
        self.logger.info(f"Minimum amounts: {self.min_amounts}")
        
        tasks = [
            self.track_eth_transactions(),
            self.track_solana_transactions(),
            self.track_ltc_transactions(),
            self.track_doge_transactions(),
            self.track_polkadot_transactions(),  # Add DOT tracking
            self.btc_tracker.track_whale_transactions(),
            self.stablecoin_tracker.start_tracking()
        ]
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    tracker = UnifiedCryptoTracker()
    try:
        asyncio.run(tracker.start_tracking())
    except KeyboardInterrupt:
        print("\nStopping unified crypto tracker...")
