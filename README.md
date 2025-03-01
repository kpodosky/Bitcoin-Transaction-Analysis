This project analyzes Bitcoin blockchain data to explore transaction patterns, active addresses, and exchange flows. 
The analysis includes visualizations of transaction frequencies, exchange inflows/outflows, and network visitation patterns.

Transaction frequency patterns for Bitcoin addresses
Identification of major exchanges and their transaction volumes
Visualization of inflows and outflows using pie charts
Network analysis of transaction patterns

# Bitcoin Transaction Analysis

A data analysis project exploring Bitcoin transaction patterns, exchange flows, and network visualization.

## Project Overview
This project analyzes Bitcoin blockchain data to understand transaction patterns, identify major exchanges, and visualize cryptocurrency flows across the network. The analysis focuses on transaction frequencies, exchange identification, and network visualization.

## Features
- Transaction frequency analysis by address
- Exchange inflow and outflow tracking
- Visualization with interactive charts and graphs
- Network analysis of transaction relationships
- Temporal patterns in Bitcoin transactions

## Data Sources
The project uses the following data sources:
- Bitcoin blockchain data via Bitcoin Core API or public datasets
- Known exchange address lists from public repositories
- Historical Bitcoin price data for contextual analysis

### Prerequisites
- Python 3.8+
- Bitcoin Core (optional for direct blockchain access)
- PostgreSQL or similar database for storing processed data

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/bitcoin-transaction-analysis.git
cd bitcoin-transaction-analysis

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.yml config.yml
# Edit config.yml with your settings
```

## Project Structure
bitcoin-transaction-analysis/
├── data/                      # Raw and processed data
├── notebooks/                 # Jupyter notebooks for exploration
├── scripts/                   # Data processing scripts
├── src/                       # Source code
│   ├── data/                  # Data collection and processing
│   ├── analysis/              # Analysis modules
│   ├── visualization/         # Visualization code
│   └── utils/                 # Utility functions
├── tests/                     # Unit tests
├── results/                   # Output figures and results
├── config.yml                 # Configuration file
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Usage

### Data Collection

```bash
# Fetch blockchain data
python scripts/fetch_blockchain_data.py --start-date 2023-01-01 --end-date 2023-12-31

# Identify and label exchange addresses
python scripts/identify_exchanges.py
```

### Analysis

```bash
# Run transaction frequency analysis
python scripts/analyze_transaction_frequency.py

# Generate exchange flow reports
python scripts/analyze_exchange_flows.py
```

### Visualization

```bash
# Generate visualizations
python scripts/generate_visualizations.py

# Start interactive dashboard
python scripts/run_dashboard.py
```

## Analysis Modules

### Transaction Frequency Analysis

- Identifies high-frequency addresses
- Calculates statistical metrics on transaction patterns
- Classifies addresses by activity patterns

### Exchange Flow Analysis

- Tracks major exchanges by transaction volume
- Measures inflows and outflows over time
- Identifies relationships between exchanges

### Network Visualization

- Creates network graphs of transaction relationships
- Highlights major hubs and transaction paths
- Visualizes clusters of related addresses

## Sample Results

### Exchange Transaction Volume (Jan-Dec 2023)
![Sample Exchange Volume Chart](data/images/exchange_volume_sample.png)

### Top 10 Exchanges by Transaction Volume
![Top Exchanges Pie Chart](data/images/top_exchanges_sample.png)

### Transaction Network Visualization
![Transaction Network](data/images/network_sample.png)

## Future Work

- Real-time transaction monitoring
- Machine learning for anomaly detection
- Integration with DeFi protocol analysis
- Address clustering improvements
- Whale transaction tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Blockchain.com](https://www.blockchain.com/explorer) for blockchain data
- [BitcoinWhosWho](https://www.bitcoinwhoswho.com/) for address tagging information
- [Graphsense](https://graphsense.info/) for address clustering techniques
