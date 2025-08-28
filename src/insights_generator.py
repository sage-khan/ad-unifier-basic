import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta

class InsightsGenerator:
    """Generates AI-powered insights from ad campaign data"""
    
    def __init__(self, use_llm: bool = False, llm_api_key: Optional[str] = None):
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key
    
    def generate_performance_insights(self, df: pd.DataFrame, processor, detector) -> List[Dict]:
        """Generate comprehensive performance insights"""
        insights = []
        
        # Platform performance insights
        platform_summary = processor.get_platform_summary(df)
        insights.extend(self._analyze_platform_performance(platform_summary))
        
        # Trend analysis
        daily_trends = processor.get_daily_trends(df)
        insights.extend(self._analyze_trends(daily_trends))
        
        # Anomaly insights
        anomaly_summary = detector.get_anomaly_summary(df)
        recommendations = detector.generate_budget_recommendations(df)
        insights.extend(self._analyze_anomalies(anomaly_summary, recommendations))
        
        # Campaign efficiency insights
        campaign_perf = processor.get_campaign_performance(df)
        insights.extend(self._analyze_campaign_efficiency(campaign_perf))
        
        return insights
    
    def _analyze_platform_performance(self, platform_summary: pd.DataFrame) -> List[Dict]:
        """Analyze platform performance and generate insights"""
        insights = []
        
        if platform_summary.empty:
            return insights
        
        # Best performing platform by ROAS
        best_roas_platform = platform_summary.loc[platform_summary['roas'].idxmax()]
        insights.append({
            'type': 'platform_performance',
            'priority': 'high',
            'title': f'Top ROAS Platform: {best_roas_platform["platform"]}',
            'description': f'{best_roas_platform["platform"]} delivers the highest ROAS at {best_roas_platform["roas"]:.2f}, generating ${best_roas_platform["roas"]:.2f} for every $1 spent.',
            'metric': 'roas',
            'value': best_roas_platform['roas'],
            'platform': best_roas_platform['platform']
        })
        
        # Most cost-effective platform by CPA
        best_cpa_platform = platform_summary.loc[platform_summary['cpa'].idxmin()]
        insights.append({
            'type': 'platform_performance',
            'priority': 'medium',
            'title': f'Lowest CPA: {best_cpa_platform["platform"]}',
            'description': f'{best_cpa_platform["platform"]} has the most cost-effective acquisition at ${best_cpa_platform["cpa"]:.2f} per conversion.',
            'metric': 'cpa',
            'value': best_cpa_platform['cpa'],
            'platform': best_cpa_platform['platform']
        })
        
        # Platform with highest engagement (CTR)
        best_ctr_platform = platform_summary.loc[platform_summary['ctr'].idxmax()]
        insights.append({
            'type': 'platform_performance',
            'priority': 'medium',
            'title': f'Highest Engagement: {best_ctr_platform["platform"]}',
            'description': f'{best_ctr_platform["platform"]} shows the highest user engagement with a {best_ctr_platform["ctr"]:.3%} click-through rate.',
            'metric': 'ctr',
            'value': best_ctr_platform['ctr'],
            'platform': best_ctr_platform['platform']
        })
        
        # Budget allocation insights
        total_spend = platform_summary['spend'].sum()
        for _, platform in platform_summary.iterrows():
            spend_share = platform['spend'] / total_spend
            roas_rank = platform_summary['roas'].rank(ascending=False)[platform.name]
            
            if spend_share > 0.4 and roas_rank > len(platform_summary) / 2:
                insights.append({
                    'type': 'budget_allocation',
                    'priority': 'high',
                    'title': f'Budget Reallocation Opportunity: {platform["platform"]}',
                    'description': f'{platform["platform"]} receives {spend_share:.1%} of total budget but ranks #{int(roas_rank)} in ROAS performance. Consider reallocating budget to higher-performing platforms.',
                    'metric': 'budget_efficiency',
                    'value': spend_share,
                    'platform': platform['platform']
                })
        
        return insights
    
    def _analyze_trends(self, daily_trends: pd.DataFrame) -> List[Dict]:
        """Analyze daily trends and identify patterns"""
        insights = []
        
        if len(daily_trends) < 7:
            return insights
        
        # ROAS trend analysis
        recent_roas = daily_trends['roas'].tail(7).mean()
        previous_roas = daily_trends['roas'].head(7).mean()
        roas_change = (recent_roas - previous_roas) / previous_roas if previous_roas > 0 else 0
        
        if abs(roas_change) > 0.1:  # 10% change
            trend_direction = "improved" if roas_change > 0 else "declined"
            insights.append({
                'type': 'trend_analysis',
                'priority': 'high' if abs(roas_change) > 0.2 else 'medium',
                'title': f'ROAS Trend: {trend_direction.title()}',
                'description': f'ROAS has {trend_direction} by {abs(roas_change):.1%} over the recent period (current: {recent_roas:.2f} vs previous: {previous_roas:.2f}).',
                'metric': 'roas_trend',
                'value': roas_change,
                'platform': 'all'
            })
        
        # Spend volatility analysis
        spend_std = daily_trends['spend'].std()
        spend_mean = daily_trends['spend'].mean()
        spend_cv = spend_std / spend_mean if spend_mean > 0 else 0
        
        if spend_cv > 0.3:  # High volatility
            insights.append({
                'type': 'trend_analysis',
                'priority': 'medium',
                'title': 'High Spending Volatility Detected',
                'description': f'Daily spending shows high volatility (CV: {spend_cv:.2f}). Consider implementing more consistent budget pacing for better performance predictability.',
                'metric': 'spend_volatility',
                'value': spend_cv,
                'platform': 'all'
            })
        
        return insights
    
    def _analyze_anomalies(self, anomaly_summary: Dict, recommendations: List[Dict]) -> List[Dict]:
        """Analyze anomalies and recommendations"""
        insights = []
        
        # Anomaly summary insights
        total_anomalies = anomaly_summary['spend_anomalies'] + anomaly_summary['roas_anomalies'] + anomaly_summary['ctr_anomalies']
        
        if total_anomalies > 0:
            insights.append({
                'type': 'anomaly_detection',
                'priority': 'high',
                'title': f'{total_anomalies} Performance Anomalies Detected',
                'description': f'Detected {anomaly_summary["spend_anomalies"]} spend, {anomaly_summary["roas_anomalies"]} ROAS, and {anomaly_summary["ctr_anomalies"]} CTR anomalies across {anomaly_summary["campaigns_affected"]} campaigns.',
                'metric': 'anomaly_count',
                'value': total_anomalies,
                'platform': 'multiple'
            })
        
        # Recommendation insights
        if recommendations:
            high_confidence_recs = [r for r in recommendations if r['confidence'] == 'HIGH']
            if high_confidence_recs:
                insights.append({
                    'type': 'recommendations',
                    'priority': 'high',
                    'title': f'{len(high_confidence_recs)} High-Confidence Budget Recommendations',
                    'description': f'AI analysis suggests {len(high_confidence_recs)} budget adjustments with high confidence. Implementing these could optimize campaign performance.',
                    'metric': 'recommendations',
                    'value': len(high_confidence_recs),
                    'platform': 'multiple'
                })
        
        return insights
    
    def _analyze_campaign_efficiency(self, campaign_perf: pd.DataFrame) -> List[Dict]:
        """Analyze campaign efficiency and identify optimization opportunities"""
        insights = []
        
        if campaign_perf.empty:
            return insights
        
        # Top performing campaign
        top_campaign = campaign_perf.loc[campaign_perf['roas'].idxmax()]
        insights.append({
            'type': 'campaign_performance',
            'priority': 'medium',
            'title': f'Top Campaign: {top_campaign["campaign_name"]}',
            'description': f'{top_campaign["campaign_name"]} on {top_campaign["platform"]} delivers exceptional ROAS of {top_campaign["roas"]:.2f}. Consider scaling this campaign or applying its strategies to others.',
            'metric': 'campaign_roas',
            'value': top_campaign['roas'],
            'platform': top_campaign['platform']
        })
        
        # Underperforming campaigns
        low_roas_campaigns = campaign_perf[campaign_perf['roas'] < 1.0]  # ROAS < 1 means losing money
        if not low_roas_campaigns.empty:
            insights.append({
                'type': 'campaign_performance',
                'priority': 'high',
                'title': f'{len(low_roas_campaigns)} Underperforming Campaigns',
                'description': f'{len(low_roas_campaigns)} campaigns have ROAS below 1.0, indicating negative ROI. Review and optimize these campaigns urgently.',
                'metric': 'underperforming_campaigns',
                'value': len(low_roas_campaigns),
                'platform': 'multiple'
            })
        
        return insights
    
    def generate_executive_summary(self, insights: List[Dict]) -> str:
        """Generate an executive summary from insights"""
        if not insights:
            return "No significant insights found in the current data."
        
        # Categorize insights by priority
        high_priority = [i for i in insights if i['priority'] == 'high']
        medium_priority = [i for i in insights if i['priority'] == 'medium']
        
        summary_parts = []
        
        if high_priority:
            summary_parts.append(f"🚨 **Critical Findings ({len(high_priority)}):**")
            for insight in high_priority[:3]:  # Top 3 high priority
                summary_parts.append(f"• {insight['title']}: {insight['description']}")
        
        if medium_priority:
            summary_parts.append(f"\n📊 **Key Opportunities ({len(medium_priority)}):**")
            for insight in medium_priority[:2]:  # Top 2 medium priority
                summary_parts.append(f"• {insight['title']}: {insight['description']}")
        
        # Add overall recommendation
        summary_parts.append(f"\n💡 **Recommendation:** Focus on addressing the {len(high_priority)} critical findings first, then explore the identified opportunities for optimization.")
        
        return "\n".join(summary_parts)
    
    def get_insights_by_platform(self, insights: List[Dict], platform: str) -> List[Dict]:
        """Filter insights by platform"""
        return [i for i in insights if i.get('platform') == platform or i.get('platform') == 'all' or i.get('platform') == 'multiple']

def main():
    """Test insights generation"""
    import os
    from data_processor import AdDataProcessor
    from anomaly_detector import AnomalyDetector
    
    # Load processed data
    if not os.path.exists('data/unified_ad_data.csv'):
        print("No processed data found. Please run data_processor.py first.")
        return
    
    df = pd.read_csv('data/unified_ad_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Initialize components
    processor = AdDataProcessor()
    detector = AnomalyDetector()
    insights_gen = InsightsGenerator()
    
    # Run anomaly detection if not already done
    if 'spend_anomaly' not in df.columns:
        df = detector.detect_spend_anomalies(df)
        df = detector.detect_performance_anomalies(df)
    
    # Generate insights
    print("Generating performance insights...")
    insights = insights_gen.generate_performance_insights(df, processor, detector)
    
    # Display insights
    print(f"\n=== Generated {len(insights)} Insights ===")
    for insight in insights:
        print(f"\n[{insight['priority'].upper()}] {insight['title']}")
        print(f"  {insight['description']}")
        print(f"  Type: {insight['type']} | Platform: {insight['platform']}")
    
    # Generate executive summary
    print("\n=== Executive Summary ===")
    summary = insights_gen.generate_executive_summary(insights)
    print(summary)

if __name__ == "__main__":
    main()
