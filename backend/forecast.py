import pandas as pd
import json
from prophet import Prophet
import sqlite3
from pathlib import Path
import os
import ollama

from backend.agents.config import get_current_model

# DB Path matching database.py
DB_DIR = Path(__file__).resolve().parent / "data"
DB_NAME = str(DB_DIR / "procurement.db")

def analyze_seasonality():
    """ Runs mathematical Prophet analysis directly on SQLite orders table. """
    try:
        conn = sqlite3.connect(DB_NAME)
        
        # Pull required orders + item details joined
        query = '''
            SELECT o.created_at, o.qty, i.name 
            FROM orders o
            JOIN items i ON o.item_id = i.id
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
             return {"error": "No orders found in database to analyze."}

        df['created_at'] = pd.to_datetime(df['created_at'], format='mixed')
        
        # Aggregate quantity by item and month
        df['month'] = df['created_at'].dt.strftime('%B')
        df['month_num'] = df['created_at'].dt.month
        
        monthly_sales = df.groupby(['name', 'month', 'month_num'])['qty'].sum().reset_index()
        
        findings = {}
        
        # Analyze top 15 items by total volume
        top_items = df.groupby('name')['qty'].sum().nlargest(15).index
        
        for item in top_items:
            item_data = monthly_sales[monthly_sales['name'] == item].sort_values('month_num')
            if len(item_data) > 1:
                avg_sales = item_data['qty'].mean()
                peak_month_row = item_data.loc[item_data['qty'].idxmax()]
                peak_month = peak_month_row['month']
                peak_sales = peak_month_row['qty']
                
                # Calculate percentage increase
                if avg_sales > 0:
                    pct_increase = ((peak_sales - avg_sales) / avg_sales) * 100
                    if pct_increase > 25: # Strong seasonal trend threshold
                        findings[item] = f"Demand spikes in {peak_month}, increasing by {pct_increase:.0f}% compared to the monthly average."
                        
        # Prophet trend decomposition on aggregate daily store sales
        chart_data = [] # Data array specifically for Recharts
        top_items_data = monthly_sales[monthly_sales['name'].isin(top_items)]
        
        # We need a stable pivot for Recharts: rows are months, columns are item quantities
        if not top_items_data.empty:
            pivot = top_items_data.pivot_table(index='month_num', columns='name', values='qty', aggfunc='sum').fillna(0)
            
            # Month mapping
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                           7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
                           
            for month_num in pivot.index:
                row_dict = {"name": month_names.get(month_num, str(month_num))}
                for col in pivot.columns:
                    row_dict[col] = float(pivot.at[month_num, col])
                chart_data.append(row_dict)
                
        try:
            daily_sales = df.groupby(df['created_at'].dt.date)['qty'].sum().reset_index()
            daily_sales.columns = ['ds', 'y']
            
            if len(daily_sales) >= 14:
                # Initialize Prophet model
                m = Prophet(daily_seasonality=False, yearly_seasonality=False)
                m.fit(daily_sales)
                
                forecast = m.predict(daily_sales)
                
                trend_start = forecast['trend'].iloc[0]
                trend_end = forecast['trend'].iloc[-1]
                trend_direction = "upward" if trend_end > trend_start else "downward"
                pct_change = abs((trend_end - trend_start) / trend_start) * 100 if trend_start != 0 else 0
                
                findings["Overall Store Trend"] = f"Prophet analysis shows an {trend_direction} volume trend of {pct_change:.0f}% over the analyzed period."
        except Exception as e:
            pass # Silently drop if Prophet fails on small datasets
            
        return {"findings": findings, "chart_data": chart_data}

    except Exception as e:
        return {"error": f"Failed to analyze data: {str(e)}"}


def generate_forecast_report():
    """ Generates math stats then asks Ollama to format as Markdown. """
    analysis_result = analyze_seasonality()
    
    if "error" in analysis_result:
        return _generate_error_md("Data Analysis Error", analysis_result["error"])

    stats_data = analysis_result.get("findings", {})
    chart_data = analysis_result.get("chart_data", [])
    
    stats_json = json.dumps(stats_data, indent=2)

    # Use the centralized dynamic configuration for consistency across agents
    model_name = get_current_model("forecast")
    
    try:
        client = ollama.Client() # Assumes default localhost:11434
        
        system_prompt = (
            "You are a highly analytical structural agent. Your task is to process the raw Prophet data into a structured JSON payload.\n"
            "Return strictly a JSON object with the following exact schema:\n"
            "{\n"
            '  "executive_summary": "A comprehensive 2-3 sentence strategic executive overview string.",\n'
            '  "overall_trend": {"direction": "upward/downward", "percentage": "number as string", "analysis": "Detailed commentary string"},\n'
            '  "anomalies": [\n'
            '    {"item": "string", "insight": "string explaining what this means", "recommended_action": "Actionable procurement step", "severity": "High/Medium/Low"}\n'
            "  ]\n"
            "}\n"
            "Do not output markdown, NO code block wrappers, only the raw JSON."
        )
        
        user_prompt = f"Please map the following statistical data into the rigid JSON schema:\n\n{stats_json}"
        
        response = client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.1},
            format="json"
        )
        
        markdown_content = response['message']['content'].strip()
        
        # Clean up any potential markdown code block wrappers
        if markdown_content.startswith("```markdown"):
            markdown_content = markdown_content[11:].strip()
        if markdown_content.startswith("```"):
            markdown_content = markdown_content[3:].strip()
        if markdown_content.endswith("```"):
            markdown_content = markdown_content[:-3].strip()
            
        return {
            "stats_json": stats_json,
            "markdown": markdown_content,
            "chart_data": chart_data
        }
        
    except Exception as e:
        err_dict = _generate_error_md("Ollama Agent Error", f"Could not connect to Ollama or process prompt. Details: {str(e)}")
        err_dict["stats_json"] = stats_json
        return err_dict

def _generate_error_md(title, message):
    """Helper to generate a styled error block as a proper response dict."""
    md = f"""# ❌ {title}

**Error Details:**
{message}
"""
    return {"error": True, "markdown": md.strip()}
