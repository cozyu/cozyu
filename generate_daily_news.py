import os
import sys
from datetime import datetime, timezone, timedelta

# Adjust path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.admin_page import collect_recent_news, generate_report
from github_storage import load_feeds, save_report

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)

    print("Loading feeds...")
    current_feeds = load_feeds()
    
    print("Collecting recent news (last 24 hours)...")
    articles = collect_recent_news(current_feeds, hours=24)
    
    if not articles:
        print("No articles found in the last 24 hours.")
        sys.exit(0)
        
    print(f"Collected {len(articles)} articles. Generating report...")
    report = generate_report(api_key, articles)
    
    KST = timezone(timedelta(hours=9))
    today_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    print("Saving report...")
    save_report(today_str, report)
    
    print("Daily report generated and saved successfully.")

if __name__ == "__main__":
    main()
