# Multi-Agent Number Converter

A multi-agent system using **LangGraph** to orchestrate specialized AI agents, featuring a **React + Vite** frontend and **FastAPI** backend.

## System Architecture

### Backend (Python)
- **Orchestrator**: Analyzes input to route to specific agents.
- **Agent A (Num2Text)**: Converts digits to text (e.g., "42" -> "forty-two").
- **Agent B (Text2Num)**: Converts text to digits (e.g., "one hundred" -> "100").
- **FastAPI**: Exposes the workflow via REST API.

### Frontend (React)
- **Vite + React + TypeScript**: Fast, modern frontend.
- **Shadcn UI + Tailwind**: Premium design components.
- **Framer Motion**: Smooth animations for status updates.

## Prerequisites

1.  **Python 3.9+**
2.  **Node.js 18+**
3.  **Ollama**: Running locally with `mistral` model (`ollama pull mistral`).

## Installation

### 1. Backend Setup
```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

## Usage

### 1. Start the Backend Server
From the root directory:
```bash
uvicorn backend.api:app --reload
```
The API will run at `http://localhost:8000`.

### 2. Start the Frontend Application
From the `frontend/` directory:
```bash
npm run dev
```
Open the provided URL (usually `http://localhost:5173`).

## Project Structure

- `backend/`: Python backend logic (LangGraph, Agents, API).
- `frontend/`: React frontend application.
- `app.py`: Legacy Streamlit app.
