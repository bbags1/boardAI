# BoardAI - AI Advisory Board for Organizations

BoardAI is a web application that provides organizations with an AI-powered advisory board. It allows users to upload company documents, engage with AI advisors with different expertise, and receive insights and recommendations based on their organization's data.

## Features

- **User Authentication**: Secure login and registration system
- **Document Management**: Upload, view, and manage company documents (supports PDF and text files)
- **AI Advisory Board**: Interact with AI advisors with expertise in different domains (legal, financial, technology, etc.)
- **Conversation History**: Keep track of all discussions with the AI advisors

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **AI**: Google Generative AI
- **Authentication**: JWT tokens with bcrypt password hashing

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Google API key for Generative AI

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/boardAI.git
   cd boardAI
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   GOOGLE_API_KEY=your_google_api_key
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=boardai
   SECRET_KEY=your_secret_key
   ```

5. Initialize the database:
   ```
   cd backend
   alembic upgrade head
   ```

## Running the Application

1. Start the backend server:
   ```
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend application (in a new terminal):
   ```
   cd frontend
   streamlit run app.py
   ```

3. Access the application:
   - Frontend: http://localhost:8501
   - Backend API docs: http://localhost:8000/docs

## Project Structure

```
boardAI/
├── backend/
│   ├── app/
│   │   ├── core/        # Core configuration
│   │   ├── db/          # Database setup
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routes/      # API endpoints
│   │   ├── schemas/     # Pydantic schemas
│   │   └── main.py      # FastAPI application
│   └── alembic/         # Database migrations
├── frontend/
│   └── app.py           # Streamlit application
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## API Documentation

The API documentation is available at http://localhost:8000/docs when the backend server is running.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.