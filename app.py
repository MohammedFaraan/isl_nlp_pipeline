from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS module
from main import isl_pipeline


app = Flask(__name__)
CORS(app)
@app.route('/api/isl', methods=['POST'])
def process_isl():
    # Expect JSON with a "sentence" key
    data = request.get_json()
    sentence = data.get('sentence', '')
    if not sentence:
        return jsonify({'error': 'No sentence provided'}), 400

    try:
        # Process the sentence using the pipeline
        isl_gloss = isl_pipeline(sentence)
        return jsonify({'isl_gloss': isl_gloss}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)