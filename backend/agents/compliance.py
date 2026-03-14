"""
Compliance / Gatekeeper Agent: Rule-based checks and LLM-powered explanations.
"""
from langchain_core.messages import HumanMessage, SystemMessage

from backend.agents.config import compliance_llm


def run_gatekeeper_checks(analysis: dict) -> dict:
    """
    Rule-based compliance checks against inventory, budgets, and policies.
    Returns: { 'passed': bool, 'failures': [str], 'warnings': [str] }
    """
    from backend.database import get_db_connection, get_department_for_item

    failures, warnings = [], []
    item_id    = analysis.get('item_id')
    vendor_id  = analysis.get('vendor_id')
    total_cost = analysis.get('total_cost', 0) or 0
    quantity   = analysis.get('quantity', 0) or 0
    item_name  = analysis.get('item_name', 'Unknown Item')

    conn = get_db_connection()
    c = conn.cursor()
    try:
        # ── Check 1: Inventory ──────────────────────────
        if item_id:
            c.execute("SELECT qty_on_hand, min_qty, max_capacity FROM inventory WHERE item_id = ?", (item_id,))
            inv = c.fetchone()
            if inv:
                if inv['qty_on_hand'] > inv['min_qty']:
                    warnings.append(
                        f"Inventory: Stock for '{item_name}' is {inv['qty_on_hand']} units "
                        f"(above min threshold of {inv['min_qty']}). Order may not be urgent."
                    )
                projected = inv['qty_on_hand'] + quantity
                if inv['max_capacity'] > 0 and projected > inv['max_capacity']:
                    failures.append(
                        f"Inventory: Ordering {quantity} units would exceed max capacity "
                        f"({projected} > {inv['max_capacity']})."
                    )
            else:
                warnings.append(f"Inventory: No record found for item_id={item_id}.")
        else:
            warnings.append("Inventory: Item not found in catalog — check skipped.")

        # ── Check 2: Budget ─────────────────────────────
        dept = get_department_for_item(item_name)
        c.execute("SELECT period, limit_amount, used_amount FROM budgets WHERE dept = ? ORDER BY period DESC LIMIT 1", (dept,))
        budget = c.fetchone()
        if budget:
            remaining = budget['limit_amount'] - budget['used_amount']
            if total_cost > remaining:
                failures.append(
                    f"Budget: Order cost ${total_cost:,.2f} exceeds remaining budget "
                    f"${remaining:,.2f} for dept '{dept}' ({budget['period']})."
                )
            else:
                warnings.append(
                    f"Budget: ${total_cost:,.2f} within budget. Remaining after order: "
                    f"${remaining - total_cost:,.2f} ({dept}, {budget['period']})."
                )
        else:
            warnings.append(f"Budget: No budget record found for '{dept}' — check skipped.")

        # ── Check 3: Policies ───────────────────────────
        c.execute("SELECT value FROM policies WHERE key = 'max_single_order_amount'")
        row = c.fetchone()
        if row and total_cost > float(row['value']):
            failures.append(
                f"Policy: Order amount ${total_cost:,.2f} exceeds single-order limit of ${float(row['value']):,.2f}."
            )

        c.execute("SELECT value FROM policies WHERE key = 'min_vendor_score'")
        row = c.fetchone()
        if row and vendor_id:
            min_score = float(row['value'])
            c.execute("SELECT name, ext_score, approved FROM vendors WHERE id = ?", (vendor_id,))
            vendor = c.fetchone()
            if vendor:
                if not vendor['approved']:
                    failures.append(f"Policy: Vendor '{vendor['name']}' is not approved.")
                if vendor['ext_score'] < min_score:
                    failures.append(
                        f"Policy: Vendor '{vendor['name']}' score {vendor['ext_score']} "
                        f"is below minimum {min_score}."
                    )
    finally:
        conn.close()

    return {'passed': len(failures) == 0, 'failures': failures, 'warnings': warnings}


def explain_compliance_result(analysis: dict, gate_result: dict) -> str:
    """
    Uses LLM to explain compliance result in plain English with recommendations.
    Returns a user-friendly narrative string.
    """
    passed     = gate_result['passed']
    failures   = gate_result.get('failures', [])
    warnings   = gate_result.get('warnings', [])
    item_name  = analysis.get('item_name', 'the requested item')
    total_cost = analysis.get('total_cost', 0) or 0
    priority   = analysis.get('priority', 'Unknown')

    status_str = "PASSED" if passed else "FAILED"
    failures_str = "\n".join(f"- {f}" for f in failures) if failures else "None"
    warnings_str = "\n".join(f"- {w}" for w in warnings) if warnings else "None"

    prompt = f"""You are a procurement compliance officer. 
Explain the compliance result for a purchase request clearly and professionally.

REQUEST DETAILS:
- Item: {item_name}
- Total Cost: ${total_cost:,.2f}
- Priority: {priority}

COMPLIANCE STATUS: {status_str}
FAILURES:
{failures_str}
WARNINGS:
{warnings_str}

Write a concise 2-4 sentence explanation:
1. State whether the request passed or failed, and why.
2. If failed, give a clear recommendation (e.g., split order, switch vendor, request budget override).
3. If passed with warnings, briefly mention them.
Keep it professional and direct. Do NOT use bullet points."""

    try:
        response = compliance_llm.invoke([
            SystemMessage(content="You are a professional procurement compliance officer. Respond in plain English only, no JSON, no bullet points."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        # Fallback to raw summary if LLM fails
        if passed:
            return f"Compliance passed for '{item_name}'. {' '.join(warnings)}"
        else:
            return f"Compliance failed for '{item_name}': {' '.join(failures)}"
