import pandas as pd
import json
from prophet import Prophet
import os

def analyze_seasonality():
    try:
        # Resolve paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        orders_path = os.path.join(base_dir, 'mock_orders.csv')
        items_path = os.path.join(base_dir, 'items.csv')
        
        # Load data
        if not os.path.exists(orders_path) or not os.path.exists(items_path):
            return {"error": "Mock data files not found. Please ensure mock_orders.csv and items.csv exist."}
            
        orders = pd.read_csv(orders_path)
        items = pd.read_csv(items_path)
        
        # Merge orders with items to get item names
        df = orders.merge(items, left_on='item_id', right_on='id')
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Aggregate quantity by item and month
        df['month'] = df['order_date'].dt.strftime('%B')
        df['month_num'] = df['order_date'].dt.month
        
        monthly_sales = df.groupby(['name', 'month', 'month_num'])['quantity'].sum().reset_index()
        
        findings = {}
        
        # Analyze top 15 items by total volume
        top_items = df.groupby('name')['quantity'].sum().nlargest(15).index
        
        for item in top_items:
            item_data = monthly_sales[monthly_sales['name'] == item].sort_values('month_num')
            if len(item_data) > 1:
                avg_sales = item_data['quantity'].mean()
                peak_month_row = item_data.loc[item_data['quantity'].idxmax()]
                peak_month = peak_month_row['month']
                peak_sales = peak_month_row['quantity']
                
                # Calculate percentage increase
                if avg_sales > 0:
                    pct_increase = ((peak_sales - avg_sales) / avg_sales) * 100
                    if pct_increase > 25: # Strong seasonal trend threshold
                        findings[item] = f"Demand spikes in {peak_month}, increasing by {pct_increase:.0f}% compared to the monthly average."
                        
        # Prophet trend decomposition on aggregate daily store sales
        try:
            daily_sales = df.groupby('order_date')['quantity'].sum().reset_index()
            # Prophet requires 'ds' and 'y' columns
            daily_sales.columns = ['ds', 'y']
            
            if len(daily_sales) >= 14:
                # Initialize Prophet model
                m = Prophet(daily_seasonality=False, yearly_seasonality=False)
                m.fit(daily_sales)
                
                # We can predict over the same dates to get the trend component
                forecast = m.predict(daily_sales)
                
                trend_start = forecast['trend'].iloc[0]
                trend_end = forecast['trend'].iloc[-1]
                trend_direction = "upward" if trend_end > trend_start else "downward"
                pct_change = abs((trend_end - trend_start) / trend_start) * 100 if trend_start != 0 else 0
                
                findings["Overall Store Trend"] = f"Prophet analysis shows an {trend_direction} volume trend of {pct_change:.0f}% over the analyzed period."
        except Exception as e:
            pass # Silently drop if Prophet fails on this particular small mock data
            
        return findings

    except Exception as e:
        return {"error": f"Failed to analyze data: {str(e)}"}

if __name__ == "__main__":
    print(json.dumps(analyze_seasonality(), indent=2))
