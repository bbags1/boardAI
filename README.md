## AI Advisory Board

An interactive AI-powered advisory board system that provides expert analysis from multiple perspectives: legal, financial, and technological. The system supports both text and voice interactions, document management, and collaborative AI discussions.

## Features

- 🤖 Multiple AI Advisors (Legal, Financial, Technology)
- 🎤 Voice Input Support
- 📄 Document Management System
- 💬 Interactive Chat Interface
- 🤝 Multi-Advisor Synthesis
- 📊 Context-Aware Responses
- 🗄️ Conversation Memory

## Installation

1. Clone the repository:
bash
git clone https://github.com/yourusername/boardAI.git
cd boardAI

2. Create a virtual environment:
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies:
bash
pip install -r requirements.txt

4. Set up environment variables:
Create a `.env` file in the root directory with:

GOOGLE_API_KEY=your_google_api_key_here

## Usage

1. Start the application:
bash
streamlit run src/app.py

2. Select advisors from the sidebar
3. Interact through:
   - Text input
   - Voice recording (click microphone button)
   - Document uploads

## Project Structure
boardAI/
├── src/
│ ├── app.py # Streamlit interface
│ ├── main.py # Core AI logic
│ ├── memory.py # Conversation memory
│ └── document_manager.py # Document handling
├── data/
│ ├── memory/ # Stored conversations
│ └── documents/ # Uploaded documents
├── temp/ # Temporary files
├── requirements.txt
└── README.md

## Dependencies

See `requirements.txt` for full list of dependencies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]