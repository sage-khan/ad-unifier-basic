# Run this `streamlit run src/dashboard.py --server.port=8501 --server.address=0.0.0.0`

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime, timedelta

from data_processor import AdDataProcessor
from anomaly_detector import AnomalyDetector

# Page configuration
st.set_page_config(
    page_title="Unified Ads Campaign Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and cache the unified ad data"""
    processor = AdDataProcessor()
    detector = AnomalyDetector()
    
    if os.path.exists('data/unified_ad_data_with_anomalies.csv'):
        df = pd.read_csv('data/unified_ad_data_with_anomalies.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df, processor, detector
    elif os.path.exists('data/unified_ad_data.csv'):
        df = pd.read_csv('data/unified_ad_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        # Run anomaly detection
        df = detector.detect_spend_anomalies(df)
        df = detector.detect_performance_anomalies(df)
        return df, processor, detector
    else:
        st.error("No data found. Please run the data generation and processing scripts first.")
        return None, None, None

def create_kpi_cards(df, processor):
    """Create KPI summary cards"""
    summary = processor.get_platform_summary(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = summary['spend'].sum()
    total_revenue = summary['revenue'].sum()
    total_roas = total_revenue / total_spend if total_spend > 0 else 0
    total_conversions = summary['conversions'].sum()
    total_cpa = total_spend / total_conversions if total_conversions > 0 else 0
    
    with col1:
        st.metric(
            label="Total Spend",
            value=f"${total_spend:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Revenue", 
            value=f"${total_revenue:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Overall ROAS",
            value=f"{total_roas:.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Average CPA",
            value=f"${total_cpa:.2f}",
            delta=None
        )

def create_platform_comparison_chart(df, processor):
    """Create platform comparison chart"""
    summary = processor.get_platform_summary(df)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('ROAS by Platform', 'CPA by Platform', 'CTR by Platform', 'Spend by Platform'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # ROAS
    fig.add_trace(
        go.Bar(x=summary['platform'], y=summary['roas'], name='ROAS', marker_color='lightblue'),
        row=1, col=1
    )
    
    # CPA
    fig.add_trace(
        go.Bar(x=summary['platform'], y=summary['cpa'], name='CPA', marker_color='lightcoral'),
        row=1, col=2
    )
    
    # CTR
    fig.add_trace(
        go.Bar(x=summary['platform'], y=summary['ctr'], name='CTR', marker_color='lightgreen'),
        row=2, col=1
    )
    
    # Spend
    fig.add_trace(
        go.Bar(x=summary['platform'], y=summary['spend'], name='Spend', marker_color='gold'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Platform Performance Comparison")
    return fig

def create_daily_trends_chart(df, processor):
    """Create daily trends chart"""
    daily_trends = processor.get_daily_trends(df)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Daily Spend', 'Daily ROAS', 'Daily CTR', 'Daily Conversions'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Daily Spend
    fig.add_trace(
        go.Scatter(x=daily_trends['date'], y=daily_trends['spend'], 
                  mode='lines+markers', name='Spend', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Daily ROAS
    fig.add_trace(
        go.Scatter(x=daily_trends['date'], y=daily_trends['roas'], 
                  mode='lines+markers', name='ROAS', line=dict(color='green')),
        row=1, col=2
    )
    
    # Daily CTR
    fig.add_trace(
        go.Scatter(x=daily_trends['date'], y=daily_trends['ctr'], 
                  mode='lines+markers', name='CTR', line=dict(color='orange')),
        row=2, col=1
    )
    
    # Daily Conversions
    fig.add_trace(
        go.Scatter(x=daily_trends['date'], y=daily_trends['conversions'], 
                  mode='lines+markers', name='Conversions', line=dict(color='purple')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Daily Performance Trends")
    return fig

def create_anomaly_chart(df):
    """Create anomaly visualization"""
    # Filter data with anomalies
    anomalies = df[
        (df['spend_anomaly'] == True) | 
        (df['roas_anomaly'] == True) | 
        (df['ctr_anomaly'] == True)
    ].copy()
    
    if anomalies.empty:
        st.info("No anomalies detected in the current dataset.")
        return None
    
    fig = px.scatter(
        anomalies,
        x='date',
        y='spend',
        color='platform',
        size='roas',
        hover_data=['campaign_name', 'spend_anomaly_score', 'roas_anomaly_score'],
        title='Anomalies Detection - Spend vs Date (Size = ROAS)'
    )
    
    fig.update_layout(height=500)
    return fig

def display_recommendations(df, detector):
    """Display budget recommendations"""
    recommendations = detector.generate_budget_recommendations(df)
    
    if not recommendations:
        st.info("No budget recommendations at this time.")
        return
    
    st.subheader("💡 Budget Recommendations")
    
    for i, rec in enumerate(recommendations):
        with st.expander(f"{rec['platform']} - {rec['campaign']} ({rec['recommendation']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Recommendation:** {rec['recommendation']}")
                change_pct = rec['suggested_change'] * 100
                st.write(f"**Suggested Change:** {change_pct:+.0f}%")
                st.write(f"**Confidence:** {rec['confidence']}")
            
            with col2:
                st.write(f"**Current Spend:** ${rec['current_spend']:.2f}")
                st.write(f"**Current ROAS:** {rec['current_roas']:.2f}")
            
            st.write(f"**Reason:** {rec['reason']}")

def main():
    """Main dashboard function"""
    st.title("📊 Unified Ads Campaign Insights Dashboard")
    st.markdown("---")
    
    # Load data
    df, processor, detector = load_data()
    
    if df is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Platform filter
    platforms = ['All'] + list(df['platform'].unique())
    selected_platform = st.sidebar.selectbox("Select Platform", platforms)
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_platform != 'All':
        filtered_df = filtered_df[filtered_df['platform'] == selected_platform]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) & 
            (filtered_df['date'].dt.date <= end_date)
        ]
    
    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Anomalies", "💡 Recommendations", "📊 Raw Data"])
    
    with tab1:
        st.header("Performance Overview")
        
        # KPI Cards
        create_kpi_cards(filtered_df, processor)
        
        st.markdown("---")
        
        # Platform comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Platform Comparison")
            platform_chart = create_platform_comparison_chart(filtered_df, processor)
            st.plotly_chart(platform_chart, use_container_width=True)
        
        with col2:
            st.subheader("Daily Trends")
            trends_chart = create_daily_trends_chart(filtered_df, processor)
            st.plotly_chart(trends_chart, use_container_width=True)
        
        # Campaign performance table
        st.subheader("Campaign Performance")
        campaign_perf = processor.get_campaign_performance(filtered_df)
        st.dataframe(
            campaign_perf.round(3),
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        st.header("Anomaly Detection")
        
        # Anomaly summary
        anomaly_summary = detector.get_anomaly_summary(filtered_df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Spend Anomalies", anomaly_summary['spend_anomalies'])
        with col2:
            st.metric("ROAS Anomalies", anomaly_summary['roas_anomalies'])
        with col3:
            st.metric("CTR Anomalies", anomaly_summary['ctr_anomalies'])
        with col4:
            st.metric("Campaigns Affected", anomaly_summary['campaigns_affected'])
        
        # Anomaly visualization
        anomaly_chart = create_anomaly_chart(filtered_df)
        if anomaly_chart:
            st.plotly_chart(anomaly_chart, use_container_width=True)
        
        # Detailed anomaly table
        st.subheader("Anomaly Details")
        anomalies_detail = filtered_df[
            (filtered_df['spend_anomaly'] == True) | 
            (filtered_df['roas_anomaly'] == True) | 
            (filtered_df['ctr_anomaly'] == True)
        ][['date', 'platform', 'campaign_name', 'spend', 'roas', 'ctr', 
           'spend_anomaly_score', 'roas_anomaly_score', 'ctr_anomaly_score']]
        
        if not anomalies_detail.empty:
            st.dataframe(
                anomalies_detail.round(3),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No anomalies detected in the filtered data.")
    
    with tab3:
        st.header("Budget Recommendations")
        display_recommendations(filtered_df, detector)
    
    with tab4:
        st.header("Raw Data")
        
        # Display options
        col1, col2 = st.columns(2)
        with col1:
            show_anomaly_columns = st.checkbox("Show Anomaly Columns", value=False)
        with col2:
            max_rows = st.number_input("Max Rows to Display", min_value=10, max_value=1000, value=100)
        
        # Prepare data for display
        display_df = filtered_df.head(max_rows).copy()
        
        if not show_anomaly_columns:
            # Hide anomaly-related columns
            anomaly_cols = [col for col in display_df.columns if 'anomaly' in col.lower()]
            display_df = display_df.drop(columns=anomaly_cols, errors='ignore')
        
        st.dataframe(
            display_df.round(3),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"ad_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        Unified Ads Campaign Insights Dashboard | Built with Streamlit & Python
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
