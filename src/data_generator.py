import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def generate_google_ads_data(days=30, campaigns=5):
    """Generate mock Google Ads data with Google-specific field names"""
    np.random.seed(42)
    
    dates = [datetime.now() - timedelta(days=x) for x in range(days)]
    campaign_names = [f"Google_Campaign_{i+1}" for i in range(campaigns)]
    
    data = []
    for date in dates:
        for campaign in campaign_names:
            # Simulate realistic ad performance with some variance
            impressions = np.random.poisson(10000)
            clicks = np.random.binomial(impressions, 0.02)  # ~2% CTR
            cost = clicks * np.random.uniform(1.5, 3.0)  # $1.5-3 CPC
            conversions = np.random.binomial(clicks, 0.05)  # ~5% conversion rate
            conv_value = conversions * np.random.uniform(50, 200)  # $50-200 per conversion
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Campaign': campaign,
                'Campaign ID': f"goog_{hash(campaign) % 10000}",
                'Impressions': impressions,
                'Clicks': clicks,
                'Cost': round(cost, 2),
                'Conversions': conversions,
                'Conv. value': round(conv_value, 2)
            })
    
    return pd.DataFrame(data)

def generate_meta_ads_data(days=30, campaigns=4):
    """Generate mock Meta (Facebook) Ads data with Meta-specific field names"""
    np.random.seed(43)
    
    dates = [datetime.now() - timedelta(days=x) for x in range(days)]
    campaign_names = [f"Meta_Campaign_{i+1}" for i in range(campaigns)]
    
    data = []
    for date in dates:
        for campaign in campaign_names:
            # Meta typically has different performance characteristics
            reach = np.random.poisson(8000)
            impressions = int(reach * np.random.uniform(1.2, 2.0))  # Frequency > 1
            link_clicks = np.random.binomial(impressions, 0.015)  # Slightly lower CTR
            amount_spent = link_clicks * np.random.uniform(1.0, 2.5)  # Lower CPC
            actions = np.random.binomial(link_clicks, 0.08)  # Higher conversion rate
            action_values = actions * np.random.uniform(40, 180)
            
            data.append({
                'reporting_starts': date.strftime('%Y-%m-%d'),
                'campaign_name': campaign,
                'campaign_id': f"meta_{hash(campaign) % 10000}",
                'reach': reach,
                'impressions': impressions,
                'link_clicks': link_clicks,
                'amount_spent': round(amount_spent, 2),
                'actions': actions,
                'action_values': round(action_values, 2)
            })
    
    return pd.DataFrame(data)

def generate_linkedin_ads_data(days=30, campaigns=3):
    """Generate mock LinkedIn Ads data with LinkedIn-specific field names"""
    np.random.seed(44)
    
    dates = [datetime.now() - timedelta(days=x) for x in range(days)]
    campaign_names = [f"LinkedIn_Campaign_{i+1}" for i in range(campaigns)]
    
    data = []
    for date in dates:
        for campaign in campaign_names:
            # LinkedIn typically has higher costs but better B2B conversion
            impressions = np.random.poisson(3000)  # Lower volume
            clicks = np.random.binomial(impressions, 0.025)  # Higher CTR for B2B
            total_spent = clicks * np.random.uniform(3.0, 8.0)  # Much higher CPC
            leads = np.random.binomial(clicks, 0.12)  # Higher conversion for B2B
            lead_value = leads * np.random.uniform(200, 500)  # Higher value per lead
            
            data.append({
                'start_at': date.strftime('%Y-%m-%d'),
                'campaign_group_name': campaign,
                'campaign_group_id': f"li_{hash(campaign) % 10000}",
                'impressions': impressions,
                'clicks': clicks,
                'cost_in_usd': round(total_spent, 2),
                'leads': leads,
                'lead_value_usd': round(lead_value, 2)
            })
    
    return pd.DataFrame(data)

def save_mock_data():
    """Generate and save mock data for all platforms"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate data for each platform
    google_data = generate_google_ads_data()
    meta_data = generate_meta_ads_data()
    linkedin_data = generate_linkedin_ads_data()
    
    # Save to CSV files
    google_data.to_csv('data/google_ads_raw.csv', index=False)
    meta_data.to_csv('data/meta_ads_raw.csv', index=False)
    linkedin_data.to_csv('data/linkedin_ads_raw.csv', index=False)
    
    print("Mock data generated successfully!")
    print(f"Google Ads: {len(google_data)} rows")
    print(f"Meta Ads: {len(meta_data)} rows")
    print(f"LinkedIn Ads: {len(linkedin_data)} rows")
    
    return google_data, meta_data, linkedin_data

if __name__ == "__main__":
    save_mock_data()
