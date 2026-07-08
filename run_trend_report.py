"""
Trend Report Generator - Standalone
Generates only the fashion trend report without inventory analysis
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path
import traceback

# Add src to path to allow for importing from the 'src' directory
src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables BEFORE importing any local modules that need them
load_dotenv()

# Now that the path and env vars are set, we can import the agent
try:
    from agents.trend_agent import TrendAgent
except ImportError:
    print("ERROR: Could not import TrendAgent. Ensure 'src/agents/trend_agent.py' exists.")
    sys.exit(1)

def main():
    """
    Main function to generate and save the trend report.
    """
    print("Trend Report Generator")
    print("======================")
    
    print("\nConfiguration Check:")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    print(f"  - Project: {project}")
    print(f"  - Location: {location}\n")

    if not project or not location:
        print("ERROR: GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set in the .env file.")
        return

    print("Initializing agents and services...")
    try:
        # Instantiate the agent here, after env vars are loaded
        trend_agent = TrendAgent()
    except Exception as e:
        print(f"ERROR: Failed to initialize TrendAgent: {e}")
        return
    
    print("\nGenerating trend report for January 2026...")
    
    try:
        trends = trend_agent.get_daily_trends()
        
        if not trends:
            print("ERROR: No trends were generated. The LLM may have returned an empty or invalid response.")
            return

        report = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_period": "January 2026",
            "trend_count": len(trends),
            "trends": trends
        }

        output_filename = os.path.join('src', 'trends_report_jan_2026.json')
        with open(output_filename, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"\nSUCCESS: Report saved to {output_filename}")

        markdown_summary = "## January 2026 Men's Fashion Trend Report\n\n"
        for trend in trends:
            markdown_summary += f"- **{trend.get('trend_name', 'N/A')}**: {trend.get('description', 'No description provided.')}\n"
        
        summary_filename = "trends_report_jan_2026.md"
        with open(summary_filename, 'w') as f:
            f.write(markdown_summary)
            
        print(f"SUCCESS: Markdown summary saved to {summary_filename}")

    except Exception as e:
        print(f"ERROR: An unexpected error occurred during trend generation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
