# InsideOut

InsideOut is a calm, friendly web application designed to help you reflect on your emotions and regain balance. It serves as a non-judgmental companion for self-reflection.

## Project Structure

```
InsideOut/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Global styles
│   │   └── js/
│   │       └── script.js       # Client-side interactions
│   ├── templates/
│   │   ├── base.html           # Base layout
│   │   ├── index.html          # Landing page
│   │   ├── feeling.html        # Input flow
│   │   └── reflection.html     # Response page
│   ├── __init__.py             # Flask app factory
│   └── routes.py               # Route definitions
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── run.py                      # Entry point
└── README.md                   # This file
```

## Data Flow

1.  **User Visits Home** (`/`): The `index` route renders `index.html`.
2.  **User Clicks Start**: Navigates to `/feeling`.
3.  **User Enters Emotion**: The form in `feeling.html` POSTs data to `/feeling`.
4.  **Backend Processes**: Use `routes.py` to capture the input.
5.  **Reflection**: The app renders `reflection.html`, passing the user's emotion to the template to generate a personalized response.

## Setup & Running

1.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python run.py
    ```

4.  **Open in Browser**:
    Visit `http://127.0.0.1:5000` to start reflecting.
