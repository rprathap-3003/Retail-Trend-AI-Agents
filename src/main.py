import os
import json
import logging
from dotenv import load_dotenv

from pathlib import Path

# Robust path handling - supports execution from root or src/
current_file = Path(__file__).resolve()
env_path = current_file.parent.parent / ".env"

if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

# Verify Vertex AI configuration
print("🔵 Checking Vertex AI configuration...")
if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    print("❌ ERROR: GOOGLE_CLOUD_PROJECT not found in environment.")
    print("   Please set GOOGLE_CLOUD_PROJECT in your .env file.")
    print("   Example: GOOGLE_CLOUD_PROJECT=sandbox-7940")
    exit(1)

print(f"✅ Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
print(f"✅ Location: {os.getenv('GOOGLE_CLOUD_LOCATION', 'us-east4')}")
print("✅ Authentication: Using Application Default Credentials (OAuth2)")
print()

from services.generator import generator
from services.vector_store import vector_store
from agents.trend_agent import trend_agent
from agents.inventory_agent import inventory_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_or_generate_data():
    # Check for enhanced flower inventory first
    if os.path.exists("data/inventory_with_flowers.json"):
        logging.info("Loading enhanced inventory with flower items...")
        with open("data/inventory_with_flowers.json", "r") as f:
            inventory = json.load(f)
    elif os.path.exists("data/inventory.json"):
        logging.info("Loading existing inventory...")
        with open("data/inventory.json", "r") as f:
            inventory = json.load(f)
        # Generate flower-themed test images
        generator.generate_images(inventory)
        # Reload the enhanced inventory
        with open("data/inventory_with_flowers.json", "r") as f:
            inventory = json.load(f)
    else:
        logging.info("No data found. Generating synthetic inventory...")
        inventory = generator.generate_inventory(count=50)
        # Generate flower-themed test images
        generator.generate_images(inventory)
        # Reload the enhanced inventory
        with open("data/inventory_with_flowers.json", "r") as f:
            inventory = json.load(f)
    
    return inventory

def format_trends_report(trends):
    """Format the trends report for management/buyers"""
    report = "\n" + "="*70 + "\n"
    report += "   JANUARY 2026 FASHION TRENDS REPORT\n"
    report += "   Source: Web Research & Social Media Analysis\n"
    report += "   Date: January 10, 2026\n"
    report += "="*70 + "\n\n"
    
    report += "EXECUTIVE SUMMARY:\n"
    report += f"• Total trends identified: {len(trends)}\n"
    report += "• Sources: Google Search, DuckDuckGo, Fashion Blogs, Social Media\n"
    report += "• Data Period: December 10, 2025 - January 10, 2026\n\n"
    
    # Group by category
    categories = {}
    for trend in trends:
        cat = trend.get('category', 'Other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(trend)
    
    for category, items in categories.items():
        report += f"\n{'='*50}\n"
        report += f"   {category.upper()} TRENDS ({len(items)} items)\n"
        report += f"{'='*50}\n"
        
        for i, trend in enumerate(items, 1):
            report += f"\n{i:2d}. {trend.get('name', 'Unknown')}\n"
            report += f"    Colors: {', '.join(trend.get('colors', []))}\n"
            report += f"    Style: {trend.get('description', 'N/A')}\n"
            if trend.get('pattern_details'):
                report += f"    Pattern: {trend.get('pattern_details')}\n"
            report += "-" * 40 + "\n"
    
    return report

def format_replenishment_report(recommendations):
    """Format the replenishment report for purchasing team"""
    report = "\n" + "="*70 + "\n"
    report += "   URGENT REPLENISHMENT ORDERS - PURCHASING DEPARTMENT\n"
    report += "   Date: January 10, 2026\n"
    report += "="*70 + "\n\n"
    
    # Separate by priority
    urgent_items = []
    replenish_items = []
    
    for rec in recommendations:
        if rec.get('action') == 'URGENT BUY':
            urgent_items.append(rec)
        elif rec.get('action') == 'REPLENISH':
            replenish_items.append(rec)
    
    if urgent_items:
        report += "🚨 CRITICAL - ORDER IMMEDIATELY (Stock: 0-5 units)\n"
        report += "="*50 + "\n"
        for item in urgent_items:
            analysis_method = item.get('analysis_method', 'DESCRIPTION')
            confidence = item.get('match_confidence', 0)
            analysis_icon = "🖼️ AI Image Analysis" if analysis_method == 'IMAGE_AI' else "📝 Description Match"
            
            report += f"• {item.get('trend', 'Unknown')}\n"
            report += f"  Match Method: {analysis_icon} ({confidence:.0f}% confidence)\n"
            report += f"  Reason: {item.get('reason', 'High demand trend')}\n"
            report += f"  Current Stock: {item.get('stock_level', 0)} units\n"
            report += f"  RECOMMENDED ORDER: 200 units\n"
            
            # Add image analysis details if available
            if analysis_method == 'IMAGE_AI' and item.get('image_analysis'):
                img_data = item['image_analysis']
                report += f"  🎨 AI Detected: {', '.join(img_data.get('colors_detected', []))}\n"
                report += f"  🖌️ Patterns: {', '.join(img_data.get('patterns_detected', []))}\n"
            
            report += "-" * 30 + "\n"
    
    if replenish_items:
        report += "\n⚠️ MEDIUM PRIORITY - ORDER WITHIN 7 DAYS (Stock: 5-50 units)\n"
        report += "="*50 + "\n"
        for item in replenish_items:
            analysis_method = item.get('analysis_method', 'DESCRIPTION')
            confidence = item.get('match_confidence', 0)
            analysis_icon = "🖼️ AI Image Analysis" if analysis_method == 'IMAGE_AI' else "📝 Description Match"
            
            report += f"• {item.get('trend', 'Unknown')}\n"
            report += f"  Match Method: {analysis_icon} ({confidence:.0f}% confidence)\n"
            report += f"  Reason: {item.get('reason', 'Moderate demand trend')}\n"
            report += f"  Current Stock: {item.get('stock_level', 0)} units\n"
            report += f"  RECOMMENDED ORDER: 50 units\n"
            
            # Add image analysis details if available
            if analysis_method == 'IMAGE_AI' and item.get('image_analysis'):
                img_data = item['image_analysis']
                report += f"  🎨 AI Detected: {', '.join(img_data.get('colors_detected', []))}\n"
                report += f"  🖌️ Patterns: {', '.join(img_data.get('patterns_detected', []))}\n"
            
            report += "-" * 30 + "\n"
    
    # New Product Opportunities
    new_opportunities = [r for r in recommendations if r.get('action') == 'NEW PRODUCT OPPORTUNITY']
    if new_opportunities:
        report += "\n✨ NEW PRODUCT OPPORTUNITIES (Trends with No Inventory)\n"
        report += "="*50 + "\n"
        for item in new_opportunities:
             report += f"• {item.get('trend', 'Unknown')}\n"
             report += f"  Status: {item.get('action')}\n"
             report += f"  Reason: {item.get('reason')}\n"
             report += f"  Suggest: Sourcing team to review '{item.get('trend', '')}' for potential addition.\n"
             report += "-" * 30 + "\n"
    
    # Summary
    total_urgent = len(urgent_items)
    total_replenish = len(replenish_items)
    image_analyzed = len([r for r in recommendations if r.get('analysis_method') == 'IMAGE_AI'])
    
    report += f"\nORDER SUMMARY:\n"
    report += f"• Critical Orders: {total_urgent} items\n"
    report += f"• Medium Priority: {total_replenish} items\n"
    report += f"• Total Items to Order: {total_urgent + total_replenish}\n"
    report += f"• 🖼️ Items Identified via AI Image Analysis: {image_analyzed}\n"
    
    return report

def format_store_display_report(recommendations):
    """Format the store display report for sales associates"""
    report = "\n" + "="*70 + "\n"
    report += "   STORE DISPLAY GUIDE - SALES ASSOCIATES\n"
    report += "   January 2026 Trend-Based Merchandising\n"
    report += "="*70 + "\n\n"
    
    # Get top 5 trending items regardless of action type, prioritizing AI matches
    sorted_recs = sorted(recommendations, 
                        key=lambda x: (x.get('analysis_method') == 'IMAGE_AI', x.get('match_confidence', 0)),
                        reverse=True)[:5]
    
    report += "🏆 TOP 5 TRENDING ITEMS - Feature These!\n"
    report += "="*50 + "\n"
    
    if sorted_recs:
        for i, item in enumerate(sorted_recs, 1):
            analysis_method = item.get('analysis_method', 'DESCRIPTION')
            confidence = item.get('match_confidence', 0)
            stock_level = item.get('stock_level', 0)
            analysis_icon = "🖼️" if analysis_method == 'IMAGE_AI' else "📝"
            action_icon = "🚨" if item['action'] == 'URGENT BUY' else "⚠️" if item['action'] == 'REPLENISH' else "✅"
            
            report += f"{i}. {analysis_icon} {item.get('trend', 'Unknown')}\n"
            report += f"   Item: {item['matched_item']['name']}\n"
            report += f"   Status: {action_icon} {item['action']} - Stock: {stock_level} units\n"
            report += f"   Match: {confidence:.0f}% confidence ({analysis_method.replace('_', ' ').title()})\n"
            report += f"   Price: ${item['matched_item']['price']}\n"
            
            # Add image analysis insights for better selling
            if analysis_method == 'IMAGE_AI' and item.get('image_analysis'):
                img_data = item['image_analysis']
                colors = img_data.get('colors_detected', [])
                patterns = img_data.get('patterns_detected', [])
                matching_elements = img_data.get('matching_elements', [])
                
                if colors:
                    report += f"   🎨 Highlight Colors: {', '.join(colors[:3])}\n"
                if patterns:
                    report += f"   🖌️ Key Patterns: {', '.join(patterns[:2])}\n"
                if matching_elements:
                    report += f"   💡 Selling Points: {', '.join(matching_elements[:2])}\n"
            else:
                report += f"   💡 Selling Points: Trending style, high demand\n"
            
            # Specific display tips based on action
            if item['action'] == 'URGENT BUY':
                report += f"   📋 Display Tip: Last chance sale! Create urgency with limited stock signage\n"
            elif item['action'] == 'REPLENISH':
                report += f"   📋 Display Tip: Feature prominently - restocking soon\n"
            else:
                report += f"   📋 Display Tip: Feature prominently with good lighting\n"
            
            report += "\n"
    else:
        report += "• No trending items found for display\n\n"
    # Add general merchandising tips
    report += "\n" + "="*50 + "\n"
    report += "MERCHANDISING TIPS:\n"
    image_analyzed_count = len([r for r in recommendations if r.get('analysis_method') == 'IMAGE_AI'])
    
    report += f"• 🖼️ {image_analyzed_count} items verified by AI image analysis\n"
    report += "• Group similar colors and patterns together for visual impact\n"
    report += "• Use proper lighting to highlight textures and patterns\n"
    report += "• Cross-sell accessories with suits and shirts\n"
    report += "• Keep high-confidence items at eye level\n"
    report += "• Update displays weekly based on AI analysis results\n"
    
    return report

def format_report(recommendations):
    """Legacy function - kept for compatibility"""
    report = "\n" + "="*50 + "\n"
    report += "   MEN'S WEARHOUSE - TREND & REPLENISHMENT REPORT   \n"
    report += "="*50 + "\n\n"
    
    for rec in recommendations:
        report += f"TREND: {rec['trend']}\n"
        report += f"  - Status: {rec['action']}\n"
        report += f"  - Details: {rec['reason']}\n"
        if "suggested_buy" in rec:
            report += f"  - ACTION: Order {rec['suggested_buy']} units immediately.\n"
        report += "-"*30 + "\n"
        
    return report

def main():
    print("Retail Trend AI - Initializing...")
    
    # 1. Data Setup
    inventory = load_or_generate_data()
    
    # 2. Enhanced Vector DB Ingestion with CLIP embeddings
    print("🚀 Initializing Enhanced Vector DB with CLIP embeddings...")
    vector_store.initialize_db(inventory)
    
    # 2a. Generate Image Analysis Report
    print("\n--- BULK IMAGE ANALYSIS ---\n")
    try:
        # Cluster inventory by visual similarity
        cluster_results = inventory_agent.cluster_inventory(n_clusters=5)
        if cluster_results:
            print("📊 INVENTORY CLUSTERS (Visual Similarity):")
            for cluster_id, stats in cluster_results.get('clusters', {}).items():
                print(f"  Cluster {cluster_id}: {stats['size']} items, "
                      f"avg similarity: {stats['avg_similarity']:.1%}")
                      
            # Save cluster analysis
            with open("inventory_clusters.json", "w", encoding='utf-8') as f:
                json.dump(cluster_results, f, indent=2)
            print("💾 Cluster analysis saved to 'inventory_clusters.json'")
        
        # Find similar products for our test items
        test_items = ["FLOWER-008", "FLOWER-009"]  # Our generic items with specific images
        for item_id in test_items:
            similar = inventory_agent.find_similar_products(item_id, k=3)
            if similar:
                print(f"\n🔍 Items similar to {item_id}:")
                for sim_item in similar[:2]:  # Show top 2
                    print(f"  • {sim_item.get('text', 'N/A')[:50]}... "
                          f"(similarity: {sim_item['similarity']:.1%})")
                          
    except Exception as e:
        print(f"⚠️ Image analysis skipped: {e}")
    
    # 3. Analyze Trends
    print("\n--- ANALYZING JAN 2026 TRENDS ---\n")
    trends = trend_agent.get_daily_trends()
    print(f"\nFound {len(trends)} trends.\n")
    
    # 3a. Display Detailed Trends Report
    print("\n" + "="*60)
    print("   TOP 25 FASHION TRENDS - JANUARY 2026")
    print("="*60)
    
    for i, trend in enumerate(trends, 1):
        print(f"\n{i:2d}. {trend.get('name', 'Unknown Trend')}")
        print(f"    Category: {trend.get('category', 'N/A')}")
        print(f"    Style: {trend.get('description', 'N/A')}")
        print(f"    Colors: {', '.join(trend.get('colors', []))}")
        if trend.get('pattern_details'):
            print(f"    Pattern: {trend.get('pattern_details')}")
        print("-" * 50)
    
    print(f"\nTotal trends identified: {len(trends)}")
    print("\\nNow checking inventory for these trends...")
    
    # 4. Enhanced Inventory Check with CLIP + Gemini Vision
    print("\n--- ENHANCED INVENTORY ANALYSIS (CLIP + Gemini Vision) ---\n")
    recommendations = inventory_agent.check_trends_against_inventory(trends)
    
    # 5. Generate Three Separate Reports
    print("\n--- GENERATING REPORTS ---\n")
    
    # Report 1: Trends Report (for management/buyers)
    trends_report = format_trends_report(trends)
    with open("trends_report_jan_2026.txt", "w", encoding='utf-8') as f:
        f.write(trends_report)
    print("📊 Trends Report saved to 'trends_report_jan_2026.txt'")
    
    # Report 2: Replenishment Report (for purchasing team)
    replenishment_report = format_replenishment_report(recommendations)
    with open("replenishment_orders.txt", "w", encoding='utf-8') as f:
        f.write(replenishment_report)
    print("📦 Replenishment Report saved to 'replenishment_orders.txt'")
    
    # Report 3: Store Display Report (for sales associates)
    display_report = format_store_display_report(recommendations)
    with open("store_display_guide.txt", "w", encoding='utf-8') as f:
        f.write(display_report)
    print("🏪 Store Display Guide saved to 'store_display_guide.txt'")
    
    # Legacy combined report
    combined_report = format_report(recommendations)
    with open("trend_report.txt", "w", encoding='utf-8') as f:
        f.write(combined_report)
    
    # --- export data for web dashboard --- (ADDED)
    print("🌐 Exporting data for Web Dashboard...")
    dashboard_data = {
        "metadata": {
            "date": "January 10, 2026",
            "source": "Retail Trend AI"
        },
        "trends": trends,
        "recommendations": recommendations,
        "cluster_results": cluster_results if 'cluster_results' in locals() else {}
    }
    
    # Helper to convert non-serializable objects (like Pydantic models or NumPy types)
    def json_serial(obj):
        if hasattr(obj, 'dict'):
            return obj.dict()
        if hasattr(obj, 'tolist'):
             return obj.tolist()
        return str(obj)

    # Use explicit absolute path based on known project structure
    # This ensures it goes to C:\Hackathon\retail_trend_ai\data
    base_dir = r"C:\Hackathon\retail_trend_ai"
    data_dir = os.path.join(base_dir, "data")
    output_path = os.path.join(data_dir, "dashboard_data.json")
    
    # Ensure directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"📊 Saving dashboard data to: {output_path}")
    try:
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(dashboard_data, f, default=json_serial, indent=2)
        print(f"✅ Success! Dashboard data saved.")
    except Exception as e:
        print(f"❌ Error saving dashboard data: {e}")
        # Fallback to current directory if absolute fails
        with open("dashboard_data.json", "w", encoding='utf-8') as f:
            json.dump(dashboard_data, f, default=json_serial, indent=2)
        print("⚠️ Saved to local directory instead due to error.")
    # -------------------------------------
    
    print("\n✅ All reports generated successfully!")
    
    # Enhanced summary with AI metrics
    clip_analyzed = len([r for r in recommendations if r.get('detailed_method', '').startswith('CLIP')])
    gemini_analyzed = len([r for r in recommendations if r.get('detailed_method', '').startswith('GEMINI')])
    
    print("\nREPORT SUMMARY:")
    print(f"• {len(trends)} trends analyzed from web research")
    print(f"• {len([r for r in recommendations if r.get('action') == 'URGENT BUY'])} critical replenishment items")
    print(f"• {len([r for r in recommendations if r.get('action') == 'REPLENISH'])} medium priority items")
    print(f"• {len([r for r in recommendations if r.get('action') == 'PROMOTE'])} items ready for prominent display")
    print(f"• 🖼️ CLIP embedding analysis: {clip_analyzed} items")
    print(f"• 🔍 Gemini Vision fallback: {gemini_analyzed} items")
    
    if cluster_results:
        print(f"• 📊 Inventory clustered into {cluster_results.get('n_clusters', 0)} visual groups")

if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        traceback.print_exc()
