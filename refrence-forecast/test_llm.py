import asyncio
import json
from data_analyzer import analyze_seasonality
from llm_agent import generate_report

async def test_run():
    print("Testing data analyzer...")
    stats = analyze_seasonality()
    print(f"Stats: {stats}")
    
    print("\nTesting LLM Agent...")
    stats_json = json.dumps(stats, indent=2)
    html_report = generate_report(stats_json)
    
    print("\nHTML Report Output (First 500 chars):")
    print(html_report[:500] if html_report else "NO OUTPUT GENERATED")

if __name__ == "__main__":
    asyncio.run(test_run())
