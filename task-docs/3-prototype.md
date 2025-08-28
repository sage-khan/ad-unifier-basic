# Unified Ads Campaign Insights Prototype - Implementation Documentation

## Executive Summary

This prototype demonstrates a unified ad campaign insights platform that consolidates data from multiple advertising platforms (Google Ads, Meta Ads, LinkedIn Ads) into a single analytical dashboard. The solution addresses the core challenge of fragmented marketing data by providing normalized KPIs, anomaly detection, and AI-powered recommendations.

_P.S: I have used AI for formatting extensively here. My military background and association with Linux forces me into all of this OCD like behavior._

## Thought Process & Design Decisions

### 1. Problem Understanding
The core challenge is discussed in detail in the document `docs/1-prob-understand-product-think.md` where we discuss how marketing teams struggle with fragmented data across platforms, inconsistent metrics, and lack of unified decision-making tools. 

My approach to this is:

- **Identifying the pain points**: Different field names, varying attribution windows, scattered insights
- **Focusing on actionable metrics**: ROAS, CPA, CTR as the three most critical KPIs
- **Data Operations**: Setting up data pipeline, data ingestion, data normalization, data analytics, data serving
- **Prioritizing automation**: Anomaly detection and budget recommendations to reduce manual analysis
- **User Experience**: Interactive dashboard with filtering, exporting capabilities, and export capabilities. 


### 2. Architecture Philosophy
I chose a **layered architecture** that mirrors real-world data engineering patterns:

```
Data Sources → Ingestion → Normalization → Analytics → Serving
```

**Key Design Principles:**
- **Separation of Concerns**: Each module has a single responsibility
- **Extensibility**: Easy to add new platforms or metrics
- **Testability**: Mock data allows for consistent testing
- **Scalability**: Architecture supports growth from prototype to production

Remember that this is a minimalistic version I have made. If I were to build this thing to last, I will follow proper directory structuring based on Django or Flask (to stick to industry standards). Flask is more used but I like Django's structure more. That would depend on the team I have and their comfort as well and availability of developers in that framework in the market.

I keep modularity and security in mind. I will use proper authentication and authorization for the production version. I will also use proper logging and monitoring for the production version.
    - **Security**: Authentication or authorization
    - **Performance**: Optimization for for large datasets
    - **Data Quality**: <1% data discrepancy vs. platform native tools

### 3. Technology Stack Rationale

**Python Ecosystem Choice:**
- **Pandas**: Excellent for data manipulation and analysis
- **FastAPI**: Modern, fast, with automatic API documentation
- **Streamlit**: Rapid dashboard development with minimal frontend code
- **Plotly**: Interactive visualizations that work well with Streamlit

I Avoided React/Vue.js as it would require separate frontend development. I also skipped Spark/Airflow as it is overkill for prototype scale. I chose SQLite over PostgreSQL: Simpler setup, sufficient for demo.

As bare minimum, I always dockerize my applications as it allows for portability, scalability and robustness.

### 4. Data Model Design

**Unified Schema:**
```python
{
    'date', 'platform', 'campaign_id', 'campaign_name', 
    'impressions', 'clicks', 'spend', 'conversions', 'revenue'
}
```

This schema balances:
- **Completeness**: Captures essential metrics across platforms
- **Simplicity**: Easy to understand and extend
- **Compatibility**: Maps naturally to different platform APIs

## Implementation Highlights

### 1. Multi-Platform Data Simulation
Created realistic mock data generators that simulate actual platform differences:

- **Google Ads**: Standard performance with ~2% CTR, $1.5-3 CPC
- **Meta Ads**: Lower CPC but frequency-based impressions
- **LinkedIn Ads**: Higher CPC ($3-8) but better B2B conversion rates

### 2. Robust Anomaly Detection
Implemented statistical anomaly detection using:
- **Rolling Z-Score with Median + MAD**: More robust than standard deviation
- **7-day rolling window**: Balances sensitivity with stability
- **Multi-metric detection**: Spend, ROAS, and CTR anomalies

### 3. AI-Powered Recommendations
Built rule-based intelligence that:
- Detects spend spikes without matching ROAS → Recommend -20% budget
- Identifies ROAS surges with stable spend → Recommend +20% budget
- Flags CTR drops → Recommend creative refresh

### 4. Interactive Dashboard
Developed a comprehensive Streamlit dashboard with:
- **Real-time filtering**: Platform and date range filters
- **Multi-tab interface**: Overview, Anomalies, Recommendations, Raw Data
- **Export capabilities**: CSV download for further analysis

## How to Extend into a Complete Product

### Phase 1: Production Infrastructure (6 months)
**Data Pipeline:**
- Replace mock data with real API integrations (Google Ads API, Meta Marketing API, LinkedIn Campaign Manager API)
- Implement Apache Airflow for orchestration
- Add PostgreSQL/BigQuery for data warehousing
- Set up dbt for data transformations
-
**Reliability:**
- Add comprehensive error handling and retry logic
- Implement data quality checks and validation
- Set up monitoring and alerting (Datadog/New Relic)
- Add automated testing suite
- Improve directory structure as per industry standards like Flask or Django with separate frontend and backend (all Dockerized)

**Security:**
- Implement authentication and authorization
- Implement data encryption
- Implement access control
- Implement rate limiting

**Performance:**
- Implement caching
- Implement load balancing
- Implement horizontal scaling


### Phase 2: Advanced Analytics (6-12 months)
**Enhanced ML Capabilities:**
- Time series forecasting for budget planning
- Clustering analysis for audience segmentation
- Attribution modeling across platforms
- Real LLM integration (GPT-4/Claude) for insights generation

**Data Pipeline:**
- Implement Apache Airflow for orchestration
- Implement PostgreSQL/BigQuery for data warehousing
- Implement dbt for data transformations

**Data Quality:**
- Implement data validation
- Implement data quality checks
- Implement data quality metrics
- Implement data quality reporting
- Industry Standard Data Ops and Governance Practices

**Advanced Features:**
- Multi-touch attribution
- Incrementality testing
- Competitive intelligence
- Creative performance analysis

### Phase 3: Enterprise Features (12-18 months)
**Scalability:**
- Multi-tenant architecture
- Role-based access control
- Custom dashboard builder
- White-label solutions
- Kubernetes Clustering

**Integration:**
- CRM integration (Salesforce, HubSpot)
- BI tool connectors (Tableau, PowerBI)
- Marketing automation platforms
- Data lake integration

### Phase 4: AI-First Platform (18+ months)
**Autonomous Optimization:**
- Automated bid management
- Creative optimization recommendations
- Budget reallocation algorithms
- Predictive audience targeting

## Trade-offs Considered

### 1. Simplicity vs. Completeness
I Chose simplicity for the prototype for now because Better to have a working simple system than a complex broken one. Faster development, easier to understand. Howver, it is missing advanced features like attribution modeling.

### 2. Real-time vs. Batch Processing
Implemented batch processing because most marketing decisions in my view donot need real time data. It is a simpler architecture, sufficient for most use cases but obviously we do not real-time insights. 

### 3. Statistical vs. ML-based Anomaly Detection
I opted for statistical methods (Z-score with MAD) because they offer several advantages for small datasets. They are interpretable, meaning it's easy to understand why a particular metric is considered anomalous. They also require no training data, which is a benefit for prototyping. Additionally, statistical methods are relatively fast, making them suitable for real-time processing. However, statistical methods have a limitation. They are less sophisticated than machine learning approaches. They may not be able to capture complex patterns or relationships in the data. For example, they may not be able to detect anomalies that are not easily explainable by statistical means. Given the characteristics of our prototype, with its small dataset and simplicity-oriented approach, using statistical methods was the best choice. I have already covered that for a full project, I lean towards more LLM based methods. I believe SLMs are a game changer as they can be locally deployed and can give great results. In that case an Ollama Server with relevant SLM like Mistral or LLAMA can be integrated. Vectordbs will be introduced for more RAG based approach where required.

### 4. Custom UI vs. Streamlit
Used Streamlit for rapid prototyping. It is extremely fast development, Python-native. Limited customization, not production-ready for complex UIs

### 5. SQLite vs. PostgreSQL
Used CSV files and in-memory processing. No database setup required, portable. Not scalable, no concurrent access

### 6. Mock Data vs. Real API Integration
Created realistic mock data. No API keys required, consistent testing, faster development

## Technical Debt and Known Limitations

### Current Limitations:
1. **Data Volume**: Limited to small datasets (hundreds of records)
2. **Concurrency**: No support for multiple users
3. **Data Persistence**: No database, data regenerated each run
4. **Error Handling**: Basic error handling, not production-ready
5. **Security**: No authentication or authorization
6. **Performance**: Not optimized for large datasets

### Planned Improvements:
1. **Database Integration**: PostgreSQL with proper indexing
2. **Caching**: Redis for frequently accessed data
3. **Authentication**: OAuth integration with major platforms
4. **API Rate Limiting**: Proper throttling and queuing
5. **Data Validation**: Comprehensive input validation
6. **Logging**: Structured logging with correlation IDs

## Success Metrics and Validation

### Prototype Success Criteria (✅ Achieved):
- [x] Normalize data from 3+ platforms
- [x] Calculate core KPIs (ROAS, CPA, CTR)
- [x] Implement anomaly detection
- [x] Generate actionable recommendations
- [x] Interactive dashboard with filtering
- [x] REST API with documentation

### Production Success Metrics (Future):
- **User Adoption**: DAU/MAU, session duration
- **Business Impact**: Improved ROAS, reduced CPA
- **System Performance**: <2s dashboard load time, 99.9% uptime
- **Data Quality**: <1% data discrepancy vs. platform native tools

## Conclusion

This prototype successfully demonstrates the core concept of unified ad campaign insights. The modular architecture, realistic data simulation, and comprehensive analytics provide a solid foundation for production development.

The key innovation is the combination of:
1. **Unified data model** that works across platforms
2. **Robust anomaly detection** using statistical methods
3. **Actionable AI recommendations** with confidence levels
4. **Interactive dashboard** for self-service analytics

The prototype proves that fragmented marketing data can be effectively unified to provide actionable insights, setting the stage for a full production system that could significantly improve marketing decision-making across organizations.

---

**Built with**: Python, FastAPI, Streamlit, Pandas, Plotly  
**Development Time**: ~8 hours of AI-assisted development  
**Lines of Code**: ~1,200 lines across 8 modules  
**Test Coverage**: Mock data provides consistent testing environment