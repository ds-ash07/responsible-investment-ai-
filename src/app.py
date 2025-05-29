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
    "Methodology"
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

def display_investment_recommendation(sdg_results, sentiment_results):
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

    # First, add the custom CSS
    st.markdown("""
    <style>
    .recommendation-box {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        color: white;
    }
    .recommendation-title {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    .score-box {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .score-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .score-text {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .score-value {
        font-size: 1.5rem;
        color: #90caf9;
    }
    .analysis-box {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        color: #333;
    }
    .analysis-header {
        color: #1a237e;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .analysis-content {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1a237e;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Then, create the recommendation box
    recommendation_html = f"""
    <div class="recommendation-box">
        <div class="recommendation-title">Investment Recommendation</div>
        <div class="score-box">
            <div class="score-icon">{icon}</div>
            <div class="score-text" style="color: {color}">{recommendation}</div>
            <div class="score-value">Overall Score: {final_score:.1f}/10</div>
        </div>
        <div class="analysis-box">
            <div class="analysis-header">
                <span>🤖</span>
                AI Investment Analysis
            </div>
            <div class="analysis-content">
                {get_ai_recommendation(st.session_state.current_company, sdg_score, sentiment_score, esg_score)}
            </div>
        </div>
    </div>
    """
    
    # Finally, render the HTML
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
        
        <div style='
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            margin-top: 2rem;
        '>
            <!-- Profitability Metrics -->
            <div style='
                background: white;
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                border-left: 4px solid #4caf50;
            '>
                <h3 style='
                    color: #1a237e;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    <span>📈</span> Profitability Metrics
                </h3>
                <div style='display: grid; gap: 1rem;'>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Return on Equity (ROE)</span>
                        <span style='
                            font-weight: bold;
                            color: #4caf50;
                        '>{financial_results.get('roe', 'N/A')}%</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Return on Assets (ROA)</span>
                        <span style='
                            font-weight: bold;
                            color: #4caf50;
                        '>{financial_results.get('roa', 'N/A')}%</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Profit Margin</span>
                        <span style='
                            font-weight: bold;
                            color: #4caf50;
                        '>{financial_results.get('profit_margin', 'N/A')}%</span>
                    </div>
                </div>
            </div>

            <!-- Growth Metrics -->
            <div style='
                background: white;
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                border-left: 4px solid #2196f3;
            '>
                <h3 style='
                    color: #1a237e;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    <span>🚀</span> Growth Metrics
                </h3>
                <div style='display: grid; gap: 1rem;'>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Revenue Growth</span>
                        <span style='
                            font-weight: bold;
                            color: #2196f3;
                        '>{financial_results.get('revenue_growth', 'N/A')}%</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>EPS Growth</span>
                        <span style='
                            font-weight: bold;
                            color: #2196f3;
                        '>{financial_results.get('eps_growth', 'N/A')}%</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Stock Momentum</span>
                        <span style='
                            font-weight: bold;
                            color: #2196f3;
                        '>{financial_results.get('stock_momentum', 'N/A')}/10</span>
                    </div>
                </div>
            </div>

            <!-- Market Position -->
            <div style='
                background: white;
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                border-left: 4px solid #9c27b0;
            '>
                <h3 style='
                    color: #1a237e;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    <span>🎯</span> Market Position
                </h3>
                <div style='display: grid; gap: 1rem;'>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>P/E Ratio</span>
                        <span style='
                            font-weight: bold;
                            color: #9c27b0;
                        '>{financial_results.get('pe_ratio', 'N/A')}</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Market Cap (B)</span>
                        <span style='
                            font-weight: bold;
                            color: #9c27b0;
                        '>${financial_results.get('market_cap', 'N/A')}</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Dividend Yield</span>
                        <span style='
                            font-weight: bold;
                            color: #9c27b0;
                        '>{financial_results.get('dividend_yield', 'N/A')}%</span>
                    </div>
                </div>
            </div>

            <!-- Risk Metrics -->
            <div style='
                background: white;
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                border-left: 4px solid #ff9800;
            '>
                <h3 style='
                    color: #1a237e;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                '>
                    <span>⚠️</span> Risk Metrics
                </h3>
                <div style='display: grid; gap: 1rem;'>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Beta</span>
                        <span style='
                            font-weight: bold;
                            color: #ff9800;
                        '>{financial_results.get('beta', 'N/A')}</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Debt/Equity</span>
                        <span style='
                            font-weight: bold;
                            color: #ff9800;
                        '>{financial_results.get('debt_equity', 'N/A')}</span>
                    </div>
                    <div style='
                        background: #f8f9fa;
                        padding: 1rem;
                        border-radius: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span>Current Ratio</span>
                        <span style='
                            font-weight: bold;
                            color: #ff9800;
                        '>{financial_results.get('current_ratio', 'N/A')}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Overall Financial Health Summary -->
        <div style='
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            border-radius: 20px;
            padding: 2rem;
            margin-top: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        '>
            <h3 style='
                font-size: 1.8rem;
                margin-bottom: 1rem;
                color: white;
            '>Overall Financial Health</h3>
            <div style='
                display: flex;
                justify-content: center;
                gap: 2rem;
                flex-wrap: wrap;
                margin-top: 1rem;
            '>
                <div style='
                    background: rgba(255,255,255,0.1);
                    padding: 1rem 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                '>
                    <div style='font-size: 1.2rem; opacity: 0.9;'>Growth Rate</div>
                    <div style='font-size: 1.8rem; font-weight: bold;'>{financial_results.get('growth_rate', 'N/A')}%</div>
                </div>
                <div style='
                    background: rgba(255,255,255,0.1);
                    padding: 1rem 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                '>
                    <div style='font-size: 1.2rem; opacity: 0.9;'>Market Trend</div>
                    <div style='font-size: 1.8rem; font-weight: bold;'>{financial_results.get('trend', 'N/A').title()}</div>
                </div>
                <div style='
                    background: rgba(255,255,255,0.1);
                    padding: 1rem 2rem;
                    border-radius: 15px;
                    backdrop-filter: blur(5px);
                '>
                    <div style='font-size: 1.2rem; opacity: 0.9;'>Volatility</div>
                    <div style='font-size: 1.8rem; font-weight: bold;'>{financial_results.get('volatility', 'N/A').title()}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Update session state
    st.session_state.analysis_complete = True
    st.session_state.company_data = final_data

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
            
            # Investment Recommendation
            st.subheader("Investment Recommendation")
            
            # Determine recommendation based on overall score
            if overall_score >= 8.0:
                recommendation = "Strongly Recommended"
                color = "#00c853"
                icon = "⭐⭐⭐⭐⭐"
            elif overall_score >= 7.0:
                recommendation = "Recommended"
                color = "#64dd17"
                icon = "⭐⭐⭐⭐"
            elif overall_score >= 6.0:
                recommendation = "Neutral"
                color = "#ffd600"
                icon = "⭐⭐⭐"
            else:
                recommendation = "Not Recommended"
                color = "#ff1744"
                icon = "⚠️"
            
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(26, 35, 126, 0.98) 0%, rgba(13, 71, 161, 0.98) 100%);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 3rem;
                margin: 3rem 0;
                color: white;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.1);
            '>
                <h2 style='text-align: center; font-size: 2.5rem; margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                    Investment Recommendation
                </h2>
                <div style='
                    background: rgba(255,255,255,0.1);
                    backdrop-filter: blur(5px);
                    border-radius: 20px;
                    padding: 2.5rem;
                    text-align: center;
                    margin: 2rem 0;
                    border: 1px solid rgba(255,255,255,0.2);
                '>
                    <div style='font-size: 3.5rem; margin-bottom: 1.5rem;'>{icon}</div>
                    <div style='font-size: 2.5rem; color: {color}; margin-bottom: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
                        {recommendation}
                    </div>
                    <div style='font-size: 1.8rem; opacity: 0.9;'>Overall Score: {overall_score:.1f}/10</div>
                    <div style='
                        background: rgba(255,255,255,0.1);
                        height: 10px;
                        border-radius: 10px;
                        margin-top: 1.5rem;
                        overflow: hidden;
                    '>
                        <div style='
                            width: {overall_score*10}%;
                            height: 100%;
                            background: {color};
                            border-radius: 10px;
                            transition: width 1s ease;
                        '></div>
                    </div>
                </div>
                <div style='
                    background: white;
                    border-radius: 20px;
                    padding: 2rem;
                    margin-top: 2rem;
                    color: #333;
                '>
                    <h3 style='
                        color: #1a237e;
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                        font-size: 1.5rem;
                    '>
                        <span>🤖</span>
                        AI Investment Analysis
                    </h3>
                    <p style='
                        font-size: 1.1rem;
                        line-height: 1.6;
                        color: #555;
                    '>
                        Based on comprehensive analysis of ESG metrics, SDG alignment, and market sentiment,
                        {company_name} shows {
                        'exceptional' if overall_score >= 8.0 else
                        'strong' if overall_score >= 7.0 else
                        'moderate' if overall_score >= 6.0 else
                        'concerning'
                        } performance in sustainable and responsible business practices.
                        {
                        'The company demonstrates leadership in ESG initiatives and maintains strong stakeholder relationships.' if overall_score >= 8.0 else
                        'The company shows commitment to sustainability with room for improvement in some areas.' if overall_score >= 7.0 else
                        'While there are positive aspects, significant improvements are needed in key areas.' if overall_score >= 6.0 else
                        'Substantial improvements are needed across multiple dimensions before considering investment.'
                        }
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Update session state
            st.session_state.analysis_complete = True
            st.session_state.company_data = final_data
            
        except Exception as e:
            st.error(f"Error analyzing company: {str(e)}")
            print(f"Analysis error: {str(e)}")
            traceback.print_exc()
            st.session_state.analysis_complete = False

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
            st.session_state.current_company = company_name
            st.session_state.current_ticker = ticker
            analyze_company()

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

else:  # Methodology page
    display_methodology()

# Add this at the end of your file
if st.session_state.analysis_complete:
    st.sidebar.success(f"Currently analyzing: {st.session_state.current_company} ({st.session_state.current_ticker})")
    if st.sidebar.button("Clear Analysis"):
        st.session_state.analysis_complete = False
        st.session_state.company_data = None
        st.session_state.current_company = None
        st.session_state.current_ticker = None
        st.rerun() 
