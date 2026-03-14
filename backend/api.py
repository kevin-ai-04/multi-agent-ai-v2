from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from pathlib import Path
import datetime
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

# Ensure orders directory exists and mount it as static
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORDERS_DIR = PROJECT_ROOT / "orders"
ORDERS_DIR.mkdir(exist_ok=True)
app.mount("/static/orders", StaticFiles(directory=str(ORDERS_DIR)), name="orders")

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    agent_num2text_enabled: bool = True
    agent_text2num_enabled: bool = True
    agent_email_enabled: bool = True
    agent_compliance_enabled: bool = True
    agent_pdf_enabled: bool = True
    agent_forecast_enabled: bool = True

class ChatResponse(BaseModel):
    response_text: str
    steps: list[str]
    ui_actions: list[dict] = []

class OrdersSummaryResponse(BaseModel):
    total_count: int
    total_volume: float

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        initial_state = {
            "input_text": request.message,
            "steps": [],
            "agent_num2text_enabled": request.agent_num2text_enabled,
            "agent_text2num_enabled": request.agent_text2num_enabled,
            "agent_email_enabled": request.agent_email_enabled,
            "agent_compliance_enabled": request.agent_compliance_enabled,
            "agent_pdf_enabled": request.agent_pdf_enabled,
            "agent_forecast_enabled": request.agent_forecast_enabled,
            "routing_decision": "unknown",
            "output_text": "",
            "ui_actions": [],
            "gatekeeper_results": [],
            "order_ids": []
        }
        
        result = workflow.invoke(initial_state)
        
        return ChatResponse(
            response_text=result.get("output_text", "Error processing request."),
            steps=result.get("steps", []),
            ui_actions=result.get("ui_actions", [])
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
    has_analysis: bool = False

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

# --- Orders API ---
@app.get("/orders")
async def api_get_orders():
    try:
        from backend.database import get_orders as db_get_orders
        orders = db_get_orders()
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Forecast API ---
@app.post("/forecast/generate")
async def api_generate_forecast():
    """ Runs historical math analysis and LLM summarization. """
    try:
        from backend.forecast import generate_forecast_report
        result = generate_forecast_report()
        if "error" in result and result["error"] is True:
            # We still return the markdown error message so the UI can render it gracefully
            return result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Email Analysis API ---
from backend.agents import analyze_email_content
from backend.database import get_item_by_name, get_vendor, save_email_analysis, get_email_analysis, get_unanalyzed_emails, get_db_connection, find_analysis_by_item_name

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

@app.post("/procurement/manual/compliance")
async def manual_compliance_check(payload: dict):
    from backend.database import get_item_by_name, get_vendor
    from backend.agents import run_gatekeeper_checks, explain_compliance_result
    
    item_name = payload.get("item_name")
    quantity = payload.get("quantity", 1)
    expected_date_str = payload.get("expected_date")  # YYYY-MM-DD
    summary = payload.get("summary", "")
    
    if not item_name:
        raise HTTPException(status_code=400, detail="item_name is required")
        
    item = get_item_by_name(item_name)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    total_cost = item['unit_price'] * quantity
    vendor = get_vendor(item.get('default_vendor_id'))
    
    # Calculate priority based on expected_date
    priority = "Normal"
    if expected_date_str:
        try:
            expected_date = datetime.datetime.strptime(expected_date_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            days_available = (expected_date - today).days
            if days_available <= 7:
                priority = "High"
            elif days_available <= 30:
                priority = "Medium"
            else:
                priority = "Low"
        except ValueError:
            pass
            
    fake_analysis = {
        "item_id": item['id'],
        "item_name": item['name'],
        "vendor_id": vendor['id'] if vendor else None,
        "quantity": quantity,
        "total_cost": total_cost,
        "priority": priority,
        "summary": summary
    }
    
    gate = run_gatekeeper_checks(fake_analysis)
    explanation = explain_compliance_result(fake_analysis, gate)
    
    return {
        "status": "success",
        "passed": gate['passed'],
        "explanation": explanation,
        "total_cost": total_cost,
        "fake_analysis_context": fake_analysis
    }

@app.post("/procurement/manual/order")
async def manual_order_create(payload: dict):
    from backend.database import create_order, get_order_by_id as db_get_order_by_id
    from backend.agents import generate_order_pdf
    
    context = payload.get("context")
    if not context:
        raise HTTPException(status_code=400, detail="Order context is required (must run compliance first).")
        
    try:
        order_id = create_order(
            item_id=context['item_id'],
            vendor_id=context['vendor_id'],
            qty=context['quantity'],
            amount=context['total_cost']
        )
        
        order_data = db_get_order_by_id(order_id)
        if order_data:
            order_data['priority'] = context.get('priority', 'Normal')
            
        pdf_path = generate_order_pdf(order_data)
        
        from backend.database import get_db_connection
        conn = get_db_connection()
        conn.execute("UPDATE orders SET pdf_path = ? WHERE id = ?", (pdf_path, order_id))
        conn.commit()
        conn.close()
        
        import os
        filename = os.path.basename(pdf_path)
        return {
            "status": "success",
            "order_id": order_id,
            "pdf_path": f"/static/orders/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/procurement/{email_id}/compliance")
async def check_compliance(email_id: str):
    from backend.agents import run_gatekeeper_checks, explain_compliance_result
    try:
        analysis = get_email_analysis(email_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        gate = run_gatekeeper_checks(analysis)
        explanation = explain_compliance_result(analysis, gate)
        
        passed = bool(gate['passed'])
        status_text = 'Passed' if passed else 'Failed'
        
        conn = get_db_connection()
        conn.execute(
            "UPDATE email_analysis SET compliance_explanation = ? WHERE email_id = ?",
            (explanation, email_id)
        )
        conn.commit()
        conn.close()
        
        return {"status": "success", "passed": passed, "explanation": explanation}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/procurement/{email_id}/order")
async def generate_procurement_order(email_id: str):
    from backend.database import create_order, get_order_by_id as db_get_order_by_id
    from backend.agents import generate_order_pdf
    try:
        analysis = get_email_analysis(email_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        order_id = create_order(
            item_id=analysis['item_id'],
            vendor_id=analysis['vendor_id'],
            qty=analysis['item_quantity'],
            amount=analysis['total_cost']
        )
        
        conn = get_db_connection()
        conn.execute(
            "UPDATE email_analysis SET order_id = ? WHERE email_id = ?",
            (order_id, email_id)
        )
        conn.commit()
        conn.close()
        
        order_data = db_get_order_by_id(order_id)
        if order_data:
            order_data['order_id'] = order_id
            
        # Fix: ensure order_data for PDF generator contains everything
        pdf_path = generate_order_pdf(order_data)
        
        # Save pdf_path back to orders table
        conn = get_db_connection()
        conn.execute("UPDATE orders SET pdf_path = ? WHERE id = ?", (pdf_path, order_id))
        conn.commit()
        conn.close()
        
        # Return URL-friendly path
        filename = os.path.basename(pdf_path)
        return {
            "status": "success", 
            "order_id": order_id, 
            "pdf_path": f"/static/orders/{filename}"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/procurement/compliance-by-item")
async def compliance_by_item_name(payload: dict):
    """
    Runs compliance checks for the most recent email analysis matching the given item name.
    """
    from backend.agents import run_gatekeeper_checks, explain_compliance_result
    item_name = payload.get("item_name", "").strip()
    if not item_name:
        raise HTTPException(status_code=400, detail="item_name is required")

    analysis = find_analysis_by_item_name(item_name)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No email analysis found for '{item_name}'")

    gate = run_gatekeeper_checks(analysis)
    explanation = explain_compliance_result(analysis, gate)
    passed = bool(gate["passed"])
    status_text = "Passed" if passed else "Failed"

    conn = get_db_connection()
    conn.execute(
        "UPDATE email_analysis SET compliance_explanation = ? WHERE email_id = ?",
        (explanation, analysis["email_id"])
    )
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "item_name": analysis.get("item_name"),
        "email_id": analysis["email_id"],
        "passed": passed,
        "explanation": explanation
    }


@app.post("/procurement/order-by-item")
async def order_by_item_name(payload: dict):
    """
    Creates a purchase order + generates PDF for the most recent compliant
    email analysis matching the given item name.
    """
    from backend.database import create_order, get_order_by_id as db_get_order_by_id
    from backend.agents import generate_order_pdf

    item_name = payload.get("item_name", "").strip()
    if not item_name:
        raise HTTPException(status_code=400, detail="item_name is required")

    analysis = find_analysis_by_item_name(item_name)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No email analysis found for '{item_name}'")

    order_id = create_order(
        item_id=analysis["item_id"],
        vendor_id=analysis["vendor_id"],
        qty=analysis["item_quantity"],
        amount=analysis["total_cost"]
    )

    conn = get_db_connection()
    conn.execute(
        "UPDATE email_analysis SET order_id = ? WHERE email_id = ?",
        (order_id, analysis["email_id"])
    )
    conn.commit()
    conn.close()

    order_data = db_get_order_by_id(order_id)
    pdf_path = generate_order_pdf(order_data)

    return {
        "status": "success",
        "item_name": analysis.get("item_name"),
        "order_id": order_id,
        "pdf_path": pdf_path,
        "message": f"Order #{order_id} created and PDF generated."
    }

@app.get("/items/lookup")
async def lookup_item(name: str):
    """Looks up an item by name for manual order creation."""
    from backend.database import get_item_by_name, get_vendor
    item = get_item_by_name(name)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    vendor = get_vendor(item['default_vendor_id']) if item.get('default_vendor_id') else None
    return {"status": "success", "item": item, "vendor": vendor}



# --- Order Management API ---
from fastapi.responses import FileResponse
from fastapi import Query
from backend.database import (
    get_orders as db_get_orders,
    get_orders_paginated as db_get_orders_paginated,
    get_orders_summary as db_get_orders_summary,
    get_order_by_id as db_get_order_by_id,
)
from backend.agents import generate_order_pdf

@app.get("/orders/list")
async def list_orders_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None)
):
    """Paginated orders list with optional filtering."""
    try:
        result = db_get_orders_paginated(page=page, per_page=per_page, search=search)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/summary")
async def orders_summary():
    """Aggregate stats for the orders header."""
    try:
        return {"status": "success", **db_get_orders_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
async def list_orders():
    """List all orders with item and vendor details (legacy, unpaginated)."""
    try:
        return {"status": "success", "orders": db_get_orders()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get a single order by ID."""
    try:
        order = db_get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"status": "success", "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders/{order_id}/generate-pdf")
async def generate_pdf_endpoint(order_id: int):
    """
    Generates a PDF Purchase Order using LLM-written content.
    Returns the PDF file as a download.
    """
    try:
        order = db_get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Build the dict that the PDF generator expects
        order_context = {
            "order_id":    order_id,
            "item_name":   order.get("item_name", "N/A"),
            "quantity":    order.get("qty", 0),
            "unit_price":  order.get("unit_price", 0),
            "total_cost":  order.get("amount", 0),
            "vendor_name": order.get("vendor_name", "N/A"),
            "vendor_email":order.get("vendor_email", "N/A"),
            "created_at":  order.get("created_at", ""),
        }

        pdf_path = generate_order_pdf(order_context)

        # Update the pdf_path in the orders table
        from backend.database import get_db_connection
        conn = get_db_connection()
        conn.execute("UPDATE orders SET pdf_path = ? WHERE id = ?", (pdf_path, order_id))
        conn.commit()
        conn.close()

        return FileResponse(
            path=pdf_path,
            filename=f"PO_{order_id}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
