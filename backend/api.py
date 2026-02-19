from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.graph import app as workflow

app = FastAPI(title="Multi-Agent Number Converter API")

# Configure CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    input_text: str
    agent_a_enabled: bool = True
    agent_b_enabled: bool = True

class ChatResponse(BaseModel):
    response_text: str
    steps: list[str]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        inputs = {
            "input_text": request.input_text,
            "agent_a_enabled": request.agent_a_enabled,
            "agent_b_enabled": request.agent_b_enabled
        }
        
        result = workflow.invoke(inputs)
        
        return ChatResponse(
            response_text=result.get("output_text", "Error processing request."),
            steps=result.get("steps", [])
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
