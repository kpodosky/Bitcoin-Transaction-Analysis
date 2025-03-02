Here's how the complete Bitcoin Transaction Analysis system would run, step-by-step:

##System Setup

1.Clone repository & install dependencies

git clone https://github.com/yourusername/bitcoin-transaction-analysis.git
cd bitcoin-transaction-analysis
pip install -r requirements.txt

2. Create directory structure
mkdir -p data/{raw,processed} results network_graphs

##Data Collection
3. Fetch blockchain data (using Bitcoin Core RPC)

python data-collection-script.py \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --output-dir data/raw \
  --use-rpc

This would:
    Connect to Bitcoin node via RPC
    Fetch blocks and transactions for 2023
    Save raw data to data/raw/ as JSON files


#Data Processing

3. In transaction-analysis.py

analyzer = TransactionFrequencyAnalyzer(
    data_dir="data/raw",
    output_dir="data/processed",
    exchange_addresses="exchange_addresses.json"
)
analyzer.load_transaction_data()
analyzer.identify_high_frequency_addresses(threshold=100)
analyzer.analyze_exchange_flows()

Note: Outputs:
    high_frequency_addresses.csv
    exchange_flows.csv
    Processed Parquet files in data/processed/        

## Exchange Flow Analysis
        
4.In exchange-analyzer(2).py
        
analyzer = ExchangeFlowAnalyzer(
    data_dir="data/processed",
    output_dir="results/exchange_analysis",
    exchange_addresses_file="exchange_addresses.json"
)
analyzer.analyze_transactions()
analyzer.generate_visualizations()
      Generates:

Note : CSV reports (exchange_flow_summary.csv, daily_exchange_flows.csv)
Visualizations in results/exchange_analysis/charts/  

## Network Visualization  
        
5. python visualization-code.py \
        
  --data-dir data/processed \
  --output-dir network_graphs \
  --max-transactions 50000      

Note: Creates:
    Interactive network HTML files
    Hub subgraphs
    Static network PNG preview

##  Dashboard Launch   
        
6. python dashboard-code.py \
        
  --data-dir data/processed \
  --results-dir results \
  --host 0.0.0.0 \
  --port 8050
        
note: 
    Accessible at http://localhost:8050 with:
    Interactive exchange flow charts
    High-frequency address analysis
    Network visualization links


## Workflow Diagram
7. graph TD
        
    A[Data Collection] --> B[Raw Data]
    B --> C[Data Processing]
    C --> D[Processed Data]
    D --> E[Transaction Analysis]
    D --> F[Exchange Analysis]
    E --> G[High Frequency Addresses]
    F --> H[Exchange Flow Reports]
    D --> I[Network Visualization]
    G --> J[Dashboard]
    H --> J
    I --> J        
        
        

        
