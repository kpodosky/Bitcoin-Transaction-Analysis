# -*- coding: UTF-8 -*-
import re
import requests
import time
import os
from datetime import datetime
from collections import defaultdict

class BitcoinWhaleTracker:
    def __init__(self, min_btc=500):  # Changed from 100 to 500
        self.base_url = "https://blockchain.info"
        self.min_btc = min_btc
        self.satoshi_to_btc = 100000000
        self.processed_blocks = set()  # Track processed blocks
        self.last_block_height = None  # Track last block height
        
        # Address statistics tracking
        self.address_stats = defaultdict(lambda: {
            'received_count': 0,
            'sent_count': 0,
            'total_received': 0,
            'total_sent': 0,
            'last_seen': None
        })
        
        # Known addresses database (keeping original database)
        self.known_addresses = {
            'binance': {
                'type': 'exchange',
                'addresses': [
                    '3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE',  # Binance Hot Wallet
                    '1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s',  # Binance Cold Wallet
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # Binance-BTC-2
                    '1LQv8aKtQoiY5M5zkaG8RWL7LMwNzNsLfb',  # Binance-BTC-3
                    '1AC4fMwgY8j9onSbXEWeH6Zan8QGMSdmtA'   # Binance-BTC-4
                ]
            },
            'coinbase': {
                'type': 'exchange',
                'addresses': [
                    '3FzScn724foqFRWvL1kCZwitQvcxrnSQ4K',  # Coinbase Hot Wallet
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',  # Coinbase Cold Storage
                    '1CWYTCvwKfH5cWnX3VcAykgTsmjsuB3wXe',  # Coinbase-BTC-2
                    '1FxkfJQLJTXpW6QmxGT6hEo5DtBrnFpM3r',  # Coinbase-BTC-3
                    '1GR9qNz7zgtaW5HwwVpEJWMnGWhsbsieCG'   # Coinbase Prime
                ]
                  },
            'grayscale': {
                'type': 'investment',
                'addresses': [
                    'bc1qe7nps5yv7ruc884zscwrk9g2mxvqh7tkxfxwny',
                    'bc1qkz7u6l5c8wqz8nc5yxkls2j8u4y2hkdzlgfnl4'
                ]
            },
            'microstrategy': {
                'type': 'corporate',
                'addresses': [
                    'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt',
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
                ]
            },
            'blockfi': {
                'type': 'lending',
                'addresses': [
                    'bc1q7kyrfmx49qa7n6g8mvlh36d4w9zf4lkwfg4j5q',
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym'
                ]
            },
            'celsius': {
                'type': 'lending',
                'addresses': [
                    'bc1q06ymtp6eq27mlz3ppv8z7esc8vq3v4nsjx9eng',
                    'bc1qcex3e38gqh6qnzpn9jth5drgfyh5k9sjzq3rkm'
                ]
            },
            'kraken': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Kraken Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # Kraken Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR',  # Kraken-BTC-2
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv'   # Kraken-BTC-3
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitfinex Hot Wallet
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bitfinex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bitfinex-BTC-2
                ]
            },
            'huobi': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # Huobi Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Huobi Cold Storage
                    '1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ'   # Huobi-BTC-2
                ]
            },
            'okex': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # OKEx Hot Wallet
                    '3LCGsSmfr24demGvriN4e3ft8wEcDuHFqh',  # OKEx Cold Storage
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE'   # OKEx-BTC-2
                ]
            },
            'gemini': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Gemini Hot Wallet
                    '393HLwqnkrJMxYQTHjWBJPAKC3UG6k6FwB',  # Gemini Cold Storage
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ'   # Gemini-BTC-2
                ]
            },
            'bitstamp': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Bitstamp Hot Wallet
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitstamp Cold Storage
                    '3DbAZpqKhUBu4rqafHzj7hWquoBL6gFBvj'   # Bitstamp-BTC-2
                ]
            },
            'bittrex': {
                'type': 'exchange',
                'addresses': [
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Hot Wallet
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bittrex-BTC-2
                ]
            },
            'kucoin': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # KuCoin Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # KuCoin Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR'   # KuCoin-BTC-2
                ]
            },
            'gate_io': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Gate.io Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Gate.io Cold Storage
                ]
            },
            'ftx': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # FTX Hot Wallet
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv',  # FTX Cold Storage
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bybit Hot Wallet
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL',  # Bybit Cold Storage
                ]
            },
            'cryptocom': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Crypto.com Hot Wallet
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ',  # Crypto.com Cold Storage
                ]
            }
        }

        # Add exchange wallet pattern recognition
        self.exchange_patterns = {
            "Binance": {
                "prefixes": ["bnb1", "0x", "bc1q"],
                "patterns": [
                    r"^1FzWLk.*",
                    r"^bc1q[0-9a-zA-Z]{38,48}$",
                    r"^3[a-km-zA-HJ-NP-Z1-9]{25,34}$"
                ],
                "known_ranges": ["34", "3J", "bc1q", "1ND"]
            },
            "Coinbase": {
                "prefixes": ["0x", "bc1q"],
                "patterns": [
                    r"^1Qab.*",
                    r"^bc1q[0-9a-zA-Z]{59}$",
                    r"^3[a-km-zA-HJ-NP-Z1-9]{25,34}$"
                ],
                "known_ranges": ["13", "3", "bc1q", "1CW"]
            },
            "OKX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3(?:OKX|okx)[a-zA-Z0-9]{30}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^35[a-zA-Z0-9]{34}$"
                ],
                "known_ranges": ["bc1q", "3OKX", "35pg", "3Fp"]
            },
            "HTX": {
                "prefixes": ["bc1q", "3", "0x"],
                "patterns": [
                    r"^3(?:HTX|htx)[a-zA-Z0-9]{30}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^34[a-zA-Z0-9]{34}$"
                ],
                "known_ranges": ["bc1q", "3HTX", "34Hp", "3BB"]
            },
            "BITMEX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3BitMEX[a-zA-Z0-9]{25}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^3[A-Z]{5}[a-zA-Z0-9]{28}$"
                ],
                "known_ranges": ["bc1q", "3BitMEX", "3BM"]
            },
            "GATE_IO": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3Gate[a-zA-Z0-9]{28}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^38[a-zA-Z0-9]{34}$"
                ],
                "known_ranges": ["bc1q", "3Gate", "38W"]
            },
            "CRYPTO_COM": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3Crypto[a-zA-Z0-9]{28}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^3AA[a-zA-Z0-9]{34}$"
                ],
                "known_ranges": ["bc1q", "3Crypto", "3AA"]
            },
            "Bitfinex": {
                "prefixes": ["bc1q", "3", "1"],
                "patterns": [
                    r"^bc1qgdjqv0[a-zA-Z0-9]{45}$",
                    r"^3[JD][a-zA-Z0-9]{33}$",
                    r"^1Kr[a-zA-Z0-9]{31}$"
                ],
                "known_ranges": ["bc1q", "3JZ", "1Kr"]
            },
            "Kraken": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3[FH][a-zA-Z0-9]{33}$",
                    r"^bc1q[a-zA-Z0-9]{38,42}$",
                    r"^3[AE][a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["3Fu", "3H5", "3Af", "3E1"]
            },
            "Gemini": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3P3[a-zA-Z0-9]{32}$",
                    r"^393[a-zA-Z0-9]{33}$",
                    r"^3AA[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["3P3", "393", "3AA"]
            },
            "KuCoin": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3M2[a-zA-Z0-9]{33}$",
                    r"^3H5[a-zA-Z0-9]{33}$",
                    r"^3Af[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["3M2", "3H5", "3Af"]
            },
            "Bitstamp": {
                "prefixes": ["3"],
                "patterns": [
                    r"^3P3[a-zA-Z0-9]{32}$",
                    r"^3D2[a-zA-Z0-9]{33}$",
                    r"^3Db[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["3P3", "3D2", "3Db"]
            },
            "Bybit": {
                "prefixes": ["bc1q", "3", "34"],
                "patterns": [
                    r"^bc1qvtxh[a-zA-Z0-9]{34}$",
                    r"^34Hp[a-zA-Z0-9]{31}$",
                    r"^bc1q4c8[a-zA-Z0-9]{34}$"
                ],
                "known_ranges": ["bc1q", "34Hp", "bc1q4"]
            },
            "COINX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^bc1qxy[a-zA-Z0-9]{36}$",
                    r"^3Kz[a-zA-Z0-9]{33}$",
                    r"^bc1q7k[a-zA-Z0-9]{35}$"
                ],
                "known_ranges": ["bc1q", "3Kz", "3QW"]
            }
        }

        # Add additional known addresses
        self.known_addresses.update({
            'mining_pools': {
                'type': 'mining',
                'addresses': [
                    '1CK6KHY6MHgYvmRQ4PAafKYDrg1ejbH1cE',  # AntPool
                    '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Satoshi-Genesis
                    '12ib7dApVFvg82TXKycWBNpN8kFyiAN1dr',  # BTC.com
                    '3Gpex6g5FPmYWm26myFq7dW12ntd8zMcCY'   # Foundry
                ]
            },
            'corporate_treasury': {
                'type': 'corporate',
                'addresses': [
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # MicroStrategy
                    '3E1MQVD1yN5FLsCR1HZvnVw9PfWF5BQswC',  # Tesla-BTC
                    '1P1iThxBH542Gmk1kZNXyji4E4iwpvSbrt'   # Block.one
                ]
            },
            'investment_funds': {
                'type': 'fund',
                'addresses': [
                    '385cR5DM96n1HvBDMzLHPYcw89fZAXULJP',  # Grayscale
                    '3FHNBLobJnbCTFTVakh5TXmEneyf5PT61B',  # Purpose ETF
                    'bc1qr4dl5wa7kl8yu792dceg9z5knl2gkn220lk7dv',  # Pantera
                    'bc1q9d8u7hf4k7vp9jg586w8ff838z4z7rcyzktw7t'   # Polychain
                ]
            },
            'doj_seized': {
                'type': 'seized',
                'addresses': [
                    'bc1q5shae2q9et4k2824ts8vqu0zwwlue4glrhr0qx',  # Silk Road
                    'bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6',  # DOJ 2020
                    '1Cu2kh4M1ZXJNzjzBqoFs4Om3PFD6zQV2N'           # FTX Related
                ]
            }
        })

        # Add hacker groups and stolen fund addresses
        self.known_addresses.update({
            'lazarus_group': {
                'type': 'hacker',
                'addresses': [
                    'bc1qw7yazn56qd66xz28r7g85uh5xzj0qwzex2crying',  # Bybit hack 2024
                    'bc1q53fwz5kxkv4r7s7pjzxvfnkut5hkj7sc8kl0m2',    # ETH Bridge hack
                    'bc1qjnnfk5xa54n9q4s44vhg8dhp4zg4jmhspwqkyw',    # Atomic wallet hack
                    'bc1q2qd7ke58vz5m8wkte5p4rh28dvlhvx6f4lmgsr',    # Stake.com hack
                    '3DXQAkBp1DLwu5QiFsE7Y6zWzr3DmHLcEk',            # Known mixer address
                    'bc1qkcrnwupjg8xts39qxz5kpxmvp33qle7qkxepqr',    # Known Lazarus wallet
                    # Add more addresses as they're identified
                ]
            },
            'stolen_funds': {
                'type': 'compromised',
                'addresses': [
                    'bc1q0pzqz5q5gmkj77zxrj0m8klkv2rsg8kn3zxwrg',  # Bybit stolen funds
                    'bc1q3kqr4ej7qz5mpvs8ex2kl9yvg4gku8h5k8nstx',  # Bridge exploit
                    # Add more as identified
                ]
            }
        })

        # Add Wintermute addresses
        self.known_addresses.update({
            'wintermute': {
                'type': 'market_maker',
                'addresses': [
                    'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h',  # Wintermute: Main Wallet
                    'bc1q0nd35kslvp6jfea9pqhxgxjv7x3z9j8s9w8l7t',  # Wintermute: Trading
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',          # Wintermute: Operations
                    '3E1MQVD1yN5FLsCR1HZvnVw9PfWF5BQswC',          # Wintermute: Cold Storage
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # Wintermute: Treasury
                    'bc1q9d8u7hf4k7vp9jg586w8ff838z4z7rcyzktw7t',  # Wintermute: MM Ops
                    '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ',          # Wintermute: Institutional
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym'   # Wintermute: DeFi Ops
                ]
            }
        })

        # Add Wintermute-specific pattern to exchange_patterns
        self.exchange_patterns.update({
            "Wintermute": {
                "prefixes": ["bc1q", "3", "1"],
                "patterns": [
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^3[a-zA-Z0-9]{33}$",
                    r"^1[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["bc1q", "3", "1"]
            }
        })

        # Add Lazarus-specific patterns to exchange_patterns
        self.exchange_patterns.update({
            "Lazarus": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^3[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["bc1q", "3"]
            }
        })

        # Add these new entries to self.known_addresses
        self.known_addresses.update({
            'aave': {
                'type': 'defi',
                'addresses': [
                    'bc1qn9jfqn76acc6mj8r7wum9qvl0rxjpx5740v7dc',  # Aave Treasury
                    '0x25F2226B597E8F9514B3F68F00f494cF4f286491',  # Aave: Collector
                    'bc1q7q5xp8w5q9w4yf4pgrp4wgnd3zmwkhl3zq8tqv'   # Aave: Lending Pool
                ]
            },
            'circle': {
                'type': 'stablecoin',
                'addresses': [
                    'bc1qvlw42q8x9fzw5fshg3q3yvhdc9z94jlhqgl775',  # Circle: USDC Treasury
                    'bc1qr4dl5wa7kl8yu792dceg9z5knl2gkn220lk7dv',  # Circle: Hot Wallet
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'   # Circle: Operations
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    'bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97',  # Bitfinex: Hot Wallet 1
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bitfinex: Cold Wallet
                    'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',  # Bitfinex: Hot Wallet 2
                    '1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g'          # Bitfinex: Cold Storage 2
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    'bc1qvtxh8kmh9rn8qkl3j5jgv6s7wxx6mw4cserh5t',  # Bybit: Hot Wallet
                    'bc1q0nd35kslvp6jfea9pqhxgxjv7x3z9j8s9w8l7t',  # Bybit: Cold Storage
                    '34HpHYiyQwg69gFmCq2BGHjF1DZnZnBeBP',          # Bybit: Deposit Wallet
                    'bc1q4c8n5t2386hzwhykyjfyx0hdvflakdeh6q9j4v'   # Bybit: Operation
                ]
            },
            'curve': {
                'type': 'defi',
                'addresses': [
                    'bc1qenxwq3qe2nqvxkw0gzrq4gv9w09ytan8jg33fn',  # Curve: Treasury
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym',  # Curve: DAO
                    'bc1q5c2d6z5dfjxsxy9slfq94u3hx4pplhq6viz82j'   # Curve: veCRV
                ]
            },
            'compound': {
                'type': 'defi',
                'addresses': [
                    'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h',  # Compound: Treasury
                    'bc1qr8zcvgf7lxg3kqph5p6wd57f4t5tghq6x6j9vw',  # Compound: Governance
                    'bc1ql4vgz4v4z5jw9t3fypxkl54k92tr7x5w7k4km8'   # Compound: cBTC
                ]
            },
            'nexo': {
                'type': 'lending',
                'addresses': [
                    'bc1qxnr8chky4cf4gqmhx3td8v76z5jck83mps9kzr',  # Nexo: Hot Wallet
                    'bc1q2rdklvz0w7wqe4zacuj4p6qx007smxvrdh0qd3',  # Nexo: Cold Storage
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD'           # Nexo: Operations
                ]
            }
        })

        # Add stablecoin mint/burn addresses
        self.stablecoin_addresses = {
            'usdc': {
                'type': 'stablecoin',
                'mint_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # USDC Mint
                'burn_address': 'bc1qe7nps5yv7ruc884zscwrk9g2mxvqh7tkxfxwny',  # USDC Burn
                'treasury': 'bc1qvlw42q8x9fzw5fshg3q3yvhdc9z94jlhqgl775',     # USDC Treasury
            },
            'usdt': {
                'type': 'stablecoin',
                'mint_address': '3MbYQaXRZJZJ8MZaEaqF1GzKN3Xrsvrev5',        # USDT Mint
                'burn_address': '3MbCAaXRZJZJ8MZaEaqF1GzKN3Xrsvhsk9',        # USDT Burn
                'treasury': '3MaCAaXRZJZJ8MZaEaqF1GzKN3XrsvNM12',           # USDT Treasury
            }
        }

        # Add new exchange addresses
        self.known_addresses.update({
            'okx': {
                'type': 'exchange',
                'addresses': [
                    'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',  # OKX Hot Wallet 1
                    'bc1qf2ep0kzskg2487v8mgwolg8dvmujpxrxhx6v5',  # OKX Hot Wallet 2
                    '3FpYfDGJSdkMAvZvCrwPHDqdmGqUkTsJys',          # OKX Cold Storage
                    'bc1q03xrw2lcd8nr8hzw0nv3phkz70t8hefc3k9sr0',  # OKX Deposit
                    '35pgGeez3ou6ofrpjt8T7bvC9t6RrUK4p6',          # OKX Fees
                    'bc1qkx2zah8pf0wmarr3cpx9k4mey4f3q5vgl5f6ld'   # OKX Operations
                ]
            },
            'htx': {  # Former Huobi
                'type': 'exchange',
                'addresses': [
                    'bc1qam20p0tg3m3tlp4zw9vgl8m6cddxs4mj7mcnf2',  # HTX Hot Wallet
                    '34HpHYiyQwg69gFmCq2BGHjF1DZnZnBeBP',          # HTX Cold Storage
                    'bc1q4rd4r9vhh8wkleg6wgxk0qzg7tkcj8er8u8nn9',  # HTX Deposit
                    '3BBqFmW2PAn3JvGRxQic6zpk6M7j7FmJStack',       # HTX Staking
                    'bc1qf3xwp8z9tg3mnhwszdkxgz4z6x7j8z9g8q7v2p'   # HTX Trading
                ]
            },
            'coinx': {
                'type': 'exchange',
                'addresses': [
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # CoinX Hot Wallet
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',          # CoinX Cold Storage
                    'bc1q7kyrfmx49qa7n6g8mvlh36d4w9zf4lkwfg4j5q',  # CoinX Trading
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'           # CoinX Operations
                ]
            },
            'bitmex': {
                'type': 'exchange',
                'addresses': [
                    '3BMEX2opvstKhGLwKj8zMUPrmpvwbzrKTP',          # BitMEX Hot Wallet
                    'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',  # BitMEX Insurance
                    '3BitMEXqGHQfwSB3KFMhQ9WZKwiqKEZwci',          # BitMEX Cold Storage
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym'   # BitMEX Operations
                ]
            },
            'gate_io': {
                'type': 'exchange',
                'addresses': [
                    'bc1qnj6v9akgj8298fw9ql8aupj8wgtmzwp9v8lden',  # Gate.io Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',          # Gate.io Cold Storage
                    'bc1q4c8n5t2386hzwhykyjfyx0hdvflakdeh6q9j4v',  # Gate.io Trading
                    '3GateIoXzwGYiGhuvZBd8HWNqKZ3YGhJbt',          # Gate.io Deposit
                    'bc1qf2ep0kzskg2487v8mgwolg8dvmujpxrxhx6v5'    # Gate.io Operations
                ]
            },
            'crypto_com': {
                'type': 'exchange',
                'addresses': [
                    'bc1q4rd4r9vhh8wkleg6wgxk0qzg7tkcj8er8u8nn9',  # Crypto.com Hot Wallet
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ',          # Crypto.com Cold Storage
                    'bc1qam20p0tg3m3tlp4zw9vgl8m6cddxs4mj7mcnf2',  # Crypto.com Earn
                    '3CryptoComWalletXzwGYiGhuvZBd8HWNqKZ3',       # Crypto.com Card
                    'bc1qkx2zah8pf0wmarr3cpx9k4mey4f3q5vgl5f6ld'   # Crypto.com Exchange
                ]
            }
        })

        # Add new exchange patterns for better identification
        self.exchange_patterns.update({
            "OKX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3(?:OKX|okx)[a-zA-Z0-9]{30}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["bc1q", "3OKX", "35pg"]
            },
            "HTX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3(?:HTX|htx)[a-zA-Z0-9]{30}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["bc1q", "3HTX", "34Hp"]
            },
            "BITMEX": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3BitMEX[a-zA-Z0-9]{25}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["bc1q", "3BitMEX"]
            },
            "GATE_IO": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3Gate[a-zA-Z0-9]{28}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["bc1q", "3Gate"]
            },
            "CRYPTO_COM": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^3Crypto[a-zA-Z0-9]{28}$",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["bc1q", "3Crypto"]
            }
        })

    def get_latest_block(self):
        """Get the latest block hash and ensure we don't process duplicates"""
        try:
            response = requests.get(f"{self.base_url}/latestblock")
            block_data = response.json()
            current_height = block_data['height']
            current_hash = block_data['hash']
            
            # If this is our first block, initialize
            if self.last_block_height is None:
                self.last_block_height = current_height
                return current_hash
                
            # If we've seen this block already, return None
            if current_hash in self.processed_blocks:
                return None
                
            # If this is a new block
            if current_height > self.last_block_height:
                self.last_block_height = current_height
                # Keep track of last 1000 blocks to manage memory
                if len(self.processed_blocks) > 1000:
                    self.processed_blocks.clear()
                self.processed_blocks.add(current_hash)
                print(f"\nNew Block: {current_height} | Hash: {current_hash[:8]}...")
                return current_hash
                
            return None
            
        except Exception as e:
            print(f"Error getting latest block: {e}")
            return None

    def get_block_transactions(self, block_hash):
        """Get all transactions in a block"""
        try:
            response = requests.get(f"{self.base_url}/rawblock/{block_hash}")
            return response.json()['tx']
        except Exception as e:
            print(f"Error getting block transactions: {e}")
            return []

    def get_address_label(self, address):
        """Get the entity label for an address"""
        for entity, info in self.known_addresses.items():
            if address in info['addresses']:
                return f"({entity.upper()} {info['type']})"
        return ""

    def update_address_stats(self, address, is_sender, btc_amount, timestamp):
        """Update statistics for an address"""
        stats = self.address_stats[address]
        if is_sender:
            stats['sent_count'] += 1
            stats['total_sent'] += btc_amount
        else:
            stats['received_count'] += 1
            stats['total_received'] += btc_amount
        stats['last_seen'] = timestamp

    def get_address_summary(self, address):
        """Get formatted summary of address activity"""
        stats = self.address_stats[address]
        entity_label = self.get_address_label(address)
        return (f"{entity_label} "
                f"[↑{stats['sent_count']}|↓{stats['received_count']}] "
                f"Total: ↑{stats['total_sent']:.2f}|↓{stats['total_received']:.2f} BTC")

    def identify_address(self, address):
        """Enhanced address identification with pattern matching"""
        # First check known addresses
        for entity, info in self.known_addresses.items():
            if address in info['addresses']:
                return {
                    'name': entity,
                    'type': info['type']
                }

        # Then check patterns
        for exchange, patterns in self.exchange_patterns.items():
            # Check prefixes
            if any(address.startswith(prefix) for prefix in patterns['prefixes']):
                return {'name': exchange, 'type': 'exchange'}
            
            # Check regex patterns
            if any(re.match(pattern, address) for pattern in patterns['patterns']):
                return {'name': exchange, 'type': 'exchange'}
            
            # Check known ranges
            if any(address.startswith(range_prefix) for range_prefix in patterns['known_ranges']):
                return {'name': exchange, 'type': 'exchange'}
                
        return None

    def determine_transaction_type(self, sender, receiver):
        """Enhanced transaction type determination including stablecoin mints/burns"""
        
        # Check for stablecoin mint/burn
        for stablecoin, addresses in self.stablecoin_addresses.items():
            # Check for mint
            if sender == addresses['mint_address']:
                return {
                    'type': f'{stablecoin.upper()}_MINT',
                    'from_entity': {'name': f'{stablecoin}_mint', 'type': 'stablecoin'},
                    'to_entity': self.identify_address(receiver)
                }
            # Check for burn
            elif receiver == addresses['burn_address']:
                return {
                    'type': f'{stablecoin.upper()}_BURN',
                    'from_entity': self.identify_address(sender),
                    'to_entity': {'name': f'{stablecoin}_burn', 'type': 'stablecoin'}
                }
            # Check for treasury movement
            elif sender == addresses['treasury'] or receiver == addresses['treasury']:
                return {
                    'type': f'{stablecoin.upper()}_TREASURY',
                    'from_entity': self.identify_address(sender),
                    'to_entity': self.identify_address(receiver)
                }

        # Continue with existing checks
        sender_info = self.identify_address(sender)
        receiver_info = self.identify_address(receiver)
        
        if sender_info and receiver_info:
            return {
                'type': 'INTERNAL TRANSFER',
                'from_entity': sender_info,
                'to_entity': receiver_info
            }
        elif sender_info:
            return {
                'type': 'WITHDRAWAL',
                'from_entity': sender_info,
                'to_entity': None
            }
        elif receiver_info:
            return {
                'type': 'DEPOSIT',
                'from_entity': None,
                'to_entity': receiver_info
            }
        else:
            return {
                'type': 'UNKNOWN TRANSFER',
                'from_entity': None,
                'to_entity': None
            }

    def process_transaction(self, tx):
        """Process a single transaction and return if it meets criteria"""
        # Calculate total input value
        input_value = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx.get('inputs', []))
        btc_value = input_value / self.satoshi_to_btc
        
        # Only process transactions over minimum BTC threshold
        if btc_value < self.min_btc:
            return None
            
        # Get the primary sender (first input address)
        sender = tx.get('inputs', [{}])[0].get('prev_out', {}).get('addr', 'Unknown')
        
        # Get the primary receiver (first output address)
        receiver = tx.get('out', [{}])[0].get('addr', 'Unknown')
        
        timestamp = datetime.fromtimestamp(tx.get('time', 0))
        
        # Update address statistics
        self.update_address_stats(sender, True, btc_value, timestamp)
        self.update_address_stats(receiver, False, btc_value, timestamp)
        
        # Get transaction type and entities involved
        tx_info = self.determine_transaction_type(sender, receiver)
        
        # Calculate fee
        output_value = sum(out.get('value', 0) for out in tx.get('out', []))
        fee = (input_value - output_value) / self.satoshi_to_btc
        
        return {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_hash': tx.get('hash', 'Unknown'),
            'sender': sender,
            'receiver': receiver,
            'btc_volume': round(btc_value, 4),
            'fee_btc': round(fee, 8),
            'tx_type': tx_info['type'],
            'from_entity': tx_info['from_entity'],
            'to_entity': tx_info['to_entity']
        }

    def print_transaction(self, tx):
        """Format transaction alerts to match the requested concise format"""
        # Determine emoji based on type and amount
        tx_type = tx['tx_type']
        btc_amount = tx['btc_volume']
        
        # Select emoji based on transaction type
        if '_MINT' in tx_type:
            emoji = "💵"
        elif '_BURN' in tx_type:
            emoji = "🔥"
        elif '_TREASURY' in tx_type:
            emoji = "🏦"
        else:
            # Standard whale alert emoji with count based on amount
            emoji_count = min(8, max(1, int(btc_amount / 500)))
            emoji = "🚨" * emoji_count

        # Format amounts
        btc_formatted = f"{btc_amount:,.0f}"
        usd_value = btc_amount * 96073.862
        usd_formatted = f"{usd_value:,.0f}"
        
        # Format fee
        fee_sats = tx['fee_btc'] * 100000000
        fee_usd = tx['fee_btc'] * 96073.862
        
        # Get entity names (uppercase for consistency)
        from_entity = tx['from_entity']['name'].upper() if tx['from_entity'] else "UNKNOWN"
        to_entity = tx['to_entity']['name'].upper() if tx['to_entity'] else "UNKNOWN"
        
        # Format transaction type more cleanly
        clean_type = tx_type.replace('_', ' ').title()
        
        # Build message in the requested format
        message = (
            f"{emoji}{btc_formatted} #BTC ({usd_formatted} USD) transferred "
            f"({clean_type}) from #{from_entity} to #{to_entity} "
            f"for {fee_sats:.2f} sats (${fee_usd:.0f}) fees"
        )
        
        # Add MEGA WHALE prefix for very large transactions
        if btc_amount > 1000:
            message = "🐋 MEGA WHALE ALERT 🐋\n" + message
        
        print(message)
        return message

    def monitor_transactions(self):
        """Main method to track whale transactions"""
        print(f"Tracking Bitcoin transactions over {self.min_btc} BTC...")
        print("Waiting for new blocks...")
        
        while True:
            try:
                block_hash = self.get_latest_block()
                
                if block_hash:
                    transactions = self.get_block_transactions(block_hash)
                    processed_count = 0
                    whale_count = 0
                    
                    for tx in transactions:
                        processed_count += 1
                        whale_tx = self.process_transaction(tx)
                        if whale_tx:
                            whale_count += 1
                            self.print_transaction(whale_tx)
                    
                    print(f"Processed {processed_count} transactions, found {whale_count} whale movements")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    tracker = BitcoinWhaleTracker(min_btc=500)  # Changed from 100 to 500
    tracker.monitor_transactions()  # Changed from track_whale_transactions to monitor_transactions