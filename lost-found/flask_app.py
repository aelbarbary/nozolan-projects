from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMS_FILE = os.path.join(BASE_DIR, 'items.json')

def read_items():
    """Read items from JSON file"""
    if not os.path.exists(ITEMS_FILE):
        return []
    try:
        with open(ITEMS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading items: {e}")
        return []

def write_items(items):
    """Write items to JSON file"""
    try:
        with open(ITEMS_FILE, 'w') as f:
            json.dump(items, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing items: {e}")
        return False

@app.route('/')
def home():
    """Render home page"""
    return render_template('home.html')

@app.route('/add-item')
def add_item():
    """Render add item page"""
    return render_template('add-item.html')

@app.route('/api/items', methods=['GET'])
def get_items():
    """API endpoint to get all items"""
    items = read_items()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def create_item():
    """API endpoint to add a new item"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'description' not in data or 'image' not in data:
            return jsonify({'error': 'Missing required fields: name, description, image'}), 400
        
        items = read_items()
        new_item = {
            'image': data['image'],
            'name': data['name'],
            'description': data['description']
        }
        items.insert(0, new_item)  # Add to beginning
        
        if write_items(items):
            return jsonify({'success': True, 'item': new_item}), 201
        else:
            return jsonify({'error': 'Failed to save item'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
