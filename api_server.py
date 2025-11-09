#!/usr/bin/env python3
"""
FastAPI Backend for Hybrid Analysis Dashboard

Exposes hybrid analysis (statistical + Grok) to Next.js dashboard via HTTP API.

Endpoints:
- GET  /api/recommendations - Get cached recommendations
- POST /api/analyze - Trigger new analysis
- GET  /api/status - Check analysis status

Usage:
    python api_server.py
    
    # Or specify port
    python api_server.py --port 8000
"""

import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from hybrid_analysis import analyze_all_markets

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Kalshi Hybrid Analysis API",
    description="Statistical + Grok AI betting recommendations",
    version="1.0.0"
)

# Enable CORS for dashboard
# Note: For ngrok hosting, we allow all origins. In production, restrict this!
import re

def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed (localhost, vercel, or ngrok)"""
    if not origin:
        return False
    
    allowed_patterns = [
        r"^http://localhost:\d+$",           # localhost any port
        r"^https://.*\.vercel\.app$",        # Vercel
        r"^https://.*\.ngrok\.io$",          # ngrok
        r"^https://.*\.ngrok-free\.app$",    # ngrok free tier
    ]
    
    return any(re.match(pattern, origin) for pattern in allowed_patterns)

# Custom CORS middleware that allows ngrok URLs
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import ALL_METHODS
from starlette.responses import Response

@app.middleware("http")
async def custom_cors_middleware(request, call_next):
    """Custom CORS middleware to handle ngrok URLs"""
    origin = request.headers.get("origin")
    
    response = await call_next(request)
    
    # Allow all origins for demo (ngrok, localhost, etc.)
    # In production, use is_allowed_origin(origin) check
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AnalysisState:
    """Shared state for analysis results"""
    
    def __init__(self):
        self.recommendations: List[Dict[str, Any]] = []
        self.last_updated: Optional[datetime] = None
        self.is_analyzing: bool = False
        self.analysis_error: Optional[str] = None
        self.total_analyzed: int = 0
    
    def to_dict(self):
        return {
            'recommendations': self.recommendations,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None,
            'isAnalyzing': self.is_analyzing,
            'error': self.analysis_error,
            'totalAnalyzed': self.total_analyzed,
        }

# Global state
state = AnalysisState()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    edge_threshold: float = 0.10
    max_recommendations: int = 20
    quant_weight: float = 0.75
    sentiment_weight: float = 0.25

class StatusResponse(BaseModel):
    status: str
    isAnalyzing: bool
    lastUpdated: Optional[str]
    count: int
    error: Optional[str]


# ============================================================================
# BACKGROUND ANALYSIS TASK
# ============================================================================

async def run_analysis_task(
    edge_threshold: float = 0.10,
    max_recommendations: int = 20,
    quant_weight: float = 0.75,
    sentiment_weight: float = 0.25
):
    """Background task to run hybrid analysis"""
    global state
    
    try:
        state.is_analyzing = True
        state.analysis_error = None
        
        print(f"\n{'='*100}")
        print(f"🔄 STARTING NEW ANALYSIS")
        print(f"{'='*100}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"Parameters:")
        print(f"  • Edge threshold: {edge_threshold:.1%}")
        print(f"  • Max recommendations: {max_recommendations}")
        print(f"  • Weights: {quant_weight:.0%} quant, {sentiment_weight:.0%} sentiment")
        print(f"{'='*100}\n")
        
        # Run hybrid analysis
        recommendations = await analyze_all_markets(
            edge_threshold=edge_threshold,
            max_recommendations=max_recommendations,
            quant_weight=quant_weight,
            sentiment_weight=sentiment_weight
        )
        
        # Update state
        state.recommendations = recommendations
        state.last_updated = datetime.now()
        state.total_analyzed += len(recommendations)
        
        print(f"\n{'='*100}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*100}")
        print(f"Total recommendations: {len(recommendations)}")
        print(f"Total analyzed (lifetime): {state.total_analyzed}")
        
        # Print summary of recommendations
        if recommendations:
            print(f"\n📊 RECOMMENDATIONS SUMMARY:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                print(f"\n{i}. {rec['ticker']}")
                print(f"   Action: {rec['action']}")
                print(f"   Edge: {rec['quant_edge']:.1%}")
                print(f"   Confidence: {rec['combined_confidence']:.1%}")
                print(f"   Grok: {rec['grok_sentiment'].get('label')} ({rec['grok_sentiment'].get('score')}%)")
            
            if len(recommendations) > 5:
                print(f"\n   ... and {len(recommendations) - 5} more")
        
        print(f"{'='*100}\n")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        state.analysis_error = str(e)
    
    finally:
        state.is_analyzing = False


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Kalshi Hybrid Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/status")
async def get_status() -> StatusResponse:
    """Get current analysis status"""
    return StatusResponse(
        status="analyzing" if state.is_analyzing else "ready",
        isAnalyzing=state.is_analyzing,
        lastUpdated=state.last_updated.isoformat() if state.last_updated else None,
        count=len(state.recommendations),
        error=state.analysis_error
    )


@app.get("/api/recommendations")
async def get_recommendations():
    """
    Get current recommendations.
    
    Returns cached results from last analysis.
    Use POST /api/analyze to trigger new analysis.
    """
    print(f"\n📥 GET /api/recommendations - Request received at {datetime.now().strftime('%H:%M:%S')}")
    
    if state.is_analyzing:
        print(f"   ⏳ Analysis in progress, returning status")
        return {
            "status": "analyzing",
            "message": "Analysis in progress, please wait...",
            "opportunities": [],
            "lastUpdated": None
        }
    
    if state.analysis_error:
        print(f"   ❌ Last analysis failed: {state.analysis_error}")
        raise HTTPException(
            status_code=500,
            detail=f"Last analysis failed: {state.analysis_error}"
        )
    
    if not state.recommendations:
        print(f"   ⚠️  No recommendations available yet")
        return {
            "status": "empty",
            "message": "No recommendations yet. Trigger analysis with POST /api/analyze",
            "opportunities": [],
            "lastUpdated": None
        }
    
    print(f"   ✅ Returning {len(state.recommendations)} recommendations")
    print(f"   📅 Last updated: {state.last_updated.strftime('%H:%M:%S') if state.last_updated else 'Never'}")
    
    return {
        "status": "success",
        "opportunities": state.recommendations,
        "lastUpdated": state.last_updated.isoformat() if state.last_updated else None,
        "count": len(state.recommendations)
    }


@app.post("/api/analyze")
async def trigger_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger new hybrid analysis.
    
    Runs in background. Check status with GET /api/status.
    """
    if state.is_analyzing:
        return {
            "status": "already_running",
            "message": "Analysis already in progress"
        }
    
    # Start background task
    background_tasks.add_task(
        run_analysis_task,
        edge_threshold=request.edge_threshold,
        max_recommendations=request.max_recommendations,
        quant_weight=request.quant_weight,
        sentiment_weight=request.sentiment_weight
    )
    
    return {
        "status": "started",
        "message": "Analysis started in background",
        "params": {
            "edge_threshold": request.edge_threshold,
            "max_recommendations": request.max_recommendations,
            "quant_weight": request.quant_weight,
            "sentiment_weight": request.sentiment_weight
        }
    }


@app.get("/api/recommendations/{ticker}")
async def get_recommendation_by_ticker(ticker: str):
    """Get specific recommendation by ticker"""
    for rec in state.recommendations:
        if rec['ticker'] == ticker:
            return rec
    
    raise HTTPException(status_code=404, detail=f"Recommendation for {ticker} not found")


# ============================================================================
# AUTO-REFRESH
# ============================================================================

async def auto_refresh_loop():
    """Auto-refresh recommendations every 5 minutes"""
    while True:
        try:
            # Wait 5 minutes
            await asyncio.sleep(300)
            
            # Only refresh if not already analyzing
            if not state.is_analyzing:
                print("\n🔄 Auto-refresh triggered")
                await run_analysis_task()
        
        except Exception as e:
            print(f"❌ Auto-refresh failed: {e}")
            await asyncio.sleep(60)  # Retry in 1 minute


@app.on_event("startup")
async def startup_event():
    """Run initial analysis and start auto-refresh"""
    print("\n" + "="*80)
    print("🚀 KALSHI HYBRID ANALYSIS API STARTING")
    print("="*80)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Docs: http://localhost:8000/docs")
    print(f"API: http://localhost:8000/api/recommendations")
    print("="*80)
    print()
    
    # Check for API keys
    if not os.getenv("X_API_KEY"):
        print("⚠️  WARNING: X_API_KEY not set. Grok sentiment analysis will fail!")
        print("   Set it in .env or environment: export X_API_KEY=your-key")
        print()
    
    # Run initial analysis
    print("🔄 Running initial analysis...")
    asyncio.create_task(run_analysis_task())
    
    # Start auto-refresh loop
    print("⏰ Starting auto-refresh (every 5 minutes)")
    asyncio.create_task(auto_refresh_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n" + "="*80)
    print("👋 KALSHI HYBRID ANALYSIS API SHUTTING DOWN")
    print("="*80)
    print(f"Total recommendations analyzed: {state.total_analyzed}")
    print(f"Last updated: {state.last_updated.isoformat() if state.last_updated else 'Never'}")
    print("="*80)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid Analysis API Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

