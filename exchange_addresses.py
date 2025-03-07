import json
from pathlib import Path
from typing import Dict, List, Optional

# Exchange address patterns
EXCHANGE_PATTERNS = {
    'binance': [r'^bnb1', r'^0x'],
    'coinbase': [r'^0x', r'^1'],
    'kraken': [r'^0x', r'^bc1q'],
    'bitfinex': [r'^0x', r'^1'],
    'huobi': [r'^ht', r'^0x']
}

# Known exchange addresses
KNOWN_ADDRESSES = {
    "binance": [
        "1FzWLkAahHooV3kzTgyx6qsswXJ6sCXkSR",
        "3FHNBLobJnbCTFTVakh5TXmEneyf5PT61B",
        "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
    ],
    "coinbase": [
        "1QHa9R7mj4gGZFBHGNQgFpwEYXF5C4YVzP",
        "3AgF6KovmZYyqtews1gUxZC4JPz74JTUE9",
        "bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6",
    ],
    "kraken": [
        "3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE",
        "3H5JTt42K7RmZtromfTSefcMEFMMe18pMD",
        "bc1qx9t2l3pyny2spqpqlye8svce70nppwtaxwdrp4",
    ],
    "huobi": [
        "1HuobiWYmRvjXkU3QftXEMwfEqeYAXYLik",
        "3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6",
        "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
    ]
}

# Dictionary of known exchange addresses
EXCHANGE_ADDRESSES = {
    'binance': [
        '1FzWLkAahHooV3kzTgyx6qsswXJ6sCXkSR',  # Binance Hot Wallet
        'bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97',  # Binance Cold
        'bc1q9d8u7hf4k7vp9jg586w8ff838z4z7rcyzktw7t'  # Binance Reserve
    ],
    'coinbase': [
        '1QHa9R7mj4gGZFBHGNQgFpwEYXF5C4YVzP',  # Coinbase Hot
        'bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6',  # Coinbase Cold
        'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'  # Coinbase Reserve
    ],
    'kraken': [
        '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Kraken Hot
        '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # Kraken Cold
    ],
    'bitfinex': [
        '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitfinex Hot
        'bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97'  # Bitfinex Cold
    ],
    'huobi': [
        'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',  # Huobi Hot
        '1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ'  # Huobi Cold
    ]
}

def load_exchange_addresses() -> Dict[str, List[str]]:
    """Load exchange addresses from file or return default addresses"""
    try:
        with open('exchange_addresses.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return KNOWN_ADDRESSES

def save_exchange_addresses(addresses: Dict[str, List[str]]) -> None:
    """Save exchange addresses to file"""
    with open('exchange_addresses.json', 'w') as f:
        json.dump(addresses, f, indent=4)

def get_exchange_addresses() -> Dict[str, str]:
    """
    Returns a combined dictionary of all known exchange addresses
    
    Returns:
        Dict[str, str]: Dictionary with addresses as keys and exchange names as values
    """
    combined_addresses = EXCHANGE_ADDRESSES.copy()
    
    # Add addresses from KNOWN_ADDRESSES to the combined dictionary
    for exchange, addresses in KNOWN_ADDRESSES.items():
        for address in addresses:
            combined_addresses[address] = exchange.capitalize()
    
    return combined_addresses

def is_exchange_address(address: str) -> tuple[bool, Optional[str]]:
    """
    Check if a given address belongs to a known exchange
    
    Args:
        address (str): The Bitcoin address to check
        
    Returns:
        tuple: (bool, str) - (is_exchange, exchange_name)
    """
    # Check against known addresses
    for exchange, addresses in EXCHANGE_ADDRESSES.items():
        if address in addresses:
            return True, exchange

    # Check against patterns
    for exchange, patterns in EXCHANGE_PATTERNS.items():
        for pattern in patterns:
            if address.startswith(pattern):
                return True, exchange

    return False, None

def add_exchange_address(exchange: str, address: str) -> bool:
    """Add a new exchange address"""
    addresses = load_exchange_addresses()
    if exchange.lower() not in addresses:
        addresses[exchange.lower()] = []
    
    if address not in addresses[exchange.lower()]:
        addresses[exchange.lower()].append(address)
        save_exchange_addresses(addresses)
        return True
    return False

def remove_exchange_address(exchange: str, address: str) -> bool:
    """Remove an exchange address"""
    addresses = load_exchange_addresses()
    if exchange.lower() in addresses and address in addresses[exchange.lower()]:
        addresses[exchange.lower()].remove(address)
        save_exchange_addresses(addresses)
        return True
    return False

def identify_wallet_type(address):
    """
    Identify the type of wallet based on the address
    
    Args:
        address (str): The Bitcoin address to check
        
    Returns:
        str: The type of wallet ('exchange' or 'unknown')
    """
    is_exchange, _ = is_exchange_address(address)
    return 'exchange' if is_exchange else 'unknown'
