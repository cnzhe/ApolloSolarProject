# How to Run the Chatbot Locally

## Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

## Backend Setup
1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install Python dependencies
```bash
pip install -r requirements.txt
```

3. Add Environment Variables
- Add a `.env` file
- Fill in your API key

## Frontend Setup
1. Navigate to the frontend directory
```bash
cd frontend
```

2. Install npm dependencies
```bash
npm install
```

## Running the Application
### Backend
From project root directory, run:
```bash
export AUTOGEN_USE_DOCKER=False
uvicorn backend.app:app --reload --port 8000
```

### Frontend
From frontend directory, run:
```bash
npm start
```

## Project Components
- `backend/app.py`: Main backend application logic
- `backend/bot_config.py`: Bot configuration settings
- `frontend/src/`: React/Vue source files
- `requirements.txt`: Python package dependencies
- `frontend/package.json`: Frontend package dependencies