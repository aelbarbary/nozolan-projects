from flask import Flask, render_template, request, jsonify, url_for
import json
import os
import time
from werkzeug.utils import secure_filename

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
    """API endpoint to add a new item.

    Accepts multipart/form-data with:
    - name (str)
    - description (str)
    - image (file upload)
    """
    try:
        if not request.content_type.startswith('multipart/form-data'):
            return jsonify({'error': 'Use multipart/form-data with fields: name, description, image file'}), 400

        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_file = request.files.get('image')

        if not name or not description or image_file is None:
            return jsonify({'error': 'Missing required fields: name, description, image'}), 400

        filename = secure_filename(image_file.filename or 'upload')
        if not filename:
            return jsonify({'error': 'Invalid image filename'}), 400

        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)

        # Ensure unique filename
        timestamp = int(time.time() * 1000)
        name_part, ext = os.path.splitext(filename)
        stored_filename = f"{name_part}_{timestamp}{ext or '.jpg'}"
        file_path = os.path.join(uploads_dir, stored_filename)
        image_file.save(file_path)

        image_url = url_for('static', filename=f'uploads/{stored_filename}')

        items = read_items()
        new_item = {
            'image': image_url,
            'name': name,
            'description': description
        }
        items.insert(0, new_item)  # Add to beginning

        if write_items(items):
            return jsonify({'success': True, 'item': new_item}), 201
        return jsonify({'error': 'Failed to save item'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
