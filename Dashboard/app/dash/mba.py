import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import pandas as pd
import networkx as nx
import dash_cytoscape as cyto
from config import Config
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

def create_mba_dashboard(server):
    mba_dash = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/mba/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # Load Dataset
    df = pd.read_csv(Config.CAFE_DATA)
    df['Items'] = df['Items'].apply(lambda x: x.split(', '))
    
    # One-Hot Encoding for FP-Growth
    te = TransactionEncoder()
    te_ary = te.fit(df['Items']).transform(df['Items'])
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    # Apply FP-Growth
    frequent_itemsets = fpgrowth(df_encoded, min_support=0.003, use_colnames=True, max_len=3)

    # Generate Association Rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)

    # Convert frozensets to lists for JSON serialization
    rules["antecedents"] = rules["antecedents"].apply(lambda x: list(x))
    rules["consequents"] = rules["consequents"].apply(lambda x: list(x))

    # Convert itemsets to strings for the bar chart
    frequent_itemsets['itemsets_str'] = frequent_itemsets['itemsets'].apply(lambda x: ', '.join(list(x)))

    mba_dash.layout = dbc.Container([
        dbc.NavbarSimple(
            brand="Market Basket Analysis",
            brand_href="/dash/",
            color="dark",
            dark=True,
            className="mb-4"
        ),
        html.H1("Market Basket Analysis Dashboard"),
        
        # Frequent Itemsets Bar Chart
        dcc.Graph(
            id='bar-chart',
            figure=px.bar(frequent_itemsets.nlargest(10, 'support'), x='itemsets_str', y='support',
                          title='Top Frequent Itemsets')
        ),
        
        # Heatmap for Item Co-occurrence
        dcc.Graph(
            id='heatmap',
            figure=px.imshow(df_encoded.corr(), labels=dict(color='Correlation'),
                             title='Item Co-occurrence Heatmap')
        ),

        # Network Graph for Association Rules
        cyto.Cytoscape(
            id='network-graph',
            elements=[
                {'data': {'id': ','.join(row['antecedents']), 'label': ','.join(row['antecedents'])}} for _, row in rules.iterrows()
            ] + [
                {'data': {'id': ','.join(row['consequents']), 'label': ','.join(row['consequents'])}} for _, row in rules.iterrows()
            ] + [
                {'data': {'source': ','.join(row['antecedents']), 'target': ','.join(row['consequents'])}} for _, row in rules.iterrows()
            ],
            style={'width': '100%', 'height': '500px'},
            layout={'name': 'circle'}
        ),

        # Association Rules Table
        html.Div([
            html.H2("Association Rules"),
            dbc.Table.from_dataframe(
                rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10),
                striped=True,
                bordered=True,
                hover=True
            )
        ])
    ])    
    
    return mba_dash.server