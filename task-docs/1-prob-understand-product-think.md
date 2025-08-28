# Unified Ad Campaign Insights Prototype

## Understanding the Problem

Internet has expanded more in last 5 years than in last few decades after it was created. Data is everywhere and the amount of data generated from 2000 to 2025 exceeds the amount we have from centuries prior to this. This data generation rate will increase with progress in AI.

We find tools everywhere on the internet starting from a small problem like a Todo list app to bigger complex problems like building complete Data Operations using Apache Spark. Social Media has allowed marketing companies to run targetted ads which in turn provide alot of sales revenue. Face book reports 3.07 Billion active users as of July 2025. They generate 4 petabytes of data every single day which is a massive amount of information.

Now that we have so much data and so much tooling available, it gets hard to keep track of everything. There are thousands of platforms, each with their own pros and cons. Marketing companies want to leverage it to collect the relevant data for their ad campaigns. Every platform has its own nuances. Every platform (Google/Meta/LinkedIn/TikTok) labels things differently (campaign/ad set/ad group, “reach” vs “impressions”), exposes different metrics, and refreshes data on different cadences. Teams spend time stitching instead of deciding. CPA on platform A ≠ CPA on platform B if attribution windows, deduping, and conversion definitions differ. “Total ROAS” is often double-counted.

There are dozens of charts, but few reliable decision KPIs. Non-marketing stakeholders want crisp signals (what to cut/scale?) and confidence intervals. Metric definitions live in slide decks, not in code. When someone asks “why is ROAS down?”, there’s no semantic layer to reproduce the number.

It will be alot more efficient and feasible if all these platforms were brought on single dashboard where relevant information on the ad campains like engagement, CTR etc are measured effectively. That way better data-driven decisions can be taken.

## Core KPIs

- Return on Ad Spend or ROAS (Revenue ÷ Spend) — direct efficiency signal when you do have revenue/conversion value. Use platform-specific and unified (de-duplicated) views. Measures revenue generated per dollar spent (e.g., revenue / ad spend). It's crucial for assessing overall profitability and is widely used in tools like Google Analytics.
- Cost per acquisition or CPA (Spend ÷ Conversions) — when you target leads/events with consistent post-click value. Pairs with ROAS to reveal volume vs. efficiency tension. Calculates clicks divided by impressions, indicating ad relevance and audience engagement. A benchmark CTR is around 1-2% for display ads, per industry data.
- Click through rates or CTR (Clicks ÷ Impressions) — early creative quality signal; good for quick iteration, especially top-funnel. (Keep CPM and CVR as supportive). Tracks the cost to acquire a customer (ad spend / conversions). This helps identify efficient channels, with averages varying by industry (e.g., $50-100 for e-commerce).

These span funnel layers i.e.e attention -> efficiency -> Value) and can be easily interpretted to make data-driven budget calls.

CVR and CPM are also secondarily useful but we keep it to the 3 KPIs above.

## Smart Feature

If we go for basic anomaly detection types, we can add Anomaly-aware budget shifter. It will detect platform/campaign anomalies in spend (and optionally CTR/ROAS) using a robust rolling z-score (median + MAD). If spend spikes without matching ROAS, recommend a −20% trim; if ROAS surges with stable spend, recommend a +20% boost. Keep it transparent: include the evidence (last 7-day ROAS, CPA, anomaly score).

My inclination is to bring in Small Language Models in my architecture which can actually do good reasoning like Mistral AI or Llama. For charts we can utilize multimodal LLMs and they have a good potential to go through the past data and give prediciton. They can also query through data and give interesting insights. I had some success working with Balance sheets using Mistral AI in a client's project about 2 years ago on this.
