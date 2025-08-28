from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import os
from typing import List, Dict, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

from data_processor import AdDataProcessor
from anomaly_detector import AnomalyDetector

app = FastAPI(
    title="Unified Ads Campaign Insights API",
    description="""
    ## 📊 Unified Ads Campaign Insights API
    
    A comprehensive API for analyzing ad campaign performance across multiple platforms.
    
    ### Features:
    - **Multi-platform Data**: Google Ads, Meta Ads, LinkedIn Ads
    - **Core KPIs**: ROAS, CPA, CTR calculations
    - **Anomaly Detection**: Statistical anomaly detection using rolling z-score
    - **Smart Recommendations**: AI-powered budget optimization suggestions
    
    ### Quick Start:
    1. Check API health: `GET /health`
    2. View available platforms: `GET /platforms`
    3. Get KPI summary: `GET /kpis/summary`
    4. Access interactive dashboard: [http://localhost:8501](http://localhost:8501)
    """,
    version="1.0.0",
    contact={
        "name": "Ads Insights Team",
        "email": "insights@company.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "health",
            "description": "API health and status endpoints",
        },
        {
            "name": "data",
            "description": "Raw data access and management",
        },
        {
            "name": "kpis",
            "description": "Key Performance Indicators and metrics",
        },
        {
            "name": "anomalies",
            "description": "Anomaly detection and analysis",
        },
        {
            "name": "recommendations",
            "description": "AI-powered budget and optimization recommendations",
        },
        {
            "name": "campaigns",
            "description": "Campaign-specific performance data",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
unified_data = None
processor = AdDataProcessor()
detector = AnomalyDetector()

class KPIResponse(BaseModel):
    platform: str = Field(..., description="Ad platform name", example="Google Ads")
    total_spend: float = Field(..., description="Total advertising spend in USD", example=15420.50)
    total_revenue: float = Field(..., description="Total revenue generated in USD", example=38550.25)
    total_impressions: int = Field(..., description="Total ad impressions", example=1250000)
    total_clicks: int = Field(..., description="Total ad clicks", example=25000)
    total_conversions: int = Field(..., description="Total conversions", example=1250)
    roas: float = Field(..., description="Return on Ad Spend (Revenue/Spend)", example=2.5)
    cpa: float = Field(..., description="Cost per Acquisition (Spend/Conversions)", example=12.34)
    ctr: float = Field(..., description="Click-through Rate (Clicks/Impressions)", example=0.02)

class RecommendationResponse(BaseModel):
    platform: str = Field(..., description="Ad platform name", example="Meta Ads")
    campaign: str = Field(..., description="Campaign name", example="Meta_Campaign_1")
    recommendation: str = Field(..., description="Recommendation type", example="INCREASE_BUDGET")
    suggested_change: float = Field(..., description="Suggested budget change as decimal", example=0.20)
    reason: str = Field(..., description="Detailed reason for recommendation", example="ROAS surge detected with stable spending")
    confidence: str = Field(..., description="Confidence level", example="HIGH")
    current_spend: float = Field(..., description="Current daily spend", example=150.75)
    current_roas: float = Field(..., description="Current ROAS", example=3.2)

class AnomalyDetail(BaseModel):
    date: str = Field(..., description="Date of anomaly", example="2024-08-28")
    platform: str = Field(..., description="Platform name", example="LinkedIn Ads")
    campaign_name: str = Field(..., description="Campaign name", example="LinkedIn_Campaign_1")
    spend: float = Field(..., description="Daily spend", example=245.50)
    roas: float = Field(..., description="ROAS value", example=1.8)
    ctr: float = Field(..., description="CTR value", example=0.025)
    spend_anomaly_score: float = Field(..., description="Spend anomaly z-score", example=2.8)
    roas_anomaly_score: float = Field(..., description="ROAS anomaly z-score", example=-1.2)
    ctr_anomaly_score: float = Field(..., description="CTR anomaly z-score", example=0.5)

class CampaignInfo(BaseModel):
    platform: str = Field(..., description="Platform name", example="Google Ads")
    campaign_name: str = Field(..., description="Campaign name", example="Google_Campaign_1")

class DailyTrend(BaseModel):
    date: str = Field(..., description="Date", example="2024-08-28")
    impressions: int = Field(..., description="Total impressions", example=45000)
    clicks: int = Field(..., description="Total clicks", example=900)
    spend: float = Field(..., description="Total spend", example=450.75)
    conversions: int = Field(..., description="Total conversions", example=45)
    revenue: float = Field(..., description="Total revenue", example=1125.50)
    roas: float = Field(..., description="ROAS", example=2.5)
    cpa: float = Field(..., description="CPA", example=10.02)
    ctr: float = Field(..., description="CTR", example=0.02)

def load_data():
    """Load and process data on startup"""
    global unified_data
    
    if os.path.exists('data/unified_ad_data_with_anomalies.csv'):
        unified_data = pd.read_csv('data/unified_ad_data_with_anomalies.csv')
        unified_data['date'] = pd.to_datetime(unified_data['date'])
    elif os.path.exists('data/unified_ad_data.csv'):
        unified_data = pd.read_csv('data/unified_ad_data.csv')
        unified_data['date'] = pd.to_datetime(unified_data['date'])
        # Run anomaly detection
        unified_data = detector.detect_spend_anomalies(unified_data)
        unified_data = detector.detect_performance_anomalies(unified_data)
    else:
        # Generate and process data if none exists
        from data_generator import save_mock_data
        save_mock_data()
        unified_data = processor.load_and_normalize_all_data()
        unified_data = processor.calculate_kpis(unified_data)
        unified_data = detector.detect_spend_anomalies(unified_data)
        unified_data = detector.detect_performance_anomalies(unified_data)

@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/", tags=["health"])
async def root():
    """
    ## API Root Endpoint
    
    Returns basic API information and available endpoints.
    """
    return {
        "message": "Unified Ads Campaign Insights API", 
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "dashboard": "http://localhost:8501"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """
    ## Health Check
    
    Verify API status and data availability.
    
    Returns:
    - API status
    - Data loading status
    - Record count if data is loaded
    """
    data_info = {}
    if unified_data is not None:
        data_info = {
            "records": len(unified_data),
            "platforms": unified_data['platform'].nunique(),
            "date_range": {
                "start": unified_data['date'].min().strftime('%Y-%m-%d'),
                "end": unified_data['date'].max().strftime('%Y-%m-%d')
            }
        }
    
    return {
        "status": "healthy", 
        "data_loaded": unified_data is not None,
        "data_info": data_info
    }

@app.get("/platforms", tags=["data"])
async def get_platforms():
    """
    ## Get Available Platforms
    
    Returns list of all ad platforms available in the dataset.
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    platforms = unified_data['platform'].unique().tolist()
    return {
        "platforms": platforms,
        "count": len(platforms)
    }

@app.get("/campaigns", response_model=Dict[str, List[CampaignInfo]], tags=["campaigns"])
async def get_campaigns(platform: Optional[str] = Query(None, description="Filter by platform name")):
    """
    ## Get Campaigns
    
    Returns list of campaigns, optionally filtered by platform.
    
    **Parameters:**
    - **platform**: Optional platform filter (e.g., "Google Ads", "Meta Ads", "LinkedIn Ads")
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = unified_data
    if platform:
        df = df[df['platform'] == platform]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Platform '{platform}' not found")
    
    campaigns = df.groupby(['platform', 'campaign_name']).size().reset_index()
    campaigns_list = [
        CampaignInfo(platform=row['platform'], campaign_name=row['campaign_name'])
        for _, row in campaigns.iterrows()
    ]
    
    return {
        "campaigns": campaigns_list,
        "total_count": len(campaigns_list)
    }

@app.get("/kpis/summary", response_model=List[KPIResponse], tags=["kpis"])
async def get_kpi_summary():
    """
    ## KPI Summary by Platform
    
    Returns comprehensive KPI metrics aggregated by platform.
    
    **Metrics included:**
    - **ROAS**: Return on Ad Spend (Revenue ÷ Spend)
    - **CPA**: Cost per Acquisition (Spend ÷ Conversions)
    - **CTR**: Click-through Rate (Clicks ÷ Impressions)
    - Total spend, revenue, impressions, clicks, conversions
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    summary = processor.get_platform_summary(unified_data)
    
    response = []
    for _, row in summary.iterrows():
        response.append(KPIResponse(
            platform=row['platform'],
            total_spend=float(row['spend']),
            total_revenue=float(row['revenue']),
            total_impressions=int(row['impressions']),
            total_clicks=int(row['clicks']),
            total_conversions=int(row['conversions']),
            roas=float(row['roas']),
            cpa=float(row['cpa']),
            ctr=float(row['ctr'])
        ))
    
    return response

@app.get("/trends/daily", response_model=Dict[str, List[DailyTrend]], tags=["kpis"])
async def get_daily_trends(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)", example="2024-08-01"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)", example="2024-08-28"),
    platform: Optional[str] = Query(None, description="Filter by platform", example="Google Ads")
):
    """
    ## Daily Performance Trends
    
    Returns daily aggregated performance metrics with optional filtering.
    
    **Parameters:**
    - **start_date**: Filter from this date (YYYY-MM-DD format)
    - **end_date**: Filter to this date (YYYY-MM-DD format)  
    - **platform**: Filter by specific platform
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = unified_data.copy()
    
    # Filter by platform if specified
    if platform:
        df = df[df['platform'] == platform]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Platform '{platform}' not found")
    
    # Filter by date range if specified
    if start_date:
        try:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        except:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        except:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    daily_trends = processor.get_daily_trends(df)
    
    # Convert to response model
    trends_list = []
    for _, row in daily_trends.iterrows():
        trends_list.append(DailyTrend(
            date=row['date'].strftime('%Y-%m-%d'),
            impressions=int(row['impressions']),
            clicks=int(row['clicks']),
            spend=float(row['spend']),
            conversions=int(row['conversions']),
            revenue=float(row['revenue']),
            roas=float(row['roas']),
            cpa=float(row['cpa']),
            ctr=float(row['ctr'])
        ))
    
    return {
        "trends": trends_list,
        "total_days": len(trends_list),
        "filters_applied": {
            "platform": platform,
            "start_date": start_date,
            "end_date": end_date
        }
    }

@app.get("/campaigns/performance", tags=["campaigns"])
async def get_campaign_performance(platform: Optional[str] = Query(None, description="Filter by platform name")):
    """
    ## Get Campaign Performance
    
    Returns performance metrics by campaign, optionally filtered by platform.
    
    **Parameters:**
    - **platform**: Optional platform filter (e.g., "Google Ads", "Meta Ads", "LinkedIn Ads")
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = unified_data
    if platform:
        df = df[df['platform'] == platform]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Platform '{platform}' not found")
    
    campaign_perf = processor.get_campaign_performance(df)
    
    return {
        "performance": campaign_perf.to_dict('records'),
        "total_campaigns": len(campaign_perf)
    }

@app.get("/anomalies/summary", tags=["anomalies"])
async def get_anomaly_summary():
    """
    ## Anomaly Detection Summary
    
    Returns summary statistics of detected anomalies across all metrics.
    
    **Anomaly Types:**
    - **Spend Anomalies**: Unusual spending patterns
    - **ROAS Anomalies**: Performance efficiency anomalies  
    - **CTR Anomalies**: Click-through rate anomalies
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    summary = detector.get_anomaly_summary(unified_data)
    return {
        **summary,
        "detection_method": "Rolling Z-Score with Median + MAD",
        "window_size": "7 days",
        "threshold": "2.5 standard deviations"
    }

@app.get("/anomalies/details", response_model=Dict[str, List[AnomalyDetail]], tags=["anomalies"])
async def get_anomaly_details(
    platform: Optional[str] = Query(None, description="Filter by platform name"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type", example="spend")
):
    """
    ## Anomaly Details
    
    Returns detailed information about detected anomalies, optionally filtered by platform and anomaly type.
    
    **Anomaly Types:**
    - **spend**: Spend anomalies
    - **roas**: ROAS anomalies
    - **ctr**: CTR anomalies
    
    **Parameters:**
    - **platform**: Optional platform filter (e.g., "Google Ads", "Meta Ads", "LinkedIn Ads")
    - **anomaly_type**: Optional anomaly type filter (e.g., "spend", "roas", "ctr")
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = unified_data.copy()
    
    # Filter by platform if specified
    if platform:
        df = df[df['platform'] == platform]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Platform '{platform}' not found")
    
    # Filter anomalies based on type
    if anomaly_type == "spend":
        anomalies = df[df['spend_anomaly'] == True]
    elif anomaly_type == "roas":
        anomalies = df[df['roas_anomaly'] == True]
    elif anomaly_type == "ctr":
        anomalies = df[df['ctr_anomaly'] == True]
    else:
        # All anomalies
        anomalies = df[
            (df['spend_anomaly'] == True) | 
            (df['roas_anomaly'] == True) | 
            (df['ctr_anomaly'] == True)
        ]
    
    # Convert dates to strings for JSON serialization
    anomalies = anomalies.copy()
    anomalies['date'] = anomalies['date'].dt.strftime('%Y-%m-%d')
    
    # Convert to response model
    anomalies_list = []
    for _, row in anomalies.iterrows():
        anomalies_list.append(AnomalyDetail(
            date=row['date'],
            platform=row['platform'],
            campaign_name=row['campaign_name'],
            spend=float(row['spend']),
            roas=float(row['roas']),
            ctr=float(row['ctr']),
            spend_anomaly_score=float(row['spend_anomaly_score']),
            roas_anomaly_score=float(row['roas_anomaly_score']),
            ctr_anomaly_score=float(row['ctr_anomaly_score'])
        ))
    
    return {
        "anomalies": anomalies_list,
        "total_anomalies": len(anomalies_list),
        "filters_applied": {
            "platform": platform,
            "anomaly_type": anomaly_type
        }
    }

@app.get("/recommendations", response_model=List[RecommendationResponse], tags=["recommendations"])
async def get_recommendations():
    """
    ## Budget Recommendations
    
    Returns AI-powered budget optimization recommendations based on anomaly detection.
    
    **Recommendation Types:**
    - **INCREASE_BUDGET**: Scale up high-performing campaigns (+20%)
    - **DECREASE_BUDGET**: Scale down underperforming campaigns (-20%)
    - **REVIEW_CREATIVE**: Creative refresh needed for low CTR
    
    **Confidence Levels:**
    - **HIGH**: Strong statistical evidence
    - **MEDIUM**: Moderate confidence
    - **LOW**: Weak signal, monitor closely
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    recommendations = detector.generate_budget_recommendations(unified_data)
    
    response = []
    for rec in recommendations:
        response.append(RecommendationResponse(
            platform=rec['platform'],
            campaign=rec['campaign'],
            recommendation=rec['recommendation'],
            suggested_change=rec['suggested_change'],
            reason=rec['reason'],
            confidence=rec['confidence'],
            current_spend=rec['current_spend'],
            current_roas=rec['current_roas']
        ))
    
    return response

@app.get("/data/raw", tags=["data"])
async def get_raw_data(
    platform: Optional[str] = Query(None, description="Filter by platform name"),
    campaign: Optional[str] = Query(None, description="Filter by campaign name"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)", example="2024-08-01"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)", example="2024-08-28"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records to return")
):
    """
    ## Raw Data Access
    
    Returns raw unified data with optional filtering.
    
    **Parameters:**
    - **platform**: Optional platform filter (e.g., "Google Ads", "Meta Ads", "LinkedIn Ads")
    - **campaign**: Optional campaign filter (e.g., "Google_Campaign_1", "Meta_Campaign_1")
    - **start_date**: Filter from this date (YYYY-MM-DD format)
    - **end_date**: Filter to this date (YYYY-MM-DD format)  
    - **limit**: Maximum records to return (default: 1000, max: 10000)
    """
    if unified_data is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = unified_data.copy()
    
    # Apply filters
    if platform:
        df = df[df['platform'] == platform]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Platform '{platform}' not found")
    if campaign:
        df = df[df['campaign_name'] == campaign]
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Campaign '{campaign}' not found")
    if start_date:
        try:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        except:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        except:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    # Limit results
    df = df.head(limit)
    
    # Convert dates to strings
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    return {
        "data": df.to_dict('records'),
        "total_records": len(df),
        "filters_applied": {
            "platform": platform,
            "campaign": campaign,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
    }

@app.post("/data/refresh", tags=["data"])
async def refresh_data():
    """
    ## Refresh Data
    
    Refresh data by reprocessing all sources.
    """
    try:
        load_data()
        return {"message": "Data refreshed successfully", "records": len(unified_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh data: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
