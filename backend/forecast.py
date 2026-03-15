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
            
        return findings

    except Exception as e:
        return {"error": f"Failed to analyze data: {str(e)}"}


def generate_forecast_report():
    """ Generates math stats then asks Ollama to format as Markdown. """
    stats_data = analyze_seasonality()
    
    if "error" in stats_data:
        return _generate_error_md("Data Analysis Error", stats_data["error"])

    stats_json = json.dumps(stats_data, indent=2)

    # Use the centralized dynamic configuration for consistency across agents
    model_name = get_current_model("forecast")
    
    try:
        client = ollama.Client() # Assumes default localhost:11434
        
        system_prompt = (
            "You are an expert Supply Chain Analyst. Your task is to analyze the provided "
            "seasonal trend data and generate a clear, highly readable Markdown report.\n"
            "Requirements:\n"
            "- Use proper Markdown formatting (headers like #, ##, bolding, lists, tables).\n"
            "- The output MUST be ONLY valid Markdown. Do NOT wrap the output in html tags.\n"
            "- Structure the report with a clear header, an executive summary, and a detailed breakdown of the trends.\n"
            "- Do not calculate new statistics, simply present the findings beautifully."
        )
        
        user_prompt = f"Please generate the Markdown report based on the following statistical data:\n\n{stats_json}"
        
        response = client.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        markdown_content = response['message']['content'].strip()
        
        return {
            "stats_json": stats_json,
            "markdown": markdown_content
        }
        
    except Exception as e:
        return {
           "stats_json": stats_json, 
           "error": True,
           "markdown": _generate_error_md("Ollama Agent Error", f"Could not connect to Ollama or process prompt. Details: {str(e)}")
        }

def _generate_error_md(title, message):
    """Helper to generate a styled error block as a proper response dict."""
    md = f"""# ❌ {title}

**Error Details:**
{message}
"""
    return {"error": True, "markdown": md.strip()}
