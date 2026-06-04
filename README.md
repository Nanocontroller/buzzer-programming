# Flask Web App

A minimal Flask web application setup.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   └── index.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Development

The app runs in debug mode by default, so changes will automatically reload the server.
