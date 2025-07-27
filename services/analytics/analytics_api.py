from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

from .advanced_analytics import AdvancedAnalytics, AnalyticsReport
from .predictive_analytics import PredictiveAnalytics, PredictiveReport
from .custom_reports import CustomReportingEngine, ReportTemplate, CustomReport
from .advanced_ml_analytics import advanced_analytics as ml_analytics

logger = logging.getLogger(__name__)

app = FastAPI(title="Advanced Analytics API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analytics services
advanced_analytics = AdvancedAnalytics()
predictive_analytics = PredictiveAnalytics()
custom_reports = CustomReportingEngine()

# Pydantic models for API requests/responses
class AnalyticsRequest(BaseModel):
    time_range: str = "24h"
    include_anomalies: bool = True
    include_visualizations: bool = True

class PredictiveRequest(BaseModel):
    horizon: str = "24h"
    include_alerts: bool = True
    include_feature_importance: bool = True

class ReportTemplateRequest(BaseModel):
    template_id: str
    name: str
    description: str
    metrics: List[str]
    visualizations: List[str]
    schedule: Optional[str] = None
    recipients: Optional[List[str]] = None

class CustomReportRequest(BaseModel):
    template_id: str
    time_range: str = "24h"
    custom_filters: Optional[Dict[str, Any]] = None

class ExportRequest(BaseModel):
    report_id: str
    format: str = "json"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analytics/risk")
async def generate_risk_analytics(request: AnalyticsRequest) -> Dict[str, Any]:
    """Generate comprehensive risk analytics report"""
    try:
        logger.info(f"Generating risk analytics for time range: {request.time_range}")
        
        report = await advanced_analytics.generate_risk_analytics(request.time_range)
        
        # Convert to dict for JSON response
        response = {
            "report_id": report.report_id,
            "report_type": report.report_type,
            "generated_at": report.generated_at.isoformat(),
            "time_range": report.time_range,
            "metrics": [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "status": m.status,
                    "trend": m.trend,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in report.metrics
            ],
            "insights": report.insights,
            "recommendations": report.recommendations
        }
        
        if request.include_visualizations:
            response["visualizations"] = report.visualizations
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating risk analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/predictive")
async def generate_predictions(request: PredictiveRequest) -> Dict[str, Any]:
    """Generate predictive analytics report"""
    try:
        logger.info(f"Generating predictions for horizon: {request.horizon}")
        
        logger.info("Generating predictions...")
        report = await predictive_analytics.generate_predictions(request.horizon)
        logger.info(f"Predictions generated successfully: {report.report_id}")
        
        # Convert to dict for JSON response
        response = {
            "report_id": report.report_id,
            "generated_at": report.generated_at.isoformat(),
            "predictions": [
                {
                    "metric_name": p.metric_name,
                    "current_value": p.current_value,
                    "predicted_value": p.predicted_value,
                    "confidence_interval": p.confidence_interval,
                    "prediction_horizon": p.prediction_horizon,
                    "timestamp": p.timestamp.isoformat(),
                    "model_accuracy": p.model_accuracy
                }
                for p in report.predictions
            ]
        }
        
        if request.include_alerts:
            response["alerts"] = report.alerts
        
        if request.include_feature_importance:
            response["feature_importance"] = report.feature_importance
        
        logger.info("Response prepared successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/templates")
async def create_report_template(request: ReportTemplateRequest) -> Dict[str, Any]:
    """Create a new report template"""
    try:
        logger.info(f"Creating report template: {request.template_id}")
        
        template = ReportTemplate(
            template_id=request.template_id,
            name=request.name,
            description=request.description,
            metrics=request.metrics,
            visualizations=request.visualizations,
            schedule=request.schedule,
            recipients=request.recipients
        )
        
        template_id = await custom_reports.create_report_template(template)
        
        return {
            "template_id": template_id,
            "status": "created",
            "message": f"Report template {template_id} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating report template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/templates")
async def list_report_templates() -> Dict[str, Any]:
    """List all available report templates"""
    try:
        templates = []
        for template_id, template in custom_reports.templates.items():
            templates.append({
                "template_id": template.template_id,
                "name": template.name,
                "description": template.description,
                "metrics": template.metrics,
                "visualizations": template.visualizations,
                "schedule": template.schedule,
                "recipients": template.recipients
            })
        
        return {
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error listing report templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/generate")
async def generate_custom_report(request: CustomReportRequest) -> Dict[str, Any]:
    """Generate a custom report based on template"""
    try:
        logger.info(f"Generating custom report for template: {request.template_id}")
        
        report = await custom_reports.generate_custom_report(
            request.template_id,
            request.time_range,
            request.custom_filters
        )
        
        # Convert to dict for JSON response
        response = {
            "report_id": report.report_id,
            "template_id": report.template_id,
            "generated_at": report.generated_at.isoformat(),
            "time_range": report.time_range,
            "data": report.data,
            "visualizations": report.visualizations,
            "export_formats": report.export_formats,
            "metadata": report.metadata
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating custom report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/export")
async def export_report(request: ExportRequest) -> Dict[str, Any]:
    """Export a report in specified format"""
    try:
        logger.info(f"Exporting report {request.report_id} in format: {request.format}")
        
        # Find the report in history
        report = None
        for r in custom_reports.report_history:
            if r.report_id == request.report_id:
                report = r
                break
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        export_data = await custom_reports.export_report(report, request.format)
        
        return {
            "report_id": request.report_id,
            "format": request.format,
            "export_data": export_data,
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/history")
async def get_report_history() -> Dict[str, Any]:
    """Get report generation history"""
    try:
        history = []
        for report in custom_reports.report_history:
            history.append({
                "report_id": report.report_id,
                "template_id": report.template_id,
                "generated_at": report.generated_at.isoformat(),
                "time_range": report.time_range,
                "export_formats": report.export_formats,
                "metadata": report.metadata
            })
        
        return {
            "reports": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting report history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/metrics")
async def get_available_metrics() -> Dict[str, Any]:
    """Get list of available analytics metrics"""
    metrics = [
        "transaction_volume",
        "average_gas_price", 
        "total_value_transferred",
        "unique_addresses",
        "failed_transaction_rate",
        "mev_opportunities",
        "suspicious_activity",
        "large_transfers"
    ]
    
    return {
        "metrics": metrics,
        "count": len(metrics)
    }

@app.get("/analytics/visualizations")
async def get_available_visualizations() -> Dict[str, Any]:
    """Get list of available visualization types"""
    visualizations = [
        "transaction_volume_chart",
        "gas_price_analysis",
        "risk_heatmap",
        "mev_timeline"
    ]
    
    return {
        "visualizations": visualizations,
        "count": len(visualizations)
    }

# Phase 6: Advanced ML Analytics Endpoints

class MLFraudRequest(BaseModel):
    transaction_data: List[Dict[str, Any]]

class MLAnomalyRequest(BaseModel):
    transaction_data: List[Dict[str, Any]]

class MLPredictionRequest(BaseModel):
    market_data: Dict[str, Any]

class PortfolioRiskRequest(BaseModel):
    portfolio_data: Dict[str, Any]

class CrossChainRequest(BaseModel):
    chains: Optional[List[str]] = None

class RegulatoryReportRequest(BaseModel):
    report_type: str
    period_days: int = 30

@app.post("/ml/fraud-detection")
async def detect_fraud_patterns(request: MLFraudRequest) -> Dict[str, Any]:
    """Detect fraud patterns using ML models"""
    try:
        logger.info(f"Analyzing {len(request.transaction_data)} transactions for fraud")
        
        fraud_predictions = await ml_analytics.detect_fraud_patterns(request.transaction_data)
        
        return {
            "predictions": [
                {
                    "prediction_id": pred.prediction_id,
                    "model_type": pred.model_type,
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "timestamp": pred.timestamp.isoformat(),
                    "metadata": pred.metadata
                }
                for pred in fraud_predictions
            ],
            "total_analyzed": len(request.transaction_data),
            "fraud_detected": sum(1 for pred in fraud_predictions if pred.prediction),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting fraud patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/anomaly-detection")
async def detect_anomalies(request: MLAnomalyRequest) -> Dict[str, Any]:
    """Detect anomalies using ML models"""
    try:
        logger.info(f"Analyzing {len(request.transaction_data)} transactions for anomalies")
        
        anomaly_predictions = await ml_analytics.detect_anomalies_batch(request.transaction_data)
        
        return {
            "predictions": [
                {
                    "prediction_id": pred.prediction_id,
                    "model_type": pred.model_type,
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "timestamp": pred.timestamp.isoformat(),
                    "metadata": pred.metadata
                }
                for pred in anomaly_predictions
            ],
            "total_analyzed": len(request.transaction_data),
            "anomalies_detected": sum(1 for pred in anomaly_predictions if pred.prediction),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/market-predictions")
async def predict_market_trends(request: MLPredictionRequest) -> Dict[str, Any]:
    """Predict market trends using ML models"""
    try:
        logger.info("Generating market trend predictions")
        
        predictions = await ml_analytics.predict_market_trends(request.market_data)
        
        return {
            "predictions": [
                {
                    "prediction_id": pred.prediction_id,
                    "model_type": pred.model_type,
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "timestamp": pred.timestamp.isoformat(),
                    "metadata": pred.metadata
                }
                for pred in predictions
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/portfolio-risk")
async def analyze_portfolio_risk(request: PortfolioRiskRequest) -> Dict[str, Any]:
    """Analyze portfolio risk using ML models"""
    try:
        logger.info(f"Analyzing portfolio risk for {request.portfolio_data.get('portfolio_id', 'unknown')}")
        
        analysis = await ml_analytics.analyze_portfolio_risk(request.portfolio_data)
        
        return {
            "portfolio_id": analysis.portfolio_id,
            "total_value": analysis.total_value,
            "risk_score": analysis.risk_score,
            "diversification_score": analysis.diversification_score,
            "concentration_risk": analysis.concentration_risk,
            "volatility_risk": analysis.volatility_risk,
            "recommendations": analysis.recommendations,
            "timestamp": analysis.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/cross-chain-analysis")
async def analyze_cross_chain_correlations(request: CrossChainRequest) -> Dict[str, Any]:
    """Analyze cross-chain correlations"""
    try:
        logger.info("Analyzing cross-chain correlations")
        
        analyses = await ml_analytics.analyze_cross_chain_correlations(request.chains)
        
        return {
            "analyses": [
                {
                    "analysis_id": analysis.analysis_id,
                    "chain_name": analysis.chain_name,
                    "correlation_score": analysis.correlation_score,
                    "shared_addresses": analysis.shared_addresses,
                    "cross_chain_volume": analysis.cross_chain_volume,
                    "risk_factors": analysis.risk_factors,
                    "timestamp": analysis.timestamp.isoformat()
                }
                for analysis in analyses
            ],
            "total_analyses": len(analyses),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing cross-chain correlations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ml/regulatory-report")
async def generate_regulatory_report(request: RegulatoryReportRequest) -> Dict[str, Any]:
    """Generate automated regulatory compliance report"""
    try:
        logger.info(f"Generating regulatory report: {request.report_type}")
        
        report = await ml_analytics.generate_regulatory_report(
            request.report_type, 
            request.period_days
        )
        
        return {
            "report_id": report.report_id,
            "report_type": report.report_type,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_transactions": report.total_transactions,
            "total_volume": report.total_volume,
            "risk_indicators": report.risk_indicators,
            "compliance_status": report.compliance_status,
            "generated_at": report.generated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating regulatory report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/model-performance")
async def get_model_performance() -> Dict[str, Any]:
    """Get performance metrics for all ML models"""
    try:
        logger.info("Getting ML model performance metrics")
        
        performances = await ml_analytics.get_model_performance_metrics()
        
        return {
            "models": {
                model_id: {
                    "accuracy": perf.accuracy,
                    "precision": perf.precision,
                    "recall": perf.recall,
                    "f1_score": perf.f1_score,
                    "last_updated": perf.last_updated.isoformat(),
                    "training_samples": perf.training_samples
                }
                for model_id, perf in performances.items()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ml/insights")
async def get_ml_insights() -> Dict[str, Any]:
    """Get insights from ML models"""
    try:
        logger.info("Generating ML insights")
        
        insights = await ml_analytics.generate_ml_insights()
        
        return {
            "fraud_detection_rate": insights.get("fraud_detection_rate", 0.0),
            "anomaly_detection_rate": insights.get("anomaly_detection_rate", 0.0),
            "prediction_accuracy": insights.get("prediction_accuracy", 0.0),
            "recommendations": insights.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating ML insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 