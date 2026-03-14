import pytest
import sqlite3
import os
import sys
from httpx import AsyncClient, ASGITransport

# Add backend to path so we can import app and db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import app
from database import get_db_connection, DB_NAME

@pytest.fixture(autouse=True)
def setup_test_db():
    # Setup: We will use the actual development DB, but insert a specific dummy test record
    conn = get_db_connection()
    c = conn.cursor()
    # Create a dummy email
    c.execute("INSERT OR REPLACE INTO emails (id, subject, sender, date, body, folder) VALUES ('TEST_999', 'Fake', 'fake@test.com', '2023-01-01', 'Test body', 'inbox')")
    
    # Create an un-complianced analysis row
    c.execute("""
        INSERT OR REPLACE INTO email_analysis 
        (email_id, priority, summary, item_id, item_name, item_quantity, item_unit_price, vendor_id, vendor_name, total_cost, compliance_status) 
        VALUES ('TEST_999', 'Low', 'Test', 1, 'Laptop', 1, 1500.0, 1, 'TechCorp', 1500.0, 'Pending')
    """)
    conn.commit()
    conn.close()
    
    yield
    
    # Teardown
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM emails WHERE id = 'TEST_999'")
    c.execute("DELETE FROM email_analysis WHERE email_id = 'TEST_999'")
    c.execute("DELETE FROM orders WHERE item_id = 1 AND qty = 1 AND amount = 1500.0")
    conn.commit()
    conn.close()

@pytest.mark.asyncio
async def test_compliance_endpoint_integration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Run compliance (Should pass since quantity is 1 and price is 1500)
        response = await ac.post("/procurement/TEST_999/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["passed"] is True
        assert "explanation" in data
        
        # Verify DB was updated
        conn = get_db_connection()
        row = conn.execute("SELECT compliance_status, compliance_explanation FROM email_analysis WHERE email_id = 'TEST_999'").fetchone()
        conn.close()
        assert row["compliance_status"] == 'Passed'
        assert row["compliance_explanation"] == data["explanation"]

@pytest.mark.asyncio
async def test_order_generation_rejects_uncomplianced():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Reset compliance to Pending
        conn = get_db_connection()
        conn.execute("UPDATE email_analysis SET compliance_status = 'Pending' WHERE email_id = 'TEST_999'")
        conn.commit()
        conn.close()

        # Try to order
        response = await ac.post("/procurement/TEST_999/order")
        assert response.status_code == 400
        assert "Cannot create order" in response.text

@pytest.mark.asyncio
async def test_order_generation_integration():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Set compliance to Passed manually
        conn = get_db_connection()
        conn.execute("UPDATE email_analysis SET compliance_status = 'Passed' WHERE email_id = 'TEST_999'")
        conn.commit()
        conn.close()

        # Generate order
        response = await ac.post("/procurement/TEST_999/order")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "order_id" in data
        assert "pdf_path" in data
        
        # Verify DB references
        conn = get_db_connection()
        row = conn.execute("SELECT order_id FROM email_analysis WHERE email_id = 'TEST_999'").fetchone()
        conn.close()
        assert row["order_id"] == data["order_id"]
        assert os.path.exists(data["pdf_path"])
