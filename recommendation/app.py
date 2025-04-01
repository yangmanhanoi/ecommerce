from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask_cors import CORS  # Allow cross-origin requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_db"]  # Your MongoDB database
books_collection = db["books"]  # Collection for books
comments_collection = db["comments"]  # Collection for comments

# Load models
cnn_model = tf.keras.models.load_model("models/cnn_sentiment_model.h5")
rnn_model = tf.keras.models.load_model("models/rnn_sentiment_model.h5")
lstm_model = tf.keras.models.load_model("models/lstm_sentiment_model.h5")

# Load tokenizer
with open("models/tokenizer.pkl", "rb") as handle:
    tokenizer = pickle.load(handle)

# Define sentiment labels
sentiment_labels = {0: "Negative", 1: "Neutral", 2: "Positive"}

# Predict sentiment
def predict_sentiment(comment, model):
    sequence = tokenizer.texts_to_sequences([comment])
    padded_sequence = pad_sequences(sequence, maxlen=100, padding="post")
    predicted_prob = model.predict(padded_sequence)
    predicted_class = np.argmax(predicted_prob)
    return predicted_class  # Return class (0, 1, 2)

# Define API route
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    user_id = data.get("user_id", "").strip()
    product_id = data.get("product_id", "").strip()  # Ensure book_id is provided
    comment = data.get("comment", "").strip()

    if not product_id or not comment:
        return jsonify({"error": "Missing product_id or comment"}), 400

    # Predict sentiment using different models
    cnn_pred = predict_sentiment(comment, cnn_model)
    rnn_pred = predict_sentiment(comment, rnn_model)
    lstm_pred = predict_sentiment(comment, lstm_model)

    # Majority voting for final prediction
    predictions = [cnn_pred, rnn_pred, lstm_pred]
    final_prediction = max(set(predictions), key=predictions.count)

    # Save to MongoDB
    comment_data = {
        "user_id": user_id,
        "product_id": product_id,
        "comment": comment,
        "evaluate": int(final_prediction)  # Store as 0, 1, or 2
    }
    comments_collection.insert_one(comment_data)
    return jsonify({
        "user_id": user_id,
        "product_id": str(product_id),  # Convert ObjectId to string for JSON
        "comment": comment,
        "evaluate": int(final_prediction),  # Ensure JSON serializable format
        "message": "Sentiment saved successfully"
    })


# Get all books from MongoDB
def fetch_books():
    books = list(books_collection.find({}, {"_id": 1, "title": 1, "author_ids": 1, "publisher": 1, "language": 1, "published_year": 1}))
    for book in books:
        book["id"] = str(book["_id"])  # Convert ObjectId to string
    return books

# Get sentiment scores from MongoDB
def fetch_sentiment_scores():
    comments = list(comments_collection.find({}, {"_id": 0, "product_id": 1, "evaluate": 1}))
    return {str(comment["product_id"]): comment["evaluate"] for comment in comments}

# Convert book data into a single text representation
def get_book_text_representation(book):
    return f"{' '.join(map(str, book.get('author_ids', [])))} {book.get('publisher', '')} {book.get('language', '')} {book.get('published_year', '')}"

@app.route("/recommend", methods=["GET"])
def recommend_books():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # Fetch user reviews with positive sentiment
    liked_books = list(comments_collection.find(
        {"user_id": user_id, "evaluate": {"$gte": 1}},  # Positive sentiment (1=positive, 2=very positive)
        {"_id": 0, "product_id": 1}
    ))

    if not liked_books:
        return jsonify({"message": "No liked books found for this user", "recommended_books": []}), 200

    liked_book_ids = [str(book["product_id"]) for book in liked_books]

    # Fetch all books from MongoDB
    books = fetch_books()
    sentiment_scores = fetch_sentiment_scores()

    # Get representations of books for TF-IDF
    book_texts = [get_book_text_representation(book) for book in books]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(book_texts)

    # Find similar books based on liked books
    recommended_books = {}
    for book_id in liked_book_ids:
        target_book = next((book for book in books if book["id"] == book_id), None)
        if not target_book:
            continue

        target_index = books.index(target_book)
        cosine_similarities = cosine_similarity(tfidf_matrix[target_index], tfidf_matrix).flatten()

        for i, book in enumerate(books):
            if book["id"] != book_id and book["id"] not in liked_book_ids:
                similarity_score = cosine_similarities[i]
                sentiment_score = sentiment_scores.get(book["id"], 0)  # Default 0 if no sentiment data
                if book["id"] in recommended_books:
                    recommended_books[book["id"]]["similarity"] += similarity_score
                    recommended_books[book["id"]]["sentiment"] = max(recommended_books[book["id"]]["sentiment"], sentiment_score)
                else:
                    recommended_books[book["id"]] = {"book": book, "similarity": similarity_score, "sentiment": sentiment_score}

    # Sort books by sentiment score first, then similarity
    sorted_books = sorted(recommended_books.values(), key=lambda x: (x["sentiment"], x["similarity"]), reverse=True)

    # Return top 5 recommendations
    response = [{"id": book["book"]["id"], "title": book["book"]["title"], "score": book["sentiment"]} for book in sorted_books[:5]]

    return jsonify({"recommended_books": response})



# @app.route("/recommend", methods=["POST"])
# def recommend():
#     data = request.get_json()
#     user_comment = data.get("comment", "")

#     if not user_comment:
#         return jsonify({"error": "No comment provided"}), 400

#     # Predict user sentiment
#     user_sentiment = predict_sentiment(user_comment, cnn_model)

#     # Recommend products based on sentiment
#     recommended_products = sorted(products, key=lambda x: abs(x["average_sentiment"] - user_sentiment))

#     return jsonify({"recommended_products": recommended_products})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

#change