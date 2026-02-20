from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.graph import app as workflow

app = FastAPI(title="Multi-Agent Procurement System API")

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

# --- Generic Database Functionality ---
from backend.database import get_tables as db_get_tables, get_table_data as db_get_table_data, update_table_row as db_update_table_row

class UpdateRowRequest(BaseModel):
    original_row: dict
    updated_row: dict

@app.get("/database/tables")
async def api_get_tables():
    try:
        tables = db_get_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/tables/{table_name}")
async def api_get_table_data(table_name: str):
    try:
        data = db_get_table_data(table_name)
        return {"data": data}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/database/tables/{table_name}")
async def api_update_table_row(table_name: str, request: UpdateRowRequest):
    try:
        db_update_table_row(table_name, request.original_row, request.updated_row)
        return {"status": "success"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/database/tables/{table_name}")
async def api_delete_table_data(table_name: str):
    try:
        from backend.database import delete_table_data as db_delete_table_data
        db_delete_table_data(table_name)
        return {"status": "success", "message": f"Deleted all records from {table_name}"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Email Analysis API ---
from backend.agents import analyze_email_content
from backend.database import get_item_by_name, get_vendor, save_email_analysis, get_email_analysis, get_unanalyzed_emails, get_db_connection

def _process_email_analysis(email_id: str, body: str):
    # Call LLM
    extraction = analyze_email_content(body)
    if not extraction:
        raise ValueError("Failed to extract structured data from email.")
        
    item_name = extraction.get('item_name', '')
    
    # 1. Find matching item
    item_data = get_item_by_name(item_name)
    vendor_data = None
    
    # 2. Get vendor if item found
    if item_data and item_data.get('default_vendor_id'):
        vendor_data = get_vendor(item_data['default_vendor_id'])
            
    # 3. Save to database
    save_email_analysis(email_id, extraction, item_data, vendor_data)
    
    # 4. Return the saved data
    return get_email_analysis(email_id)

@app.post("/emails/{email_id}/analyze")
async def analyze_single_email(email_id: str):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT body FROM emails WHERE id = ?", (email_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Email not found")
            
        body = row['body']
        result = _process_email_analysis(email_id, body)
        step_msg = f"Email Agent: Analyzed email '{email_id}'"
        if result and result.get('item_name'):
             step_msg += f" -> {result.get('item_name')}"
        return {"status": "success", "data": result, "step": step_msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/emails/analyze_all")
async def analyze_all_emails():
    try:
        unanalyzed = get_unanalyzed_emails()
        results = []
        for email in unanalyzed:
             try:
                 res = _process_email_analysis(email['id'], email['body'])
                 step_msg = f"Email Agent: Analyzed email '{email['id']}'"
                 if res and res.get('item_name'):
                      step_msg += f" -> {res.get('item_name')}"
                 results.append({"email_id": email['id'], "status": "success", "data": res, "step": step_msg})
             except Exception as e:
                 results.append({"email_id": email['id'], "status": "error", "message": str(e)})
        return {"status": "success", "processed_count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emails/{email_id}/analysis")
async def get_email_analysis_endpoint(email_id: str):
    try:
        data = get_email_analysis(email_id)
        if data:
            return {"status": "success", "data": data}
        else:
            return {"status": "not_found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
