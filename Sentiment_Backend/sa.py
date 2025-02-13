import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon (only required once)
nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Sample data
data = {
    "Product Name": [
        "Espresso", "Espresso", "Espresso", "Espresso", "Espresso",
        "Americano", "Americano", "Americano", "Americano", "Americano",
        "Cappuccino", "Cappuccino", "Cappuccino", "Cappuccino", "Cappuccino",
        "Mocha", "Mocha", "Mocha", "Mocha", "Mocha",
        "Cold Brew", "Cold Brew", "Cold Brew", "Cold Brew", "Cold Brew",
        "French Press", "French Press", "French Press", "French Press", "French Press",
        "Latte", "Latte", "Latte", "Latte", "Latte",
        "Decaf Coffee", "Decaf Coffee", "Decaf Coffee", "Decaf Coffee", "Decaf Coffee"
    ],
    "Review Text": [
        "This espresso is rich and full of flavor! Highly recommend.",
        "Too strong for my taste, but good quality.",
        "Best espresso I've ever had!",
        "Not what I expected, a bit bitter.",
        "Perfect for my morning routine!",
        "Too bitter for my taste. I won't be buying this again.",
        "A decent Americano, but I've had better.",
        "Love the strong flavor!",
        "Not strong enough for my liking.",
        "Great for a quick caffeine fix!",
        "A perfect balance of coffee and milk. Love it!",
        "Too milky for my taste.",
        "My favorite drink at the cafe!",
        "Good, but not the best I've had.",
        "Perfect for a cozy afternoon!",
        "The mocha was okay, but I've had better elsewhere.",
        "Delicious and sweet, just how I like it!",
        "Too sweet for my taste.",
        "A nice treat, but not something I would order regularly.",
        "Rich and chocolatey, loved it!",
        "Refreshing and smooth! Perfect for hot days.",
        "Not strong enough for my taste.",
        "Great flavor, will order again!",
        "A bit too watery for my liking.",
        "Perfect for summer afternoons!",
        "I found it too strong and not to my liking.",
        "A rich and bold flavor, just how I like it!",
        "Not worth the price, unfortunately.",
        "I love the aroma of this coffee!",
        "Too weak for my taste.",
        "Delicious and creamy! My go-to coffee.",
        "I appreciate the option for decaf, but it lacks flavor.",
        "Not bad, but I prefer regular coffee.",
        "A rich and bold flavor, just how I like it!",
        "Not worth the price, unfortunately.",
        "I love the aroma of this coffee!",
        "Too weak for my taste.",
        "Delicious and creamy! My go-to coffee.",
        "I appreciate the option for decaf, but it lacks flavor.",
        "Not bad, but I prefer regular coffee."
    ]
}
# Create DataFrame
df = pd.DataFrame(data)

# Function to get sentiment score
def get_sentiment(text):
    score = sia.polarity_scores(text)
    if score['compound'] >= 0.05:
        return 'Positive'
    elif score['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Apply sentiment analysis
df['Sentiment'] = df['Review Text'].apply(get_sentiment)

# Count sentiment occurrences for each product
sentiment_counts = df.groupby(['Product Name', 'Sentiment']).size().unstack(fill_value=0)

# Convert to dictionary format for API response
def get_sentiment_data():
    result = {}
    for product, sentiments in sentiment_counts.iterrows():
        result[product] = {
            "Positive": int(sentiments.get("Positive", 0)),  # Ensure JSON serialization
            "Negative": int(sentiments.get("Negative", 0)),
            "Neutral": int(sentiments.get("Neutral", 0)),
        }
    return result
