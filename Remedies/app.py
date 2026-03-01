# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load the Excel file
excel_file = "cell_salts_db.xlsx"

def load_remedies():
    """Load remedies from Excel file"""
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        return df.to_dict('records')
    return []

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    """Search remedies by ailment"""
    query = request.args.get('q', '').lower().strip()
    remedies = load_remedies()
    
    if not query:
        return jsonify(remedies)
    
    # Filter remedies based on search query
    results = [
        r for r in remedies 
        if query in str(r.get('Ailment', '')).lower() or 
           query in str(r.get('Description', '')).lower() or
           query in str(r.get('Cell Salt Remedy', '')).lower()
    ]
    
    return jsonify(results)

@app.route('/api/all', methods=['GET'])
def get_all():
    """Get all remedies"""
    remedies = load_remedies()
    return jsonify(remedies)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
