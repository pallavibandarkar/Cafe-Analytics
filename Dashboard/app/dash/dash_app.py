import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from config import Config


def init_dashboard(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]  
    )

    # Load the dataset
    df = pd.read_csv(Config.CAFE_DATA)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
  # Convert to datetime

    df["Date"]=df["date"]
    df["Quantity"]=len(df["TransactionID"])
    df["Revenue"] = df["TotalCost"]
    print(df["paymentMethod"].unique())

    # Aggregate counts for each payment method
    payment_counts = df["paymentMethod"].value_counts().reset_index()
    payment_counts.columns = ["paymentMethod", "Count"]

    # Group by product and sum the quantity sold
    top_products = df.groupby("Items")["Quantity"].sum().reset_index()
    top_products = top_products[top_products["Items"].str.lower() != "Salad"]

    # Sort in descending order and take the top 10
    top_products = top_products.sort_values(by="Quantity", ascending=False).head(10)
    
    # Create a bar chart
    fig = px.bar(
    top_products, 
    x="Quantity", 
    y="Items",  
    orientation="h",  
    #title="Top 10 Most Sold Products", 
    template='plotly_dark', 
    labels={"Quantity": "Total Sold", "Product Name": "Product"},
    text_auto=True
)

    # Reverse the order to show highest at the top
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))

    # Group by week (start of the week) and sum revenue
    weekly_revenue = df.resample("W", on="date")["Revenue"].sum().reset_index()
    monthly_revenue = df.resample("ME", on="date")["Revenue"].sum().reset_index()


    fig_weekly = px.line(
    weekly_revenue, 
    x="date", 
    y="Revenue", 
    #title="Weekly Revenue Trend",
    template='plotly_dark',
    labels={"Date": "Week", "Revenue": "Total Revenue (₹)"},
    markers=True
    )

    fig_payment = px.pie(
    payment_counts, 
    names="paymentMethod", 
    values="Count", 
    #title="Payment Method Distribution",
    template='plotly_dark',  
    hole=0.4,  # Creates a donut-style chart
    color_discrete_sequence=px.colors.qualitative.Set3  # Color palette
    )
    
    #Layout
    dash_app.layout = dbc.Container([
        dbc.NavbarSimple(
            brand="Cafe Analytics Dashboard",
            brand_href="/dash/",
            color="primary",
            dark=True,
            className="mb-4",
           
        ),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Total Revenue", className="card-title"),
                    html.H2(f"₹{df['TotalCost'].sum():,.2f}", className="text-success")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Average Transaction", className="card-title"),
                    html.H2(f"₹{df['TotalCost'].mean():,.2f}", className="text-primary")
                ])
            ]), width=4),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Total Transactions", className="card-title"),
                    html.H2(f"{len(df):,}", className="text-warning")
                ])
            ]), width=4)
        ], className="mb-4"),
        
        dbc.Row([
            html.H2("Top 10 most sold products"),
            dbc.Col(dcc.Graph(id='bar-chart', figure=fig), width=12),
            #dbc.Col(dcc.Graph(id='daily-revenue', figure=generate_daily_revenue_fig()), width=12),
        ]),

        html.Div(children=[  
        html.H3("Weekly Revenue Growth"),  
        dcc.Graph(figure=fig_weekly), 

        html.Div(children=[  
        html.H3("Payment Method Distribution"),  
        dcc.Graph(figure=fig_payment),
    ])   
    ])
    ], fluid=True)

    return dash_app.server
