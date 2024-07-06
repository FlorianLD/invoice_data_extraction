from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Dictionary to store valid API keys
API_KEYS = {
    "user1": "key1",
    "user2": "key2"
}

# Root route to handle GET requests to "/"
@app.route('/')
def home():
    return "Welcome to the Flask API!"

# Route that requires an API key
@app.route('/uppercase', methods=['POST'])
def uppercase():
    api_key = request.headers.get('x-api-key')
    if not api_key or api_key not in API_KEYS.values():
        abort(401)  # Unauthorized

    data = request.get_json()
    if 'word' not in data:
        abort(400)  # Bad Request

    word = data['word']
    uppercase_word = f'the current word is {word}'

    return jsonify({"Result": uppercase_word})

if __name__ == '__main__':
    app.run(debug=True)