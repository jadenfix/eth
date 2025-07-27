#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_async_init():
    """Test async initialization of predictive analytics"""
    try:
        print("Testing async initialization...")
        
        from services.analytics.predictive_analytics import PredictiveAnalytics
        print("✅ Import successful")
        
        # Test global initialization
        predictive_analytics = PredictiveAnalytics()
        print("✅ Global initialization successful")
        
        # Test async method
        report = await predictive_analytics.generate_predictions("24h")
        print("✅ Async method successful")
        print(f"Report ID: {report.report_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in async initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_async_init()) 