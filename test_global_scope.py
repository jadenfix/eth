#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simulate the global initialization
from services.analytics.predictive_analytics import PredictiveAnalytics

# Initialize analytics services (like in the API)
predictive_analytics = PredictiveAnalytics()

async def test_global_scope():
    """Test if global variable is accessible"""
    try:
        print("Testing global scope...")
        
        # Test if global variable is accessible
        print(f"Global predictive_analytics: {predictive_analytics}")
        print(f"Type: {type(predictive_analytics)}")
        
        # Test the method
        report = await predictive_analytics.generate_predictions("24h")
        print("✅ Global scope test successful")
        print(f"Report ID: {report.report_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in global scope test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_global_scope()) 