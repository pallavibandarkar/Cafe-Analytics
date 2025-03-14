import pandas as pd
import random
import torch
from transformers import pipeline
from mlxtend.frequent_patterns import apriori, association_rules
import json

# Load BERT-based Sentiment Analysis Model
sentiment_pipeline = pipeline("sentiment-analysis")

# Sample products for transactions
products = ["Coffee", "Tea", "Cake", "Sandwich", "Bagel", "Pizza", "Pasta", "Muffin", "Juice", "Smoothie"]

# Set random seed for reproducibility
random.seed(42)

# Generate sample transaction data (20 entries)
transactions = []
for _ in range(20):
    num_items = random.randint(1, 3)  # Each transaction has 1 to 3 items
    items = random.sample(products, num_items)
    transactions.append(", ".join(items))

# Create transactions DataFrame
transactions_df = pd.DataFrame({"Items": transactions})

# Sample customer reviews (replace with real data from web scraping)
sample_reviews = {
    "Coffee": "The coffee was strong and full of flavor. Loved it!",
    "Tea": "Tea was too bitter for my taste.",
    "Cake": "Absolutely delicious and fresh!",
    "Sandwich": "The sandwich was okay but could be better.",
    "Bagel": "Bagel was too dry and hard.",
    "Pizza": "Tasty and loaded with toppings!",
    "Pasta": "Perfectly cooked and creamy.",
    "Muffin": "Soft and fresh, really enjoyed it.",
    "Juice": "Refreshing and not too sweet.",
    "Smoothie": "Could use more fruit flavor."
}

# Get sentiment scores using AI (BERT)
def get_sentiment_score(text):
    try:
        result = sentiment_pipeline(text)[0]  # Run sentiment analysis
        score = result["score"] if result["label"] == "POSITIVE" else -result["score"]
        return score  # Sentiment score (-1 to +1)
    except Exception as e:
        print(f"Error analyzing sentiment for text: '{text}'. Error: {e}")
        return 0  # Default score in case of error

# Apply AI-based sentiment analysis
sentiment_df = pd.DataFrame([(product, get_sentiment_score(review)) for product, review in sample_reviews.items()],
                            columns=["Product", "Sentiment_Score"])

# Preprocess transaction data
def preprocess_transactions(df):
    df['Items'] = df['Items'].apply(lambda x: x.split(', '))
    items = sorted(set(item for sublist in df['Items'] for item in sublist))
    df_expanded = pd.DataFrame([{item: (item in trans) for item in items} for trans in df['Items']])
    return df_expanded, items

df_expanded, item_list = preprocess_transactions(transactions_df)

# Market Basket Analysis using Apriori
frequent_itemsets = apriori(df_expanded, min_support=0.01, use_colnames=True)

if frequent_itemsets.empty:
    print("No frequent itemsets found. Try lowering min_support further.")
    recommendations = {}
else:
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=0.5)
    if rules.empty:
        print("No association rules generated. Try adjusting parameters.")
        recommendations = {}
    else:
        # Recommendation System
        def recommend_items(score_threshold=4):
            recommendations = {}
            for purchased_item in item_list:
                associated_items = rules[rules['antecedents'].apply(lambda x: purchased_item in list(x))]
                if not associated_items.empty:
                    associated_items = associated_items[['consequents', 'lift']]
                    associated_items['consequents'] = associated_items['consequents'].apply(lambda x: list(x))
                    associated_items = associated_items.explode('consequents')

                    # Merge with AI-based sentiment scores
                    recommended = associated_items.merge(sentiment_df, left_on='consequents', right_on='Product', how='left')
                    recommended['score'] = recommended['lift'] + recommended['Sentiment_Score']  # Combined score

                    # Filter based on score threshold
                    recommended = recommended[recommended['score'] >= score_threshold]

                    if not recommended.empty:
                        recommended = recommended[['consequents', 'score']].sort_values(by='score', ascending=False)
                        recommendations[purchased_item] = recommended.set_index('consequents')['score'].to_dict()

            return recommendations
        
        # Generate recommendations using AI-enhanced analysis
        recommendations = recommend_items()

# Print recommendations (Can be returned as JSON for website integration)
print("Recommendations:")
print(recommendations)

recommendations_json = json.dumps(recommendations, indent=4)

# Print the JSON output
print("********************* JSON OUTPUT **********************")
print(recommendations_json)