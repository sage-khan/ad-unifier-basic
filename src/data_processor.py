import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

class AdDataProcessor:
    """Processes and normalizes ad data from multiple platforms"""
    
    def __init__(self):
        self.unified_schema = [
            'date', 'platform', 'campaign_id', 'campaign_name', 
            'impressions', 'clicks', 'spend', 'conversions', 'revenue'
        ]
    
    def normalize_google_ads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Google Ads data to unified schema"""
        normalized = pd.DataFrame()
        normalized['date'] = pd.to_datetime(df['Date'])
        normalized['platform'] = 'Google Ads'
        normalized['campaign_id'] = df['Campaign ID']
        normalized['campaign_name'] = df['Campaign']
        normalized['impressions'] = df['Impressions']
        normalized['clicks'] = df['Clicks']
        normalized['spend'] = df['Cost']
        normalized['conversions'] = df['Conversions']
        normalized['revenue'] = df['Conv. value']
        return normalized
    
    def normalize_meta_ads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize Meta Ads data to unified schema"""
        normalized = pd.DataFrame()
        normalized['date'] = pd.to_datetime(df['reporting_starts'])
        normalized['platform'] = 'Meta Ads'
        normalized['campaign_id'] = df['campaign_id']
        normalized['campaign_name'] = df['campaign_name']
        normalized['impressions'] = df['impressions']
        normalized['clicks'] = df['link_clicks']
        normalized['spend'] = df['amount_spent']
        normalized['conversions'] = df['actions']
        normalized['revenue'] = df['action_values']
        return normalized
    
    def normalize_linkedin_ads(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize LinkedIn Ads data to unified schema"""
        normalized = pd.DataFrame()
        normalized['date'] = pd.to_datetime(df['start_at'])
        normalized['platform'] = 'LinkedIn Ads'
        normalized['campaign_id'] = df['campaign_group_id']
        normalized['campaign_name'] = df['campaign_group_name']
        normalized['impressions'] = df['impressions']
        normalized['clicks'] = df['clicks']
        normalized['spend'] = df['cost_in_usd']
        normalized['conversions'] = df['leads']
        normalized['revenue'] = df['lead_value_usd']
        return normalized
    
    def load_and_normalize_all_data(self) -> pd.DataFrame:
        """Load all platform data and normalize to unified schema"""
        all_data = []
        
        # Load Google Ads data
        if os.path.exists('data/google_ads_raw.csv'):
            google_df = pd.read_csv('data/google_ads_raw.csv')
            google_normalized = self.normalize_google_ads(google_df)
            all_data.append(google_normalized)
        
        # Load Meta Ads data
        if os.path.exists('data/meta_ads_raw.csv'):
            meta_df = pd.read_csv('data/meta_ads_raw.csv')
            meta_normalized = self.normalize_meta_ads(meta_df)
            all_data.append(meta_normalized)
        
        # Load LinkedIn Ads data
        if os.path.exists('data/linkedin_ads_raw.csv'):
            linkedin_df = pd.read_csv('data/linkedin_ads_raw.csv')
            linkedin_normalized = self.normalize_linkedin_ads(linkedin_df)
            all_data.append(linkedin_normalized)
        
        # Combine all data
        if all_data:
            unified_df = pd.concat(all_data, ignore_index=True)
            unified_df = unified_df.sort_values(['date', 'platform'])
            return unified_df
        else:
            return pd.DataFrame(columns=self.unified_schema)
    
    def calculate_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate core KPIs: ROAS, CPA, CTR"""
        df = df.copy()
        
        # Avoid division by zero
        df['roas'] = np.where(df['spend'] > 0, df['revenue'] / df['spend'], 0)
        df['cpa'] = np.where(df['conversions'] > 0, df['spend'] / df['conversions'], 0)
        df['ctr'] = np.where(df['impressions'] > 0, df['clicks'] / df['impressions'], 0)
        
        # Additional useful metrics
        df['cpc'] = np.where(df['clicks'] > 0, df['spend'] / df['clicks'], 0)
        df['cvr'] = np.where(df['clicks'] > 0, df['conversions'] / df['clicks'], 0)
        df['cpm'] = np.where(df['impressions'] > 0, (df['spend'] / df['impressions']) * 1000, 0)
        
        return df
    
    def get_platform_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get aggregated metrics by platform"""
        summary = df.groupby('platform').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calculate KPIs for summary
        summary['roas'] = np.where(summary['spend'] > 0, summary['revenue'] / summary['spend'], 0)
        summary['cpa'] = np.where(summary['conversions'] > 0, summary['spend'] / summary['conversions'], 0)
        summary['ctr'] = np.where(summary['impressions'] > 0, summary['clicks'] / summary['impressions'], 0)
        
        return summary
    
    def get_daily_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get daily aggregated trends across all platforms"""
        daily = df.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calculate daily KPIs
        daily['roas'] = np.where(daily['spend'] > 0, daily['revenue'] / daily['spend'], 0)
        daily['cpa'] = np.where(daily['conversions'] > 0, daily['spend'] / daily['conversions'], 0)
        daily['ctr'] = np.where(daily['impressions'] > 0, daily['clicks'] / daily['impressions'], 0)
        
        return daily
    
    def get_campaign_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get performance metrics by campaign"""
        campaign_perf = df.groupby(['platform', 'campaign_name']).agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'conversions': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Calculate campaign KPIs
        campaign_perf['roas'] = np.where(campaign_perf['spend'] > 0, 
                                       campaign_perf['revenue'] / campaign_perf['spend'], 0)
        campaign_perf['cpa'] = np.where(campaign_perf['conversions'] > 0, 
                                      campaign_perf['spend'] / campaign_perf['conversions'], 0)
        campaign_perf['ctr'] = np.where(campaign_perf['impressions'] > 0, 
                                      campaign_perf['clicks'] / campaign_perf['impressions'], 0)
        
        return campaign_perf
    
    def save_processed_data(self, df: pd.DataFrame):
        """Save processed unified data"""
        os.makedirs('data', exist_ok=True)
        df.to_csv('data/unified_ad_data.csv', index=False)
        print(f"Processed data saved: {len(df)} rows")

def main():
    """Process all ad data and save unified dataset"""
    processor = AdDataProcessor()
    
    # Load and normalize all data
    unified_data = processor.load_and_normalize_all_data()
    
    if unified_data.empty:
        print("No data found. Please run data_generator.py first.")
        return
    
    # Calculate KPIs
    unified_data = processor.calculate_kpis(unified_data)
    
    # Save processed data
    processor.save_processed_data(unified_data)
    
    # Print summary statistics
    print("\n=== Data Processing Summary ===")
    print(f"Total records: {len(unified_data)}")
    print(f"Date range: {unified_data['date'].min()} to {unified_data['date'].max()}")
    print(f"Platforms: {', '.join(unified_data['platform'].unique())}")
    
    # Platform summary
    platform_summary = processor.get_platform_summary(unified_data)
    print("\n=== Platform Performance Summary ===")
    for _, row in platform_summary.iterrows():
        print(f"{row['platform']}: ROAS={row['roas']:.2f}, CPA=${row['cpa']:.2f}, CTR={row['ctr']:.3%}")

if __name__ == "__main__":
    main()
