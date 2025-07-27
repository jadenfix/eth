"""
Advanced Analytics Service Package

This package provides comprehensive analytics capabilities including:
- Advanced Risk Analytics with anomaly detection
- Predictive Analytics with ML models
- Custom Reporting Engine with templates
- Data export capabilities

Modules:
- advanced_analytics: Risk analytics and anomaly detection
- predictive_analytics: ML-based predictions and forecasting
- custom_reports: Template-based reporting system
- analytics_api: REST API for analytics services
"""

from .advanced_analytics import AdvancedAnalytics, AnalyticsReport, RiskMetric
from .predictive_analytics import PredictiveAnalytics, PredictiveReport, Prediction
from .custom_reports import CustomReportingEngine, ReportTemplate, CustomReport

__all__ = [
    'AdvancedAnalytics',
    'AnalyticsReport', 
    'RiskMetric',
    'PredictiveAnalytics',
    'PredictiveReport',
    'Prediction',
    'CustomReportingEngine',
    'ReportTemplate',
    'CustomReport'
] 