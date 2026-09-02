def get_custom_css():
    return """
    <style>
        /* Import Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global Reset and Font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Dark Theme Background */
        .stApp {
            background-color: #09090b !important;
            color: #fafafa !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #121214 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: #e4e4e7 !important;
            font-weight: 600;
        }

        /* Header / Toolbar hidden */
        header {
            background-color: transparent !important;
            box-shadow: none !important;
        }
        
        /* Main Title */
        h1 {
            font-weight: 700 !important;
            letter-spacing: -0.025em;
            color: #ffffff !important;
        }

        /* Cards and Containers */
        div[data-testid="stMetric"], 
        div[data-testid="stInfo"], 
        div[data-testid="stSuccess"], 
        div[data-testid="stError"] {
            background-color: #18181b !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3) !important;
            color: #e4e4e7 !important;
        }

        /* Buttons */
        button[kind="secondary"], button[kind="primary"] {
            background-color: #27272a !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease;
        }
        
        button[kind="secondary"]:hover, button[kind="primary"]:hover {
            background-color: #3f3f46 !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            transform: translateY(-1px);
        }
        
        button[kind="primary"] {
            background-color: #2563eb !important;
            border-color: #3b82f6 !important;
        }
        
        button[kind="primary"]:hover {
            background-color: #3b82f6 !important;
            border-color: #60a5fa !important;
        }

        /* Toggles (Checkboxes/Switches) */
        .stCheckbox > label {
            color: #e4e4e7 !important;
        }

        /* Selectboxes and Inputs */
        div[data-baseweb="select"] > div, 
        input, 
        textarea {
            background-color: #18181b !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            color: #fafafa !important;
        }
        
        /* Hide Streamlit Footer */
        footer {
            display: none !important;
        }
        
        /* Dividers */
        hr {
            border-color: rgba(255, 255, 255, 0.05) !important;
        }
    </style>
    """
