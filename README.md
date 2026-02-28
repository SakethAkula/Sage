# 🌿 Sage - AI Healthcare Chatbot

An intelligent healthcare assistant powered by Claude AI that helps users understand symptoms, get health advice, and manage their wellness journey.

## ✨ Features

- **AI-Powered Chat** - Natural conversations about health concerns using Claude AI
- **Symptom Analysis** - Describe symptoms and get helpful guidance
- **Image Analysis** - Upload prescriptions or medical images for analysis
- **Health Profile** - Personalized responses based on your health history
- **Chat History** - Access previous conversations anytime
- **Dark/Light Mode** - Comfortable viewing experience

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **AI:** Anthropic Claude API
- **Design:** Glassmorphism UI

## 🚀 Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up MySQL database
4. Copy `backend/db_config_template.py` to `backend/db_config.py` and add your credentials
5. Run: `python backend/app.py`

## 📁 Project Structure

```
sage/
├── backend/
│   ├── app.py              # Flask server
│   ├── database.py         # Database operations
│   ├── sage_ai.py          # Claude AI integration
│   └── db_config.py        # Configuration (not in repo)
├── frontend/
│   ├── templates/          # HTML pages
│   └── static/
│       ├── css/            # Stylesheets
│       ├── js/             # JavaScript
│       └── images/         # Assets
├── data/                   # Health knowledge base
└── requirements.txt
```

## ⚠️ Disclaimer

Sage is for informational purposes only and is not a substitute for professional medical advice. Always consult a healthcare provider for medical concerns.

## 📄 License

MIT License