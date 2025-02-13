from flask import Flask, jsonify
from flask_cors import CORS
from sa import get_sentiment_data

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

@app.route('/sentiment-data', methods=['GET'])
def sentiment_data():
    data = get_sentiment_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
