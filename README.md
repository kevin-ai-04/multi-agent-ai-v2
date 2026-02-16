# Multi-Agent Number Converter

A proof-of-concept system using **LangGraph** to orchestrate multiple AI agents for specific tasks.

## System Architecture

The system consists of a central **Orchestrator** and two specialized agents:
1.  **Agent A (Num2Text)**: Converts digits (e.g., "42") to text (e.g., "forty-two").
2.  **Agent B (Text2Num)**: Converts text (e.g., "one hundred") to digits (e.g., "100").

### Workflow (LangGraph)
1.  **User Input**: The user enters text in the Streamlit interface.
2.  **Orchestrator Node**: Analyzes the input to determine if it is a number-to-text or text-to-number request.
3.  **Routing Logic**:
    - If `Num2Text` is needed -> Routes to Agent A.
    - If `Text2Num` is needed -> Routes to Agent B.
    - If unclear -> Routes to "Unknown" handler.
    - If the required agent is disabled via UI -> Routes to "Service Unavailable" handler.
4.  **Agent Execution**: The selected agent processes the input using a local LLM (Ollama/Mistral).
5.  **Output**: The final result is displayed to the user.

## Prerequisites

1.  **Python 3.9+**
2.  **Ollama**: You must have Ollama installed and running locally.
    - [Download Ollama](https://ollama.com/)
    - Pull the `mistral` model:
      ```bash
      ollama pull mistral
      ```

## Installation

1.  Clone the repository.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Make sure Ollama is running (`ollama serve`).
2.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
3.  Open your browser to the provided URL (usually `http://localhost:8501`).
4.  Use the sidebar to enable/disable agents.
5.  Type numbers or text in the chat input to see the agents in action.

## Project Structure

- `app.py`: The Streamlit frontend application.
- `backend/`:
    - `agents.py`: Contains the logic for communicating with Ollama (Num2Text, Text2Num, Orchestrator).
    - `graph.py`: Defines the LangGraph state machine, nodes, and conditional edges.
- `requirements.txt`: Python dependencies.
