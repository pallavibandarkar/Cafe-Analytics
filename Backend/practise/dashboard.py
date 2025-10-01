import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import dash_cytoscape as cyto
from prophet import Prophet
import numpy as np
from comm import create_comm
import plotly.graph_objects as go
def init_dashboard(server, csv_file):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # -------------------- Load Dataset -------------------- #
    df = pd.read_csv(csv_file)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df['Quantity'] = 1
    df['Revenue'] = df['TotalCost']

    # -------------------- Top Products -------------------- #
    top_products = df.groupby("Items")["Quantity"].sum().reset_index()
    top_products = top_products[top_products["Items"].str.lower() != "salad"]
    top_products = top_products.sort_values(by="Quantity", ascending=False).head(10)
    fig_top_products = px.bar(
        top_products,
        x="Quantity",
        y="Items",
        orientation="h",
        template='plotly_dark',
        labels={"Quantity": "Total Sold", "Items": "Product"},
        text_auto=True
    )
    fig_top_products.update_layout(yaxis=dict(categoryorder="total ascending"))

    # -------------------- Weekly Revenue -------------------- #
    weekly_revenue = df.resample("W", on="date")["Revenue"].sum().reset_index()
    fig_weekly_revenue = px.line(
        weekly_revenue,
        x="date",
        y="Revenue",
        template='plotly_dark',
        markers=True,
        labels={"date": "Week", "Revenue": "Total Revenue (₹)"},
    )

    # -------------------- Payment Method Distribution -------------------- #
    payment_counts = df["paymentMethod"].value_counts().reset_index()
    payment_counts.columns = ["paymentMethod", "Count"]
    fig_payment = px.pie(
        payment_counts,
        names="paymentMethod",
        values="Count",
        hole=0.4,
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # -------------------- Customer Segmentation -------------------- #
    customer_df = df.groupby('UserID').agg(
        total_spent=('Revenue', 'sum'),
        transactions=('TransactionID', 'count')
    ).reset_index()
    customer_df['avg_spent'] = customer_df['total_spent'] / customer_df['transactions']

    scaler = StandardScaler()
    features = scaler.fit_transform(customer_df[['total_spent', 'transactions', 'avg_spent']])
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    customer_df['Cluster'] = kmeans.fit_predict(features)
    cluster_labels = {0: 'Low Value', 1: 'Medium Value', 2: 'High Value'}
    customer_df['Cluster Label'] = customer_df['Cluster'].map(cluster_labels)

    cluster_counts = customer_df['Cluster Label'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster Label', 'count']  # Ensure correct column names

    fig_customer_segments = px.pie(
        cluster_counts,
        names='Cluster Label',  # Use the correct column name
        values='count',
        title='Customer Segmentation',
        template='plotly_dark'
    )

    fig_customer_scatter = px.scatter(
        customer_df,
        x='transactions',
        y='total_spent',
        color='Cluster Label',
        hover_data=['UserID', 'avg_spent'],
        template='plotly_dark',
        title='Customer Segmentation: Spend vs Transactions'
    )

    # -------------------- Market Basket Analysis -------------------- #
    df['Items_list'] = df['Items'].apply(lambda x: x.split(', '))
    te = TransactionEncoder()
    te_array = te.fit(df['Items_list']).transform(df['Items_list'])
    df_encoded = pd.DataFrame(te_array, columns=te.columns_)
    frequent_itemsets = fpgrowth(df_encoded, min_support=0.003, use_colnames=True, max_len=3)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
    rules["antecedents"] = rules["antecedents"].apply(lambda x: list(x))
    rules["consequents"] = rules["consequents"].apply(lambda x: list(x))
    frequent_itemsets['itemsets_str'] = frequent_itemsets['itemsets'].apply(lambda x: ', '.join(list(x)))

    fig_frequent_itemsets = px.bar(frequent_itemsets.nlargest(10, 'support'),
                                   x='itemsets_str', y='support',
                                   title='Top Frequent Itemsets', template='plotly_dark')

    cyto_elements = []
    for _, row in rules.iterrows():
        antecedents = ','.join(row['antecedents'])
        consequents = ','.join(row['consequents'])

        cyto_elements.append({'data': {'id': antecedents, 'label': antecedents}})
        cyto_elements.append({'data': {'id': consequents, 'label': consequents}})
        cyto_elements.append({'data': {'source': antecedents, 'target': consequents, 'label': f"Confidence: {row['confidence']:.2f}"}})

    # Remove duplicate nodes
    unique_nodes = []
    node_ids = set()
    for element in cyto_elements:
        if 'id' in element['data']:
            node_id = element['data']['id']
            if node_id not in node_ids:
                unique_nodes.append(element)
                node_ids.add(node_id)

    edges = [element for element in cyto_elements if 'source' in element['data']]
    cyto_elements = unique_nodes + edges


    # -------------------- Revenue Forecast -------------------- #
    """forecast_df = df.groupby("date")["Revenue"].sum().reset_index()
    forecast_df.rename(columns={"date": "ds", "Revenue": "y"}, inplace=True)
    model = Prophet()
    model.fit(forecast_df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    fig_forecast = px.line(
        forecast,
        x='ds',
        y='yhat',
        title='Revenue Forecast for Next 30 Days',
        template='plotly_dark'
    )"""
    forecast_df = df.groupby("date")["Revenue"].sum().reset_index()
    forecast_df.rename(columns={"date": "ds", "Revenue": "y"}, inplace=True)

# Train Prophet model
    model = Prophet()
    model.fit(forecast_df)

# Forecast 7 days (1 week ahead)
    future = model.make_future_dataframe(periods=7, freq="D")
    forecast = model.predict(future)

# Extract weekday names
    forecast["weekday"] = pd.to_datetime(forecast["ds"]).dt.day_name()

# Keep only next 7 days forecast
    forecast_week = forecast.tail(7)

# Line chart with weekdays on x-axis
    fig_forecast_weekdays = px.line(
    forecast_week,
    x="weekday",
    y="yhat",
    title="Revenue Forecast by Weekday",
    template="plotly_dark"
)

# Force weekday order (Mon → Sun)
    fig_forecast_weekdays.update_xaxes(
    categoryorder="array",
    categoryarray=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    title="Day of Week"
)
# Forecast next 30 days
  

# Forecast next 30 days
    future = model.make_future_dataframe(periods=12, freq="D")
    forecast = model.predict(future)

# Line chart daily forecast
    fig_forecast_daily = px.line(
    forecast,
    x="ds",
    y="yhat",
    title="Daily Revenue Forecast (Next 30 Days)",
    template="plotly_dark"
)

# Format x-axis to show daily ticks more cleanly
    fig_forecast_daily.update_xaxes(
    dtick="D1",                # one tick per day
    tickformat="%d",        # e.g., Sep 27
    title="Date"
)
    forecast_future = forecast.tail(30).copy()

# Add week number within the month
    forecast_future["week_of_month"] = (
    ((forecast_future["ds"].dt.day - 1) // 7) + 1
)

# Add a label like "Week 1", "Week 2", ...
    forecast_future["week_label"] = "Week " + forecast_future["week_of_month"].astype(str)

# Aggregate forecast by week
    weekly_forecast = forecast_future.groupby("week_label")["yhat"].sum().reset_index()

# Line chart with weeks as x-axis
    fig_forecast_weekly = px.line(
    weekly_forecast,
    x="week_label",
    y="yhat",
    title="Weekly Revenue Forecast (Next Month)",
    template="plotly_dark"
)
    
    # -------------------- Layout -------------------- #
    dash_app.layout = dbc.Container([
        dbc.NavbarSimple(
            dbc.Nav(
                dbc.Button("Back", color="secondary", href="http://localhost:5173/welcome", className="ml-auto"),
                className="ms-auto",  # push to right
                navbar=True
            ),
            brand="Cafe Analytics Dashboard",
            brand_href="/dash/",
            color="primary",
            dark=True,
            className="mb-4",
        ),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Revenue", className="card-title"),
                                            html.H2(f"₹{df['Revenue'].sum():,.2f}", className="text-success")])]), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Average Transaction", className="card-title"),
                                            html.H2(f"₹{df['Revenue'].mean():,.2f}", className="text-primary")])]), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Transactions", className="card-title"),
                                            html.H2(f"{len(df):,}", className="text-warning")])]), width=4)
        ], className="mb-4"),

        dbc.Row([html.H3("Top 10 Most Sold Products"), dbc.Col(dcc.Graph(figure=fig_top_products), width=12)]),
        dbc.Row([html.H3("Monthly Revenue Growth"), dbc.Col(dcc.Graph(figure=fig_weekly_revenue), width=12)]),
        dbc.Row([html.H3("Payment Method Distribution"), dbc.Col(dcc.Graph(figure=fig_payment), width=12)]),
        dbc.Row([html.H3("Customer Segmentation"),
                 dbc.Col(dcc.Graph(figure=fig_customer_segments), width=6),
                 dbc.Col(dcc.Graph(figure=fig_customer_scatter), width=6)]),
        
        dbc.Row([
    html.H3("Weekly Revenue Forecast (by Weekday)"),
    dbc.Col(dcc.Graph(figure=fig_forecast_weekdays), width=12)
]),
         
# dbc.Row([html.H3("Product Revenue Contribution"), dbc.Col(dcc.Graph(figure=fig_cum_revenue), width=12)]),
      #  dbc.Row([html.H3("Correlation Matrix"), dbc.Col(dcc.Graph(figure=fig_corr), width=12)]),
    ], fluid=True)

    return dash_app.server