# AI Advisory Board

An intelligent board room advisor system powered by Google's Gemini AI.

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a .env file with your Google API key: `GOOGLE_API_KEY=your_key_here`
6. Run the app: `streamlit run src/app.py`

## Features
- Multiple AI advisors with different expertise (Legal, Financial, Technology)
- Real-time streaming responses
- Interactive discussion between advisors
- Synthesis of different perspectives
