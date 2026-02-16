# Trading Portal

A full-stack trading portal application with React frontend and FastAPI backend.

## Project Structure

```
Trading-Portal/
├── frontend/          # React + Vite frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/           # FastAPI backend
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Tech Stack

### Frontend
- React
- Vite
- JavaScript

### Backend
- Python 3.12
- FastAPI
- Uvicorn

## Getting Started

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on: http://localhost:5173

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend will run on: http://localhost:8000

API documentation: http://localhost:8000/docs

## Development

- Frontend development server: `npm run dev` (in frontend directory)
- Backend development server: `uvicorn main:app --reload` (in backend directory)
