import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

class AnomalyDetector:
    """Detects anomalies in ad campaign data using robust statistical methods"""
    
    def __init__(self, window_size: int = 7, threshold: float = 2.5):
        self.window_size = window_size
        self.threshold = threshold
    
    def calculate_mad(self, data: pd.Series) -> float:
        """Calculate Median Absolute Deviation (MAD)"""
        median = data.median()
        mad = np.median(np.abs(data - median))
        return mad
    
    def robust_zscore(self, data: pd.Series) -> pd.Series:
        """Calculate robust z-score using median and MAD"""
        median = data.median()
        mad = self.calculate_mad(data)
        
        # Avoid division by zero
        if mad == 0:
            return pd.Series(np.zeros(len(data)), index=data.index)
        
        # Modified z-score using MAD
        # Factor of 1.4826 makes MAD consistent with standard deviation for normal distribution
        robust_z = 0.6745 * (data - median) / mad
        return robust_z
    
    def detect_spend_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect spending anomalies by platform and campaign"""
        df = df.copy()
        df['spend_anomaly_score'] = 0
        df['spend_anomaly'] = False
        
        # Group by platform and campaign for anomaly detection
        for (platform, campaign), group in df.groupby(['platform', 'campaign_name']):
            if len(group) < self.window_size:
                continue
                
            # Sort by date
            group = group.sort_values('date')
            
            # Calculate rolling robust z-score for spend
            rolling_spend = group['spend'].rolling(window=self.window_size, min_periods=3)
            
            for i in range(len(group)):
                if i < self.window_size - 1:
                    continue
                    
                window_data = group['spend'].iloc[max(0, i-self.window_size+1):i+1]
                if len(window_data) >= 3:
                    z_scores = self.robust_zscore(window_data)
                    current_z = z_scores.iloc[-1]
                    
                    # Update anomaly score and flag
                    idx = group.index[i]
                    df.loc[idx, 'spend_anomaly_score'] = current_z
                    df.loc[idx, 'spend_anomaly'] = abs(current_z) > self.threshold
        
        return df
    
    def detect_performance_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect performance anomalies in ROAS and CTR"""
        df = df.copy()
        df['roas_anomaly_score'] = 0
        df['roas_anomaly'] = False
        df['ctr_anomaly_score'] = 0
        df['ctr_anomaly'] = False
        
        # Group by platform and campaign
        for (platform, campaign), group in df.groupby(['platform', 'campaign_name']):
            if len(group) < self.window_size:
                continue
                
            group = group.sort_values('date')
            
            # Detect ROAS anomalies
            for i in range(len(group)):
                if i < self.window_size - 1:
                    continue
                    
                # ROAS anomaly detection
                roas_window = group['roas'].iloc[max(0, i-self.window_size+1):i+1]
                if len(roas_window) >= 3 and roas_window.sum() > 0:
                    roas_z_scores = self.robust_zscore(roas_window)
                    current_roas_z = roas_z_scores.iloc[-1]
                    
                    idx = group.index[i]
                    df.loc[idx, 'roas_anomaly_score'] = current_roas_z
                    df.loc[idx, 'roas_anomaly'] = abs(current_roas_z) > self.threshold
                
                # CTR anomaly detection
                ctr_window = group['ctr'].iloc[max(0, i-self.window_size+1):i+1]
                if len(ctr_window) >= 3 and ctr_window.sum() > 0:
                    ctr_z_scores = self.robust_zscore(ctr_window)
                    current_ctr_z = ctr_z_scores.iloc[-1]
                    
                    idx = group.index[i]
                    df.loc[idx, 'ctr_anomaly_score'] = current_ctr_z
                    df.loc[idx, 'ctr_anomaly'] = abs(current_ctr_z) > self.threshold
        
        return df
    
    def generate_budget_recommendations(self, df: pd.DataFrame) -> List[Dict]:
        """Generate budget recommendations based on anomaly detection"""
        recommendations = []
        
        # Get recent data (last 7 days)
        recent_data = df[df['date'] >= df['date'].max() - pd.Timedelta(days=6)]
        
        for (platform, campaign), group in recent_data.groupby(['platform', 'campaign_name']):
            if len(group) == 0:
                continue
                
            latest = group.iloc[-1]
            
            # Check for spend spike without matching ROAS
            if latest['spend_anomaly'] and latest['spend_anomaly_score'] > 0:
                if latest['roas_anomaly'] and latest['roas_anomaly_score'] < 0:
                    # High spend, low ROAS - recommend decrease
                    recommendations.append({
                        'platform': platform,
                        'campaign': campaign,
                        'recommendation': 'DECREASE_BUDGET',
                        'suggested_change': -0.20,  # -20%
                        'reason': f'Spend spike detected (z-score: {latest["spend_anomaly_score"]:.2f}) with poor ROAS performance (z-score: {latest["roas_anomaly_score"]:.2f})',
                        'confidence': 'HIGH',
                        'current_spend': latest['spend'],
                        'current_roas': latest['roas']
                    })
            
            # Check for ROAS surge with stable spend
            elif latest['roas_anomaly'] and latest['roas_anomaly_score'] > 0:
                if not latest['spend_anomaly'] or abs(latest['spend_anomaly_score']) < 1:
                    # High ROAS, stable spend - recommend increase
                    recommendations.append({
                        'platform': platform,
                        'campaign': campaign,
                        'recommendation': 'INCREASE_BUDGET',
                        'suggested_change': 0.20,  # +20%
                        'reason': f'ROAS surge detected (z-score: {latest["roas_anomaly_score"]:.2f}) with stable spending',
                        'confidence': 'HIGH',
                        'current_spend': latest['spend'],
                        'current_roas': latest['roas']
                    })
            
            # Check for CTR anomalies
            elif latest['ctr_anomaly'] and latest['ctr_anomaly_score'] < -2:
                recommendations.append({
                    'platform': platform,
                    'campaign': campaign,
                    'recommendation': 'REVIEW_CREATIVE',
                    'suggested_change': 0.0,
                    'reason': f'Significant CTR drop detected (z-score: {latest["ctr_anomaly_score"]:.2f}). Consider refreshing ad creative.',
                    'confidence': 'MEDIUM',
                    'current_spend': latest['spend'],
                    'current_roas': latest['roas']
                })
        
        return recommendations
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of detected anomalies"""
        summary = {
            'total_records': len(df),
            'spend_anomalies': df['spend_anomaly'].sum(),
            'roas_anomalies': df['roas_anomaly'].sum(),
            'ctr_anomalies': df['ctr_anomaly'].sum(),
            'platforms_affected': df[df['spend_anomaly'] | df['roas_anomaly'] | df['ctr_anomaly']]['platform'].nunique(),
            'campaigns_affected': df[df['spend_anomaly'] | df['roas_anomaly'] | df['ctr_anomaly']]['campaign_name'].nunique()
        }
        
        return summary

def main():
    """Test anomaly detection on processed data"""
    import os
    from data_processor import AdDataProcessor
    
    # Load processed data
    if not os.path.exists('data/unified_ad_data.csv'):
        print("No processed data found. Please run data_processor.py first.")
        return
    
    df = pd.read_csv('data/unified_ad_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Initialize anomaly detector
    detector = AnomalyDetector(window_size=7, threshold=2.5)
    
    # Detect anomalies
    print("Detecting spending anomalies...")
    df = detector.detect_spend_anomalies(df)
    
    print("Detecting performance anomalies...")
    df = detector.detect_performance_anomalies(df)
    
    # Generate recommendations
    print("Generating budget recommendations...")
    recommendations = detector.generate_budget_recommendations(df)
    
    # Save results
    df.to_csv('data/unified_ad_data_with_anomalies.csv', index=False)
    
    # Print summary
    summary = detector.get_anomaly_summary(df)
    print("\n=== Anomaly Detection Summary ===")
    print(f"Total records analyzed: {summary['total_records']}")
    print(f"Spend anomalies detected: {summary['spend_anomalies']}")
    print(f"ROAS anomalies detected: {summary['roas_anomalies']}")
    print(f"CTR anomalies detected: {summary['ctr_anomalies']}")
    print(f"Platforms affected: {summary['platforms_affected']}")
    print(f"Campaigns affected: {summary['campaigns_affected']}")
    
    print(f"\n=== Budget Recommendations ({len(recommendations)}) ===")
    for rec in recommendations:
        change_pct = rec['suggested_change'] * 100
        print(f"{rec['platform']} - {rec['campaign']}: {rec['recommendation']} ({change_pct:+.0f}%)")
        print(f"  Reason: {rec['reason']}")
        print(f"  Current: Spend=${rec['current_spend']:.2f}, ROAS={rec['current_roas']:.2f}")

if __name__ == "__main__":
    main()
