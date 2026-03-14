import flet as ft
import asyncio
import json

from data_analyzer import analyze_seasonality
from llm_agent import generate_report

def main(page: ft.Page):
    page.title = "Supply Chain Seasonal Trend Forecaster"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.bgcolor = "#f4f6f8"
    
    # UI Elements
    header = ft.Text("Seasonal Trend Analysis", size=32, weight=ft.FontWeight.BOLD, color="#2c3e50")
    subtitle = ft.Text("Analyze historical orders and generate an AI-powered supply chain report.", color="#7f8c8d", size=16)
    
    progress_ring = ft.ProgressRing(visible=False, width=24, height=24)
    status_text = ft.Text("Ready", color="#7f8c8d", italic=True)
    
    report_container = ft.Container(
        expand=True,
        border=ft.Border.all(1, "#dde1e5"),
        border_radius=8,
        bgcolor="#ffffff",
        padding=20,
        content=ft.Column(
            [ft.Icon("analytics", size=48, color="#bdc3c7"), ft.Text("Report will appear here.", color="#bdc3c7", size=18)], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
    )

    async def run_analysis(e):
        generate_btn.disabled = True
        progress_ring.visible = True
        status_text.value = "Analyzing data (Math Engine)..."
        report_container.content = ft.Column(
            [ft.ProgressRing(), ft.Text("Analyzing data...", size=16, color="#7f8c8d")], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        page.update()
        
        # 1. Run Data Analyzer
        stats = await asyncio.to_thread(analyze_seasonality)
        stats_json = json.dumps(stats, indent=2)
        
        # Display Prophet output before LLM
        interim_md = f"### Prophet Model Output (Math Engine)\n\n```json\n{stats_json}\n```\n\n---\n\n*Generating LLM analysis... Please wait...*"
        report_container.content = ft.Column(
            [
                ft.ProgressRing(), 
                ft.Markdown(interim_md, selectable=True, extension_set="gitHubWeb")
            ], 
            alignment=ft.MainAxisAlignment.START, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )
        status_text.value = "Generating Report (LLM Agent)..."
        page.update()
        
        # 2. Run LLM Agent
        html_report = await asyncio.to_thread(generate_report, stats_json)
        
        status_text.value = "Analysis Complete!"
        progress_ring.visible = False
        generate_btn.disabled = False
        
        # 3. Render final Markdown
        report_container.content = ft.Column(
            [ft.Markdown(html_report, selectable=True, extension_set="gitHubWeb")],
            scroll=ft.ScrollMode.AUTO
        )
        page.update()

    generate_btn = ft.FilledButton(
        "Generate Trend Report", 
        icon="document_scanner",
        style=ft.ButtonStyle(
            color="#ffffff",
            bgcolor="#3498db",
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=run_analysis
    )

    # Layout structuring
    page.add(
        ft.Row([header], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([subtitle], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=10),
        ft.Row([generate_btn, progress_ring, status_text], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=30, color="transparent"),
        report_container
    )

if __name__ == "__main__":
    ft.run(main=main)
