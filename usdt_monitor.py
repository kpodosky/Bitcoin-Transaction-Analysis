import requests
import time
import logging
from datetime import datetime
from collections import defaultdict
from keys import YOUR_ETHERSCAN_API_KEY

class USDTWhaleTracker:
    def __init__(self, min_usdt=2000):
        self.base_url = "https://api.etherscan.io/api"
        self.min_usdt = min_usdt
        self.last_block = None
        self.processed_blocks = set()
        self.api_key = YOUR_ETHERSCAN_API_KEY
        
        # Only ETH stablecoins
        self.stablecoin_contracts = {
            'usdt_ethereum': '0xdac17f958d2ee523a2206206994597c13d831ec7',  # Ethereum USDT
            'usdc_ethereum': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',  # Ethereum USDC
        }

        # Known addresses database with additional addresses
        self.known_addresses = {
            'binance': {
                'type': 'exchange',
                'addresses': [
                    '0xF977814e90dA44bFA03b6295A0616a897441aceC',  # Binance Hot Wallet
                    '0x28C6c06298d514Db089934071355E5743bf21d60',  # Binance Cold Wallet
                    '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',  # Binance Main
                    '0xD551234Ae421e3BCBA99A0Da6d736074f22192FF'   # Binance 4
                ]
            },
            'huobi': {
                'type': 'exchange',
                'addresses': [
                    '0xab5c66752a9e8167967685f1450532fb96d5d24f',  # Huobi 1
                    '0x6748F50f686bfbcA6Fe8ad62b22228b87F31ff2b',  # Huobi 2
                    '0xfdb16996831753d5331ff813c29a93c76834a0ad'   # Huobi Hot Wallet
                ]
            },
            'okx': {
                'type': 'exchange',
                'addresses': [
                    '0x6cc5f688a315f3dc28a7781717a9a798a59fda7b',  # OKX Main
                    '0x236f9f97e0e62388479bf9e5ba4889e46b0273c3',  # OKX Hot Wallet
                    '0xa7efae728d2936e78bda97dc267687568dd593f3'   # OKX Treasury
                ]
            },
            'kucoin': {
                'type': 'exchange',
                'addresses': [
                    '0x2B5634C42055806a59e9107ED44D43c426E58258',  # KuCoin 1
                    '0x689C56AEf474Df92D44A1B70850f808488F9769C',  # KuCoin 2
                    '0xa1d8d972560c2f8144af871db508f0b0b10a3fbf'   # KuCoin Hot
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    '0xf89d7b9c864f589bbF53a82105107622B35EaA40',  # ByBit Main
                    '0x0639556F03714A74a5fEEaF5736a4A64FF70D206'   # ByBit Hot
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    '0x876EabF441B2EE5B5b0554Fd502a8E0600950cFa',  # Bitfinex 1
                    '0xdcd0272462140d0a3ced6c4bf970c7641f08cd2c'   # Bitfinex Hot
                ]
            },
            'defi_protocols': {
                'type': 'defi',
                'addresses': [
                    '0x5041ed759Dd4aFc3a72b8192C143F72f4724081A',  # Aave Treasury
                    '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # MakerDAO PSM
                    '0x0000000000085d4780B73119b644AE5ecd22b376'   # TrueUSD Treasury
                ]
            },
            'market_makers': {
                'type': 'trading',
                'addresses': [
                    '0x101848D5C5bBca18E6b4431eEdF6B95E9ADF82FA',  # Wintermute
                    '0x8E23eE67D1332ad560396262C48fF272b4E23oslovakia',  # Jump Trading
                    '0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2'   # Alameda Research
                ]
            },
            'coinbase': {
                'type': 'exchange',
                'addresses': [
                    '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',  # Coinbase USDT
                    '0x503828976D22510aad0201ac7EC88293211D23Da',  # Coinbase Hot
                ]
            },
            'ftx_bankruptcy': {
                'type': 'bankruptcy',
                'addresses': [
                    '0xc61b9bb3a7a0767e3179713f3a5c7a9aedce193c',
                    '0xc8262788745f27d5a159b89908c45d0a8bf550b1'
                ]
            },
            'circle': {
                'type': 'stablecoin_issuer',
                'addresses': [
                    '0x55FE002aefF02F77364de339a1292923A15844B8',
                    '0x3755BE6b06B6aB767AaE6eB8144AeBF936768e74'
                ]
            },
            'htx': {
                'type': 'exchange',
                'addresses': [
                    '0xeEE28d484628d41A82d01e21d12E2E78D69920da',  # HTX Hot Wallet USDT
                    '0x5C985E89DDe482eFE97ea9f1950aD149Eb73829B',  # HTX Treasury USDT
                    '0x46705dfff24256421A05D056c29E81Bdc09723B8',  # HTX Bridge
                    '0xab5C66752a9E8167967685F1450532Fb96d5D24f'   # HTX Main
                ]
            },
            'aave': {
                'type': 'defi',
                'addresses': [
                    '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',  # Aave V2 Protocol
                    '0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c',  # Aave Collector V2
                    '0x25F2226B597E8F9514B3F68F00f494cF4f286491',  # Aave Treasury
                    '0xE3d9988F676457123C5fD01297605eفdd0Cba1ae'   # Aave Governance
                ]
            },
            'gemini': {
                'type': 'exchange',
                'addresses': [
                    '0x5f65f7b609678448494De4C87521CdF6cEf1e932',  # Gemini Hot Wallet
                    '0x61edcdf5bb737adffe5043706e7c5bb1f1a56eea',  # Gemini Cold Storage
                    '0x07ee55aa48bb72dcc6e9d78256648910de513eca',  # Gemini USDT Reserve
                    '0xDEa6c3211481F034479c16eE28E3Fa48974429cC'   # Gemini Operations
                ]
            }
        }
        
        self.known_addresses.update({
            'cryptocom': {
                'type': 'exchange',
                'addresses': [
                    '0x6262998Ced04146fA42253a5C0AF90CA02dfd2A3',  # Crypto.com Main USDT
                    '0x46340b20830761efd32832A74d7169B29FEB9758',  # Crypto.com Hot Wallet
                    '0x72A53cDBBcc1b9efa39c834A540550e23463AAcB',  # Crypto.com Treasury
                    '0x7758e507850dA48cd47f4380Cb8A6Df68D475743',  # Crypto.com USDT Reserve
                    '0xA0b73E1Ff0B80914AB6fe0444E65848C4C34450b',  # CRO Token Contract
                    '0x6a4FFAafa8DD400E1fA53950448e4B06679D1548',  # Crypto.com Exchange
                    '0x5bA2C55551C348Bf85b237C41c3Bec8075435451'   # Crypto.com Staking
                ]
            },
            'circle': {
                'type': 'stablecoin_issuer',
                'addresses': [
                    '0x55FE002aefF02F77364de339a1292923A15844B8',  # Circle Ops
                    '0x0bb43b32c6216f53d60fb200e9f6c0bcd1c7df35',  # USDC Treasury
                    '0x8A45AA15B42D5BC49B91960eAB953b0EbF21cB61',  # Circle Core
                    '0x7E6f38922B59545bB5A6dc3A71039B85dEA1313A',  # Circle Bridge
                    '0x0a59649758aa4d66e25f08dd01271e891fe52199'   # Circle Wallet
                ]
            },
            'wintermute': {
                'type': 'market_maker',
                'addresses': [
                    '0x0E5069514a3Dd613350BAB01B58FD850058E5ca4',  # Wintermute Operations
                    '0x7E62B53E865C549C9F51DA4db466B26875941346',  # Wintermute Deployments
                    '0x8589427373D6D84E98730D7795D8f6f8731FDA16',  # Wintermute Trading
                    '0x4f3a120E72C76c22ae802D129F599BFDbc31cb81',  # Wintermute DeFi Ops
                    '0x00000000AE347930bD1E7B0E3D11556162438D22'   # Wintermute MM Pool
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    '0xc6cde7c39eb2f0f0095f41570af89efc2c1ea828',  # Bitfinex Hot Wallet 3
                    '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',  # Bitfinex Treasury
                    '0x876EabF441B2EE5B5b0554Fd502a8E0600950cFa',  # Bitfinex Fresh Wallet
                    '0x1151314c646Ce4E0eFD76d1aF4760aE66a9Fe30F',  # Bitfinex Cold Storage 2
                    '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'   # Bitfinex USDT Controller
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    '0x0639556F03714A74a5fEEaF5736a4A64FF70D206',  # Bybit Main Treasury
                    '0xF89D7B9c864f589bbF53a82105107622B35EaA40',  # Bybit Operations
                    '0x2E3B53F65d3E926D0E738349E8D0bB60E6036657',  # Bybit Exchange Reserve
                    '0x0Edf6cE5382F3F8bF4EF32605eE8E55a402C2aBf',  # Bybit Hot Wallet 2
                    '0x9E93Aa55B3Bc78aB653841c64Dd105D960E10aBE'   # Bybit Bridge
                ]
            },
            'aave': {
                'type': 'defi',
                'addresses': [
                    '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',  # Aave V2 Protocol
                    '0x25F2226B597E8F9514B3F68F00f494cF4f286491',  # Aave Treasury
                    '0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c',  # Aave Collector V2
                    '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',  # AAVE Token Contract
                    '0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811',  # Aave USDT Pool
                    '0xC13eac3B4F9EED480045113B7af00F7B5655Ece8'   # Aave GHO Deployer
                ]
            },
            'htx': {
                'type': 'exchange',
                'addresses': [
                    '0xEEE28d484628d41A82d01e21d12E2E78D69920da',  # HTX Main Treasury
                    '0x5C985E89DDe482eFE97ea9f1950aD149Eb73829B',  # HTX Operations
                    '0x46705dfff24256421A05D056c29E81Bdc09723B8',  # HTX Bridge
                    '0x4a8D781e52bad9ae74E4d2875b201c9A6c61c85d',  # HTX Hot Wallet 3
                    '0x89891f507550A66436C646C3dAB9d64eC526B5fF',  # HTX USDT Pool
                    '0xda572b66c7130a37d84241b3a7898363943a3723'   # HTX Staking
                ]
            },
            'blackrock': {
                'type': 'institution',
                'addresses': [
                    '0x0c92aCF5540810F53BbE0e234134Af697865c677',  # BlackRock iShares ETF
                    '0x79f3BDB1974E5e77c48728A892befA73f4888722',  # BlackRock Treasury
                    '0x1B46d839Ea800239c89fc flores',              # BlackRock USDT Pool
                    '0x847f8AaB3845d7Cf929817caE33dD1337403DF72'   # BlackRock Operations
                ]
            },
            'jpmorgan': {
                'type': 'bank',
                'addresses': [
                    '0x846c0F1F8dF353C6f006E9Dc2d93663d9740b87B',  # JPM Treasury
                    '0x7AfcF11D283A8D49995936A1687D9D4ee7960F31',  # JPM Trading
                    '0x9AAb3f75489902f3a48495025729a0AF77d4b11e',  # JPM Institutional
                    '0x8A93d247134d91e0de6f96547cB0204e5BE8e5D9'   # JPM Onyx
                ]
            },
            'goldman_sachs': {
                'type': 'bank',
                'addresses': [
                    '0x9845d4e25F99B2275B9F2EEa5a5922f4736aE31B',  # GS Digital Assets
                    '0x892CC121B51D1AF623Ce4A0A617CC7F2332c6D8C',  # GS Trading
                    '0x7Bce67697eD2858d0683c631DdE7Af823B7eea38'   # GS Treasury
                ]
            },
            'fidelity': {
                'type': 'institution',
                'addresses': [
                    '0x4A9f38BaE45De0A89B7Def42010F10312fcB2952',  # Fidelity Digital
                    '0x6982508145454Ce325dDbE47a25d4ec3d2311933',  # Fidelity Custody
                    '0x2E95A75B50033Fe47DD922b4f279605c7E1CEf0A'   # Fidelity Trading
                ]
            },
            'state_street': {
                'type': 'bank',
                'addresses': [
                    '0x3845d4E25F99B2275B9F2EEa5a5922f4736aE31B',  # State Street Digital
                    '0x1CE5621D386B2801f5600F1dBe29522805b8AC11',  # State Street Custody
                ]
            }
        })

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('usdt_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('USDTMonitor')
        self.retry_count = 3    
        self.retry_delay = 5
        self.rate_limit_delay = 0.2

    def get_latest_block(self):
        """Get latest Ethereum block with retry mechanism"""
        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    f"{self.base_url}/proxy",
                    params={
                        "module": "eth",
                        "action": "eth_blockNumber",
                        "apikey": self.api_key
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('message') == 'NOTOK':
                        if 'rate limit' in data.get('result', '').lower():
                            self.logger.warning("Rate limit hit, increasing delay")
                            time.sleep(self.rate_limit_delay * 2)
                            continue
                    current_block = int(data['result'], 16)
                    return current_block
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
        return None

    def get_transfers(self, block_number):
        """Get Ethereum stablecoin transfers"""
        transfers = []
        
        for token_name, contract in self.stablecoin_contracts.items():
            print(f"Checking {token_name}...")
            try:
                response = requests.get(
                    self.base_url,
                    params={
                        "module": "account",
                        "action": "tokentx",
                        "contractaddress": contract,
                        "startblock": str(block_number - 100),
                        "endblock": str(block_number),
                        "apikey": self.api_key,
                        "sort": "desc",
                        "page": 1,
                        "offset": 100
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == '1' and data.get('result'):
                        for tx in data['result']:
                            amount = float(tx['value']) / (10 ** 6)
                            if amount >= self.min_usdt:
                                token_type = 'USDT' if 'usdt' in token_name else 'USDC'
                                transfers.append({
                                    'token': token_type,
                                    'chain': 'ethereum',
                                    'hash': tx['hash'],
                                    'from': tx['from'],
                                    'to': tx['to'],
                                    'amount': amount,
                                    'timestamp': int(tx['timeStamp'])
                                })
                                print(f"Found ETH {token_type} transfer: ${amount:,.2f}")
            except Exception as e:
                print(f"Error getting Ethereum transfers: {str(e)}")
                self.logger.error(f"Error getting Ethereum transfers: {str(e)}")

        return transfers

    def identify_address(self, address):
        """Identify address from known addresses"""
        for entity, info in self.known_addresses.items():
            if address.lower() in [addr.lower() for addr in info['addresses']]:
                return {'name': entity, 'type': info['type']}
        return None

    def format_transfer_message(self, transfer):
        """Format transfer message with small font institutional names"""
        # Determine number of alert emojis based on amount
        alert_count = min(3, max(1, int(transfer['amount'] / 10000000)))
        alerts = "🚨" * alert_count
        
        # Get entity names
        from_entity = self.identify_address(transfer['from'])
        to_entity = self.identify_address(transfer['to'])
        
        # Format entity names - use small caps for institutions
        def format_entity_name(entity):
            if not entity:
                return "Unknown"
            name = entity['name'].title()
            if entity['type'] in ['institution', 'bank']:
                # Use small caps unicode for institutional names
                return ''.join(chr(ord('ᴀ') + (ord(c.lower()) - ord('a'))) if c.isalpha() else c for c in name)
            return name
        
        from_name = format_entity_name(from_entity)
        to_name = format_entity_name(to_entity)
        
        # Add special handling for Crypto.com transfers
        if from_entity and from_entity['name'] == 'cryptocom':
            alerts += "🔵"  # Add blue dot for Crypto.com source
        if to_entity and to_entity['name'] == 'cryptocom':
            alerts += "🔵"  # Add blue dot for Crypto.com destination
        
        # Format message with token type
        message = (
            f"{alerts} {transfer['chain'].upper()} {transfer['token']} Transfer:\n"
            f"${transfer['amount']:,.2f} {transfer['token']} from "
            f"#{from_name} to #{to_name}\n"
            f"Hash: {transfer['hash'][:8]}..."
        )
        return message

    def monitor_transfers(self):
        """Monitor Ethereum transfers"""
        print("Starting Ethereum monitoring...")
        self.logger.info(f"Starting ETH monitoring (min: ${self.min_usdt:,.2f})...")
        print(f"🚀 ETH Whale Alert Monitor Started - Minimum Amount: ${self.min_usdt:,.2f}")
        
        last_check_time = 0
        check_interval = 5
        
        while True:
            try:
                current_time = time.time()
                if current_time - last_check_time < check_interval:
                    time.sleep(1)
                    continue
                
                current_block = self.get_latest_block()
                if current_block:
                    transfers = self.get_transfers(current_block)
                    
                    if transfers:
                        print(f"\nFound {len(transfers)} transfers")
                        for transfer in transfers:
                            message = self.format_transfer_message(transfer)
                            print(message)
                            print("-" * 80)
                    
                last_check_time = current_time
                
            except Exception as e:
                print(f"Monitor error: {str(e)}")
                self.logger.error(f"Monitor error: {str(e)}")
                time.sleep(self.retry_delay)

if __name__ == "__main__":
    try:
        tracker = USDTWhaleTracker(min_usdt=2000)
        tracker.monitor_transfers()
    except KeyboardInterrupt:
        print("\n👋 Shutting down ETH monitor...")
        exit(0)
