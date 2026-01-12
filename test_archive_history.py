#!/usr/bin/env python3
"""
Test script for the new archive-heatmap functionality
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.benchmark_handler import get_evaluation_activity_by_date

async def test_archive_heatmap():
    """Test the archive heatmap functionality"""
    print("🧪 Testing Archive Heatmap Functionality")
    print("=" * 50)
    
    try:
        # Test the database function
        print("1. Testing get_evaluation_activity_by_date()...")
        activity_data = await get_evaluation_activity_by_date()
        
        print(f"✅ Successfully retrieved activity data")
        print(f"📊 Found activity for {len(activity_data)} days")
        
        if activity_data:
            print("\n📅 Sample activity data:")
            # Show first 5 entries
            for i, (date, count) in enumerate(list(activity_data.items())[:5]):
                print(f"   {date}: {count} evaluation{'s' if count != 1 else ''}")
            
            if len(activity_data) > 5:
                print(f"   ... and {len(activity_data) - 5} more days")
                
            # Show total evaluations
            total_evaluations = sum(activity_data.values())
            print(f"\n📈 Total evaluations: {total_evaluations}")
        else:
            print("ℹ️  No evaluation activity found in database")
            
        print("\n✅ Archive heatmap functionality test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing archive heatmap: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_archive_heatmap())