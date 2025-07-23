"""
Gemini 2-Pro Explainability Service
Provides natural language explanations for AI model decisions and trading signals
"""

import os
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

try:
    from google.cloud import aiplatform
    AIPLATFORM_AVAILABLE = True
except ImportError:
    AIPLATFORM_AVAILABLE = False
    aiplatform = None

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
VERTEX_AI_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
VERTEX_AI_REGION = os.getenv('VERTEX_AI_REGION', 'us-central1')

if GEMINI_API_KEY and GENAI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize Vertex AI
if AIPLATFORM_AVAILABLE:
    try:
        aiplatform.init(project=VERTEX_AI_PROJECT, location=VERTEX_AI_REGION)
    except Exception as e:
        logger.warning(f"Vertex AI initialization failed: {e}")
        aiplatform = None

app = FastAPI(
    title="Gemini Explainability Service",
    description="AI model decision explanations using Gemini 2-Pro",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SignalExplanationRequest(BaseModel):
    signal_hash: str = Field(..., description="Hash of the trading signal")
    signal_type: int = Field(..., ge=1, le=10, description="Signal type (1-10)")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score")
    model_version: str = Field(..., description="ML model version")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    explanation_type: str = Field(default="technical", description="Type of explanation: technical, business, regulatory")

class ModelExplanationRequest(BaseModel):
    model_hash: str = Field(..., description="Hash of the ML model")
    model_type: str = Field(..., description="Type of model (e.g., 'mev_detection', 'risk_assessment')")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="Model performance data")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")
    explanation_depth: str = Field(default="summary", description="Depth: summary, detailed, technical")

class ComplianceExplanationRequest(BaseModel):
    transaction_hash: str = Field(..., description="Transaction hash")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    regulatory_framework: str = Field(default="US", description="Regulatory framework to explain against")

class ExplanationResponse(BaseModel):
    explanation: str = Field(..., description="Natural language explanation")
    key_points: List[str] = Field(..., description="Key bullet points")
    confidence_assessment: str = Field(..., description="Assessment of explanation confidence")
    technical_details: Optional[Dict[str, Any]] = Field(None, description="Technical implementation details")
    regulatory_considerations: Optional[List[str]] = Field(None, description="Regulatory compliance notes")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

@dataclass
class ExplanationContext:
    """Context for generating explanations"""
    domain: str
    audience: str
    detail_level: str
    regulatory_framework: str = "US"

class GeminiExplainerService:
    def __init__(self):
        self.model = None
        self.vertex_model = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize Gemini models"""
        try:
            if GEMINI_API_KEY and GENAI_AVAILABLE and genai:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("Initialized Gemini 2-Pro model via API")
            
            # Initialize Vertex AI model as fallback
            if AIPLATFORM_AVAILABLE and aiplatform:
                try:
                    self.vertex_model = aiplatform.Model.list(
                        filter='display_name="gemini-2.0-flash-preview"'
                    )
                    if self.vertex_model:
                        logger.info("Initialized Gemini via Vertex AI")
                except Exception as e:
                    logger.warning(f"Vertex AI model listing failed: {e}")
                    self.vertex_model = None
                        
        except Exception as e:
            logger.error(f"Failed to initialize Gemini models: {str(e)}")
    
    async def generate_explanation(self, prompt: str, context: ExplanationContext) -> str:
        """Generate explanation using Gemini 2-Pro"""
        try:
            # Enhance prompt with context
            enhanced_prompt = self._build_enhanced_prompt(prompt, context)
            
            if self.model:
                response = await self._generate_via_api(enhanced_prompt)
            elif self.vertex_model:
                response = await self._generate_via_vertex(enhanced_prompt)
            else:
                raise HTTPException(status_code=503, detail="Gemini models not available")
            
            return response
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")
    
    def _build_enhanced_prompt(self, base_prompt: str, context: ExplanationContext) -> str:
        """Build enhanced prompt with context"""
        system_context = f"""
You are an expert AI system explainer specializing in {context.domain}.
Your audience: {context.audience}
Detail level: {context.detail_level}
Regulatory framework: {context.regulatory_framework}

Guidelines:
- Provide clear, accurate explanations
- Use appropriate technical depth for the audience
- Highlight key decision factors
- Include regulatory considerations when relevant
- Structure responses with clear sections
- Use bullet points for key insights
- Assess confidence in your explanation

Base query:
{base_prompt}
"""
        return system_context
    
    async def _generate_via_api(self, prompt: str) -> str:
        """Generate explanation via Gemini API"""
        if not GENAI_AVAILABLE or not genai:
            raise Exception("Gemini API not available")
            
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.2,
                    top_p=0.8,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API generation failed: {str(e)}")
            raise
    
    async def _generate_via_vertex(self, prompt: str) -> str:
        """Generate explanation via Vertex AI"""
        try:
            # Use the first available model
            model = self.vertex_model[0] if self.vertex_model else None
            if not model:
                raise Exception("No Vertex AI model available")
            
            endpoint = model.deploy(
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=1,
            )
            
            response = await asyncio.to_thread(
                endpoint.predict,
                instances=[{"prompt": prompt}]
            )
            
            return response.predictions[0]['content']
            
        except Exception as e:
            logger.error(f"Vertex AI generation failed: {str(e)}")
            raise

    async def explain_trading_signal(
        self, 
        request: SignalExplanationRequest
    ) -> ExplanationResponse:
        """Explain a trading signal decision"""
        
        prompt = f"""
Explain this AI-generated trading signal:

Signal Details:
- Signal Hash: {request.signal_hash}
- Signal Type: {request.signal_type} (1=buy, 2=sell, 3=hold, etc.)
- Confidence Score: {request.confidence}%
- Model Version: {request.model_version}
- Context: {json.dumps(request.context_data, indent=2) if request.context_data else 'None'}

Please explain:
1. What this signal means in trading terms
2. Why the AI model generated this recommendation
3. How the confidence score should be interpreted
4. Key factors likely influencing this decision
5. Risk considerations for acting on this signal
6. Regulatory compliance aspects
"""
        
        context = ExplanationContext(
            domain="algorithmic_trading",
            audience="traders_and_compliance",
            detail_level=request.explanation_type,
            regulatory_framework="US"
        )
        
        explanation = await self.generate_explanation(prompt, context)
        
        # Parse the explanation to extract structured data
        key_points = self._extract_key_points(explanation)
        confidence_assessment = self._assess_explanation_confidence(explanation, request.confidence)
        
        return ExplanationResponse(
            explanation=explanation,
            key_points=key_points,
            confidence_assessment=confidence_assessment,
            technical_details={
                "signal_hash": request.signal_hash,
                "model_version": request.model_version,
                "confidence_score": request.confidence
            },
            regulatory_considerations=self._extract_regulatory_notes(explanation)
        )
    
    async def explain_model_behavior(
        self, 
        request: ModelExplanationRequest
    ) -> ExplanationResponse:
        """Explain ML model behavior and decisions"""
        
        prompt = f"""
Explain this AI model's behavior and capabilities:

Model Details:
- Model Hash: {request.model_hash}
- Model Type: {request.model_type}
- Performance Metrics: {json.dumps(request.performance_metrics, indent=2) if request.performance_metrics else 'Not provided'}
- Feature Importance: {json.dumps(request.feature_importance, indent=2) if request.feature_importance else 'Not provided'}

Please explain:
1. What this model is designed to do
2. How it makes decisions (high-level algorithm approach)
3. What the performance metrics indicate
4. Which features are most important and why
5. Model limitations and edge cases
6. Appropriate use cases and risk considerations
7. Model governance and compliance aspects
"""
        
        context = ExplanationContext(
            domain="machine_learning",
            audience="technical_and_business",
            detail_level=request.explanation_depth
        )
        
        explanation = await self.generate_explanation(prompt, context)
        
        key_points = self._extract_key_points(explanation)
        confidence_assessment = self._assess_model_explanation_confidence(explanation, request.performance_metrics)
        
        return ExplanationResponse(
            explanation=explanation,
            key_points=key_points,
            confidence_assessment=confidence_assessment,
            technical_details={
                "model_hash": request.model_hash,
                "model_type": request.model_type,
                "performance_metrics": request.performance_metrics
            },
            regulatory_considerations=self._extract_regulatory_notes(explanation)
        )
    
    async def explain_compliance_assessment(
        self, 
        request: ComplianceExplanationRequest
    ) -> ExplanationResponse:
        """Explain compliance and risk assessment"""
        
        prompt = f"""
Explain this transaction risk assessment and compliance evaluation:

Transaction Details:
- Transaction Hash: {request.transaction_hash}
- Risk Score: {request.risk_score:.3f} (0=low risk, 1=high risk)
- Risk Factors: {', '.join(request.risk_factors)}
- Regulatory Framework: {request.regulatory_framework}

Please explain:
1. What this risk score means in regulatory terms
2. How each risk factor contributes to the overall assessment
3. Specific regulatory concerns under {request.regulatory_framework} framework
4. Recommended compliance actions
5. Potential legal or business implications
6. How to mitigate identified risks
7. Reporting requirements or obligations
"""
        
        context = ExplanationContext(
            domain="regulatory_compliance",
            audience="compliance_and_legal",
            detail_level="detailed",
            regulatory_framework=request.regulatory_framework
        )
        
        explanation = await self.generate_explanation(prompt, context)
        
        key_points = self._extract_key_points(explanation)
        confidence_assessment = self._assess_compliance_confidence(explanation, request.risk_score)
        
        return ExplanationResponse(
            explanation=explanation,
            key_points=key_points,
            confidence_assessment=confidence_assessment,
            technical_details={
                "transaction_hash": request.transaction_hash,
                "risk_score": request.risk_score,
                "risk_factors": request.risk_factors
            },
            regulatory_considerations=self._extract_regulatory_notes(explanation)
        )
    
    def _extract_key_points(self, explanation: str) -> List[str]:
        """Extract key bullet points from explanation"""
        lines = explanation.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                key_points.append(line.lstrip('•-*123456789. '))
        
        # Fallback: extract sentences with key phrases
        if not key_points:
            import re
            sentences = re.split(r'[.!?]+', explanation)
            for sentence in sentences[:5]:  # Take first 5 sentences
                if sentence.strip() and len(sentence.strip()) > 20:
                    key_points.append(sentence.strip())
        
        return key_points[:10]  # Limit to 10 key points
    
    def _assess_explanation_confidence(self, explanation: str, signal_confidence: int) -> str:
        """Assess confidence in the explanation quality"""
        confidence_indicators = [
            "specific" in explanation.lower(),
            "data" in explanation.lower(), 
            "analysis" in explanation.lower(),
            len(explanation) > 500,
            signal_confidence > 70
        ]
        
        score = sum(confidence_indicators) / len(confidence_indicators)
        
        if score >= 0.8:
            return "High confidence - detailed analysis with specific factors"
        elif score >= 0.6:
            return "Medium confidence - good overview with some specifics"
        else:
            return "Lower confidence - general explanation, limited specific details"
    
    def _assess_model_explanation_confidence(self, explanation: str, metrics: Optional[Dict]) -> str:
        """Assess confidence for model explanations"""
        has_metrics = metrics is not None and len(metrics) > 0
        has_technical_detail = any(term in explanation.lower() for term in 
                                 ['algorithm', 'feature', 'training', 'accuracy', 'precision'])
        
        if has_metrics and has_technical_detail:
            return "High confidence - detailed technical explanation with performance data"
        elif has_technical_detail:
            return "Medium confidence - good technical explanation, limited metrics"
        else:
            return "Lower confidence - general explanation without detailed metrics"
    
    def _assess_compliance_confidence(self, explanation: str, risk_score: float) -> str:
        """Assess confidence for compliance explanations"""
        has_regulatory_terms = any(term in explanation.lower() for term in 
                                 ['regulation', 'compliance', 'legal', 'aml', 'kyc', 'finra'])
        risk_clarity = risk_score > 0.1  # Clear risk indication
        
        if has_regulatory_terms and risk_clarity:
            return "High confidence - specific regulatory analysis with clear risk assessment"
        elif has_regulatory_terms:
            return "Medium confidence - regulatory context provided"
        else:
            return "Lower confidence - general risk assessment without specific regulatory context"
    
    def _extract_regulatory_notes(self, explanation: str) -> List[str]:
        """Extract regulatory considerations from explanation"""
        regulatory_terms = [
            'compliance', 'regulation', 'legal', 'aml', 'kyc', 'finra', 'sec', 'cftc',
            'mifid', 'gdpr', 'reporting', 'audit', 'disclosure', 'fiduciary'
        ]
        
        sentences = explanation.split('.')
        regulatory_notes = []
        
        for sentence in sentences:
            if any(term in sentence.lower() for term in regulatory_terms):
                regulatory_notes.append(sentence.strip())
        
        return regulatory_notes[:5]  # Limit to 5 most relevant notes

# Initialize service
explainer_service = GeminiExplainerService()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gemini-explainer",
        "timestamp": datetime.utcnow().isoformat(),
        "models_available": {
            "gemini_api": explainer_service.model is not None,
            "vertex_ai": explainer_service.vertex_model is not None
        }
    }

@app.post("/explain/signal", response_model=ExplanationResponse)
async def explain_trading_signal(request: SignalExplanationRequest):
    """Generate explanation for a trading signal"""
    try:
        return await explainer_service.explain_trading_signal(request)
    except Exception as e:
        logger.error(f"Signal explanation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain/model", response_model=ExplanationResponse)
async def explain_model_behavior(request: ModelExplanationRequest):
    """Generate explanation for model behavior"""
    try:
        return await explainer_service.explain_model_behavior(request)
    except Exception as e:
        logger.error(f"Model explanation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain/compliance", response_model=ExplanationResponse)
async def explain_compliance_assessment(request: ComplianceExplanationRequest):
    """Generate explanation for compliance assessment"""
    try:
        return await explainer_service.explain_compliance_assessment(request)
    except Exception as e:
        logger.error(f"Compliance explanation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/explain/examples")
async def get_explanation_examples():
    """Get example requests for different explanation types"""
    return {
        "signal_example": {
            "signal_hash": "0xabc123...",
            "signal_type": 1,
            "confidence": 85,
            "model_version": "v2.1.0",
            "context_data": {"market_condition": "volatile", "volume": "high"},
            "explanation_type": "business"
        },
        "model_example": {
            "model_hash": "0xdef456...",
            "model_type": "mev_detection",
            "performance_metrics": {"accuracy": 0.94, "precision": 0.91, "recall": 0.89},
            "explanation_depth": "detailed"
        },
        "compliance_example": {
            "transaction_hash": "0x789ghi...",
            "risk_score": 0.75,
            "risk_factors": ["high_value", "cross_border", "new_counterparty"],
            "regulatory_framework": "US"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
