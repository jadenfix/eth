#!/usr/bin/env python3

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_global_init():
    """Test global initialization of predictive analytics"""
    try:
        print("Testing global initialization...")
        
        from services.analytics.predictive_analytics import PredictiveAnalytics
        print("✅ Import successful")
        
        # Test global initialization
        predictive_analytics = PredictiveAnalytics()
        print("✅ Global initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in global initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_global_init() 