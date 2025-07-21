"""
Minimal Flask app for diagnostic testing
"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Diagnostic Test</title>
    </head>
    <body>
        <h1>Enhanced Customer Tracking - Diagnostic Mode</h1>
        <p>App is running successfully!</p>
        <p><a href="/api/health">Check Health</a></p>
    </body>
    </html>
    """

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Diagnostic app is running',
        'version': '1.0.0'
    })

@app.route('/api/test')
def test():
    return jsonify({
        'test': 'success',
        'message': 'Basic API endpoint working'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

