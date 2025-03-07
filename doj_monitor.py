import requests
import json
import time
from datetime import datetime
import logging
from pathlib import Path

class DOJMonitor:
    def __init__(self):
        self.setup_logging()
        
        # DOJ and related agencies' Bitcoin addresses
        self.monitored_addresses = {
            'doj_seized': {
                'description': 'DOJ Seized Assets',
                'addresses': [
                    'bc1q5shae2q9et4k2824ts8vqu0zwwlue4glrhr0qx',  # Silk Road
                    'bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6',  # DOJ 2020
                    '1Cu2kh4M1ZXJNzjzBqoFs4Om3PFD6zQV2N'           # FTX Related
                ]
            },
            'fbi_seized': {
                'description': 'FBI Seized Wallets',
                'addresses': [
                    '1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX',  # Silk Road FBI
                    'bc1qmxjefnuy06v345v6vhwpwt05dztztmx4g3y7wp'  # Ransomware Seized
                ]
            },
            'usms_custody': {
                'description': 'US Marshals Service Custody',
                'addresses': [
                    'bc1q5q8K9C7Q9C9C9C9C9C9C9C9C9C9C9C9C9C9C9',  # USMS Holdings
                    '1MSUSq9C9C9C9C9C9C9C9C9C9C9C9C9C9C9C9C9C9'   # Auction Wallet
                ]
            }
        }
        
        self.address_history = {}
        self.load_address_history()

        # Add exchange addresses
        self.exchanges = {
            'Binance': [
                '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',
                'bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97'
            ],
            'Coinbase': [
                '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ',
                'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
            ]
        }

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('doj_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DOJMonitor')

    def load_address_history(self):
        """Load address transaction history"""
        try:
            with open('doj_address_history.json', 'r') as f:
                self.address_history = json.load(f)
        except FileNotFoundError:
            self.address_history = {}

    def save_address_history(self):
        """Save address transaction history"""
        with open('doj_address_history.json', 'w') as f:
            json.dump(self.address_history, f, indent=4)

    def check_address_balance(self, address: str) -> dict:
        """Check current balance and transactions for an address"""
        try:
            response = requests.get(
                f'https://blockchain.info/address/{address}?format=json',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'balance': data['final_balance'] / 100000000,  # Convert satoshis to BTC
                    'total_received': data['total_received'] / 100000000,
                    'total_sent': data['total_sent'] / 100000000,
                    'n_tx': data['n_tx']
                }
        except Exception as e:
            self.logger.error(f"Error checking address {address}: {e}")
        return None

    def identify_address_type(self, address: str) -> str:
        """Identify if address belongs to known exchange or is unknown"""
        for exchange, addresses in self.exchanges.items():
            if address in addresses:
                return exchange
        return "Unknown Cold Storage"

    def get_transaction_details(self, address: str, tx_hash: str) -> dict:
        """Get detailed transaction information"""
        try:
            response = requests.get(
                f'https://blockchain.info/rawtx/{tx_hash}',
                timeout=10
            )
            if response.status_code == 200:
                tx = response.json()
                
                # Calculate input and output addresses
                inputs = [inp['prev_out']['addr'] for inp in tx['inputs'] if 'prev_out' in inp]
                outputs = [out['addr'] for out in tx['out']]
                
                # Determine if address is sender or receiver
                is_sender = address in inputs
                
                # Get the other party's address
                other_addresses = outputs if is_sender else inputs
                other_address = next((addr for addr in other_addresses if addr != address), "Unknown")
                
                return {
                    'hash': tx_hash,
                    'fee': tx['fee'] / 100000000,  # Convert satoshis to BTC
                    'other_party': self.identify_address_type(other_address),
                    'other_address': other_address
                }
        except Exception as e:
            self.logger.error(f"Error getting transaction details: {e}")
            return None

    def get_btc_price(self) -> float:
        """Get current Bitcoin price in USD"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            )
            return float(response.json()['bitcoin']['usd'])
        except Exception as e:
            self.logger.error(f"Error getting BTC price: {e}")
            return 0

    def log_transaction(self, agency: str, address: str, amount: float, tx_type: str, tx_hash: str):
        """Log transaction details in btc_monitor style"""
        btc_price = self.get_btc_price()
        usd_amount = amount * btc_price if btc_price else 0
        
        tx_details = self.get_transaction_details(address, tx_hash)
        if tx_details:
            message = (
                f"\n{'=' * 50}\n"
                f"Transaction Type: {tx_type}\n"
                f"Amount: {amount:.8f} BTC (${usd_amount:,.2f})\n"
                f"Fee: {tx_details['fee']:.8f} BTC (${tx_details['fee'] * btc_price:,.2f})\n"
                f"Agency: {agency}\n"
                f"{'Sender' if tx_type == 'Funds Sent' else 'Receiver'}: {tx_details['other_party']}\n"
                f"{'To' if tx_type == 'Funds Sent' else 'From'} Address: {tx_details['other_address']}\n"
                f"Transaction Hash: {tx_details['hash']}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"{'=' * 50}"
            )
            self.logger.info(message)

    def monitor_addresses(self):
        """Main monitoring loop"""
        self.logger.info("Starting DOJ address monitoring...")
        
        while True:
            try:
                for agency, data in self.monitored_addresses.items():
                    for address in data['addresses']:
                        response = requests.get(
                            f'https://blockchain.info/address/{address}?format=json',
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            addr_data = response.json()
                            current_data = {
                                'balance': addr_data['final_balance'] / 100000000,
                                'total_received': addr_data['total_received'] / 100000000,
                                'total_sent': addr_data['total_sent'] / 100000000,
                                'n_tx': addr_data['n_tx']
                            }
                            
                            # Get latest transaction hash
                            if addr_data['txs']:
                                latest_tx = addr_data['txs'][0]['hash']
                            else:
                                latest_tx = None

                            previous_data = self.address_history.get(address, {
                                'balance': 0,
                                'total_sent': 0,
                                'total_received': 0
                            })
                            
                            if current_data['total_sent'] > previous_data['total_sent'] and latest_tx:
                                amount = current_data['total_sent'] - previous_data['total_sent']
                                self.log_transaction(data['description'], address, amount, "Funds Sent", latest_tx)
                            
                            if current_data['total_received'] > previous_data['total_received'] and latest_tx:
                                amount = current_data['total_received'] - previous_data['total_received']
                                self.log_transaction(data['description'], address, amount, "Funds Received", latest_tx)
                            
                            self.address_history[address] = current_data
                            self.save_address_history()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    monitor = DOJMonitor()
    monitor.monitor_addresses()
