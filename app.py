from flask import Flask, jsonify
from flask_cors import CORS
from back.scripts.gesture_regognition import main

app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['GET'])

def get_data():
    audio_base64 = main()
    if not audio_base64:
        data = {}
    else:
        data = {"key": audio_base64}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
    print("Connected to the server and connected with the React application")
