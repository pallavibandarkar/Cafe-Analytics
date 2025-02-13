import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
file_path = './cafe_transaction_dataset.xlsx' 
df = pd.read_excel(file_path) 
#df = pd.read_csv(file_path, encoding='latin1')

# Step 1: Ensure products column is a list of items
df['products'] = df['products'].str.split(',')

# Step 2: One-hot encoding of transactions
unique_products = set(item for sublist in df['products'] for item in sublist)
encoded_data = {product: df['products'].apply(lambda x: product in x) for product in unique_products}
df_encoded = pd.DataFrame(encoded_data)

# Step 3: Apply the Apriori algorithm
frequent_itemsets = apriori(df_encoded, min_support=0.03, use_colnames=True)

# Step 4: Generate association rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Step 5: Visualize results (Support vs Confidence)
plt.figure(figsize=(10, 6))
sns.scatterplot(x='support', y='confidence', size='lift', hue='lift', data=rules)
plt.title('Support vs Confidence of Rules')
plt.savefig('./support_vs_confidence.png')  

# Step 6: Visualize top 10 association rules by lift
top_rules = rules.sort_values(by='lift', ascending=False).head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x='lift', y='antecedents', data=top_rules)
plt.title('Top 10 Association Rules by Lift')
plt.savefig('./top_10_rules_by_lift.png')  

# Step 7: Display combinations of products with support and confidence
rules['product_combination'] = rules['antecedents'].astype(str) + ' -> ' + rules['consequents'].astype(str)

# Filter for strong rules (you can adjust these thresholds)
strong_rules = rules[(rules['support'] >= 0.01) & (rules['confidence'] >= 0.05)]

# Generate a summary of product combinations
summary_combinations = strong_rules[['product_combination', 'support', 'confidence']]

# Check if there are strong combinations found
if not summary_combinations.empty:
    # Print the summary
    print('The following combinations can be bought together to enhance customer engagement and revenue growth:')
    for index, row in summary_combinations.iterrows():
        print(f"Combination: {row['product_combination']}, Support: {row['support']:.2f}, Confidence: {row['confidence']:.2f}")
else:
    print("No strong product combinations found.")


# Save the rules as CSV
rules.to_csv('./association_rules.csv', index=False)

# Results are saved as PNG images and a CSV file with association rules.
#"/mnt/data/support_vs_confidence.png", "/mnt/data/top_10_rules_by_lift.png", "/mnt/data/association_rules.csv"
