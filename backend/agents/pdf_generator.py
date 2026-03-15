"""
PDF Purchase Order Generator Agent.
"""
import os
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import get_po_llm


def generate_po_content(order: dict) -> str:
    """
    Uses LLM to generate the formal text content of a Purchase Order.
    order dict should contain: item_name, quantity, unit_price, total_cost,
                               vendor_name, vendor_email, order_id, priority, created_at
    """
    prompt = f"""You are a professional procurement officer. Write a formal Purchase Order document.

ORDER DETAILS:
- PO Number: {order.get('order_id', order.get('id', 'N/A'))}
- Date: {order.get('created_at', 'Today')}
- Item: {order.get('item_name', 'N/A')}
- Quantity: {order.get('qty', order.get('quantity', 'N/A'))} units
- Unit Price: ${order.get('unit_price', 0):,.2f}
- Total Amount: ${order.get('amount', order.get('total_cost', 0)):,.2f}
- Vendor: {order.get('vendor_name', 'N/A')}
- Vendor Email: {order.get('vendor_email', 'N/A')}
- Priority: {order.get('priority', 'Standard')}
- Company: Aurora Industries

Write the body of a professional Purchase Order letter addressed to the vendor.
Include: greeting, order specifics, expected delivery urgency based on priority, payment terms (Net 30), and a closing.
Keep it formal, concise, and ready to send. Do NOT add any JSON or formatting tags."""

    try:
        response = get_po_llm().invoke([
            SystemMessage(content="You are a procurement officer writing formal business documents."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        # Fallback plain text
        return (
            f"PURCHASE ORDER #{order.get('order_id', 'N/A')}\n\n"
            f"To: {order.get('vendor_name', 'N/A')} ({order.get('vendor_email', 'N/A')})\n\n"
            f"We hereby place an order for {order.get('quantity')} units of "
            f"{order.get('item_name')} at ${order.get('unit_price', 0):,.2f} per unit, "
            f"totalling ${order.get('total_cost', 0):,.2f}.\n\n"
            f"Payment terms: Net 30.\n\nRegards,\nAurora Industries Procurement"
        )


def sanitize_text(text: str) -> str:
    """Replace Unicode characters that Helvetica can't render with ASCII equivalents."""
    replacements = {
        "\u2014": "--",   # em dash
        "\u2013": "-",    # en dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote / apostrophe
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",    # non-breaking space
        "\u00ae": "(R)",  # registered trademark
        "\u00a9": "(C)",  # copyright
        "\u2122": "(TM)", # trademark
        "\u20ac": "EUR",  # euro sign
        "\u00b0": " deg", # degree sign
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Final safety: drop any remaining non-latin1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_order_pdf(order: dict, output_dir: str = "orders") -> str:
    """
    Generates a PDF Purchase Order using fpdf2.
    Returns the path to the saved PDF file.
    """
    from fpdf import FPDF, Align

    os.makedirs(output_dir, exist_ok=True)
    order_id  = order.get('order_id') or order.get('id', 'unknown')
    file_path = f"{output_dir}/order_{order_id}.pdf"

    # Generate PO content via LLM and sanitize Unicode characters
    po_body = sanitize_text(generate_po_content(order))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ── Header ──────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, text="PURCHASE ORDER", align=Align.C)
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, text=f"PO Number: #{order_id}", align=Align.C)
    pdf.ln(6)
    pdf.cell(0, 6, text=f"Date: {order.get('created_at', datetime.now().strftime('%Y-%m-%d'))}", align=Align.C)
    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── Summary Table ───────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    fields = [
        ("Item",          order.get('item_name', 'N/A')),
        ("Quantity",      str(order.get('qty', order.get('quantity', 'N/A')))),
        ("Unit Price",    f"${order.get('unit_price', 0):,.2f}"),
        ("Total Amount",  f"${order.get('amount', order.get('total_cost', 0)):,.2f}"),
        ("Vendor",        order.get('vendor_name', 'N/A')),
        ("Vendor Email",  order.get('vendor_email', 'N/A')),
        ("Priority",      order.get('priority', 'Standard')),
    ]
    for label, value in fields:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(50, 7, text=label + ":")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, text=str(value))
        pdf.ln(7)
    pdf.ln(4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # ── LLM-Generated PO Body ───────────────────
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, text="Purchase Order Details")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, text=po_body)
    pdf.ln(6)

    # ── Footer ──────────────────────────────────
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 6, text="Aurora Industries -- Procurement Department", align=Align.C)
    pdf.ln(6)
    pdf.cell(0, 6, text="This is a system-generated Purchase Order.", align=Align.C)

    pdf.output(file_path)
    return file_path
