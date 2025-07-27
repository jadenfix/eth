#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_predictive_direct():
    """Test the predictive analytics service directly"""
    try:
        print("Testing predictive analytics service directly...")
        
        from services.analytics.predictive_analytics import PredictiveAnalytics
        
        print("✅ Import successful")
        
        # Initialize the service
        predictive_analytics = PredictiveAnalytics()
        print("✅ Service initialized")
        
        # Test the generate_predictions method
        report = await predictive_analytics.generate_predictions("24h")
        print("✅ Predictions generated successfully")
        print(f"Report ID: {report.report_id}")
        print(f"Number of predictions: {len(report.predictions)}")
        print(f"Number of alerts: {len(report.alerts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing predictive analytics service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_predictive_direct()) 