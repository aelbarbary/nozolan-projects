from flask import Flask, render_template, request, jsonify, url_for
import json
import os
import secrets
import time
import smtplib
import traceback
from email.message import EmailMessage
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMS_FILE = os.path.join(BASE_DIR, 'items.json')

ADMIN_EMAIL = 'abdelrahman.elbarbary@gmail.com'

GMAIL_SENDER_EMAIL = 'nozolan.demo@gmail.com'
GMAIL_APP_PASSWORD = "uwvdkcgsujokvqcy"


def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = GMAIL_SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print('EMAIL SEND FAILED')
        print(f'To: {to_email}')
        print(f'Subject: {subject}')
        print(f'Error: {e}')
        traceback.print_exc()
        raise


def _ensure_item_ids(items):
    changed = False
    for idx, item in enumerate(items):
        if not item.get('id'):
            item['id'] = f"item_{int(time.time() * 1000)}_{idx}_{secrets.token_hex(2)}"
            changed = True
    return changed


def _send_admin_email(subject, body):
    try:
        send_email(to_email=ADMIN_EMAIL, subject=subject, body=body)
        return True
    except Exception as e:
        print('Failed to send admin email')
        print(f'Error: {e}')
        traceback.print_exc()
        return False

def read_items():
    """Read items from JSON file"""
    if not os.path.exists(ITEMS_FILE):
        return []
    try:
        with open(ITEMS_FILE, 'r') as f:
            items = json.load(f)
        if isinstance(items, list) and _ensure_item_ids(items):
            write_items(items)
        return items
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


@app.route('/api/items/<item_id>/claim', methods=['POST'])
def claim_item(item_id):
    """Claim a found item.

    Accepts application/json:
    - email (str)

    Generates a claim code, stores it on the item, and emails the admin.
    """
    try:
        payload = request.get_json(silent=True) or {}
        claimant_email = (payload.get('email') or '').strip()

        if not claimant_email or '@' not in claimant_email:
            return jsonify({'error': 'Please provide a valid email address.'}), 400

        items = read_items()
        item = next((i for i in items if i.get('id') == item_id), None)
        if item is None:
            return jsonify({'error': 'Item not found.'}), 404

        if item.get('claim_code'):
            return jsonify({'error': 'This item has already been claimed. Please contact admin.'}), 409

        claim_code = secrets.token_hex(3).upper()
        item['claim_code'] = claim_code
        item['claimed_email'] = claimant_email
        item['claimed_at'] = int(time.time())

        if not write_items(items):
            return jsonify({'error': 'Failed to save claim. Try again.'}), 500

        subject = f"Lost & Found Claim Request: {item.get('name', 'Item')} ({claim_code})"
        body = (
            "Someone submitted a claim for a found item.\n\n"
            f"Claim Code: {claim_code}\n"
            f"Claimant Email: {claimant_email}\n\n"
            "Item Info:\n"
            f"- Name: {item.get('name', '')}\n"
            f"- Description: {item.get('description', '')}\n"
            f"- Image: {item.get('image', '')}\n"
            f"- Item ID: {item.get('id', '')}\n"
        )
        _send_admin_email(subject=subject, body=body)

        return jsonify({'success': True, 'claim_code': claim_code})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            'id': f"item_{int(time.time() * 1000)}_{secrets.token_hex(2)}",
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
