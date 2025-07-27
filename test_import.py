#!/usr/bin/env python3

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports used in the analytics API"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from fastapi import FastAPI, HTTPException
        print("✅ FastAPI imports successful")
        
        from pydantic import BaseModel
        print("✅ Pydantic imports successful")
        
        from typing import Dict, List, Any, Optional
        print("✅ Typing imports successful")
        
        # Test analytics imports
        from services.analytics.advanced_analytics import AdvancedAnalytics
        print("✅ AdvancedAnalytics import successful")
        
        from services.analytics.predictive_analytics import PredictiveAnalytics
        print("✅ PredictiveAnalytics import successful")
        
        from services.analytics.custom_reports import CustomReportingEngine
        print("✅ CustomReportingEngine import successful")
        
        # Test service initialization
        advanced_analytics = AdvancedAnalytics()
        print("✅ AdvancedAnalytics initialization successful")
        
        predictive_analytics = PredictiveAnalytics()
        print("✅ PredictiveAnalytics initialization successful")
        
        custom_reports = CustomReportingEngine()
        print("✅ CustomReportingEngine initialization successful")
        
        print("✅ All imports and initializations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1) 