# Multi-Agent Procurement Management

A sophisticated multi-agent system using **LangGraph** to orchestrate specialized AI agents for autonomous procurement workflows, featuring a **React + Vite** frontend and **FastAPI** backend with localized SQLite storage.

## System Architecture

### Backend (Python)
- **Orchestrator**: Analyzes user input and delegates tasks to specialized agents based on procurement goals.
- **Email Agent**: Parses incoming emails for orders and vendor communications.
- **Compliance Agent**: Validates requests against budgets and policies.
- **Order Agent**: Generates purchase orders and interacts with the inventory system.
- **Forecast Agent**: Predicts future inventory needs based on historical data.
- **FastAPI**: Exposes the workflow and SQLite database via REST API.

### Frontend (React)
- **Vite + React + TypeScript**: Fast, modern frontend.
- **Shadcn UI + Tailwind**: Premium design components.
- **Framer Motion**: Smooth animations for status updates.

## Prerequisites

1.  **Python 3.9+**
2.  **Node.js 18+**
3.  **Ollama**: Running locally with `mistral` model (`ollama pull mistral`).

## Configuration

You can configure the models used by the agents by creating a `.env` file in the root directory.

### `.env` Template
Copy the following into a file named `.env`:

```ini
# Helper Config
OLLAMA_BASE_URL=http://localhost:11434

# Model Selection
# You can change these to any model you have pulled in Ollama (e.g. llama3.1, mistral, gemma3:4b)
ORCHESTRATOR_MODEL=mistral
EMAIL_MODEL=mistral
COMPLIANCE_MODEL=mistral
PO_MODEL=mistral
FORECAST_MODEL=mistral
```

## Installation

### 1. Backend Setup
```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Initialization
Initialize the `procurement.db` SQLite database with the full schema and seed data before running the application:
```bash
python scripts/db_init.py
```

### 3. Frontend Setup
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
