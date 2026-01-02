# Lost and Found Flask App

A simple Flask web application for managing lost and found items with image upload support.

## Project Structure

```
mysite/
├── flask_app.py                 # Flask application
├── items.json            # JSON database for items
├── templates/            # HTML templates
│   ├── home.html        # Home page (view items)
│   └── add-item.html    # Add new item page
└── static/              # Static files
    └── css/
        └── style.css    # Styles
```

## Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run the Flask app:

```bash
python app.py
```

1. Open browser to `http://localhost:5000`

## API Endpoints

- `GET /` - Home page
- `GET /add-item` - Add item page
- `GET /api/items` - Get all items (JSON)
- `POST /api/items` - Create new item (JSON)

## Deploying to PythonAnywhere

1. Upload all files to PythonAnywhere
2. Create a new web app with Flask
3. Set the source code directory to your project folder
4. Set the working directory to your project folder
5. In the WSGI configuration file, update:

```python
import sys
path = '/home/yourusername/lost-found'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

1. Reload the web app

## Features

- View all found items with images, names, and descriptions
- Add new items with photo upload (camera or file)
- Responsive design with AI-inspired styling
- JSON-based storage (no database required)
- REST API for items management
