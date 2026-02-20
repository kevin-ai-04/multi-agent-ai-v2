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

# --- Email Functionality ---
from backend.email_service import EmailService
from backend.database import init_db, get_emails as db_get_emails

# Initialize DB on startup
# In a real app, use lifespan or startup event, but simple call here works for global scope if import side-effects are managed.
# Better to put it in a function.
@app.on_event("startup")
def on_startup():
    init_db()

email_service = EmailService()

class EmailItem(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    body: str
    folder: str

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

@app.get("/emails/{folder}", response_model=list[EmailItem])
async def get_emails(folder: str, limit: int = 20):
    try:
        # Read from local DB
        emails = db_get_emails(folder, limit)
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/sync")
async def sync_emails(folder: str = "INBOX"):
    try:
        # Fetch from IMAP and save to DB
        emails = email_service.fetch_emails(folder, limit=20)
        return {"status": "success", "count": len(emails), "message": f"Synced {len(emails)} emails from {folder}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/send")
async def send_email_endpoint(request: SendEmailRequest):
    success = email_service.send_email(request.to_email, request.subject, request.body)
    if success:
        return {"status": "success", "message": "Email sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")
