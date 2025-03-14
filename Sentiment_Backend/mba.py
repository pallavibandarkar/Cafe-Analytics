from flask import Flask, jsonify
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to access backend

# Sample Transaction Data (Replace with your actual dataset)
data = {
    "Transaction": [1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5],
    "Item": ["Milk", "Bread", "Butter", "Milk", "Diaper", "Bread", "Butter", "Diaper", "Milk", "Butter", "Bread", "Butter", "Diaper"]
}

df = pd.DataFrame(data)

# Convert to basket format
basket = df.pivot_table(index="Transaction", columns="Item", aggfunc=lambda x: 1, fill_value=0)

# Apply Apriori Algorithm
frequent_itemsets = apriori(basket.astype(bool), min_support=0.3, use_colnames=True)

# Extract Association Rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

# Convert antecedents & consequents to list
rules["antecedents"] = rules["antecedents"].apply(lambda x: list(x))
rules["consequents"] = rules["consequents"].apply(lambda x: list(x))

@app.route('/mba', methods=['GET'])
def get_mba_rules():
    filtered_rules = rules[rules["confidence"] >= 0.67]  # ✅ Keep only confidence ≥ 75%
    return jsonify(filtered_rules[["antecedents", "consequents", "support", "confidence", "lift"]].to_dict(orient="records"))


if __name__ == '__main__':
    app.run(debug=True)
