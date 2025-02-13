import pandas as pd
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon if you haven't already
nltk.download('vader_lexicon')

# Sample dataset
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
# Ensure both lists have the same length
print("Length of 'Product Name' list:", len(data["Product Name"]))
print("Length of 'Review Text' list:", len(data["Review Text"]))

# Create DataFrame
df = pd.DataFrame(data)

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

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

# Count sentiments for each product
sentiment_counts = df.groupby(['Product Name', 'Sentiment']).size().unstack(fill_value=0)

# Set up subplots for multiple pie charts
num_products = len(sentiment_counts.index)
rows = (num_products // 3) + (num_products % 3 > 0)  # Arranges in a grid (3 per row)
cols = 3  # Maximum 3 pie charts in a row

fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5))
axes = axes.flatten()  # Flatten to easily iterate

# Define correct color mapping
colors = {'Positive': 'green', 'Negative': 'red', 'Neutral': 'gray'}

# Function to format autopct (hide 0.0%)
def autopct_format(pct):
    return f'{pct:.1f}%' if pct > 0 else ''

# Generate pie charts for each product
for i, product in enumerate(sentiment_counts.index):
    product_data = sentiment_counts.loc[product]
    
    # Filter out sentiments with 0 count
    product_data = product_data[product_data > 0]

    product_data.plot(
        kind='pie',
        autopct=autopct_format,  # Hide 0.0%
        colors=[colors[label] for label in product_data.index],
        ax=axes[i],
        legend=False
    )
    axes[i].set_title(f'{product} Sentiment')
    axes[i].set_ylabel('')  # Hide y-label for better visualization

# Hide any extra subplots (if products are less than subplot slots)
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()
