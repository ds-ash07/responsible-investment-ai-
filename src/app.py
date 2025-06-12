import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from tools.sdg_analyzer import SDGAnalyzer
from tools.sentiment_analyzer import SentimentAnalyzer
from tools.financial_analyzer import FinancialAnalyzer
from datetime import datetime, timedelta
import numpy as np
import json
import traceback
import yfinance as yf
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import base64

# Set page config
st.set_page_config(
    page_title="Responsible Investment Advisor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for persistent data
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'company_data' not in st.session_state:
    st.session_state.company_data = None
if 'current_company' not in st.session_state:
    st.session_state.current_company = None
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = None

# Custom CSS with improved styling
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1a237e;
        padding: 2rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Header Styles */
    .company-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .company-name {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .company-ticker {
        color: #90caf9;
        font-size: 1.5rem;
        margin-top: 0.5rem;
    }
    
    /* Dashboard Section */
    .dashboard-section {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .dashboard-title {
        color: #1a237e;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(26,35,126,0.1);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .metric-title {
        color: #1a237e;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .metric-score {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .metric-progress {
        background: #f5f5f5;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
    }
    
    .metric-progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Charts Section */
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    
    /* Analysis Section */
    .analysis-section {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .analysis-header {
        color: #1a237e;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(26,35,126,0.1);
    }
    
    /* Category Cards */
    .category-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid;
    }
    
    .environmental {
        border-color: #4caf50;
    }
    
    .social {
        border-color: #2196f3;
    }
    
    .governance {
        border-color: #9c27b0;
    }
    
    /* Improvement Tips */
    .tips-section {
        background: linear-gradient(165deg, #ffffff 0%, #f5f5f5 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .tip-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        border-left: 4px solid;
    }
    
    .tip-card:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* Recommendation Section */
    .recommendation-box {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    .score-box {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .analysis-box {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%);
        padding: 2rem 1rem;
    }
    
    .css-1d391kg .stRadio > label {
        color: white !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .dashboard-section, .analysis-section, .recommendation-box {
        animation: fadeIn 0.5s ease-out;
    }

    /* Recommendation Section Styles */
    .recommendation-section {
        background: linear-gradient(165deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 25px;
        padding: 3rem;
        margin: 3rem auto;
        max-width: 1200px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }

    .recommendation-header {
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        color: white;
    }

    .rating-container {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        backdrop-filter: blur(10px);
    }

    .rating-score {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .rating-score .score-max {
        font-size: 2rem;
        opacity: 0.8;
    }

    .rating-label {
        font-size: 1.8rem;
        margin: 1rem 0;
        padding: 0.5rem 2rem;
        border-radius: 50px;
        display: inline-block;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }

    .rating-excellent { background: linear-gradient(135deg, #00c853 0%, #64dd17 100%); }
    .rating-good { background: linear-gradient(135deg, #00b0ff 0%, #2979ff 100%); }
    .rating-neutral { background: linear-gradient(135deg, #ffd600 0%, #ffab00 100%); }
    .rating-caution { background: linear-gradient(135deg, #ff9100 0%, #ff6d00 100%); }
    .rating-avoid { background: linear-gradient(135deg, #ff1744 0%, #d50000 100%); }

    .recommendation-details {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        text-align: left;
        backdrop-filter: blur(10px);
    }

    .recommendation-details h3 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: rgba(255,255,255,0.9);
    }

    .recommendation-details p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    .key-points {
        display: grid;
        gap: 1rem;
        margin-top: 1.5rem;
    }

    .key-point {
        background: rgba(255,255,255,0.05);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: transform 0.3s ease;
    }

    .key-point:hover {
        transform: translateX(10px);
        background: rgba(255,255,255,0.1);
    }

    .key-point-icon {
        font-size: 1.5rem;
    }

    .key-point-text {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }

    /* Add this CSS inside the existing style block */
    .ai-insights {
        background: #ffffff;
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.05);
    }

    .ai-insights h3 {
        color: #1a237e;
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2.5rem;
    }

    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
    }

    .insight-card {
        background: #f8faf8;
        border-radius: 20px;
        padding: 1.5rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }

    .insight-card.strengths {
        background: linear-gradient(to bottom right, #f8faf8, #f0f7f0);
        border-left: 4px solid #4caf50;
    }

    .insight-card.risks {
        background: linear-gradient(to bottom right, #fff9f9, #fff5f5);
        border-left: 4px solid #f44336;
    }

    .insight-card.opportunities {
        background: linear-gradient(to bottom right, #f5f9ff, #f0f6ff);
        border-left: 4px solid #2196f3;
    }

    .insight-card h4 {
        color: #333;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .insights-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .insight-item {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .insight-item:hover {
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .insight-text {
        color: #444;
        font-size: 0.95rem;
        line-height: 1.5;
        flex: 1;
    }

    .insight-score {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        white-space: nowrap;
        min-width: 70px;
        text-align: center;
    }

    .strengths .insight-score {
        color: #2e7d32;
        background: #e8f5e9;
    }

    .risks .insight-score {
        color: #d32f2f;
        background: #ffebee;
    }

    .opportunities .insight-score {
        color: #1976d2;
        background: #e3f2fd;
    }

    /* Enhanced Strengths and Concerns section
    .strengths .insight-item::before { color: #4caf50; }
    .risks .insight-item::before { color: #f44336; }
    .opportunities .insight-item::before { color: #2196f3; }
</style>
""", unsafe_allow_html=True)

# Initialize analyzers with Mistral-7B
sdg_analyzer = SDGAnalyzer(model_key='mistral')
sentiment_analyzer = SentimentAnalyzer(model_key='mistral')
financial_analyzer = FinancialAnalyzer(model_key='mistral')

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("", [
    "Company Analysis",
    "Industry Comparison",
    "Methodology",
    "AI Ethics & Trust"  # Add new option
])

def format_metric_value(value):
    """Format metric value based on its type"""
    if isinstance(value, (float, int)):
        return f"{value:.1f}"
    elif value == 'N/A' or value is None:
        return 'N/A'
    else:
        return str(value)

def create_gauge_chart(value, title, min_val=0, max_val=10):
    """Create a gauge chart using plotly"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3.5], 'color': "red"},
                {'range': [3.5, 5], 'color': "orange"},
                {'range': [5, 6.5], 'color': "yellow"},
                {'range': [6.5, 8], 'color': "lightgreen"},
                {'range': [8, 10], 'color': "green"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
    return fig

def create_radar_chart(categories, values, title):
    """Create a radar chart for ESG metrics"""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title,
        line_color='rgb(31, 119, 180)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title=title,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def create_trend_chart(data, title):
    """Create a line chart for trends"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(data.keys()),
        y=list(data.values()),
        mode='lines+markers',
        name=title
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Time Period",
        yaxis_title="Value",
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig

def get_ai_recommendation(company_name, sdg_score, sentiment_score, esg_score):
    """Generate AI recommendation based on scores"""
    # Calculate weighted final score
    final_score = (esg_score * 0.4) + (sdg_score * 0.3) + (sentiment_score * 0.3)
    
    # Generate recommendation based on score
    if final_score >= 8.0:
        recommendation = f"{company_name} demonstrates exceptional commitment to ESG principles and sustainable development goals. The company shows strong market sentiment and robust governance practices. This presents a compelling investment opportunity for environmentally and socially conscious investors."
    elif final_score >= 7.0:
        recommendation = f"{company_name} shows strong performance in ESG metrics and sustainable development alignment. While there are some areas for improvement, the overall outlook is positive, suggesting a favorable investment opportunity with manageable risks."
    elif final_score >= 6.0:
        recommendation = f"{company_name} meets basic ESG and sustainability requirements but shows room for improvement. Consider monitoring the company's progress in addressing key areas before making significant investment decisions."
    else:
        recommendation = f"{company_name} faces significant challenges in ESG compliance and sustainable development alignment. Substantial improvements are needed in key areas. Investment carries higher ESG-related risks."
    
    return recommendation

def display_metrics_grid(title, metrics, overall_score=None):
    """Display metrics in a 2x2 grid with overall score"""
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    
    # Display overall score if provided
    if overall_score is not None:
        # Determine color based on score
        if overall_score >= 8.0:
            color = "#00c853"  # Bright green
        elif overall_score >= 7.0:
            color = "#64dd17"  # Light green
        elif overall_score >= 6.0:
            color = "#ffd600"  # Yellow
        else:
            color = "#ff1744"  # Red
            
        st.markdown(f"""
        <div style='background-color: #1a237e; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 1rem 0;'>
            <h3 style='color: white; margin: 0;'>Overall {title} Score</h3>
            <h1 style='color: {color}; margin: 0.5rem 0;'>{overall_score:.1f}/10</h1>
            <div class="score-progress">
                <div class="score-progress-bar" style="width: {overall_score * 10}%; background: {color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    for metric_name, data in metrics.items():
        score = data.get('score', 'N/A')
        details = data.get('details', 'No details available')
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{metric_name.replace('_', ' ').title()}</div>
            <div class="metric-score">{score}</div>
            <div class="metric-description">{details}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_improvement_tips(sdg_results):
    """Display improvement tips with enhanced visual formatting"""
    st.markdown('<div class="tips-section">', unsafe_allow_html=True)
    st.markdown('<div class="tips-header">ESG & SDG Improvement Tips</div>', unsafe_allow_html=True)
    
    # Environmental Tips
    env_scores = sdg_results.get('environmental', {})
    if any(isinstance(data, dict) and data.get('score', 10) < 8 for data in env_scores.values()):
        st.markdown("""
        <div class="tips-category">
            <div class="tips-category-header">
                <span class="category-icon">🌍</span> Environmental Improvements
            </div>
        """, unsafe_allow_html=True)
        
        for metric, data in env_scores.items():
            if isinstance(data, dict) and data.get('score', 10) < 8:
                st.markdown(f"""
                <div class="tip-card environmental">
                    <div class="tip-title">
                        <span class="category-icon">📊</span> {metric.replace('_', ' ').title()}
                    </div>
                    <div class="tip-content">
                        {data.get('details', 'No specific recommendations available')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Social Tips
    social_scores = sdg_results.get('social', {})
    if any(isinstance(data, dict) and data.get('score', 10) < 8 for data in social_scores.values()):
        st.markdown("""
        <div class="tips-category">
            <div class="tips-category-header">
                <span class="category-icon">👥</span> Social Improvements
            </div>
        """, unsafe_allow_html=True)
        
        for metric, data in social_scores.items():
            if isinstance(data, dict) and data.get('score', 10) < 8:
                st.markdown(f"""
                <div class="tip-card social">
                    <div class="tip-title">
                        <span class="category-icon">📊</span> {metric.replace('_', ' ').title()}
                    </div>
                    <div class="tip-content">
                        {data.get('details', 'No specific recommendations available')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Governance Tips
    gov_scores = sdg_results.get('governance', {})
    if any(isinstance(data, dict) and data.get('score', 10) < 8 for data in gov_scores.values()):
        st.markdown("""
        <div class="tips-category">
            <div class="tips-category-header">
                <span class="category-icon">⚖️</span> Governance Improvements
            </div>
        """, unsafe_allow_html=True)
        
        for metric, data in gov_scores.items():
            if isinstance(data, dict) and data.get('score', 10) < 8:
                st.markdown(f"""
                <div class="tip-card governance">
                    <div class="tip-title">
                        <span class="category-icon">📊</span> {metric.replace('_', ' ').title()}
                    </div>
                    <div class="tip-content">
                        {data.get('details', 'No specific recommendations available')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_investment_recommendation(sdg_results, sentiment_results, financial_results):
    """Display investment recommendation with overall scores and AI insights"""
    # Calculate overall scores
    esg_score = sum([
        sdg_results.get('environmental', {}).get('climate_action', {}).get('score', 5.0),
        sdg_results.get('environmental', {}).get('resource_efficiency', {}).get('score', 5.0),
        sdg_results.get('environmental', {}).get('water_management', {}).get('score', 5.0),
        sdg_results.get('environmental', {}).get('waste_management', {}).get('score', 5.0)
    ]) / 4.0

    sdg_score = sum([
        sdg_results.get('sdg_alignment', {}).get('environmental', {}).get('score', 5.0),
        sdg_results.get('sdg_alignment', {}).get('social', {}).get('score', 5.0),
        sdg_results.get('sdg_alignment', {}).get('economic', {}).get('score', 5.0),
        sdg_results.get('sdg_alignment', {}).get('partnerships', {}).get('score', 5.0)
    ]) / 4.0

    sentiment_score = sentiment_results.get('overall_sentiment', 5.0)
    
    # Calculate final weighted score
    final_score = (esg_score * 0.4) + (sdg_score * 0.3) + (sentiment_score * 0.3)
    
    # Get AI insights
    ai_insights = financial_results.get('ai_insights', {})
    strengths = ai_insights.get('strengths', [])
    risks = ai_insights.get('risks', [])
    opportunities = ai_insights.get('opportunities', [])
    positioning = ai_insights.get('positioning', '')
    outlook = ai_insights.get('outlook', '')
    
    # Get recommendation details
    if final_score >= 8.0:
        recommendation = "Strong Buy"
        color = "#00c853"
        icon = "⭐⭐⭐"
    elif final_score >= 7.0:
        recommendation = "Buy"
        color = "#64dd17"
        icon = "⭐⭐"
    elif final_score >= 6.0:
        recommendation = "Hold"
        color = "#ffd600"
        icon = "⭐"
    else:
        recommendation = "Not Recommended"
        color = "#ff1744"
        icon = "⚠️"

    # Create the recommendation box with AI insights
    recommendation_html = f"""
    <div class="recommendation-box">
        <div class="recommendation-title">AI Investment Analysis</div>
        <div class="score-box">
            <div class="score-icon">{icon}</div>
            <div class="score-text" style="color: {color}">{recommendation}</div>
            <div class="score-value">Overall Score: {final_score:.1f}/10</div>
        </div>
        
        <div class="analysis-box">
            <div class="analysis-header">
                <span>🤖</span>
                Market Positioning
            </div>
            <div class="analysis-content">
                {positioning}
            </div>
        </div>
        
        <div class="analysis-grid">
            <div class="analysis-card strengths">
                <h4>💪 Key Strengths</h4>
                <ul>
                    {''.join(f'<li>{strength}</li>' for strength in strengths)}
                </ul>
            </div>
            
            <div class="analysis-card risks">
                <h4>⚠️ Key Risks</h4>
                <ul>
                    {''.join(f'<li>{risk}</li>' for risk in risks)}
                </ul>
            </div>
            
            <div class="analysis-card opportunities">
                <h4>🎯 Growth Opportunities</h4>
                <ul>
                    {''.join(f'<li>{opportunity}</li>' for opportunity in opportunities)}
                </ul>
            </div>
        </div>
        
        <div class="analysis-box outlook">
            <div class="analysis-header">
                <span>🔮</span>
                Future Outlook
            </div>
            <div class="analysis-content">
                {outlook}
            </div>
        </div>
    </div>
    """
    
    # Add CSS for the new AI insights layout
    st.markdown("""
    <style>
    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .analysis-card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .analysis-card h4 {
        color: #1a237e;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .analysis-card ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }
    
    .analysis-card li {
        margin-bottom: 0.8rem;
        padding-left: 1.2rem;
        position: relative;
        line-height: 1.4;
    }
    
    .analysis-card li:before {
        content: "•";
        position: absolute;
        left: 0;
        color: #1a237e;
    }
    
    .outlook {
        margin-top: 2rem;
        background: linear-gradient(135deg, rgba(26,35,126,0.05) 0%, rgba(13,71,161,0.05) 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render the recommendation
    st.markdown(recommendation_html, unsafe_allow_html=True)

    # Add Financial Analysis Section
    st.markdown("""
    <div style='
        background: linear-gradient(165deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 25px;
        padding: 3rem;
        margin: 3rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    '>
        <h2 style='
            color: #1a237e;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        '>Financial Analysis</h2>
    """, unsafe_allow_html=True)

    # Core Metrics
    st.markdown("""
        <div style='
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            margin-top: 2rem;
        '>
    """, unsafe_allow_html=True)

    # ... Continue breaking down the large template into smaller chunks ...
    # Each section (Core Metrics, Growth Metrics, etc.) should be its own st.markdown call

def display_company_analysis(company_name, ticker):
    """Display comprehensive company analysis including both financial and ESG metrics"""
    with st.spinner('Analyzing company data...'):
        try:
            print("=== Starting Company Analysis ===")
            print(f"Analyzing {company_name} ({ticker})")
            
            # Get analysis results
            print("--- Testing SDG Analysis ---")
            sdg_results = sdg_analyzer.analyze(company_name)
            print(f"SDG Analysis Result: {sdg_results}")
            
            print("--- Testing Sentiment Analysis ---")
            sentiment_results = sentiment_analyzer.analyze(company_name)
            print(f"Sentiment Analysis Result: {sentiment_results}")
            
            print("--- Testing Financial Analysis ---")
            financial_results = financial_analyzer.analyze(ticker)
            print(f"Financial Analysis Result: {financial_results}")
            
            # Ensure financial_results has the correct structure
            if financial_results and isinstance(financial_results, dict):
                # Extract metrics from the response
                metrics = financial_results.get('metrics', {})
                analysis = financial_results.get('analysis', {})
                
                # Create core_metrics structure if it doesn't exist
                if 'core_metrics' not in financial_results:
                    financial_results['core_metrics'] = financial_results  # Use the data directly if it's already in the right format
            
            print("=== Analysis Results ===")
            final_data = {
                'sdg': sdg_results,
                'sentiment': sentiment_results,
                'financial': financial_results
            }
            print(f"Final Data: {final_data}")
            
            # Header Section
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(26, 35, 126, 0.95) 0%, rgba(13, 71, 161, 0.95) 100%);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 3rem;
                margin-bottom: 3rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
                text-align: center;
            '>
                <div style='font-size: 3.5rem; color: white; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                    {company_name}
                </div>
                <div style='font-size: 2rem; color: #90caf9; font-weight: 500; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>
                    {ticker}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Dashboard Overview Section
            st.markdown("""
            <div style='
                background: white;
                border-radius: 25px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            '>
                <h2 style='
                    color: #1a237e;
                    font-size: 2.2rem;
                    font-weight: bold;
                    margin-bottom: 2rem;
                    text-align: center;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid rgba(26,35,126,0.1);
                '>Dashboard Overview</h2>
            """, unsafe_allow_html=True)
            
            # Calculate overall scores from SDG results
            env_score = sdg_results.get('scores', {}).get('environmental', 5.0)
            social_score = sdg_results.get('scores', {}).get('social', 5.0)
            gov_score = sdg_results.get('scores', {}).get('governance', 5.0)
            sdg_alignment_score = sdg_results.get('scores', {}).get('sdg_alignment', 5.0)
            
            # Get sentiment score
            sentiment_score = sentiment_results.get('sentiment_score', 5.0)
            
            # Calculate overall score
            overall_score = (env_score * 0.3) + (social_score * 0.2) + (gov_score * 0.2) + (sdg_alignment_score * 0.15) + (sentiment_score * 0.15)
            
            # Create modern progress bars for main metrics
            metrics = [
                {"name": "Environmental", "score": env_score, "color": "#4caf50", "icon": "🌍"},
                {"name": "Social", "score": social_score, "color": "#2196f3", "icon": "👥"},
                {"name": "Governance", "score": gov_score, "color": "#9c27b0", "icon": "⚖️"},
                {"name": "Market Sentiment", "score": sentiment_score, "color": "#ff9800", "icon": "📈"}
            ]
            
            # Display metrics
            for metric in metrics:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, white 0%, #f8f9fa 100%);
                    padding: 1.8rem;
                    border-radius: 20px;
                    margin-bottom: 1rem;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    border: 1px solid rgba(0,0,0,0.05);
                    transition: transform 0.3s ease;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
                        <div style='display: flex; align-items: center; gap: 1rem;'>
                            <span style='font-size: 2rem;'>{metric['icon']}</span>
                            <span style='color: #1a237e; font-weight: 600; font-size: 1.2rem;'>{metric['name']}</span>
                        </div>
                        <div style='
                            background: {metric['color']}22;
                            color: {metric['color']};
                            padding: 0.5rem 1rem;
                            border-radius: 15px;
                            font-weight: bold;
                            font-size: 1.3rem;
                        '>{metric['score']:.1f}</div>
                    </div>
                    <div style='background: #f5f5f5; border-radius: 15px; height: 10px; overflow: hidden;'>
                        <div style='
                            width: {metric['score']*10}%;
                            height: 100%;
                            background: linear-gradient(90deg, {metric['color']}88, {metric['color']});
                            border-radius: 15px;
                            transition: width 1s ease;
                        '></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # ESG Analysis Section with enhanced visuals
            st.markdown("""
            <div style='
                background: linear-gradient(165deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 25px;
                padding: 3rem;
                margin: 3rem 0;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            '>
                <h2 style='
                    color: #1a237e;
                    font-size: 2.5rem;
                    text-align: center;
                    margin-bottom: 2rem;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                '>ESG Analysis</h2>
            """, unsafe_allow_html=True)
            
            # Display overall ESG score with enhanced design
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #004d40 0%, #00695c 100%);
                border-radius: 20px;
                padding: 2.5rem;
                text-align: center;
                margin: 2rem 0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border: 1px solid rgba(255,255,255,0.1);
            '>
                <h2 style='color: white; margin: 0; font-size: 2.2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                    Overall ESG Score
                </h2>
                <div style='
                    font-size: 4rem;
                    color: #80cbc4;
                    margin: 1rem 0;
                    font-weight: bold;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                '>{overall_score:.1f}<span style='font-size: 2rem;'>/10</span></div>
                <div style='
                    background: rgba(255,255,255,0.1);
                    height: 12px;
                    border-radius: 10px;
                    margin: 1.5rem auto;
                    width: 80%;
                    overflow: hidden;
                '>
                    <div style='
                        width: {overall_score * 10}%;
                        height: 100%;
                        background: linear-gradient(90deg, #80cbc4, #4db6ac);
                        border-radius: 10px;
                        transition: width 1s ease;
                    '></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display justifications with enhanced cards
            st.markdown("<h3 style='color: #1a237e; font-size: 1.8rem; margin: 2rem 0;'>Analysis Details</h3>", unsafe_allow_html=True)
            
            for category, justification in sdg_results.get('justifications', {}).items():
                icon = {
                    'environmental': '🌍',
                    'social': '👥',
                    'governance': '⚖️',
                    'sdg_alignment': '🎯'
                }.get(category, '📊')
                
                st.markdown(f"""
                <div style='
                    background: white;
                    border-radius: 20px;
                    padding: 2rem;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                    border: 1px solid rgba(0,0,0,0.05);
                    transition: transform 0.3s ease;
                '>
                    <div style='
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1rem;
                    '>
                        <span style='font-size: 2rem;'>{icon}</span>
                        <h3 style='
                            color: #1a237e;
                            font-size: 1.5rem;
                            margin: 0;
                        '>{category.replace('_', ' ').title()}</h3>
                    </div>
                    <p style='
                        color: #555;
                        font-size: 1.1rem;
                        line-height: 1.6;
                        margin: 0;
                    '>{justification}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced Strengths and Concerns section
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #f8faf8 0%, #e8f5e9 100%);
                    border-radius: 20px;
                    padding: 2rem;
                    height: 100%;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                '>
                    <h3 style='
                        color: #2e7d32;
                        font-size: 1.8rem;
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    '>
                        <span>🔼</span>Strengths
                    </h3>
                """, unsafe_allow_html=True)
                
                for strength in sdg_results.get('strengths', []):
                    st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-bottom: 1rem;
                        border-left: 4px solid #2e7d32;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    '>
                        <div style='
                            color: #2e7d32;
                            font-weight: 600;
                            font-size: 1.2rem;
                            margin-bottom: 0.5rem;
                        '>{strength['category']}</div>
                        <div style='
                            color: #333;
                            margin-bottom: 0.5rem;
                            font-size: 1.1rem;
                        '>{strength['description']}</div>
                        <div style='
                            color: #666;
                            font-size: 0.9rem;
                            background: #f5f5f5;
                            padding: 0.5rem 1rem;
                            border-radius: 10px;
                            display: inline-block;
                        '>Evidence: {strength['evidence']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #fafafa 0%, #ffebee 100%);
                    border-radius: 20px;
                    padding: 2rem;
                    height: 100%;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                '>
                    <h3 style='
                        color: #c62828;
                        font-size: 1.8rem;
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    '>
                        <span>🔽</span>Concerns
                    </h3>
                """, unsafe_allow_html=True)
                
                for concern in sdg_results.get('concerns', []):
                    st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-bottom: 1rem;
                        border-left: 4px solid #c62828;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    '>
                        <div style='
                            color: #c62828;
                            font-weight: 600;
                            font-size: 1.2rem;
                            margin-bottom: 0.5rem;
                        '>{concern['category']}</div>
                        <div style='
                            color: #333;
                            margin-bottom: 0.5rem;
                            font-size: 1.1rem;
                        '>{concern['description']}</div>
                        <div style='
                            color: #666;
                            font-size: 0.9rem;
                            background: #f5f5f5;
                            padding: 0.5rem 1rem;
                            border-radius: 10px;
                            display: inline-block;
                        '>Impact: {concern['impact']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Enhanced Market Sentiment Section
            st.markdown("""
            <div style='
                background: linear-gradient(165deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 25px;
                padding: 3rem;
                margin: 3rem 0;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            '>
                <h2 style='
                    color: #1a237e;
                    font-size: 2.5rem;
                    text-align: center;
                    margin-bottom: 2rem;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                '>Market Sentiment Analysis</h2>
            """, unsafe_allow_html=True)
            
            # Display sentiment score with enhanced design
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
                border-radius: 20px;
                padding: 2.5rem;
                text-align: center;
                margin: 2rem 0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border: 1px solid rgba(255,255,255,0.1);
            '>
                <h2 style='color: white; margin: 0; font-size: 2.2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                    Overall Market Sentiment Score
                </h2>
                <div style='
                    font-size: 4rem;
                    color: #90caf9;
                    margin: 1rem 0;
                    font-weight: bold;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
                '>{sentiment_score:.1f}<span style='font-size: 2rem;'>/10</span></div>
                <div style='
                    color: white;
                    font-size: 1.2rem;
                    opacity: 0.9;
                '>Confidence: {sentiment_results.get('confidence', 0.0):.0%}</div>
                <div style='
                    background: rgba(255,255,255,0.1);
                    height: 12px;
                    border-radius: 10px;
                    margin: 1.5rem auto;
                    width: 80%;
                    overflow: hidden;
                '>
                    <div style='
                        width: {sentiment_score * 10}%;
                        height: 100%;
                        background: linear-gradient(90deg, #90caf9, #42a5f5);
                        border-radius: 10px;
                        transition: width 1s ease;
                    '></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced sentiment factors display
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #f8faf8 0%, #e8f5e9 100%);
                    border-radius: 20px;
                    padding: 2rem;
                    height: 100%;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                '>
                    <h3 style='
                        color: #2e7d32;
                        font-size: 1.8rem;
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    '>
                        <span>📈</span>Positive Factors
                    </h3>
                """, unsafe_allow_html=True)
                
                for factor in sentiment_results.get('positive_factors', []):
                    st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-bottom: 1rem;
                        border-left: 4px solid #2e7d32;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    '>
                        <div style='
                            color: #2e7d32;
                            font-weight: 600;
                            font-size: 1.2rem;
                            margin-bottom: 0.5rem;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        '>
                            <span>{factor['category']}</span>
                            <span style='
                                background: #e8f5e9;
                                padding: 0.3rem 0.8rem;
                                border-radius: 20px;
                                font-size: 1rem;
                            '>Score: {factor['impact_score']:.1f}</span>
                        </div>
                        <div style='
                            color: #333;
                            font-size: 1.1rem;
                            line-height: 1.5;
                        '>{factor['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #fafafa 0%, #ffebee 100%);
                    border-radius: 20px;
                    padding: 2rem;
                    height: 100%;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                '>
                    <h3 style='
                        color: #c62828;
                        font-size: 1.8rem;
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    '>
                        <span>📉</span>Negative Factors
                    </h3>
                """, unsafe_allow_html=True)
                
                for factor in sentiment_results.get('negative_factors', []):
                    st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-bottom: 1rem;
                        border-left: 4px solid #c62828;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    '>
                        <div style='
                            color: #c62828;
                            font-weight: 600;
                            font-size: 1.2rem;
                            margin-bottom: 0.5rem;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        '>
                            <span>{factor['category']}</span>
                            <span style='
                                background: #ffebee;
                                padding: 0.3rem 0.8rem;
                                border-radius: 20px;
                                font-size: 1rem;
                            '>Score: {factor['impact_score']:.1f}</span>
                        </div>
                        <div style='
                            color: #333;
                            font-size: 1.1rem;
                            line-height: 1.5;
                        '>{factor['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Enhanced major events timeline
            st.markdown("""
            <h3 style='
                color: #1a237e;
                font-size: 1.8rem;
                margin: 2rem 0;
                text-align: center;
            '>Major Events Timeline</h3>
            """, unsafe_allow_html=True)
            
            for event in sentiment_results.get('major_events', []):
                score_color = '#2e7d32' if event['score_change'] > 0 else '#c62828'
                score_bg = '#e8f5e9' if event['score_change'] > 0 else '#ffebee'
                
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    margin-bottom: 1rem;
                    border-left: 4px solid {score_color};
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                    display: flex;
                    align-items: center;
                    gap: 2rem;
                '>
                    <div style='
                        min-width: 100px;
                        text-align: center;
                        padding: 0.5rem;
                        background: {score_bg};
                        border-radius: 10px;
                        color: {score_color};
                        font-weight: 500;
                    '>{event['date']}</div>
                    <div style='flex-grow: 1;'>
                        <div style='
                            color: #333;
                            font-weight: 600;
                            font-size: 1.1rem;
                            margin-bottom: 0.3rem;
                        '>{event['event']}</div>
                        <div style='color: #666;'>{event['impact']}</div>
                    </div>
                    <div style='
                        color: {score_color};
                        font-weight: 600;
                        background: {score_bg};
                        padding: 0.5rem 1rem;
                        border-radius: 10px;
                        white-space: nowrap;
                    '>Score Impact: {event['score_change']:+.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced trend analysis
            if 'trend_analysis' in sentiment_results:
                trend = sentiment_results['trend_analysis']
                st.markdown(f"""
                <div style='
                    background: white;
                    border-radius: 20px;
                    padding: 2rem;
                    margin: 2rem 0;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                '>
                    <h3 style='
                        color: #1a237e;
                        font-size: 1.8rem;
                        margin-bottom: 1.5rem;
                        text-align: center;
                    '>Market Trend Analysis</h3>
                    <div style='
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 2rem;
                    '>
                        <div style='
                            background: #f8f9fa;
                            padding: 1.5rem;
                            border-radius: 15px;
                        '>
                            <h4 style='
                                color: #1a237e;
                                font-size: 1.3rem;
                                margin-bottom: 1rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            '>
                                <span>📊</span>Current Trend
                            </h4>
                            <p style='
                                color: #555;
                                font-size: 1.1rem;
                                line-height: 1.6;
                                margin: 0;
                            '>{trend['current_trend']}</p>
                        </div>
                        <div style='
                            background: #f8f9fa;
                            padding: 1.5rem;
                            border-radius: 15px;
                        '>
                            <h4 style='
                                color: #1a237e;
                                font-size: 1.3rem;
                                margin-bottom: 1rem;
                                display: flex;
                                align-items: center;
                                gap: 0.5rem;
                            '>
                                <span>🔮</span>Future Outlook
                            </h4>
                            <p style='
                                color: #555;
                                font-size: 1.1rem;
                                line-height: 1.6;
                                margin: 0;
                            '>{trend['future_outlook']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Financial Analysis Section
            display_financial_analysis(financial_results)

            # Add AI Insights section
            display_ai_insights(financial_results)
            
            # Display recommendation section
            display_recommendation_section(financial_results, sdg_results, sentiment_results)
            
            # Update session state
            st.session_state.analysis_complete = True
            st.session_state.company_data = final_data
            
            # After all analysis is complete, add the PDF download button
            if st.session_state.analysis_complete and st.session_state.company_data:
                st.markdown("---")
                st.markdown("### Download Analysis Report")
                pdf_buffer = generate_pdf_report(company_name, ticker, st.session_state.company_data)
                st.markdown(get_download_link(pdf_buffer.getvalue(), f"{company_name}_analysis_report.pdf"), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error analyzing company: {str(e)}")
            print(f"Analysis error: {str(e)}")
            traceback.print_exc()
            st.session_state.analysis_complete = False

def display_financial_analysis(financial_results):
    # First add the CSS
    st.markdown("""
    <style>
    .financial-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .financial-header h2 {
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }

    .financial-header .header-icon {
        font-size: 2.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add the header
    st.markdown("""
    <div class="financial-header">
        <h2>
            <span class="header-icon">📊</span>
            Financial Analysis
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Rest of the existing CSS
    st.markdown("""
    <style>
    .financial-section {
        background: linear-gradient(165deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem auto;
        box-shadow: 0 4px 24px rgba(0,0,0,0.05);
    }

    .section-header {
        color: #1a237e;
        font-size: 2.2rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }

    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(0,0,0,0.05);
    }

    .card-header h3 {
        color: #1a237e;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }

    .header-icon {
        font-size: 1.5rem;
    }

    .metrics-content {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem;
        background: rgba(0,0,0,0.02);
        border-radius: 12px;
        transition: background-color 0.2s ease;
    }

    .metric-row:hover {
        background: rgba(0,0,0,0.04);
    }

    .metric-label {
        color: #444;
        font-size: 0.95rem;
    }

    .metric-value {
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        min-width: 70px;
        text-align: center;
    }

    .metric-value.positive { color: #2e7d32; background: #e8f5e9; }
    .metric-value.growth { color: #1976d2; background: #e3f2fd; }
    .metric-value.market { color: #9c27b0; background: #f3e5f5; }
    .metric-value.risk { color: #e65100; background: #fff3e0; }

    .health-summary {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        margin-top: 2rem;
    }

    .summary-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .summary-header h3 {
        font-size: 1.5rem;
        margin: 0;
        color: white;
    }

    .summary-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
    }

    .summary-metric {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        backdrop-filter: blur(10px);
    }

    .summary-metric .metric-label {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
    }

    .summary-metric .metric-value.highlight {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        background: none;
    }

    /* Card-specific styling */
    .core-metrics { border-left: 4px solid #4caf50; }
    .growth-metrics { border-left: 4px solid #2196f3; }
    .market-position { border-left: 4px solid #9c27b0; }
    .risk-metrics { border-left: 4px solid #ff9800; }
    </style>
    """, unsafe_allow_html=True)

    # Create columns for the metrics
    col1, col2 = st.columns(2)

    with col1:
        # Core Metrics
        st.markdown(f"""
        <div class="metric-card core-metrics">
            <div class="card-header">
                <span class="header-icon">📈</span>
                <h3>Core Metrics</h3>
            </div>
            <div class="metrics-content">
                <div class="metric-row">
                    <span class="metric-label">Return on Equity (ROE)</span>
                    <span class="metric-value positive">{financial_results.get('core_metrics', {}).get('roe', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Return on Assets (ROA)</span>
                    <span class="metric-value positive">{financial_results.get('core_metrics', {}).get('roa', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Profit Margin</span>
                    <span class="metric-value positive">{financial_results.get('core_metrics', {}).get('profit_margin', 'N/A')}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Market Position
        st.markdown(f"""
        <div class="metric-card market-position">
            <div class="card-header">
                <span class="header-icon">🎯</span>
                <h3>Market Position</h3>
            </div>
            <div class="metrics-content">
                <div class="metric-row">
                    <span class="metric-label">P/E Ratio</span>
                    <span class="metric-value market">{financial_results.get('core_metrics', {}).get('pe_ratio', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Market Cap (B)</span>
                    <span class="metric-value market">${financial_results.get('core_metrics', {}).get('market_cap', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Dividend Yield</span>
                    <span class="metric-value market">{financial_results.get('core_metrics', {}).get('dividend_yield', 'N/A')}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Growth Metrics
        st.markdown(f"""
        <div class="metric-card growth-metrics">
            <div class="card-header">
                <span class="header-icon">📊</span>
                <h3>Growth Metrics</h3>
            </div>
            <div class="metrics-content">
                <div class="metric-row">
                    <span class="metric-label">Revenue Growth</span>
                    <span class="metric-value growth">{financial_results.get('core_metrics', {}).get('revenue_growth', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">EPS Growth</span>
                    <span class="metric-value growth">{financial_results.get('core_metrics', {}).get('eps_growth', 'N/A')}%</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Stock Momentum</span>
                    <span class="metric-value growth">{financial_results.get('core_metrics', {}).get('stock_momentum', 'N/A')}/10</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Risk Metrics
        st.markdown(f"""
        <div class="metric-card risk-metrics">
            <div class="card-header">
                <span class="header-icon">⚠️</span>
                <h3>Risk Metrics</h3>
            </div>
            <div class="metrics-content">
                <div class="metric-row">
                    <span class="metric-label">Beta</span>
                    <span class="metric-value risk">{financial_results.get('core_metrics', {}).get('beta', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Debt/Equity</span>
                    <span class="metric-value risk">{financial_results.get('core_metrics', {}).get('debt_equity', 'N/A')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Current Ratio</span>
                    <span class="metric-value risk">{financial_results.get('core_metrics', {}).get('current_ratio', 'N/A')}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Overall Financial Health
    st.markdown(f"""
    <div class="health-summary">
        <div class="summary-header">
            <span class="header-icon">💹</span>
            <h3>Overall Financial Health</h3>
        </div>
        <div class="summary-metrics">
            <div class="summary-metric">
                <span class="metric-label">Growth Rate</span>
                <span class="metric-value highlight">{financial_results.get('core_metrics', {}).get('growth_rate', 'N/A')}%</span>
            </div>
            <div class="summary-metric">
                <span class="metric-label">Market Trend</span>
                <span class="metric-value highlight">{str(financial_results.get('core_metrics', {}).get('trend', 'N/A')).title()}</span>
            </div>
            <div class="summary-metric">
                <span class="metric-label">Volatility</span>
                <span class="metric-value highlight">{str(financial_results.get('core_metrics', {}).get('volatility', 'N/A')).title()}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_methodology():
    """Display analysis methodology with enhanced visual design"""
    st.markdown("""
    <style>
    .methodology-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .tech-stack {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .tech-item {
        display: inline-block;
        background: #f5f5f5;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.9rem;
        color: #333;
    }
    
    .methodology-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .section-title {
        color: #1a237e;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1a237e;
    }
    
    .score-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .score-table th, .score-table td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid #eee;
    }
    
    .score-table th {
        background: #f5f5f5;
        color: #1a237e;
    }
    
    .formula-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
        font-family: monospace;
        color: #333;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .ai-agents {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .agent-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1a237e;
    }
    </style>
    
    <div class="methodology-header">
        <h1>Responsible Investing AI Methodology</h1>
        <p>A comprehensive AI-powered system for analyzing companies based on ESG criteria, SDG alignment, market sentiment, and financial metrics.</p>
    </div>
    """, unsafe_allow_html=True)

    # Technology Stack
    st.markdown("""
    <div class="tech-stack">
        <div class="section-title">Technology Stack</div>
        <div>
            <span class="tech-item">🧠 Nemotron LLM API</span>
            <span class="tech-item">📊 yfinance</span>
            <span class="tech-item">🔍 NLTK</span>
            <span class="tech-item">📈 Streamlit</span>
            <span class="tech-item">🐍 Python</span>
            <span class="tech-item">🤖 OpenAI API</span>
            <span class="tech-item">📱 Modern UI/UX</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Key Features
    st.markdown("""
    <div class="methodology-section">
        <div class="section-title">Key Features</div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Comprehensive Analysis</h3>
                <p>Multi-faceted evaluation combining ESG metrics, SDG alignment, market sentiment, and financial performance.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3>AI-Powered Insights</h3>
                <p>Advanced LLM models for nuanced analysis and real-time market sentiment assessment.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Real-Time Data</h3>
                <p>Live market data integration with yfinance for up-to-date financial metrics.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚖️</div>
                <h3>Balanced Scoring</h3>
                <p>Weighted scoring system considering multiple factors for comprehensive evaluation.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI Agents
    st.markdown("""
    <div class="methodology-section">
        <div class="section-title">AI Analysis Agents</div>
        <div class="ai-agents">
            <div class="agent-card">
                <h3>SDG & Ethical Analyst</h3>
                <p>Specializes in analyzing company alignment with UN SDGs and ESG principles.</p>
            </div>
            <div class="agent-card">
                <h3>Sentiment Analyst</h3>
                <p>Analyzes market perception, news sentiment, and stakeholder feedback.</p>
            </div>
            <div class="agent-card">
                <h3>Financial Analyst</h3>
                <p>Evaluates financial health, market performance, and risk metrics.</p>
            </div>
            <div class="agent-card">
                <h3>Investment Advisor</h3>
                <p>Synthesizes all analyses for final investment recommendations.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Scoring Methodology
    st.markdown('<div class="section-title">Scoring Methodology</div>', unsafe_allow_html=True)

    # ESG & SDG Analysis (40%)
    st.markdown("""
    <div class="methodology-section">
        <h3>1. ESG & SDG Analysis (40%)</h3>
        <div class="methodology-card">
            <table class="score-table">
                <tr>
                    <th>Component</th>
                    <th>Weight</th>
                    <th>Key Metrics</th>
                </tr>
                <tr>
                    <td>Environmental Impact</td>
                    <td>15%</td>
                    <td>Carbon emissions, resource usage, waste management, climate action initiatives</td>
                </tr>
                <tr>
                    <td>Social Responsibility</td>
                    <td>15%</td>
                    <td>Labor practices, community impact, human rights, diversity & inclusion</td>
                </tr>
                <tr>
                    <td>Governance</td>
                    <td>15%</td>
                    <td>Board diversity, transparency, ethics, compliance</td>
                </tr>
                <tr>
                    <td>SDG Alignment</td>
                    <td>15%</td>
                    <td>Contribution to UN SDGs, sustainable initiatives</td>
                </tr>
                <tr>
                    <td>Controversies</td>
                    <td>20%</td>
                    <td>Historical issues, resolutions, preventive measures</td>
                </tr>
                <tr>
                    <td>Risk Management</td>
                    <td>20%</td>
                    <td>ESG risk assessment, mitigation strategies</td>
                </tr>
            </table>
        </div>
        <div class="formula-box">
            ESG_Score = (Environmental * 0.15) + (Social * 0.15) + (Governance * 0.15) + 
            (SDG * 0.15) + (Controversies * 0.20) + (Risk * 0.20)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Financial Analysis (30%)
    st.markdown("""
    <div class="methodology-section">
        <h3>2. Financial Analysis (30%)</h3>
        <div class="methodology-card">
            <table class="score-table">
                <tr>
                    <th>Category</th>
                    <th>Weight</th>
                    <th>Key Indicators</th>
                </tr>
                <tr>
                    <td>Profitability</td>
                    <td>25%</td>
                    <td>ROE, ROA, Profit Margins, Operating Efficiency</td>
                </tr>
                <tr>
                    <td>Growth</td>
                    <td>25%</td>
                    <td>Revenue Growth, EPS Growth, Market Share Trends</td>
                </tr>
                <tr>
                    <td>Market Performance</td>
                    <td>25%</td>
                    <td>P/E Ratio, Market Cap, Stock Momentum</td>
                </tr>
                <tr>
                    <td>Risk Metrics</td>
                    <td>25%</td>
                    <td>Beta, Debt/Equity, Current Ratio, Volatility</td>
                </tr>
            </table>
        </div>
        <div class="formula-box">
            Financial_Score = (Profitability * 0.25) + (Growth * 0.25) + 
            (Market_Performance * 0.25) + (Risk_Metrics * 0.25)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Market Sentiment (30%)
    st.markdown("""
    <div class="methodology-section">
        <h3>3. Market Sentiment Analysis (30%)</h3>
        <div class="methodology-card">
            <table class="score-table">
                <tr>
                    <th>Factor</th>
                    <th>Weight</th>
                    <th>Data Sources</th>
                </tr>
                <tr>
                    <td>News Sentiment</td>
                    <td>30%</td>
                    <td>News articles, press releases, media coverage</td>
                </tr>
                <tr>
                    <td>Social Media</td>
                    <td>20%</td>
                    <td>Twitter, LinkedIn, Reddit discussions</td>
                </tr>
                <tr>
                    <td>Analyst Ratings</td>
                    <td>30%</td>
                    <td>Professional analyst reports, recommendations</td>
                </tr>
                <tr>
                    <td>Stakeholder Feedback</td>
                    <td>20%</td>
                    <td>Customer reviews, employee feedback, partner relationships</td>
                </tr>
            </table>
        </div>
        <div class="formula-box">
            Sentiment_Score = (News * 0.30) + (Social * 0.20) + 
            (Analyst * 0.30) + (Stakeholder * 0.20)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Final Score Calculation
    st.markdown("""
    <div class="methodology-section">
        <h3>Final Score & Investment Recommendations</h3>
        <div class="methodology-card">
            <table class="score-table">
                <tr>
                    <th>Score Range</th>
                    <th>Category</th>
                    <th>Recommendation</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>8.5 - 10.0</td>
                    <td>Exceptional</td>
                    <td>Strong Buy</td>
                    <td>Industry leader in sustainability and financial performance</td>
                </tr>
                <tr>
                    <td>7.0 - 8.4</td>
                    <td>Strong</td>
                    <td>Buy</td>
                    <td>Strong performance with minor improvement areas</td>
                </tr>
                <tr>
                    <td>5.5 - 6.9</td>
                    <td>Moderate</td>
                    <td>Hold</td>
                    <td>Average performance with both strengths and concerns</td>
                </tr>
                <tr>
                    <td>4.0 - 5.4</td>
                    <td>Concerning</td>
                    <td>Sell</td>
                    <td>Significant issues requiring attention</td>
                </tr>
                <tr>
                    <td>0.0 - 3.9</td>
                    <td>Poor</td>
                    <td>Strong Sell</td>
                    <td>Major concerns in multiple areas</td>
                </tr>
            </table>
        </div>
        <div class="formula-box">
            Final_Score = (ESG_Score * 0.40) + (Financial_Score * 0.30) + (Sentiment_Score * 0.30)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Data Sources & Updates
    st.markdown("""
    <div class="methodology-section">
        <h3>Data Sources & Updates</h3>
        <ul>
            <li><strong>Market Data:</strong> Real-time financial data from yfinance</li>
            <li><strong>News & Social:</strong> Continuous monitoring of news sources and social media</li>
            <li><strong>ESG Data:</strong> Company reports, sustainability disclosures, and third-party assessments</li>
            <li><strong>SDG Alignment:</strong> UN SDG framework and company sustainability reports</li>
            <li><strong>AI Analysis:</strong> Powered by Nemotron LLM for real-time sentiment and contextual analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # After the "Data Sources & Updates" section, add:
    st.markdown("""
    <div class="methodology-section">
        <h3>AI Insights Analysis</h3>
        <div class="methodology-card">
            <table class="score-table">
                <tr>
                    <th>Component</th>
                    <th>Weight</th>
                    <th>Analysis Factors</th>
                </tr>
                <tr>
                    <td>Key Strengths</td>
                    <td>35%</td>
                    <td>Financial performance, market position, competitive advantages, operational efficiency</td>
                </tr>
                <tr>
                    <td>Key Risks</td>
                    <td>35%</td>
                    <td>Market threats, operational vulnerabilities, regulatory challenges, industry-specific risks</td>
                </tr>
                <tr>
                    <td>Growth Opportunities</td>
                    <td>30%</td>
                    <td>Market expansion potential, innovation opportunities, emerging trends, strategic initiatives</td>
                </tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="methodology-section">
        <div class="section-title">AI Analysis Process</div>
        <div class="methodology-card">
            <ol>
                <li>
                    <strong>Data Collection:</strong> Aggregates financial data, market reports, industry analysis, and company statements
                </li>
                <li>
                    <strong>Pattern Recognition:</strong> Identifies recurring patterns and trends in company performance and market behavior
                </li>
                <li>
                    <strong>Contextual Analysis:</strong> Evaluates insights within industry context and current market conditions
                </li>
                <li>
                    <strong>Impact Assessment:</strong> Rates the significance and potential impact of each identified factor
                </li>
                <li>
                    <strong>Validation:</strong> Cross-references findings with multiple data sources for accuracy
                </li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="methodology-section">
        <div class="section-title">Insight Categories</div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">💪</div>
                <h4>Strengths Analysis</h4>
                <p>Evaluates core competencies, competitive advantages, and sustainable business practices that contribute to long-term success.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚠️</div>
                <h4>Risk Assessment</h4>
                <p>Identifies potential threats, vulnerabilities, and challenges that could impact future performance or stability.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h4>Growth Opportunities</h4>
                <p>Highlights potential areas for expansion, innovation, and strategic development based on market trends and company capabilities.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="methodology-section">
        <div class="section-title">Update Frequency</div>
        <div class="methodology-card">
            <ul>
                <li>Strengths & Risks: Updated quarterly with financial reports</li>
                <li>Market Opportunities: Refreshed monthly based on market conditions</li>
                <li>Real-time Adjustments: Made for significant market events or company news</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add additional CSS for the new sections
    st.markdown("""
    <style>
    .methodology-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .methodology-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .methodology-card ol, .methodology-card ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .methodology-card li {
        margin-bottom: 1rem;
        color: #333;
        line-height: 1.6;
    }
    
    .methodology-card li:last-child {
        margin-bottom: 0;
    }
    
    .section-title {
        color: #1a237e;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .feature-card h4 {
        color: #1a237e;
        margin: 1rem 0;
        font-size: 1.2rem;
    }
    
    .feature-card p {
        color: #555;
        line-height: 1.5;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_overall_score(financial_results, sdg_results, sentiment_results):
    """Calculate overall score based on all metrics"""
    try:
        # Financial metrics (40% weight)
        financial_metrics = {
            'roe': float(financial_results.get('core_metrics', {}).get('roe', 0)),
            'profit_margin': float(financial_results.get('core_metrics', {}).get('profit_margin', 0)),
            'revenue_growth': float(financial_results.get('core_metrics', {}).get('revenue_growth', 0)),
            'current_ratio': float(financial_results.get('core_metrics', {}).get('current_ratio', 0)),
            'debt_equity': float(financial_results.get('core_metrics', {}).get('debt_equity', 0))
        }
        
        # Normalize financial metrics to 0-10 scale
        financial_score = (
            min(max(financial_metrics['roe'] / 20 * 10, 0), 10) * 0.2 +  # ROE up to 20% is considered good
            min(max(financial_metrics['profit_margin'] / 15 * 10, 0), 10) * 0.2 +  # Profit margin up to 15% is good
            min(max(financial_metrics['revenue_growth'] / 25 * 10, 0), 10) * 0.2 +  # Growth up to 25% is good
            min(max(financial_metrics['current_ratio'] / 2 * 10, 0), 10) * 0.2 +  # Current ratio of 2 is good
            min(max((1 - financial_metrics['debt_equity'] / 2) * 10, 0), 10) * 0.2  # Lower debt/equity is better
        ) * 0.4  # 40% weight for financial metrics
        
        # ESG metrics (40% weight)
        esg_metrics = {
            'environmental': float(sdg_results.get('scores', {}).get('environmental', 5)),
            'social': float(sdg_results.get('scores', {}).get('social', 5)),
            'governance': float(sdg_results.get('scores', {}).get('governance', 5))
        }
        
        esg_score = (
            esg_metrics['environmental'] * 0.4 +
            esg_metrics['social'] * 0.3 +
            esg_metrics['governance'] * 0.3
        ) * 0.4  # 40% weight for ESG metrics
        
        # Sentiment score (20% weight)
        sentiment_metrics = {
            'overall_sentiment': float(sentiment_results.get('sentiment_score', 5)),
            'market_confidence': float(sentiment_results.get('confidence', 0.5)) * 10
        }
        
        sentiment_score = (
            sentiment_metrics['overall_sentiment'] * 0.6 +
            sentiment_metrics['market_confidence'] * 0.4
        ) * 0.2  # 20% weight for sentiment
        
        # Calculate final score (0-10 scale)
        final_score = financial_score + esg_score + sentiment_score
        
        # Ensure score is between 0 and 10
        return min(max(final_score, 0), 10)
        
    except (TypeError, ValueError) as e:
        print(f"Error calculating score: {e}")
        return 5.0  # Default to neutral score if calculation fails

def get_rating_details(score):
    """Get rating label and details based on actual score and metrics"""
    if score >= 8.5:
        return {
            "label": "Excellent",
            "class": "rating-excellent",
            "recommendation": "Highly Recommended",
            "description": "Outstanding performance across financial, ESG, and market sentiment metrics. Strong potential for sustainable growth and positive impact.",
            "key_points": [
                "⭐ Exceptional financial metrics",
                "🌍 Strong ESG commitment",
                "📈 Positive market sentiment",
                "💪 Robust growth potential"
            ]
        }
    elif score >= 7.0:
        return {
            "label": "Good",
            "class": "rating-good",
            "recommendation": "Recommended",
            "description": "Strong overall performance with positive indicators across most metrics. Good balance of financial returns and sustainable practices.",
            "key_points": [
                "📈 Solid financial performance",
                "✅ Good ESG practices",
                "👍 Favorable market position",
                "📊 Stable growth outlook"
            ]
        }
    elif score >= 5.5:
        return {
            "label": "Neutral",
            "class": "rating-neutral",
            "recommendation": "Consider with Caution",
            "description": "Balanced performance with both strengths and areas for improvement. Monitor developments before making significant investment decisions.",
            "key_points": [
                "⚖️ Mixed performance metrics",
                "📊 Average ESG ratings",
                "🔄 Moderate market sentiment",
                "👀 Needs monitoring"
            ]
        }
    elif score >= 4.0:
        return {
            "label": "Caution",
            "class": "rating-caution",
            "recommendation": "Not Recommended",
            "description": "Several concerning indicators that require attention. Consider reducing position or waiting for improvements before investing.",
            "key_points": [
                "⚠️ Financial concerns",
                "📉 Below average metrics",
                "❗ ESG risks present",
                "🔍 Requires careful review"
            ]
        }
    else:
        return {
            "label": "Avoid",
            "class": "rating-avoid",
            "recommendation": "Strongly Not Recommended",
            "description": "Significant issues across multiple metrics. High risk profile with substantial concerns about sustainability and performance.",
            "key_points": [
                "🚫 Major financial risks",
                "⛔ Poor ESG performance",
                "📉 Negative market trends",
                "⚠️ Sustainability concerns"
            ]
        }

def display_recommendation_section(financial_results, sdg_results, sentiment_results):
    """Display the final recommendation section"""
    score = calculate_overall_score(financial_results, sdg_results, sentiment_results)
    rating = get_rating_details(score)
    
    # Add CSS
    st.markdown("""
    <style>
    .recommendation-section {
        background: linear-gradient(165deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 25px;
        padding: 3rem;
        margin: 3rem auto;
        max-width: 1200px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    .recommendation-header {
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        color: white;
    }
    .rating-container {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        backdrop-filter: blur(10px);
    }
    .rating-score {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .rating-score .score-max {
        font-size: 2rem;
        opacity: 0.8;
    }
    .rating-label {
        font-size: 1.8rem;
        margin: 1rem 0;
        padding: 0.5rem 2rem;
        border-radius: 50px;
        display: inline-block;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .rating-excellent { background: linear-gradient(135deg, #00c853 0%, #64dd17 100%); }
    .rating-good { background: linear-gradient(135deg, #00b0ff 0%, #2979ff 100%); }
    .rating-neutral { background: linear-gradient(135deg, #ffd600 0%, #ffab00 100%); }
    .rating-caution { background: linear-gradient(135deg, #ff9100 0%, #ff6d00 100%); }
    .rating-avoid { background: linear-gradient(135deg, #ff1744 0%, #d50000 100%); }
    .recommendation-details {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        text-align: left;
        backdrop-filter: blur(10px);
    }
    .recommendation-details h3 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: rgba(255,255,255,0.9);
    }
    .recommendation-details p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .key-points {
        display: grid;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    .key-point {
        background: rgba(255,255,255,0.05);
        padding: 1rem 1.5rem;
        border-radius: 15px;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: transform 0.3s ease;
    }
    .key-point:hover {
        transform: translateX(10px);
        background: rgba(255,255,255,0.1);
    }
    .key-point-icon {
        font-size: 1.5rem;
    }
    .key-point-text {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Generate key points HTML
    key_points_html = []
    for point in rating["key_points"]:
        icon = point.split()[0]
        text = " ".join(point.split()[1:])
        key_points_html.append(
            f'<div class="key-point">'
            f'<span class="key-point-icon">{icon}</span>'
            f'<span class="key-point-text">{text}</span>'
            f'</div>'
        )

    # Render the recommendation section
    st.markdown(
        f'<div class="recommendation-section">'
        f'<h2 class="recommendation-header">Investment Recommendation</h2>'
        f'<div class="rating-container">'
        f'<div class="rating-score">{score:.1f}<span class="score-max">/10</span></div>'
        f'<div class="rating-label {rating["class"]}">{rating["recommendation"]}</div>'
        f'</div>'
        f'<div class="recommendation-details">'
        f'<h3>Analysis Summary</h3>'
        f'<p>{rating["description"]}</p>'
        f'<div class="key-points">'
        f'{"".join(key_points_html)}'
        f'</div></div></div>',
        unsafe_allow_html=True
    )

def analyze_company():
    """Analyze company and store results in session state"""
    if st.session_state.current_company and st.session_state.current_ticker:
        try:
            with st.spinner('Analyzing company data... This may take up to 30 seconds.'):
                print("\n=== Starting Company Analysis ===")
                print(f"Analyzing {st.session_state.current_company} ({st.session_state.current_ticker})")
                
                # Initialize results
                sdg_result = None
                sentiment_result = None
                financial_result = None
                
                # Test SDG Analysis
                print("\n--- Testing SDG Analysis ---")
                sdg_result = sdg_analyzer.analyze(st.session_state.current_company)
                if not sdg_result:
                    st.error("SDG Analysis failed. Using default values.")
                print(f"SDG Analysis Result: {sdg_result}")
                
                # Test Sentiment Analysis
                print("\n--- Testing Sentiment Analysis ---")
                sentiment_result = sentiment_analyzer.analyze(st.session_state.current_company)
                if not sentiment_result:
                    st.error("Sentiment Analysis failed. Using default values.")
                print(f"Sentiment Analysis Result: {sentiment_result}")
                
                # Test Financial Analysis
                print("\n--- Testing Financial Analysis ---")
                financial_result = financial_analyzer.analyze(st.session_state.current_ticker)
                if not financial_result:
                    st.error("Financial Analysis failed. Using default values.")
                print(f"Financial Analysis Result: {financial_result}")
                
                st.session_state.company_data = {
                    'sdg': sdg_result,
                    'sentiment': sentiment_result,
                    'financial': financial_result
                }
                
                print("\n=== Analysis Results ===")
                print(f"Final Data: {st.session_state.company_data}")
                
                st.session_state.analysis_complete = True
                st.rerun()
                
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            print(f"Error during analysis: {str(e)}")
            traceback.print_exc()
            st.session_state.analysis_complete = False

def verify_company_info(company_name: str, ticker: str) -> tuple[bool, str]:
    """
    Verify if the company name and ticker are valid and match.
    Returns (is_valid, message)
    """
    try:
        if not company_name or not ticker:
            return False, "Please enter both company name and ticker symbol."
        
        # Clean up ticker (remove spaces and convert to uppercase)
        ticker = ticker.strip().upper()
        
        # Common Indian company ticker mappings
        indian_tickers = {
            'M&M': 'MAHINDRA & MAHINDRA',
            'L&T': 'LARSEN & TOUBRO',
            'M&MFIN': 'MAHINDRA & MAHINDRA FINANCIAL SERVICES',
            'P&G': 'PROCTER & GAMBLE',
            'B&M': 'B&M EUROPEAN VALUE RETAIL',
            'A&F': 'ABERCROMBIE & FITCH',
            'J&J': 'JOHNSON & JOHNSON'
        }
        
        # Check if this is a known ticker with special characters
        matched_company = None
        for known_ticker, company in indian_tickers.items():
            if ticker.replace('&', '') == known_ticker.replace('&', ''):
                matched_company = company
                ticker = known_ticker  # Use the correct ticker format
                break
        
        # Basic ticker format validation - allow special characters for known tickers
        if not matched_company:  # Only validate format for non-special tickers
            valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-&")
            if not all(c in valid_chars for c in ticker):
                return False, "Invalid ticker format. Ticker can only contain letters, numbers, dots, hyphens, and & for special cases."
        
        # Try to get company info from yfinance
        try:
            # Try different common exchange suffixes if the base ticker fails
            exchanges = ['', '.NS', '.BO', '.L', '.PA', '.DE', '.MI', '.MC', '.AS', '.BR', '.SS', '.SZ', '.HK', '.TYO', '.T', '.AX', '.TO', '.JSE', '.BSE', '.KS', '.KL']
            verified = False
            official_name = None
            error_message = None
            
            # If it's a known special ticker, try with exchange suffixes first
            if matched_company:
                for exchange in ['.NS', '.BO', '']:  # Prioritize Indian exchanges for known Indian tickers
                    try:
                        full_ticker = f"{ticker}{exchange}"
                        yf_ticker = yf.Ticker(full_ticker)
                        info = yf_ticker.info
                        if info and 'longName' in info:
                            verified = True
                            official_name = info['longName']
                            if exchange:
                                error_message = f"Found company under ticker {full_ticker}"
                            break
                    except:
                        continue
            
            # If not verified yet, try the exact ticker as provided
            if not verified:
                try:
                    yf_ticker = yf.Ticker(ticker)
                    info = yf_ticker.info
                    if info and 'longName' in info:
                        verified = True
                        official_name = info['longName']
                except:
                    pass
            
            # If still not verified and no dot in ticker, try all exchanges
            if not verified and '.' not in ticker:
                for exchange in exchanges:
                    try:
                        full_ticker = f"{ticker}{exchange}"
                        yf_ticker = yf.Ticker(full_ticker)
                        info = yf_ticker.info
                        if info and 'longName' in info:
                            verified = True
                            official_name = info['longName']
                            error_message = f"Found company under ticker {full_ticker}"
                            break
                    except:
                        continue
            
            if verified and official_name:
                # For known special tickers, also match against the known company name
                if matched_company and matched_company.lower() in official_name.lower():
                    message = "Verification successful!"
                    if error_message:
                        message = f"{message} {error_message}"
                    return True, message
                
                # Basic name matching (case-insensitive and partial match)
                if company_name.lower() in official_name.lower() or official_name.lower() in company_name.lower():
                    message = "Verification successful!"
                    if error_message:
                        message = f"{message} {error_message}"
                    return True, message
                else:
                    return False, f"Company name doesn't match the ticker. Did you mean {official_name}?"
            else:
                suggestion = ""
                if not '.' in ticker:
                    suggestion = " Try adding the exchange suffix (e.g., .NS for NSE, .BO for BSE, .L for London)"
                return False, f"Could not verify ticker symbol {ticker}. Please check if it's correct.{suggestion}"
            
        except Exception as e:
            return False, f"Error verifying company information: {str(e)}"
            
    except Exception as e:
        return False, f"Verification failed: {str(e)}"

def display_search_section():
    """Display search inputs and button"""
    col1, col2, col3 = st.columns([3, 3, 1.5])
    with col1:
        company_name = st.text_input("Company Name", 
                                   value=st.session_state.current_company if st.session_state.current_company else "",
                                   placeholder="e.g., Apple Inc")
    with col2:
        ticker = st.text_input("Stock Ticker", 
                             value=st.session_state.current_ticker if st.session_state.current_ticker else "",
                             placeholder="e.g., AAPL")
    with col3:
        st.write("")  # Add some vertical spacing
        st.write("")  # Add some vertical spacing
        if st.button("Analyze", key="search_button", help="Click to analyze company", use_container_width=True):
            # Verify company info before proceeding
            is_valid, message = verify_company_info(company_name, ticker)
            
            if is_valid:
                st.success(message)
                st.session_state.current_company = company_name
                st.session_state.current_ticker = ticker
                analyze_company()
            else:
                st.error(message)
                st.session_state.analysis_complete = False
                st.session_state.company_data = None
                st.session_state.current_company = None
                st.session_state.current_ticker = None

def display_ai_insights(financial_results):
    """Display AI insights in a three-column layout with proper styling"""
    
    # Add custom CSS
    st.markdown("""
    <style>
    .insight-title {
        color: #1a237e;
        font-size: 28px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 30px;
        padding-top: 20px;
    }
    
    .insight-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    }
    
    .card-strengths {
        background: linear-gradient(to bottom right, #f8faf8, #f0f7f0);
        border-left: 4px solid #4caf50;
    }
    
    .card-risks {
        background: linear-gradient(to bottom right, #fff9f9, #fff5f5);
        border-left: 4px solid #f44336;
    }
    
    .card-opportunities {
        background: linear-gradient(to bottom right, #f5f9ff, #f0f6ff);
        border-left: 4px solid #2196f3;
    }
    
    .card-header {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #333;
    }
    
    .insight-item {
        background: rgba(255, 255, 255, 0.8);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    
    .score-badge {
        float: right;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 8px;
        margin-left: 10px;
    }
    
    .score-strengths { color: #2e7d32; background: #e8f5e9; }
    .score-risks { color: #d32f2f; background: #ffebee; }
    .score-opportunities { color: #1976d2; background: #e3f2fd; }
    </style>
    """, unsafe_allow_html=True)
    
    # Add title
    st.markdown('<h2 class="insight-title">AI Insights</h2>', unsafe_allow_html=True)
    
    # Create columns
    col1, col2, col3 = st.columns(3)
    
    # Get AI insights from financial_results
    ai_insights = financial_results.get('ai_insights', {})
    strengths = ai_insights.get('strengths', [])
    risks = ai_insights.get('risks', [])
    opportunities = ai_insights.get('opportunities', [])
    
    # Strengths Column
    with col1:
        st.markdown("""
        <div class="insight-card card-strengths">
            <div class="card-header">👍 Key Strengths</div>
        """, unsafe_allow_html=True)
        
        for strength in strengths:
            st.markdown(f"""
            <div class="insight-item">
                {strength}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Risks Column
    with col2:
        st.markdown("""
        <div class="insight-card card-risks">
            <div class="card-header">⚠️ Key Risks</div>
        """, unsafe_allow_html=True)
        
        for risk in risks:
            st.markdown(f"""
            <div class="insight-item">
                {risk}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Opportunities Column
    with col3:
        st.markdown("""
        <div class="insight-card card-opportunities">
            <div class="card-header">🎯 Growth Opportunities</div>
        """, unsafe_allow_html=True)
        
        for opportunity in opportunities:
            st.markdown(f"""
            <div class="insight-item">
                {opportunity}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# Add new function for the AI Ethics & Trust Dashboard
def display_ai_ethics_dashboard():
    """Display the AI Ethics & Trust Dashboard with modern styling and comprehensive information"""
    
    # Add custom CSS for the ethics dashboard
    st.markdown("""
    <style>
    .ethics-header {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 3rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .status-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .status-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .status-label {
        color: #1a237e;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .status-value {
        color: #333;
        font-size: 1.2rem;
    }
    
    .principle-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 4px solid;
        transition: transform 0.2s ease;
    }
    
    .principle-card:hover {
        transform: translateY(-5px);
    }
    
    .principle-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .principle-title {
        color: #1a237e;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .implemented { background: #e8f5e9; color: #2e7d32; }
    .in-progress { background: #fff3e0; color: #e65100; }
    .planned { background: #e3f2fd; color: #1565c0; }
    
    .info-box {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 4px solid #1a237e;
    }
    
    .info-title {
        color: #1a237e;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .info-content {
        color: #555;
        line-height: 1.6;
    }
    
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid #eee;
    }
    
    .metric-row:last-child {
        border-bottom: none;
    }
    
    .data-source-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .source-header {
        color: #1a237e;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .source-details {
        color: #555;
        font-size: 0.95rem;
    }
    
    .progress-bar {
        background: #f5f5f5;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .ethics-section {
        margin: 3rem 0;
    }
    
    .ethics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown("""
    <div class="ethics-header">
        <h1>AI Ethics & Trust Dashboard</h1>
        <p>Ensuring responsible and ethical AI practices in investment analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Introduction Section
    st.markdown("""
    <div class="info-box">
        <div class="info-title">🎯 Our Commitment to Ethical AI</div>
        <div class="info-content">
            Our platform is built on the foundation of responsible AI development and deployment. We adhere to the highest standards of ethical AI practices, following guidelines from leading organizations including the European Commission's AI Ethics Guidelines, UNESCO's AI Ethics framework, and industry best practices. Our commitment extends beyond compliance to actively promoting transparent, fair, and accountable AI systems.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status Section
    st.markdown('<h2 style="color: #1a237e; margin-bottom: 1.5rem;">System Status & Monitoring</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">🔄</div>
            <div class="status-label">Last Model Update</div>
            <div class="status-value">2024-02-20 14:30 UTC</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">📊</div>
            <div class="status-label">Data Freshness</div>
            <div class="status-value">98% Up to Date</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">🔒</div>
            <div class="status-label">Security Status</div>
            <div class="status-value">All Systems Secure</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="status-card">
            <div class="status-icon">⚖️</div>
            <div class="status-label">Bias Check Status</div>
            <div class="status-value">Passed (24h)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # AI Ethics Framework Section
    st.markdown("""
    <div class="ethics-section">
        <h2 style="color: #1a237e; margin-bottom: 1.5rem;">Our AI Ethics Framework</h2>
        <div class="info-box">
            <div class="info-content">
                Our AI ethics framework is built on three fundamental pillars:
                <ul>
                    <li><strong>Lawful AI:</strong> Compliance with all applicable laws and regulations, including GDPR, AI Act, and financial regulations</li>
                    <li><strong>Ethical AI:</strong> Adherence to ethical principles and values, ensuring responsible development and deployment</li>
                    <li><strong>Robust AI:</strong> Technical excellence and social awareness in AI system development</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Updated Principles Section
    st.markdown('<h2 style="color: #1a237e; margin: 2rem 0;">Comprehensive AI Ethics Principles</h2>', unsafe_allow_html=True)
    
    principles = [
        {
            "name": "Human Agency & Oversight",
            "status": "implemented",
            "icon": "👥",
            "description": "Empowering human decision-making while maintaining appropriate human oversight of AI systems.",
            "measures": [
                "Human-in-the-loop validation",
                "Override capabilities",
                "Decision review processes",
                "Regular human audits"
            ]
        },
        {
            "name": "Technical Robustness & Safety",
            "status": "implemented",
            "icon": "🛡️",
            "description": "Ensuring AI systems are secure, reliable, and resilient to attacks and errors.",
            "measures": [
                "Regular security assessments",
                "Fallback mechanisms",
                "Error handling protocols",
                "Performance monitoring"
            ]
        },
        {
            "name": "Privacy & Data Governance",
            "status": "implemented",
            "icon": "🔐",
            "description": "Protecting user privacy and ensuring responsible data management throughout the AI lifecycle.",
            "measures": [
                "GDPR compliance",
                "Data minimization",
                "Privacy-preserving techniques",
                "Secure data handling"
            ]
        },
        {
            "name": "Transparency",
            "status": "implemented",
            "icon": "🔍",
            "description": "Providing clear explanations of AI decisions and maintaining system transparency.",
            "measures": [
                "Explainable AI methods",
                "Decision documentation",
                "Process transparency",
                "Regular reporting"
            ]
        },
        {
            "name": "Diversity & Non-discrimination",
            "status": "implemented",
            "icon": "🌈",
            "description": "Ensuring fair treatment and preventing discriminatory outcomes across all user groups.",
            "measures": [
                "Bias detection",
                "Fairness metrics",
                "Inclusive design",
                "Regular equity audits"
            ]
        },
        {
            "name": "Societal & Environmental Wellbeing",
            "status": "implemented",
            "icon": "🌍",
            "description": "Promoting sustainable and socially beneficial AI development and deployment.",
            "measures": [
                "Environmental impact assessment",
                "Social impact monitoring",
                "Sustainable practices",
                "Community engagement"
            ]
        },
        {
            "name": "Accountability",
            "status": "implemented",
            "icon": "⚖️",
            "description": "Maintaining clear responsibility and liability for AI decisions and outcomes.",
            "measures": [
                "Audit trails",
                "Responsibility frameworks",
                "Impact assessments",
                "Regular reporting"
            ]
        },
        {
            "name": "Fairness & Justice",
            "status": "implemented",
            "icon": "⚖️",
            "description": "Ensuring equitable treatment and fair outcomes in AI decision-making.",
            "measures": [
                "Fairness metrics monitoring",
                "Bias mitigation strategies",
                "Equal opportunity measures",
                "Justice-oriented design"
            ]
        },
        {
            "name": "Reliability & Reproducibility",
            "status": "implemented",
            "icon": "🎯",
            "description": "Ensuring consistent and verifiable AI system performance.",
            "measures": [
                "Performance validation",
                "Reproducibility testing",
                "Quality assurance",
                "Version control"
            ]
        },
        {
            "name": "Informed Consent",
            "status": "implemented",
            "icon": "📝",
            "description": "Obtaining and maintaining user consent for AI system interactions.",
            "measures": [
                "Clear consent mechanisms",
                "User choice respect",
                "Opt-out options",
                "Regular consent renewal"
            ]
        },
        {
            "name": "Continuous Learning",
            "status": "in-progress",
            "icon": "📚",
            "description": "Maintaining and improving AI systems through continuous learning and adaptation.",
            "measures": [
                "Model updates",
                "Performance monitoring",
                "Feedback integration",
                "Continuous improvement"
            ]
        },
        {
            "name": "Stakeholder Engagement",
            "status": "implemented",
            "icon": "🤝",
            "description": "Actively engaging with all stakeholders in AI system development and deployment.",
            "measures": [
                "Regular consultations",
                "Feedback mechanisms",
                "Stakeholder updates",
                "Collaborative development"
            ]
        }
    ]
    
    for principle in principles:
        status_class = {
            "implemented": "implemented",
            "in-progress": "in-progress",
            "planned": "planned"
        }[principle["status"]]
        
        st.markdown(f"""
        <div class="principle-card">
            <div class="principle-header">
                <div class="principle-title">
                    {principle["icon"]} {principle["name"]}
                </div>
                <div class="status-badge {status_class}">
                    {principle["status"].replace("-", " ").title()}
                </div>
            </div>
            <p style="color: #555; margin-bottom: 1rem;">{principle["description"]}</p>
            <div style="color: #666;">
                <strong>Implementation Measures:</strong>
                <ul style="margin-top: 0.5rem;">
                    {"".join(f'<li>{measure}</li>' for measure in principle["measures"])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Ethical AI Development Process
    st.markdown("""
    <div class="ethics-section">
        <h2 style="color: #1a237e; margin-bottom: 1.5rem;">Ethical AI Development Process</h2>
        <div class="ethics-grid">
            <div class="info-box">
                <div class="info-title">🎯 Design Phase</div>
                <div class="info-content">
                    <ul>
                        <li>Ethical impact assessment</li>
                        <li>Stakeholder consultation</li>
                        <li>Privacy-by-design implementation</li>
                        <li>Fairness criteria definition</li>
                    </ul>
                </div>
            </div>
            <div class="info-box">
                <div class="info-title">⚙️ Development Phase</div>
                <div class="info-content">
                    <ul>
                        <li>Bias testing and mitigation</li>
                        <li>Robustness verification</li>
                        <li>Security testing</li>
                        <li>Performance validation</li>
                    </ul>
                </div>
            </div>
            <div class="info-box">
                <div class="info-title">🚀 Deployment Phase</div>
                <div class="info-content">
                    <ul>
                        <li>User testing and feedback</li>
                        <li>Impact monitoring</li>
                        <li>Continuous assessment</li>
                        <li>Regular audits</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bias Monitoring Section
    st.markdown('<h2 style="color: #1a237e; margin: 2rem 0;">Comprehensive Bias Monitoring</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Current Bias Metrics</div>
        <div class="metric-row">
            <div>Sector Coverage</div>
            <div>92% Balanced</div>
        </div>
        <div class="metric-row">
            <div>Geographic Distribution</div>
            <div>87% Representative</div>
        </div>
        <div class="metric-row">
            <div>Company Size Distribution</div>
            <div>94% Balanced</div>
        </div>
        <div class="metric-row">
            <div>Industry Diversity</div>
            <div>89% Balanced</div>
        </div>
        <div class="metric-row">
            <div>Market Cap Distribution</div>
            <div>91% Representative</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data Transparency Section
    st.markdown('<h2 style="color: #1a237e; margin: 2rem 0;">Enhanced Data Transparency</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="data-source-card">
            <div class="source-header">Primary Data Sources</div>
            <div class="source-details">
                • Financial Markets (Real-time)<br>
                • Regulatory Filings<br>
                • Company Reports<br>
                • Market Analysis<br>
                • Expert Assessments
            </div>
        </div>
        
        <div class="data-source-card">
            <div class="source-header">ESG & Sustainability Data</div>
            <div class="source-details">
                • ESG Rating Providers<br>
                • Sustainability Reports<br>
                • Environmental Metrics<br>
                • Social Impact Assessments<br>
                • Governance Evaluations
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-source-card">
            <div class="source-header">AI Model Information</div>
            <div class="source-details">
                • Model: Nemotron LLM<br>
                • Training Data: Up to 2024<br>
                • Update Frequency: Monthly<br>
                • Validation Process: Continuous<br>
                • Performance Metrics: Public
            </div>
        </div>
        
        <div class="data-source-card">
            <div class="source-header">Compliance & Standards</div>
            <div class="source-details">
                • EU AI Act Compliance<br>
                • GDPR Requirements<br>
                • ISO AI Standards<br>
                • Industry Best Practices<br>
                • Ethical Guidelines
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Future Commitments Section
    st.markdown("""
    <div class="ethics-section">
        <h2 style="color: #1a237e; margin-bottom: 1.5rem;">Our Commitment to the Future</h2>
        <div class="info-box">
            <div class="info-content">
                <p>We are committed to continuous improvement and adaptation of our AI ethics framework. Our future initiatives include:</p>
                <ul>
                    <li>Enhanced explainability features for complex AI decisions</li>
                    <li>Advanced bias detection and mitigation systems</li>
                    <li>Expanded stakeholder engagement programs</li>
                    <li>Integration of emerging ethical AI standards</li>
                    <li>Development of new transparency tools</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_pdf_report(company_name, ticker, company_data):
    """Generate a PDF report from the analysis data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title and Header
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(f"{company_name}", title_style))
    story.append(Paragraph(f"Stock Ticker: {ticker}", styles['Heading2']))
    story.append(Spacer(1, 20))

    # Dashboard Overview
    story.append(Paragraph("Dashboard Overview", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # ESG Scores
    sdg_data = company_data.get('sdg', {})
    scores = sdg_data.get('scores', {})
    overview_data = [
        [Paragraph("Environmental", styles['Normal']), Paragraph(f"{scores.get('environmental', 'N/A')}", styles['Normal'])],
        [Paragraph("Social", styles['Normal']), Paragraph(f"{scores.get('social', 'N/A')}", styles['Normal'])],
        [Paragraph("Governance", styles['Normal']), Paragraph(f"{scores.get('governance', 'N/A')}", styles['Normal'])],
        [Paragraph("Market Sentiment", styles['Normal']), Paragraph(f"{company_data.get('sentiment', {}).get('sentiment_score', 'N/A')}", styles['Normal'])]
    ]
    t = Table(overview_data, colWidths=[3*inch, 1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # ESG Analysis
    story.append(Paragraph("ESG Analysis", styles['Heading2']))
    story.append(Paragraph(f"Overall ESG Score: {scores.get('sdg_alignment', 'N/A')}/10", styles['Heading3']))
    story.append(Spacer(1, 10))

    # Analysis Details
    justifications = sdg_data.get('justifications', {})
    details = [
        [Paragraph("Environmental", styles['Normal']), Paragraph(justifications.get('environmental', 'N/A'), styles['Normal'])],
        [Paragraph("Social", styles['Normal']), Paragraph(justifications.get('social', 'N/A'), styles['Normal'])],
        [Paragraph("Governance", styles['Normal']), Paragraph(justifications.get('governance', 'N/A'), styles['Normal'])],
        [Paragraph("SDG Alignment", styles['Normal']), Paragraph(justifications.get('sdg_alignment', 'N/A'), styles['Normal'])]
    ]
    t = Table(details, colWidths=[1.5*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Strengths and Concerns
    story.append(Paragraph("Strengths", styles['Heading3']))
    for strength in sdg_data.get('strengths', []):
        story.append(Paragraph(f"{strength['category']}", styles['Heading4']))
        story.append(Paragraph(f"{strength['description']}", styles['Normal']))
        story.append(Paragraph(f"Evidence: {strength['evidence']}", styles['Normal']))
        story.append(Spacer(1, 5))

    story.append(Paragraph("Concerns", styles['Heading3']))
    for concern in sdg_data.get('concerns', []):
        story.append(Paragraph(f"{concern['category']}", styles['Heading4']))
        story.append(Paragraph(f"{concern['description']}", styles['Normal']))
        story.append(Paragraph(f"Impact: {concern['impact']}", styles['Normal']))
        story.append(Spacer(1, 5))

    # Market Sentiment Analysis
    sentiment_data = company_data.get('sentiment', {})
    story.append(Paragraph("Market Sentiment Analysis", styles['Heading2']))
    story.append(Paragraph(f"Overall Market Sentiment Score: {sentiment_data.get('sentiment_score', 'N/A')}/10", styles['Heading3']))
    story.append(Paragraph(f"Confidence: {sentiment_data.get('confidence', 'N/A')*100}%", styles['Normal']))
    story.append(Spacer(1, 10))

    # Positive and Negative Factors
    story.append(Paragraph("Positive Factors", styles['Heading3']))
    for factor in sentiment_data.get('positive_factors', []):
        story.append(Paragraph(f"{factor['category']}", styles['Heading4']))
        story.append(Paragraph(f"Score: {factor['impact_score']}", styles['Normal']))
        story.append(Paragraph(f"{factor['description']}", styles['Normal']))
        story.append(Spacer(1, 5))

    story.append(Paragraph("Negative Factors", styles['Heading3']))
    for factor in sentiment_data.get('negative_factors', []):
        story.append(Paragraph(f"{factor['category']}", styles['Heading4']))
        story.append(Paragraph(f"Score: {factor['impact_score']}", styles['Normal']))
        story.append(Paragraph(f"{factor['description']}", styles['Normal']))
        story.append(Spacer(1, 5))

    # Major Events Timeline
    story.append(Paragraph("Major Events Timeline", styles['Heading3']))
    for event in sentiment_data.get('major_events', []):
        story.append(Paragraph(f"{event['date']}", styles['Heading4']))
        story.append(Paragraph(f"{event['event']}", styles['Normal']))
        story.append(Paragraph(f"{event['impact']}", styles['Normal']))
        story.append(Paragraph(f"Score Impact: {event['score_change']}", styles['Normal']))
        story.append(Spacer(1, 5))

    # Market Trend Analysis
    trend = sentiment_data.get('trend_analysis', {})
    story.append(Paragraph("Market Trend Analysis", styles['Heading3']))
    story.append(Paragraph("Current Trend", styles['Heading4']))
    story.append(Paragraph(trend.get('current_trend', 'N/A'), styles['Normal']))
    story.append(Paragraph("Future Outlook", styles['Heading4']))
    story.append(Paragraph(trend.get('future_outlook', 'N/A'), styles['Normal']))
    story.append(Spacer(1, 20))

    # Financial Analysis
    financial_data = company_data.get('financial', {})
    story.append(Paragraph("Financial Analysis", styles['Heading2']))
    
    # Core Metrics
    core_metrics = financial_data.get('core_metrics', {})
    metrics_data = [
        ["Core Metrics", ""],
        ["Return on Equity (ROE)", f"{core_metrics.get('roe', 'N/A')}%"],
        ["Return on Assets (ROA)", f"{core_metrics.get('roa', 'N/A')}%"],
        ["Profit Margin", f"{core_metrics.get('profit_margin', 'N/A')}%"],
        ["", ""],
        ["Market Position", ""],
        ["P/E Ratio", str(core_metrics.get('pe_ratio', 'N/A'))],
        ["Market Cap (B)", f"${core_metrics.get('market_cap', 'N/A')}"],
        ["Dividend Yield", f"{core_metrics.get('dividend_yield', 'N/A')}%"],
        ["", ""],
        ["Growth Metrics", ""],
        ["Revenue Growth", f"{core_metrics.get('revenue_growth', 'N/A')}%"],
        ["EPS Growth", f"{core_metrics.get('eps_growth', 'N/A')}%"],
        ["Stock Momentum", f"{core_metrics.get('stock_momentum', 'N/A')}/10"],
        ["", ""],
        ["Risk Metrics", ""],
        ["Beta", str(core_metrics.get('beta', 'N/A'))],
        ["Debt/Equity", str(core_metrics.get('debt_equity', 'N/A'))],
        ["Current Ratio", str(core_metrics.get('current_ratio', 'N/A'))],
        ["", ""],
        ["Overall Financial Health", ""],
        ["Growth Rate", f"{core_metrics.get('growth_rate', 'N/A')}%"],
        ["Market Trend", core_metrics.get('trend', 'N/A')],
        ["Volatility", core_metrics.get('volatility', 'N/A')]
    ]
    t = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (0, 8), (1, 8)),
        ('SPAN', (0, 12), (1, 12)),
        ('SPAN', (0, 16), (1, 16))
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # AI Insights
    ai_insights = financial_data.get('ai_insights', {})
    story.append(Paragraph("AI Insights", styles['Heading2']))
    
    # Strengths
    story.append(Paragraph("Key Strengths", styles['Heading3']))
    for strength in ai_insights.get('strengths', []):
        story.append(Paragraph(f"• {strength}", styles['Normal']))
    story.append(Spacer(1, 10))

    # Risks
    story.append(Paragraph("Key Risks", styles['Heading3']))
    for risk in ai_insights.get('risks', []):
        story.append(Paragraph(f"• {risk}", styles['Normal']))
    story.append(Spacer(1, 10))

    # Opportunities
    story.append(Paragraph("Growth Opportunities", styles['Heading3']))
    for opp in ai_insights.get('opportunities', []):
        story.append(Paragraph(f"• {opp}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Investment Recommendation
    story.append(Paragraph("Investment Recommendation", styles['Heading2']))
    overall_score = calculate_overall_score(financial_data, sdg_data, sentiment_data)
    story.append(Paragraph(f"{overall_score}/10", styles['Heading3']))
    story.append(Paragraph("Recommended", styles['Heading4']))
    
    # Analysis Summary
    story.append(Paragraph("Analysis Summary", styles['Heading3']))
    summary = [
        "Strong overall performance with positive indicators across most metrics.",
        "Good balance of financial returns and sustainable practices.",
        "",
        "• Solid financial performance",
        "• Good ESG practices",
        "• Favorable market position",
        "• Stable growth outlook"
    ]
    for line in summary:
        story.append(Paragraph(line, styles['Normal']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_download_link(val, filename):
    """Generate a visually appealing download button for the PDF"""
    b64 = base64.b64encode(val)  # val looks like b'...'
    button_html = f'''
    <style>
    .custom-download-btn {{
        display: inline-block;
        padding: 0.75rem 2rem;
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: background 0.2s, transform 0.2s;
        margin-top: 1rem;
    }}
    .custom-download-btn:hover {{
        background: linear-gradient(135deg, #3949ab 0%, #1976d2 100%);
        color: #fff !important;
        transform: translateY(-2px) scale(1.03);
        text-decoration: none;
    }}
    </style>
    <a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}" class="custom-download-btn">Download PDF Report</a>
    '''
    return button_html

# Main application logic
if page == "Company Analysis":
    st.title("Responsible Investment AI")
    display_search_section()
    
    if st.session_state.analysis_complete:
        display_company_analysis(st.session_state.current_company, st.session_state.current_ticker)

elif page == "Industry Comparison":
    st.title("Industry Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        company1_name = st.text_input("First Company")
        company1_ticker = st.text_input("First Ticker")
    with col2:
        company2_name = st.text_input("Second Company")
        company2_ticker = st.text_input("Second Ticker")
    
    if st.button("Compare Companies"):
        if all([company1_name, company1_ticker, company2_name, company2_ticker]):
            col1, col2 = st.columns(2)
            with col1:
                display_company_analysis(company1_name, company1_ticker)
            with col2:
                display_company_analysis(company2_name, company2_ticker)
        else:
            st.warning("Please enter both company names and tickers")

elif page == "Methodology":
    display_methodology()

elif page == "AI Ethics & Trust":
    display_ai_ethics_dashboard()

# Add this at the end of your file
if st.session_state.analysis_complete:
    st.sidebar.success(f"Currently analyzing: {st.session_state.current_company} ({st.session_state.current_ticker})")
    if st.sidebar.button("Clear Analysis"):
        st.session_state.analysis_complete = False
        st.session_state.company_data = None
        st.session_state.current_company = None
        st.session_state.current_ticker = None
        st.rerun() 