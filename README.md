# Fragrance Chatbot

An AI-powered chatbot that helps users discover personalized fragrances based on their preferences, style, and personality.

## Project Status

Currently implementing Stage 1: Core Chat & Session Management

## Features

- Real-time chat interface with streaming responses
- Session management with persistence
- Automatic session cleanup
- Comprehensive error handling
- Detailed logging system

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fragrance-chatbot.git
cd fragrance-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```env
DATABASE_URL=sqlite:///./sessions.db
OPENAI_API_KEY=your_openai_api_key
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

The API documentation is available at `/docs` when running the application.

## Project Structure

```
fragrance_chatbot/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core application logic
│   ├── models/        # Data models
│   ├── services/      # Business logic services
│   └── main.py        # Application entry point
├── static/            # Frontend static files
├── prompts/           # AI prompt templates
├── logs/              # Application logs
├── .env              # Environment variables (not in repo)
├── .gitignore        # Git ignore rules
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Development Plan

The project is being developed in stages:

1. Stage 1: Core Chat & Session Management (Current)
2. Stage 2: User Profile & Basic Information Extraction
3. Stage 3: Image Analysis Integration
4. Stage 4: Web Search Integration
5. Stage 5: Fragrance Recommendation System

Detailed documentation for each stage is available in the `documentation.md` file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 