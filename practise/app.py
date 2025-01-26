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
client = MongoClient("mongodb://localhost:27017/")
db = client['Login-Form']
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


# Step 1: Convert Sentiment to numeric ratings (1, 2, 3)
def map_sentiment_to_rating(sentiment):
    if sentiment == 'POSITIVE':
        return 3 
    elif sentiment == 'NEGATIVE':
        return 1
    else:  # NEUTRAL
        return 2

# Function to generate FP-Growth association rules
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

    min_support = 2 / len(transactions)
    frequent_itemsets = fpgrowth(df, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return pd.DataFrame()

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
    return rules

# Filter recommendations based on positive sentiment and association rules
def filter_recommendations_with_rules():
    association_rules_df = get_association_rules()

    valid_rules = []
    for _, row in association_rules_df.iterrows():
        valid_rules.append(row)

    valid_rules_df = pd.DataFrame(valid_rules)
    return valid_rules_df

# Generate a PDF menu card for the recommendations and association rules
def generate_pdf_menu(association_rules_df, start_index=0, batch_size=20):
    end_index = start_index + batch_size
    batch_rules = association_rules_df.iloc[start_index:end_index]

    # If the batch is empty, return an empty PDF
    if batch_rules.empty:
        return None, start_index

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 10)
    y_position = 750  # Start position for text

    # Add association rules to the PDF
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_position, "Association Rules:")
    y_position -= 20
    c.setFont("Helvetica", 10)

    for _, row in batch_rules.iterrows():
        if y_position < 100:
            c.showPage()
            c.setFont("Helvetica-Bold", 12)
            y_position = 750
            c.drawString(100, y_position, "Association Rules (Cont'd):")
            y_position -= 20
            c.setFont("Helvetica", 10)

        c.drawString(100, y_position, f"Rule: {', '.join(row['antecedents'])} -> {', '.join(row['consequents'])}")
        y_position -= 15
        c.drawString(120, y_position, f"Confidence: {row['confidence']:.2f}")
        y_position -= 20

    c.save()
    buffer.seek(0)
    return buffer, end_index
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
@app.route('/recommend', methods=['POST'])
def recommend():
    global reviews_df, transaction_df
    reviews_df = refresh_dataframe(reviews_collection)  # Refresh reviews collection
    transaction_df = refresh_dataframe(transactions_collection)
    
    data = request.get_json()
    user_id = int(data['user_id'])
    session_index = int(data.get('session_index') or 0)  # Default to 0 if not provided

    # Generate association rules
    valid_rules_df = get_association_rules()
    
    # Generate PDF for the current batch of association rules
    pdf_buffer, new_index = generate_pdf_menu(valid_rules_df, session_index)

    # Return PDF and updated session index
    response = send_file(pdf_buffer, as_attachment=True, download_name="filtered_recommendations.pdf", mimetype="application/pdf")
      # Set the new session index in response header
    return response


@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    # List of products
    products = [
        # Beverages
        "Espresso", "Red Eye", "Black Eye", "Americano", "Long Black", "Macchiato", "Long Macchiato", "Cortado", "Breve", "Cappuccino", 
        "Flat White", "Cafe Latte", "Iced Mocha", "Vienna", "Affogato", "Iced Coffee", "Hot Velvet Coffee", "Lemon Green Coffee", "Filter Coffee", 
        "Vanilla Latte", "Vanilla Cappuccino", "Turmeric Ginger Cappuccino", "Gourmet Belgian Hot Chocolate", "Iced Cappuccino", "Iced Latte", 
        "Alphonso Mango Frappe", "Crunchy Frappe", "Dark Frappe", "Gourmet Belgian Cold Chocolate", "Hazelnut Brownie Cake Shake", "Red Velvet Cake Shake", 
        "Lemon Cake Shake", "Cheesecake Shake", "Chocolate Fantasy Cake Shake", "Tropical Iceberg", "Vegan Shake", "Watermelon Mojito", "Peach Iced Tea", 
        "Classic Lemonade", "Watermelon Granita", "Iced Tea Latte", "Elaichi Tea", "Ginger Tea", "Masala Tea", "Hot Tea Latte", "Green Tea", "Herbal Tea", 
        "Earl Grey Orange Tea",

        # Pastries
        "Croissant", "Muffin", "Bagel", "Danish", "Scone", "Brioche", "Baguette", "Cocoa Fantasy Pastry", "Pineapple Delight Pastry", 
        "Crackling Brownie Pastry", "Flavoured Ice Cream",

        # Snacks
        "Donut", "Cookie", "Brownie", "Macaron", "Granola Bar", "Cutlet", "Popcorn",

        # Meals
        "Sandwich", "Panini", "Pasta", "Pizza", "Salad", "Soup", "Quiche", "Burrito", "Tacos",

        # Desserts
        "Cake", "Pudding", "Eclair", "Cupcake", "Mousse"
    ]
    
    # Sentiment analyzer initialization
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    
    global reviews_df, transaction_df
    reviews_df = refresh_dataframe(reviews_collection)  # Refresh reviews collection
    transaction_df = refresh_dataframe(transactions_collection)
    
    if request.is_json:
        data = request.get_json()  # Parse JSON data
        user_id = data.get('user_id')
        product = data.get('product')
        review = data.get('review')
    else:
        return "Invalid request format. JSON expected.", 400

    if not all([user_id, product, review]):
        return jsonify({"error": "Missing one or more required fields: 'user_id', 'product', 'review'"}), 400

    # Sentiment analysis logic
    prediction = sentiment_analyzer(review)
    sentiment_score = prediction[0]['label']
    sentiment_confidence = prediction[0]['score']
    sentiment_score=int(sentiment_score[0])
    if sentiment_score == 5:  # Very Positive
      sentiment = 'POSITIVE'
    elif sentiment_score == 1:  # Very Negative
      sentiment = 'NEGATIVE'
    elif sentiment_score == 2 or sentiment_score == 3:  # Neutral (score 2 or 3)
      sentiment = 'NEUTRAL'
    else:
      sentiment = 'POSITIVE'
    
    # Assuming map_sentiment_to_rating is defined elsewhere
    rating = map_sentiment_to_rating(sentiment)
    
    # Store the result in the reviews collection
    reviews_collection.insert_one({
        'UserID': user_id,
        'Product': product,
        'Review': review,
        'Sentiment': sentiment,
        'Ratings': rating
    })

    return jsonify({"result": f"Sentiment: {sentiment} for Product: {product}"})



# Flask route to predict the rating for a specific product

if __name__ == "__main__":
    app.run(debug=True)
