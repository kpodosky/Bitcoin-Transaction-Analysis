#!/usr/bin/env python3
"""
Interactive dashboard for Bitcoin transaction analysis

Provides an interactive web dashboard for exploring Bitcoin transaction data,
exchange flows, and network visualizations.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_dashboard(data_dir, results_dir):
    """
    Create and configure the Dash application.
    
    Args:
        data_dir: Directory containing processed data
        results_dir: Directory containing analysis results
    
    Returns:
        Configured Dash application
    """
    # Load data
    exchange_flows = pd.read_csv(os.path.join(results_dir, 'exchange_flows.csv'))
    exchange_flows.rename(columns={'Unnamed: 0': 'exchange'}, inplace=True)
    
    high_freq_addresses = pd.read_csv(os.path.join(results_dir, 'high_frequency_addresses.csv'))
    high_freq_addresses.rename(columns={'Unnamed: 0': 'address'}, inplace=True)
    
    # Create Dash application
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Define layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Bitcoin Transaction Analysis Dashboard", className="text-center my-4"), width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H2("Exchange Transaction Flows", className="mt-4"),
                html.P("Analysis of transaction flows through major cryptocurrency exchanges."),
                
                # Exchange selection dropdown
                html.Div([
                    html.Label("Select Exchanges:"),
                    dcc.Dropdown(
                        id='exchange-dropdown',
                        options=[{'label': ex, 'value': ex} for ex in exchange_flows['exchange'].unique()],
                        value=exchange_flows['exchange'].head(5).tolist(),
                        multi=True
                    )
                ], className="mb-4"),
                
                # Exchange pie chart
                dcc.Graph(id='exchange-pie-chart'),
                
                # Exchange inflow/outflow bar chart
                dcc.Graph(id='exchange-flow-chart')
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H2("High-Frequency Addresses", className="mt-4"),
                html.P("Addresses with high transaction volumes."),
                
                # Address filter
                html.Div([
                    html.Label("Minimum Transaction Count:"),
                    dcc.Slider(
                        id='transaction-count-slider',
                        min=min(high_freq_addresses['total']),
                        max=max(high_freq_addresses['total']),
                        step=10,
                        value=min(high_freq_addresses['total']) + 50,
                        marks={i: str(i) for i in range(
                            int(min(high_freq_addresses['total'])),
                            int(max(high_freq_addresses['total'])),
                            int((max(high_freq_addresses['total']) - min(high_freq_addresses['total'])) / 10)
                        )}
                    )
                ], className="mb-4"),
                
                # Transaction scatter plot
                dcc.Graph(id='transaction-scatter'),
                
                # Top addresses table
                html.Div(id='top-addresses-table')
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H2("Network Visualizations", className="mt-4"),
                html.P("Interactive Bitcoin transaction network visualizations."),
                
                # Network visualization links
                html.Div([
                    html.P("View interactive network visualizations:"),
                    html.Ul([
                        html.Li(html.A("Full Network Graph", href="/network_graphs/full_network.html", target="_blank")),
                        html.Li(html.A("Top Hub Networks", href="/network_graphs/", target="_blank"))
                    ])
                ], className="mb-4"),
                
                # Network preview image
                html.Img(
                    src='/network_graphs/static_network.png',
                    alt="Network Visualization Preview",
                    className="img-fluid border rounded"
                )
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col(html.Footer([
                html.Hr(),
                html.P("Bitcoin Transaction Analysis Dashboard", className="text-center"),
                html.P("Data current as of analysis date", className="text-center text-muted")
            ]), width=12)
        ])
    ], fluid=True)
    
    # Define callbacks
    @app.callback(
        Output('exchange-pie-chart', 'figure'),
        Input('exchange-dropdown', 'value')
    )
    def update_exchange_pie_chart(selected_exchanges):
        """Update the exchange volume pie chart based on selection."""
        if not selected_exchanges:
            # Default to top 5 if nothing selected
            filtered_df = exchange_flows.head(5)
        else:
            filtered_df = exchange_flows[exchange_flows['exchange'].isin(selected_exchanges)]
        
        fig = px.pie(
            filtered_df,
            values='volume_btc',
            names='exchange',
            title="Transaction Volume Distribution by Exchange"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend_title="Exchange",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        return fig
    
    @app.callback(
        Output('exchange-flow-chart', 'figure'),
        Input('exchange-dropdown', 'value')
    )
    def update_exchange_flow_chart(selected_exchanges):
        """Update the exchange inflow/outflow chart based on selection."""
        if not selected_exchanges:
            # Default to top 5 if nothing selected
            filtered_df = exchange_flows.head(5)
        else:
            filtered_df = exchange_flows[exchange_flows['exchange'].isin(selected_exchanges)]
        
        # Sort by total transaction count
        filtered_df = filtered_df.sort_values(by=['inflow', 'outflow'], ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=filtered_df['exchange'],
            y=filtered_df['inflow'],
            name='Inflow',
            marker_color='#4CAF50'
        ))
        
        fig.add_trace(go.Bar(
            x=filtered_df['exchange'],
            y=filtered_df['outflow'],
            name='Outflow',
            marker_color='#FF5722'
        ))
        
        fig.update_layout(
            title="Exchange Inflow vs Outflow",
            xaxis_title="Exchange",
            yaxis_title="Number of Transactions",
            barmode='group',
            legend_title="Transaction Type",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        return fig
    
    @app.callback(
        Output('transaction-scatter', 'figure'),
        Input('transaction-count-slider', 'value')
    )
    def update_transaction_scatter(min_txs):
        """Update the transaction scatter plot based on minimum transaction count."""
        filtered_df = high_freq_addresses[high_freq_addresses['total'] >= min_txs]
        
        fig = px.scatter(
            filtered_df,
            x='sent',
            y='received',
            size='volume_btc',
            hover_name='address',
            color='volume_btc',
            color_continuous_scale=px.colors.sequential.Blues,
            size_max=50,
            title=f"Transaction Patterns (Addresses with {min_txs}+ transactions)"
        )
        
        fig.update_layout(
            xaxis_title="Sent Transactions",
            yaxis_title="Received Transactions",
            coloraxis_colorbar_title="Volume (BTC)",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        # Add reference line for equal sent/received
        max_val = max(filtered_df['sent'].max(), filtered_df['received'].max())
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                line=dict(color='rgba(0,0,0,0.3)', dash='dash'),
                showlegend=False
            )
        )
        
        return fig
    
    @app.callback(
        Output('top-addresses-table', 'children'),
        Input('transaction-count-slider', 'value')
    )
    def update_top_addresses_table(min_txs):
        """Update the top addresses table based on minimum transaction count."""
        filtered_df = high_freq_addresses[high_freq_addresses['total'] >= min_txs]
        
        # Sort by total transactions and take top 10
        top_addresses = filtered_df.sort_values('total', ascending=False).head(10)
        
        # Create table
        table = dbc.Table([
            html.Thead(html.Tr([
                html.Th("Address"),
                html.Th("Total Txs"),
                html.Th("Sent"),
                html.Th("Received"),
                html.Th("Volume (BTC)")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(row['address']),
                    html.Td(f"{row['total']:,}"),
                    html.Td(f"{row['sent']:,}"),
                    html.Td(f"{row['received']:,}"),
                    html.Td(f"{row['volume_btc']:,.2f}")
                ])
                for _, row in top_addresses.iterrows()
            ])
        ], striped=True, bordered=True, hover=True, responsive=True)
        
        return html.Div([
            html.H4("Top High-Frequency Addresses", className="mt-4"),
            table
        ])
    
    return app

def main():
    """Run the dashboard application."""
    parser = argparse.ArgumentParser(description='Run Bitcoin analysis dashboard')
    parser.add_argument('--data-dir', required=True, help='Directory with processed data')
    parser.add_argument('--results-dir', required=True, help='Directory with analysis results')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the dashboard on')
    parser.add_argument('--port', type=int, default=8050, help='Port to run the dashboard on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    # Create and run dashboard
    app = create_dashboard(args.data_dir, args.results_dir)
    
    # Set up static file serving for network visualizations
    app.server.static_folder = args.results_dir
    
    logger.info(f"Starting dashboard on {args.host}:{args.port}")
    app.run_server(debug=args.debug, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
