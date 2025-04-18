# How to build the solution

## Project Folder Structure

```text
openai-chat-flask/
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (e.g., API keys, secret key)
├── README.md               # Project documentation
└── website/                # Main Flask package
    ├── __init__.py         # App factory: creates the Flask app, configures DB, registers blueprints
    ├── data/               # Database-related code
    │   ├── __init__.py     # (Optional) Expose models as a package
    │   └── models.py       # SQLAlchemy models (e.g., ChatHistory)
    ├── api/                # API endpoints (return JSON responses)
    │   ├── __init__.py     # Initializes the API blueprint (simply imports blueprint from chat.py)
    │   └── chat.py         # Defines the chat API route that interacts with OpenAI
    ├── views/              # View routes (render templates)
    │   ├── __init__.py     # Initializes the views blueprint (imports blueprint from home.py)
    │   └── home.py         # Contains routes for Home, ST Chat Bot, and History pages
    ├── static/             # Static assets (CSS, images, etc.)
    │   ├── favicon.ico
    │   └── globalstyles.css
    └── templates/          # Jinja2 templates
        ├── base.html       # Base layout (includes navbar and footer via includes)
        ├── navbar.html     # Navbar HTML (included in base.html)
        ├── Footer.html     # (Optional) Footer HTML (could be included in base.html)
        ├── home.html       # Home page (overview of the application)
        ├── stchatbot.html  # Single Turn Chat Bot page (chat interface)
        └── history.html    # Search History page (placeholder or chat history)
```

## File Contents

### 1. app.py

```python
# app.py
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. website/init.py

This file creates the Flask app, configures the database, and registers the blueprints from the views and API modules.

```python
# website/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "SimpleSecretKey")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"

    # Initialize the database
    db.init_app(app)

    # Register views blueprint
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    # Register API blueprint
    from .api import api
    app.register_blueprint(api, url_prefix="/api")

    # Create database if it doesn't exist
    with app.app_context():
        if not path.exists("website/" + DB_NAME):
            db.create_all()
            print("Database Created")

    return app
```

### 3. website/data/models.py

Define your SQLAlchemy models here. For example, a model for chat history:

```python
# website/data/models.py
from . import db

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
```

_(If you need to expose the models, you can add an `__init__.py` file in the data folder that imports these models.)_

### 4. website/api/chat.py

This file defines the API endpoint that communicates with OpenAI.

```python
# website/api/chat.py
from flask import Blueprint, request, jsonify, current_app
import openai
import os

# Define the API blueprint
api = Blueprint('api', __name__)

# Ensure the API key is set via environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY in environment variables.")

# Set the API key globally for the OpenAI package
openai.api_key = openai_api_key

@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    try:
        # Call OpenAI's ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=200
        )
        bot_message = response["choices"][0]["message"]["content"]
        return jsonify({"response": bot_message})
    except Exception as e:
        current_app.logger.error(f"Error in OpenAI API call: {e}")
        return jsonify({"error": "An error occurred while fetching response."}), 500
```

### 5. website/api/init.py

This file simply imports the `api` blueprint from `chat.py`.

```python
# website/api/__init__.py
from .chat import api
```

### 6. website/views/home.py

Define your view routes (rendering HTML templates) in this file.

```python
# website/views/home.py
from flask import render_template
from . import views

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/stchatbot")
def stchatbot():
    return render_template("stchatbot.html")

@views.route("/history")
def history():
    return render_template("history.html")
```

### 7. website/views/init.py

Simply import the blueprint from `home.py`.

```python
# website/views/__init__.py
from .home import views
```

### 8. Templates

#### 8.1. website/templates/base.html

This is your base layout with the navbar and footer. It now includes the navbar via an include directive.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>
      {% block title %}Single Turn Chatbot with OpenAI{% endblock %}
    </title>

    <!-- Google Fonts: Inter -->
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap"
      rel="stylesheet"
    />

    <!-- Favicon -->
    <link
      rel="icon"
      href="{{ url_for('static', filename='favicon.ico') }}"
      type="image/x-icon"
    />

    <!-- Tailwind CSS CDN (or local build if you prefer) -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Custom Global Styles -->
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='globalstyles.css') }}"
    />
  </head>
  <body class="flex flex-col min-h-screen bg-gray-50 text-gray-900 font-inter">
    <!-- Include Navbar -->
    {% include "navbar.html" %}

    <!-- Main Content -->
    <main class="container mx-auto p-4 flex-grow">
      {% block content %}{% endblock %}
    </main>

    <!-- Include Footer if separate, or place it directly -->
    {% include "Footer.html" %}
  </body>
</html>
```

#### 8.2. website/templates/navbar.html

This file contains your navbar code with active tab styling:

```html
<!-- website/templates/navbar.html -->
<nav class="bg-indigo-400 text-white shadow-md">
  <div class="container mx-auto px-4 py-2 flex justify-between items-center">
    <a
      href="/"
      class="text-2xl font-bold px-4 py-1 rounded transition-colors duration-200 hover:bg-indigo-500 hover:text-white {% if request.path == '/' %} active-tab {% endif %}"
    >
      AI Assistant
    </a>
    <div class="space-x-4">
      <a
        href="/stchatbot"
        class="px-4 py-2 rounded transition-colors duration-200 hover:bg-indigo-500 hover:text-white font-bold {% if request.path == '/stchatbot' %} active-tab {% endif %}"
      >
        ST Chat Bot
      </a>
      <a
        href="/history"
        class="px-4 py-2 rounded transition-colors duration-200 hover:bg-indigo-500 hover:text-white font-bold {% if request.path == '/history' %} active-tab {% endif %}"
      >
        Search History
      </a>
      <button
        class="bg-purple-400 hover:bg-purple-600 px-3 py-1 rounded transition-colors duration-200 font-bold"
      >
        Logout
      </button>
    </div>
  </div>
</nav>
```

#### 8.3. website/templates/Footer.html

You can place your footer here:

```html
<!-- website/templates/Footer.html -->
<footer
  class="bg-indigo-400 text-white text-center p-1 text-md border-t border-gray-100"
>
  © 2025 Chatbot - Built with Flask & OpenAI
</footer>
```

#### 8.4. website/templates/home.html

The home page provides an overview of your application:

```html
{% extends "base.html" %} {% block title %}Home{% endblock %} {% block content
%}
<div class="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow">
  <h2 class="text-2xl font-bold mb-4">Welcome to the Single Turn Chat BOT</h2>
  <p class="mb-4 text-xl">
    This application demonstrates a single-turn chat with Azure OpenAI. You can
    ask a question, and it will respond once per query.
  </p>
  <p class="mb-4 text-xl"><strong>Features:</strong></p>
  <ul class="list-disc list-inside mb-4 text-xl">
    <li>Home Page</li>
    <li>Single Turn Chat Bot (GPT-based)</li>
    <li>Search History to revisit previous queries</li>
    <li>Simple, responsive UI</li>
  </ul>
  <p class="mb-4 text-xl">
    Use the navigation bar above to explore the chatbot or view your search
    history.
  </p>
</div>
{% endblock %}
```

#### 8.5. website/templates/stchatbot.html

This page contains your chat interface. (Use your current chat UI code.)

#### 8.6. website/templates/history.html

A placeholder for the search history page:

```html
{% extends "base.html" %} {% block title %}Search History{% endblock %} {% block
content %}
<div class="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow">
  <h2 class="text-2xl font-bold mb-4">Search History</h2>
  <p>Coming soon...</p>
</div>
{% endblock %}
```

### 9. Custom Global Styles: `website/static/globalstyles.css`

```css
/* Global Styles */
body {
  font-family: "Inter", sans-serif;
  font-weight: 400;
}

/* Headings */
h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: "Inter", sans-serif;
  font-weight: 600;
}

/* Other elements */
p,
span,
button,
input,
textarea {
  font-family: "Inter", sans-serif;
  font-weight: 400;
}

/* Custom scrollbar for chat-box */
#chat-box::-webkit-scrollbar {
  width: 6px;
}
#chat-box::-webkit-scrollbar-thumb {
  background-color: #6366f1; /* Indigo-400 */
  border-radius: 6px;
}
#chat-box::-webkit-scrollbar-thumb:hover {
  background-color: #4f46e5; /* Indigo-600 */
}

/* Active tab styling for navbar links */
.active-tab {
  background-color: #4f46e5;
  color: white;
  border-radius: 0.375rem;
  padding-bottom: 0.125rem;
}
```

---

## 10. Running Your Application

### Activate the virtual environment:

```bash
   .\.venv\Scripts\activate
```

### Install dependencies:

```bash
   pip install -r requirements.txt

```

### Run the app:

```bash
   python app.py

```

### Visit your application pages:

> 1. Home: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
> 1. ST Chat Bot: [http://127.0.0.1:5000/stchatbot](http://127.0.0.1:5000/stchatbot)
> 1. Search History: [http://127.0.0.1:5000/history](http://127.0.0.1:5000/history)

## Summary

### Modular Structure

> 1. API endpoints are in `website/api/`.
> 1. Database models are in `website/data/`.
> 1. View (template) routes are in `website/views/`.
> 1. Common templates and static assets are in `website/templates/` and `website/static/`.

### Blueprints

> 1. Blueprints are used to separate view routes and API routes, making the project scalable.

### Template Includes

> 1. The navbar and footer are separated into their own files (e.g., `navbar.html` and `Footer.html`) and included in `base.html` for consistent layout and easy maintenance.

### Custom Global Styles

> 1. Tailwind CSS is used (via CDN and/or custom styles in `globalstyles.css`), along with the Inter font from Google Fonts.
