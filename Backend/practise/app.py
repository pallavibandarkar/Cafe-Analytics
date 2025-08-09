from flask import Flask, render_template, request, send_file,session,jsonify
import pandas as pd
import random
from sklearn.decomposition import TruncatedSVD
from transformers import pipeline
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import secrets
from pymongo import MongoClient
from flask_cors import CORS
 #
# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 
CORS(app)
# Load reviews and cafe menu data
 # Contains "TransactionID" and "Items" columns
client = MongoClient(MongoUrl)
db = client.get_default_database()
reviews_collection = db['reviews']
transactions_collection = db['transactions']
def refresh_dataframe(collection):
    # Fetch updated data
    data = list(collection.find())
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Drop the MongoDB ObjectId field if not needed
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    
    return df

# Update the DataFrame whenever needed
transaction_df = refresh_dataframe(transactions_collection)
reviews_df = refresh_dataframe(reviews_collection)

def get_association_rules():
    transactions = []
    cursor = transactions_collection.find({}, {"Items": 1, "_id": 0})  # Select only the 'Items' field

# Iterate over the cursor and split the items as needed
    for transaction in cursor:
        items = transaction['Items'].split(", ")  # Assuming 'Items' is a string with comma-separated values
        transactions.append(items)
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_array, columns=te.columns_)

    min_support = 3/ len(transactions)
    frequent_itemsets = fpgrowth(df, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return pd.DataFrame()

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.8)
    return rules

# Filter recommendations based on positive sentiment and association rules

# Generate a PDF menu card for the recommendations and association rules
""""
def generate_pdf_menu(association_rules_df):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 10)
    y_position = 750  # Start position for text

    # Add association rules to the PDF
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, "PRODUCT COMBINATIONS")
    y_position -= 20
    c.setFont("Helvetica", 10)

    for _, row in association_rules_df.iterrows():
        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            y_position = 750
            c.drawString(100, y_position, "PRODUCT COMBINATIONS")
            y_position -= 20
            c.setFont("Helvetica", 10)

        c.drawString(100, y_position, f"{', '.join(row['antecedents'])} -> {', '.join(row['consequents'])}")
        y_position -= 15
        y_position -= 20

    c.save()
    buffer.seek(0)
    return buffer
"""
def generate_pdf_menu(association_rules_df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter

    def draw_title():
        title = "PRODUCT COMBINATIONS"
        c.setFont("Helvetica-Bold", 20)
        title_width = c.stringWidth(title, "Helvetica-Bold", 14)
        c.drawString((page_width - title_width) / 2, page_height - 50, title)
        c.setFont("Helvetica", 12)

    y_position = page_height - 100

    # Draw initial title
    draw_title()

    for _, row in association_rules_df.iterrows():
        # Check for page overflow
        if y_position < 100:
            c.showPage()
            draw_title()
            y_position = page_height - 100

        # Draw the product combination
        c.drawString(100, y_position, f"{', '.join(row['antecedents'])} -> {', '.join(row['consequents'])}")
        y_position -= 35

    c.save()
    buffer.seek(0)
    return buffer

"""
def load_csv_to_mongo():
    # Load updated_file.csv
    reviews_df = pd.read_csv('updated_file.csv')
    reviews_collection.delete_many({})  # Clear existing data
    reviews_collection.insert_many(reviews_df.to_dict('records'))

    # Load cafe.csv
    cafe_df = pd.read_csv('transactions.csv')
    transactions_collection.delete_many({})  # Clear existing data
    transactions_collection.insert_many(cafe_df.to_dict('records'))

load_csv_to_mongo()
"""

# Flask route to display the homepage and recommendations
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to generate and display recommendations as a PDF
from sklearn.ensemble import RandomForestClassifier
import numpy as np

pdf_storage = {}  # Ensure PDF storage dictionary is initialized
session_index = 0  # Initialize session index globally

coffee_items = {
            "Espresso", "Red Eye", "Black Eye","Americano", "Long Black", "Macchiato", "Long Macchiato", "Cortado", "Breve", 
            "Cappuccino", "Flat White", "Cafe Latte", "Iced Mocha", "Vienna", "Affogato", "Iced Coffee", "Hot Velvet Coffee", 
            "Lemon Green Coffee", "Filter Coffee", "Vanilla Latte", "Vanilla Cappuccino", "Turmeric Ginger Cappuccino", 
            "Iced Cappuccino", "Iced Latte"
        }        
"""
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        global reviews_df, transaction_df, session_index, pdf_storage,coffee_items

      #  reviews_df = refresh_dataframe(reviews_collection)  
      #  transaction_df = refresh_dataframe(transactions_collection)


        # Store and use session_index **before incrementing**
     

        # Define coffee items
        # Your existing coffee items

        # Get sentiment data
        sentiment_data = get_sentiment_data()
        if sentiment_data is None:
            raise ValueError("Sentiment data is empty or None.")

        # Prepare data for AI model
        products, features, labels = [], [], []

        for product, sentiments in sentiment_data.items():
            if product in coffee_items:
                products.append(product)
                features.append([sentiments["Positive"], sentiments["Negative"], sentiments["Neutral"]])
                labels.append(1 if sentiments["Positive"] > sentiments["Negative"] and sentiments["Positive"] > sentiments["Neutral"] else 0)
                #labels.append(1 if sentiments["Positive"] > sentiments["Negative"] else 0)

        if not features:
            return jsonify({"recommended_coffees": [], "association_rules": [], "ai_algorithm": "Random Forest + FP-Growth"})

        # Train AI Model (Random Forest)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, labels)

        # Predict recommendations
        predictions = model.predict(features)
        recommended_coffees = [products[i] for i in range(len(products)) if predictions[i] == 1]
       

        # Generate association rules
        valid_rules_df = get_association_rules()
        if valid_rules_df is None or valid_rules_df.empty:
            raise ValueError("No association rules found.")

        # Filter coffee items in association rules
        coffee_rules = [
            {
                "antecedents": list(set(row['antecedents'])),
                "consequents": list(set(row['consequents'])),
                "confidence": row['confidence']
            }
        for _, row in valid_rules_df.iterrows() if set(row['consequents']).issubset(coffee_items)
           
        ]

        # Generate PDF
        valid_consequents = {item for rule in coffee_rules for item in rule["consequents"]}
        filtered_recommended_coffees = [coffee for coffee in recommended_coffees if coffee in valid_consequents]
       # Increment AFTER storing PDF

        return jsonify({
            "recommended_coffees": filtered_recommended_coffees,
            "association_rules": coffee_rules,
            "ai_algorithm": "Random Forest + FP-Growth",
             # Return correct session_index
        })

    except Exception as e:
        print(f"Error in /recommend: {str(e)}")
        return jsonify({"error": str(e)}), 500
"""
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        global reviews_df, transaction_df, session_index, pdf_storage, coffee_items
      
        sentiment_data = get_sentiment_data()
        if sentiment_data is None:
            raise ValueError("Sentiment data is empty or None.")

        # Prepare data for recommendation
        products, positive_coffees = [], []

        for product, sentiments in sentiment_data.items():
            if product in coffee_items:
                products.append(product)
                if sentiments["Positive"] > sentiments["Negative"] and sentiments["Positive"] > sentiments["Neutral"]:
                    positive_coffees.append(product)

        if not positive_coffees:
            return jsonify({"recommended_coffees": [], "association_rules": [], "ai_algorithm": "FP-Growth"})

        # Generate association rules
        valid_rules_df = get_association_rules()
        if valid_rules_df is None or valid_rules_df.empty:
            raise ValueError("No association rules found.")

        # Filter coffee items in association rules
        coffee_rules = [
            {
                "antecedents": list(set(row['antecedents'])),
                "consequents": list(set(row['consequents'])),
                "confidence": row['confidence']
            }
            for _, row in valid_rules_df.iterrows() if set(row['consequents']).issubset(coffee_items)
        ]

        # Match recommended coffees with valid association rules
        valid_consequents = {item for rule in coffee_rules for item in rule["consequents"]}
        filtered_recommended_coffees = [coffee for coffee in positive_coffees if coffee in valid_consequents]

        return jsonify({
            "recommended_coffees": filtered_recommended_coffees,
            "association_rules": coffee_rules,
            "ai_algorithm": "FP-Growth"
        })

    except Exception as e:
        print(f"Error in /recommend: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    global coffee_items
    valid_rules_df = get_association_rules()
    coffee_rules = [
            {
                "antecedents": list(set(row['antecedents'])),
                "consequents": list(set(row['consequents'])),
                "confidence": row['confidence']
            }
            for _, row in valid_rules_df.iterrows() if set(row['consequents']).issubset(coffee_items)
        ]
    coffee_rules_df=pd.DataFrame(coffee_rules)
    pdf_buffer = generate_pdf_menu(coffee_rules_df)
    return send_file(pdf_buffer, as_attachment=True, download_name="filtered_recommendations.pdf", mimetype="application/pdf")

 

# Function to get sentiment score

sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
def get_sentiment(review):
    prediction = sentiment_analyzer(review)
    sentiment_score = prediction[0]['label']
    sentiment_confidence = prediction[0]['score']
    sentiment_score = int(sentiment_score[0])
    
    if sentiment_score == 5:  # Very Positive
        sentiment = 'POSITIVE'
    elif sentiment_score == 2 or sentiment_score==1:  # Very Negative
        sentiment = 'NEGATIVE'
    elif sentiment_score == 3 or sentiment_score == 4:  # Neutral (score 2 or 3)
        sentiment = 'NEUTRAL'
    else:
        sentiment ='NEGATIVE'
    return sentiment
""""
transaction_df = refresh_dataframe(transactions_collection)
reviews_df = refresh_dataframe(reviews_collection)
reviews_df['Sentiments'] = reviews_df['Review'].apply(get_sentiment)
# Count sentiment occurrences for each product
sentiment_counts = reviews_df.groupby(['Product', 'Sentiments']).size().unstack(fill_value=0)"
"""

reviews_df['Sentiments'] = reviews_df['Review'].apply(get_sentiment)

# Count sentiment occurrences for each product
sentiment_counts = reviews_df.groupby(['Product', 'Sentiments']).size().unstack(fill_value=0)
# Convert to dictionary format for API response
def get_sentiment_data():
    result = {}
    for product, sentiments in sentiment_counts.iterrows():
        result[product] = {
            "Positive": int(sentiments.get("POSITIVE", 0)),  #Ensure JSON serialization
            "Negative": int(sentiments.get("NEGATIVE", 0)),
            "Neutral": int(sentiments.get("NEUTRAL", 0)),
        }
    return result
@app.route('/sentiment-data', methods=['GET'])
def sentiment_data():
    data = get_sentiment_data()
    return jsonify(data)

# Flask route to predict the rating for a specific product

if __name__ == "__main__":
    app.run(debug=True)
